import inspect
import json
from datetime import datetime


try:
    from seed_config import SEED_INTEGRATION_FUSION_FILE
except Exception:
    SEED_INTEGRATION_FUSION_FILE = "seed_integration_fusion.json"


REFERENCE_STACK = [
    {
        "id": "langgraph",
        "name": "LangGraph",
        "category": "orchestration",
        "copy_adapt_avoid": "adapt",
        "seed_fit": 8,
        "risk": 5,
        "priority": 8,
        "why": "Useful for durable multi-step workflows and agent graphs, but should be wrapped Seed-native."
    },
    {
        "id": "mastra",
        "name": "Mastra",
        "category": "orchestration",
        "copy_adapt_avoid": "adapt",
        "seed_fit": 6,
        "risk": 5,
        "priority": 5,
        "why": "Good design reference for agent workflows; avoid overfitting to JS stack."
    },
    {
        "id": "mem0",
        "name": "Mem0",
        "category": "memory",
        "copy_adapt_avoid": "adapt",
        "seed_fit": 9,
        "risk": 4,
        "priority": 9,
        "why": "Memory extraction/summarization patterns fit Seed strongly."
    },
    {
        "id": "qdrant",
        "name": "Qdrant",
        "category": "memory",
        "copy_adapt_avoid": "sandbox",
        "seed_fit": 8,
        "risk": 6,
        "priority": 7,
        "why": "Vector memory backend candidate; needs local service/install decision."
    },
    {
        "id": "llamaindex",
        "name": "LlamaIndex",
        "category": "memory_retrieval",
        "copy_adapt_avoid": "adapt",
        "seed_fit": 7,
        "risk": 5,
        "priority": 7,
        "why": "Useful RAG patterns; Seed should keep its own light local index first."
    },
    {
        "id": "livekit",
        "name": "LiveKit Agents",
        "category": "voice",
        "copy_adapt_avoid": "sandbox",
        "seed_fit": 8,
        "risk": 8,
        "priority": 7,
        "why": "Future real-time voice, but bigger dependency and networking stack."
    },
    {
        "id": "pipecat",
        "name": "Pipecat",
        "category": "voice",
        "copy_adapt_avoid": "sandbox",
        "seed_fit": 8,
        "risk": 8,
        "priority": 7,
        "why": "Great reference for real-time voice pipeline; prototype separately."
    },
    {
        "id": "faster-whisper",
        "name": "faster-whisper",
        "category": "voice",
        "copy_adapt_avoid": "keep",
        "seed_fit": 9,
        "risk": 4,
        "priority": 9,
        "why": "Already aligned with local voice transcription."
    },
    {
        "id": "kokoro",
        "name": "Kokoro",
        "category": "tts",
        "copy_adapt_avoid": "sandbox",
        "seed_fit": 8,
        "risk": 6,
        "priority": 7,
        "why": "Potential local TTS improvement; test voice quality separately."
    },
    {
        "id": "openhands",
        "name": "OpenHands",
        "category": "coding_agent",
        "copy_adapt_avoid": "sandbox",
        "seed_fit": 8,
        "risk": 9,
        "priority": 6,
        "why": "Powerful but high-risk broad agent; not first executor."
    },
    {
        "id": "aider",
        "name": "Aider",
        "category": "coding_agent",
        "copy_adapt_avoid": "integrate_first",
        "seed_fit": 9,
        "risk": 7,
        "priority": 9,
        "why": "Best first real coding executor due target-file workflow."
    },
    {
        "id": "browser-use",
        "name": "browser-use",
        "category": "browser_agent",
        "copy_adapt_avoid": "sandbox",
        "seed_fit": 7,
        "risk": 9,
        "priority": 5,
        "why": "Useful later, but browser actions must be approval-gated."
    },
    {
        "id": "mcp",
        "name": "MCP",
        "category": "tool_protocol",
        "copy_adapt_avoid": "integrate",
        "seed_fit": 9,
        "risk": 7,
        "priority": 8,
        "why": "Best way to expose Seed skills/tools cleanly."
    },
    {
        "id": "guardrails",
        "name": "Guardrails / NeMo Guardrails",
        "category": "safety",
        "copy_adapt_avoid": "adapt",
        "seed_fit": 8,
        "risk": 5,
        "priority": 8,
        "why": "Use policy patterns, not heavy dependency first."
    },
    {
        "id": "langfuse",
        "name": "Langfuse / OpenTelemetry",
        "category": "observability",
        "copy_adapt_avoid": "adapt",
        "seed_fit": 7,
        "risk": 5,
        "priority": 6,
        "why": "Trace/observability ideas fit Seed; keep local first."
    },
    {
        "id": "anythingllm",
        "name": "AnythingLLM / LibreChat",
        "category": "ui",
        "copy_adapt_avoid": "reference",
        "seed_fit": 6,
        "risk": 5,
        "priority": 5,
        "why": "Useful UX reference, but Seed now has custom Control Plane."
    }
]


FRIEND_ADVICE_RULES = [
    {
        "id": "local_first",
        "weight": 10,
        "rule": "Prefer local-first, inspectable, owner-controlled systems."
    },
    {
        "id": "small_core",
        "weight": 9,
        "rule": "Do not turn Seed into dependency soup; wrap external systems behind adapters."
    },
    {
        "id": "approval_gates",
        "weight": 10,
        "rule": "High-impact actions require approval, logs, and rollback."
    },
    {
        "id": "operator_clarity",
        "weight": 8,
        "rule": "Every feature should have a clear operator-facing command or panel."
    },
    {
        "id": "real_capability",
        "weight": 9,
        "rule": "Prefer features that make Seed actually do more, not just talk better."
    }
]


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def safe_module_probe(module_name):
    try:
        module = __import__(module_name)
        exported = []
        for name, value in module.__dict__.items():
            if name.startswith("_"):
                continue
            if inspect.isfunction(value):
                exported.append({"name": name, "type": "function"})
            elif isinstance(value, (list, dict, tuple, str, int, float, bool)):
                exported.append({"name": name, "type": type(value).__name__})
        return {"ok": True, "module": module_name, "exported": exported[:80]}
    except Exception as error:
        return {"ok": False, "module": module_name, "error": str(error)}


def score_candidate(item):
    fit = item.get("seed_fit", 5)
    risk = item.get("risk", 5)
    priority = item.get("priority", 5)

    advice_bonus = 0
    if item["copy_adapt_avoid"] in ["integrate", "integrate_first", "keep"]:
        advice_bonus += 2
    if risk >= 8:
        advice_bonus -= 2
    if item["category"] in ["memory", "voice", "coding_agent", "tool_protocol", "safety"]:
        advice_bonus += 1

    score = (fit * 2) + priority + advice_bonus - risk
    return max(0, min(20, score))


def decision_to_status(decision):
    if decision in ["integrate_first", "integrate", "keep"]:
        return "build_now"
    if decision in ["adapt"]:
        return "build_adapter"
    if decision in ["sandbox"]:
        return "sandbox_first"
    if decision in ["reference"]:
        return "reference_only"
    return "review"


def build_integration_fusion():
    module_probes = [
        safe_module_probe("seed_repo_arsenal"),
        safe_module_probe("seed_friend_advice_registry"),
        safe_module_probe("seed_tool_router"),
        safe_module_probe("seed_capability_planner"),
        safe_module_probe("seed_integration_gate"),
    ]

    candidates = []
    for item in REFERENCE_STACK:
        enriched = dict(item)
        enriched["score"] = score_candidate(item)
        enriched["status"] = decision_to_status(item["copy_adapt_avoid"])
        enriched["friend_advice_applied"] = [rule["id"] for rule in FRIEND_ADVICE_RULES]
        candidates.append(enriched)

    candidates = sorted(candidates, key=lambda x: (x["score"], x["priority"]), reverse=True)

    backlog = {
        "build_now": [x for x in candidates if x["status"] == "build_now"],
        "build_adapter": [x for x in candidates if x["status"] == "build_adapter"],
        "sandbox_first": [x for x in candidates if x["status"] == "sandbox_first"],
        "reference_only": [x for x in candidates if x["status"] == "reference_only"],
    }

    report = {
        "created_at": now_timestamp(),
        "version": "v3.5.0",
        "ok": True,
        "candidate_count": len(candidates),
        "friend_advice_rules": FRIEND_ADVICE_RULES,
        "module_probes": module_probes,
        "candidates": candidates,
        "backlog": backlog,
        "top_10": candidates[:10],
        "policy": {
            "copy_repo_code_directly": False,
            "adapter_first": True,
            "sandbox_high_risk": True,
            "approval_required": True,
            "no_auto_install": True
        }
    }

    with open(SEED_INTEGRATION_FUSION_FILE, "w") as file:
        json.dump(report, file, indent=4)

    return report


def integration_fusion_context(user_prompt=""):
    report = build_integration_fusion()
    lines = ["=== SEED INTEGRATION FUSION ==="]
    lines.append(f"Candidates: {report['candidate_count']}")
    lines.append("Top candidates:")
    for item in report["top_10"][:6]:
        lines.append(f"- {item['name']}: score={item['score']} status={item['status']}")
    return "\n".join(lines)


def show_integration_fusion():
    report = build_integration_fusion()

    print("\n=== SEED INTEGRATION FUSION ===")
    print(f"Candidates: {report['candidate_count']}")

    print("\nTop 10:")
    for item in report["top_10"]:
        print(f"- {item['name']} | score={item['score']} | status={item['status']} | decision={item['copy_adapt_avoid']}")
        print(f"  {item['why']}")


if __name__ == "__main__":
    show_integration_fusion()
