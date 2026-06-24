import json
from datetime import datetime
from pathlib import Path


try:
    from seed_config import SEED_REFERENCE_FUSION_STATE_FILE
except Exception:
    SEED_REFERENCE_FUSION_STATE_FILE = "seed_reference_fusion_state.json"


PUBLIC_REFERENCE_STACK = {
    "brain_workflow": {
        "primary": ["LangGraph"],
        "borrow": ["durable stateful workflows", "human-in-the-loop checkpoints", "graph-style routing"],
        "seed_use": "intent → recall → route → approval → action → verification → reply"
    },
    "memory": {
        "primary": ["Mem0", "Qdrant", "LlamaIndex"],
        "borrow": ["long-term personalized memory", "semantic retrieval", "memory lifecycle"],
        "seed_use": "memory garden, semantic recall, user-approved timeline"
    },
    "voice": {
        "primary": ["Pipecat", "LiveKit Agents", "faster-whisper", "Kokoro", "Chatterbox"],
        "borrow": ["real-time voice loop", "interruptions", "low-latency STT→LLM→TTS"],
        "seed_use": "explicit voice session, natural spoken UX, no secret always-listening"
    },
    "tool_protocol": {
        "primary": ["MCP Servers"],
        "borrow": ["standard tool/resource/prompt gateway", "server configuration patterns"],
        "seed_use": "official Seed skill/plugin layer with approval gates"
    },
    "coding_agents": {
        "primary": ["OpenHands", "Aider", "SWE-agent", "mini-SWE-agent"],
        "borrow": ["agent canvas", "microagents", "repo task workflow", "test/diff loop"],
        "seed_use": "safe coding control center with approval, branch, tests, diff, rollback"
    },
    "browser_agent": {
        "primary": ["browser-use"],
        "borrow": ["browser task planning", "web-page actions", "recovery loops"],
        "seed_use": "approval-gated browser research/action bridge"
    },
    "cockpit_ui": {
        "primary": ["Open WebUI", "LibreChat", "AnythingLLM"],
        "borrow": ["self-hosted cockpit", "RAG workspace", "conversation search", "artifacts", "model routing"],
        "seed_use": "Seed cockpit with modes, memory, tools, traces, and companion surface"
    },
    "local_companion": {
        "primary": ["Moltbot AI Assistant", "OpenClaw", "Moltworker", "Hermes Agent"],
        "borrow": ["local-first assistant", "multi-channel inbox", "multi-agent routing", "control plane"],
        "seed_use": "Seed as always-available local companion shell"
    },
    "avatar_world": {
        "primary": ["Godot", "three-vrm", "OpenAvatarChat"],
        "borrow": ["memory garden", "companion room", "avatar presence"],
        "seed_use": "visual companion space after core UX is smooth"
    },
    "safety_observability": {
        "primary": ["NeMo Guardrails", "Guardrails AI", "Langfuse", "OpenTelemetry"],
        "borrow": ["guardrails", "output validation", "traces", "debuggability"],
        "seed_use": "why Seed said/did this, risk logs, approval trace"
    }
}


FRIEND_ADVICE_RULES = [
    {
        "id": "friend-001",
        "rule": "Do not install everything blindly.",
        "seed_policy": "Seed may know the arsenal, but must route tools through approval, sandboxing, and tests."
    },
    {
        "id": "friend-002",
        "rule": "Use coding agents only through safe edit flow.",
        "seed_policy": "Coding agents require approval, branch/backup, tests, diff review, and rollback."
    },
    {
        "id": "friend-003",
        "rule": "Memory should upgrade gradually.",
        "seed_policy": "Keep working memory alive while adding retrieval/vector layers."
    },
    {
        "id": "friend-004",
        "rule": "Voice must remain explicit.",
        "seed_policy": "Voice starts only from visible user launch; no secret always-listening."
    },
    {
        "id": "friend-005",
        "rule": "Browser and external tools require permission.",
        "seed_policy": "External/account/browser actions require clear user approval."
    }
]


REFERENCE_PRIORITY = [
    "smooth command center",
    "mode-aware companion behavior",
    "semantic memory + life timeline",
    "MCP skill system",
    "coding agent control center",
    "browser research/action bridge",
    "real-time voice pipeline",
    "cockpit/desktop presence",
    "avatar/world/memory garden"
]


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def safe_save_json(path, data):
    with open(path, "w") as file:
        json.dump(data, file, indent=4)


def read_optional_file(path):
    p = Path(path)
    if not p.exists():
        return ""
    try:
        return p.read_text(errors="ignore")[:12000]
    except Exception:
        return ""


def load_local_dna_summary():
    candidates = [
        "seed_research/OPEN_SOURCE_DNA_REPORT.md",
        "seed_research/open_source_dna.json"
    ]

    found = []
    for candidate in candidates:
        text = read_optional_file(candidate)
        if text:
            found.append({
                "path": candidate,
                "chars": len(text),
                "preview": text[:1200]
            })

    return found


def build_reference_fusion_state():
    local_dna = load_local_dna_summary()

    state = {
        "created_at": now_timestamp(),
        "version": "v2.4.0",
        "goal": "Make Seed feel like a real local-first companion command center before doing usage fix packs.",
        "public_reference_stack": PUBLIC_REFERENCE_STACK,
        "friend_advice_rules": FRIEND_ADVICE_RULES,
        "reference_priority": REFERENCE_PRIORITY,
        "local_dna_sources": local_dna,
        "execution_policy": {
            "blind_installs": False,
            "copy_random_repo_code": False,
            "risky_tool_execution_without_approval": False,
            "safe_default": "study, adapt patterns, route through approval, verify results"
        }
    }

    safe_save_json(SEED_REFERENCE_FUSION_STATE_FILE, state)
    return state


def build_seed_almost_perfect_plan():
    state = build_reference_fusion_state()

    return {
        "created_at": now_timestamp(),
        "version": "v2.4.0",
        "title": "Seed Almost-Perfect Build Plan",
        "phase_now": "Experience Fusion Layer",
        "why_now": "Seed already has core gates, action kernel, semantic memory, and tool gateways. Now it needs a smooth assistant surface.",
        "milestones": [
            {
                "id": "ux-001",
                "name": "Jarvis Home",
                "result": "One command shows current mode, memory, tools, voice, cockpit, next actions."
            },
            {
                "id": "ux-002",
                "name": "Mode System",
                "result": "Seed changes behavior between Companion, Coding, Research, Focus, Guardian, Muse, Archive."
            },
            {
                "id": "ux-003",
                "name": "Reference Fusion",
                "result": "Seed knows which repo/tool pattern to borrow for each capability."
            },
            {
                "id": "ux-004",
                "name": "Smooth Natural Router",
                "result": "Natural commands like 'start coding mode' or 'show me what you can do' route correctly."
            },
            {
                "id": "ux-005",
                "name": "Control Plane",
                "result": "Seed surfaces actions, approvals, memory, traces, cockpit, and plans from one place."
            },
            {
                "id": "future-001",
                "name": "Real MCP Skill System",
                "result": "Filesystem/Git/browser skills become real approval-gated tools."
            },
            {
                "id": "future-002",
                "name": "Real-Time Voice Stack",
                "result": "Pipecat/LiveKit-style voice loop with interruptions and lower latency."
            },
            {
                "id": "future-003",
                "name": "Coding Agent Control Center",
                "result": "OpenHands/Aider/SWE-agent run safely with branch, tests, diff, approval."
            }
        ],
        "friend_rules_applied": [rule["id"] for rule in state["friend_advice_rules"]],
        "reference_stack_categories": list(state["public_reference_stack"].keys())
    }


def reference_fusion_context(user_prompt=""):
    state = build_reference_fusion_state()

    text = "=== SEED v2.4 REFERENCE FUSION CONTEXT ===\n"
    text += "Seed should behave like a smooth local-first companion command center, not just a menu.\n"
    text += "Reference priorities:\n"

    for item in REFERENCE_PRIORITY:
        text += f"- {item}\n"

    text += "\nFriend advice rules:\n"
    for rule in FRIEND_ADVICE_RULES:
        text += f"- {rule['id']}: {rule['seed_policy']}\n"

    text += "\nReference stack:\n"
    for key, value in PUBLIC_REFERENCE_STACK.items():
        text += f"- {key}: {', '.join(value['primary'])} → {value['seed_use']}\n"

    text += "\nRules:\n"
    text += "- Do not blindly install/copy repos.\n"
    text += "- Borrow architecture patterns first.\n"
    text += "- Route risky actions through approval gates.\n"
    text += "- Make UX smooth: modes, short answers, clear next action.\n"

    return text


def show_reference_fusion():
    state = build_reference_fusion_state()

    print("\n=== SEED REFERENCE FUSION ===")
    print(f"Version: {state['version']}")
    print(f"Goal: {state['goal']}")
    print("\nReference stack:")
    for key, value in state["public_reference_stack"].items():
        print(f"- {key}: {', '.join(value['primary'])}")
        print(f"  Seed use: {value['seed_use']}")

    print("\nFriend advice:")
    for rule in state["friend_advice_rules"]:
        print(f"- {rule['id']}: {rule['seed_policy']}")

    print("\nLocal DNA sources:")
    if not state["local_dna_sources"]:
        print("- none found")
    for source in state["local_dna_sources"]:
        print(f"- {source['path']} chars={source['chars']}")


def show_almost_perfect_plan():
    plan = build_seed_almost_perfect_plan()

    print("\n=== SEED ALMOST-PERFECT BUILD PLAN ===")
    print(f"Phase now: {plan['phase_now']}")
    print(plan["why_now"])

    print("\nMilestones:")
    for item in plan["milestones"]:
        print(f"- {item['id']} — {item['name']}")
        print(f"  {item['result']}")


if __name__ == "__main__":
    show_reference_fusion()
