import json
from datetime import datetime

try:
    from seed_config import SEED_TOOL_ROUTER_TRACE_FILE
except Exception:
    SEED_TOOL_ROUTER_TRACE_FILE = "seed_tool_router_trace.jsonl"

try:
    from seed_repo_arsenal import search_arsenal, get_repo_arsenal
except Exception:
    search_arsenal = None
    get_repo_arsenal = None

try:
    from seed_trace_engine import append_trace
    TRACE_AVAILABLE = True
except Exception:
    TRACE_AVAILABLE = False


CAPABILITY_RULES = [
    {
        "capability": "coding",
        "keywords": ["code", "bug", "repo", "edit", "implement", "feature", "fix", "tests", "python", "javascript"],
        "recommended_tools": ["openhands", "swe_agent", "aider", "cline"],
        "approval": "required_for_write_or_shell",
        "risk": "file_write_and_shell",
        "sandbox": "git branch, backup, py_compile/tests, rollback"
    },
    {
        "capability": "browser",
        "keywords": ["browser", "webpage", "website", "click", "online", "search page", "form"],
        "recommended_tools": ["browser_use", "mcp"],
        "approval": "required_for_external_web_or_account_actions",
        "risk": "external_web_action",
        "sandbox": "no account actions, no purchases, explicit scope"
    },
    {
        "capability": "memory",
        "keywords": ["memory", "remember", "vector", "semantic", "rag", "recall", "retrieve"],
        "recommended_tools": ["mem0", "qdrant", "pgvector", "llamaindex"],
        "approval": "required_for_migration_or_memory_write",
        "risk": "memory_write",
        "sandbox": "export current memory, test retrieval, rollback JSON state"
    },
    {
        "capability": "voice",
        "keywords": ["voice", "speak", "stt", "tts", "microphone", "whisper", "audio"],
        "recommended_tools": ["livekit_agents", "pipecat", "faster_whisper", "kokoro_tts", "chatterbox_tts"],
        "approval": "required_for_microphone_or_realtime_voice",
        "risk": "audio_io",
        "sandbox": "push-to-talk only, no always-listening, local test first"
    },
    {
        "capability": "avatar",
        "keywords": ["avatar", "3d", "vrm", "godot", "visual", "face", "world"],
        "recommended_tools": ["godot", "openavatarchat", "three_vrm"],
        "approval": "required_for_large_dependency",
        "risk": "frontend_or_large_dependency",
        "sandbox": "separate prototype folder, no core rewrite"
    },
    {
        "capability": "safety",
        "keywords": ["guardrail", "safety", "policy", "validation", "refuse", "schema"],
        "recommended_tools": ["nemo_guardrails", "guardrails_ai"],
        "approval": "required_for_policy_layer_changes",
        "risk": "policy_dependency",
        "sandbox": "test on sample prompts before enabling"
    },
    {
        "capability": "observability",
        "keywords": ["trace", "logs", "metrics", "observability", "debug", "analytics"],
        "recommended_tools": ["langfuse", "opentelemetry"],
        "approval": "required_for_external_telemetry",
        "risk": "telemetry",
        "sandbox": "local/private first, no secret upload"
    },
    {
        "capability": "agent_graph",
        "keywords": ["agent", "workflow", "graph", "planner", "orchestration", "multi-agent"],
        "recommended_tools": ["langgraph", "mastra"],
        "approval": "required_for_architecture_rewrite",
        "risk": "code_dependency",
        "sandbox": "prototype wrapper before core migration"
    }
]


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def append_router_trace(data):
    try:
        with open(SEED_TOOL_ROUTER_TRACE_FILE, "a") as file:
            file.write(json.dumps(data) + "\n")
    except Exception:
        pass


def route_task(task):
    text = task.lower()
    matches = []

    for rule in CAPABILITY_RULES:
        score = 0
        for keyword in rule["keywords"]:
            if keyword in text:
                score += 1

        if score:
            item = dict(rule)
            item["score"] = score
            matches.append(item)

    if not matches:
        matches = [{
            "capability": "general",
            "recommended_tools": [],
            "approval": "depends_on_action",
            "risk": "unknown",
            "sandbox": "ask clarifying question or use normal chat",
            "score": 0
        }]

    matches = sorted(matches, key=lambda item: item["score"], reverse=True)
    best = matches[0]

    repos = []
    if get_repo_arsenal:
        arsenal = get_repo_arsenal()
        ids = set(best.get("recommended_tools", []))
        repos = [repo for repo in arsenal if repo.get("id") in ids]

    route = {
        "created_at": now_timestamp(),
        "task": task,
        "best_capability": best.get("capability"),
        "risk": best.get("risk"),
        "approval": best.get("approval"),
        "sandbox": best.get("sandbox"),
        "recommended_tools": best.get("recommended_tools", []),
        "recommended_repos": repos,
        "all_matches": matches,
        "execution_policy": "recommend_and_plan_only_until_user_approves"
    }

    append_router_trace(route)

    if TRACE_AVAILABLE:
        try:
            append_trace(
                trace_type="tool_trace",
                title="Tool router decision",
                summary=json.dumps(route, indent=2)[:2500],
                sources=["tool_router", "repo_arsenal"],
                decision="routed",
                risk=route.get("risk")
            )
        except Exception:
            pass

    return route


def show_tool_route():
    task = input("Task to route: ").strip()
    result = route_task(task)
    print("\n=== TOOL ROUTE ===")
    print(json.dumps(result, indent=4))


def get_tool_router_context_for_prompt(user_prompt=""):
    result = route_task(user_prompt or "general task")
    text = "=== TOOL ROUTER CONTEXT ===\n"
    text += f"Task route: {result.get('best_capability')}\n"
    text += f"Risk: {result.get('risk')}\n"
    text += f"Approval: {result.get('approval')}\n"
    text += f"Sandbox: {result.get('sandbox')}\n"
    text += f"Tools: {', '.join(result.get('recommended_tools', []))}\n"
    text += "Rule: recommend and plan only until Altan explicitly approves risky execution.\n"
    return text


if __name__ == "__main__":
    show_tool_route()
