import json
from datetime import datetime


try:
    from seed_config import SEED_AGENT_HQ_FILE
except Exception:
    SEED_AGENT_HQ_FILE = "seed_agent_hq_v30.json"


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


AGENTS = {
    "aider_agent": {
        "status": "ready_guarded",
        "mission": "real patch executor",
        "tooling": ["Aider", "git diff", "gates"],
        "risk": "medium",
        "default_mode": "dry_run"
    },
    "browser_agent": {
        "status": "sandbox_planned",
        "mission": "read-only web research and page summaries",
        "tooling": ["browser-use"],
        "risk": "high",
        "default_mode": "read_only"
    },
    "memory_agent": {
        "status": "planned",
        "mission": "extract durable memories and semantic recall",
        "tooling": ["Mem0 patterns", "Qdrant optional"],
        "risk": "medium",
        "default_mode": "review_queue"
    },
    "voice_agent": {
        "status": "planned",
        "mission": "push-to-talk and realtime voice later",
        "tooling": ["faster-whisper", "LiveKit", "Pipecat"],
        "risk": "medium",
        "default_mode": "push_to_talk"
    },
    "workflow_agent": {
        "status": "seed_native",
        "mission": "durable goal/task workflow",
        "tooling": ["LangGraph patterns", "Seed Task OS"],
        "risk": "medium",
        "default_mode": "manual_tick"
    },
    "mcp_agent": {
        "status": "ready_guarded",
        "mission": "tool marketplace and permission layer",
        "tooling": ["MCP server/client"],
        "risk": "medium",
        "default_mode": "allowlist"
    },
    "openhands_agent": {
        "status": "sandbox_only",
        "mission": "heavy coding agent experiment",
        "tooling": ["OpenHands"],
        "risk": "high",
        "default_mode": "sandbox"
    },
    "swe_agent": {
        "status": "sandbox_only",
        "mission": "issue repair benchmark agent",
        "tooling": ["SWE-agent", "mini-swe-agent"],
        "risk": "high",
        "default_mode": "sandbox"
    },
    "ui_agent": {
        "status": "reference",
        "mission": "dashboard/workspace UX",
        "tooling": ["Open WebUI", "AnythingLLM", "Khoj"],
        "risk": "low",
        "default_mode": "pattern_reference"
    },
    "computer_control_agent": {
        "status": "blocked_until_sandbox",
        "mission": "computer-control harness",
        "tooling": ["Open Interpreter", "Cline patterns"],
        "risk": "very_high",
        "default_mode": "disabled"
    },
    "stateful_companion_agent": {
        "status": "reference",
        "mission": "stateful long-term companion architecture",
        "tooling": ["Letta patterns", "Seed Memory v2"],
        "risk": "medium",
        "default_mode": "pattern_reference"
    }
}


def build_agent_hq():
    try:
        from seed_integration_scoreboard import build_integration_scoreboard
        board = build_integration_scoreboard()
    except Exception as error:
        board = {"ok": False, "error": str(error), "top_20": []}

    try:
        from seed_repo_to_seed_planner import build_repo_to_seed_plan
        plans = build_repo_to_seed_plan()
    except Exception as error:
        plans = {"ok": False, "error": str(error), "next_best_integrations": []}

    hq = {
        "created_at": now_timestamp(),
        "version": "v30.0.0",
        "ok": True,
        "release": "Seed Agent HQ v30",
        "agents": AGENTS,
        "agent_count": len(AGENTS),
        "scoreboard_top": board.get("top_20", [])[:10],
        "next_best_integrations": plans.get("next_best_integrations", [])[:8],
        "control_loop": [
            "select agent",
            "policy check",
            "sandbox/checkpoint",
            "dry run",
            "review",
            "manual approval",
            "execute",
            "verify gate",
            "log and remember"
        ],
        "hard_rules": {
            "no_blind_installs": True,
            "no_arbitrary_shell": True,
            "no_delete": True,
            "no_auto_commit": True,
            "external_agents_sandbox_first": True,
            "aider_first_real_executor": True
        }
    }

    with open(SEED_AGENT_HQ_FILE, "w") as file:
        json.dump(hq, file, indent=4)

    return hq


def show_agent_hq():
    hq = build_agent_hq()
    print("\n=== SEED AGENT HQ v30 ===")
    print(f"Agents: {hq['agent_count']}")
    for name, spec in hq["agents"].items():
        print(f"- {name}: {spec['mission']} status={spec['status']} risk={spec['risk']}")

    print("\nNext best integrations:")
    for item in hq.get("next_best_integrations", [])[:8]:
        print(f"- {item.get('name')} score={item.get('priority_score')} risk={item.get('risk')}")


if __name__ == "__main__":
    show_agent_hq()

# v30.1 performance cache helpers.
def load_agent_hq_cached():
    from pathlib import Path
    import json

    path = Path(SEED_AGENT_HQ_FILE)
    if not path.exists():
        return None

    try:
        return json.loads(path.read_text(errors="ignore"))
    except Exception:
        return None


def build_agent_hq_fast():
    cached = load_agent_hq_cached()
    if cached:
        cached["cache_mode"] = "cached_fast"
        return cached

    # First run only: build actual HQ.
    return build_agent_hq()


def show_agent_hq_fast():
    hq = build_agent_hq_fast()
    print("\n=== SEED AGENT HQ v30 FAST ===")
    print(f"Agents: {hq.get('agent_count')}")
    print(f"Cache mode: {hq.get('cache_mode', 'fresh')}")
    for name, spec in (hq.get("agents") or {}).items():
        print(f"- {name}: {spec.get('mission')} status={spec.get('status')} risk={spec.get('risk')}")

    print("\nNext best integrations:")
    for item in hq.get("next_best_integrations", [])[:8]:
        print(f"- {item.get('name')} score={item.get('priority_score')} risk={item.get('risk')}")
