import json
from datetime import datetime


try:
    from seed_config import SEED_REPO_TO_SEED_PLAN_FILE
except Exception:
    SEED_REPO_TO_SEED_PLAN_FILE = "seed_repo_to_seed_plan.json"


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def plan_for_item(item):
    adapters = item.get("adapters", [])
    risk = item.get("risk")
    mode = item.get("integration_mode")

    steps = [
        "read README/docs/examples",
        "extract useful architecture pattern",
        "write Seed adapter module",
        "run py_compile",
        "run relevant gate",
        "show in Control Plane",
        "promote only after manual approval"
    ]

    if "aider" in adapters:
        steps = [
            "wire into Aider review cockpit",
            "checkpoint target files",
            "run Aider dry-run",
            "capture diff/test output",
            "manual approval",
            "real patch",
            "gate and rollback if needed"
        ]

    if "browser-use" in adapters:
        steps = [
            "create read-only browser session adapter",
            "block login/forms/purchases",
            "log every page/action",
            "summarize page",
            "manual approval for any interactive action"
        ]

    if "openhands" in adapters or "swe-agent" in adapters:
        steps = [
            "create isolated sandbox run directory",
            "generate issue/task spec",
            "run agent only in sandbox",
            "compare plan against Aider",
            "manual promotion into core"
        ]

    if "mem0" in adapters or "qdrant" in adapters:
        steps = [
            "create memory extraction candidate",
            "store with confidence/source",
            "semantic retrieval test",
            "memory review/forget queue",
            "promote to Memory v2"
        ]

    if "livekit" in adapters or "pipecat" in adapters:
        steps = [
            "push-to-talk first",
            "transcript journal",
            "intent route",
            "TTS response",
            "only later realtime daemon"
        ]

    return {
        "repo": item.get("repo"),
        "name": item.get("name"),
        "priority_score": item.get("score"),
        "risk": risk,
        "mode": mode,
        "adapters": adapters,
        "steps": steps,
        "blocked_actions": [
            "blind install",
            "direct core mutation by external agent",
            "arbitrary shell",
            "delete",
            "auto-commit"
        ]
    }


def build_repo_to_seed_plan():
    from seed_integration_scoreboard import build_integration_scoreboard

    board = build_integration_scoreboard()
    plans = [plan_for_item(item) for item in board.get("top_20", [])]

    output = {
        "created_at": now_timestamp(),
        "version": "v30.0.0",
        "ok": True,
        "plans": plans,
        "next_best_integrations": plans[:8]
    }

    with open(SEED_REPO_TO_SEED_PLAN_FILE, "w") as file:
        json.dump(output, file, indent=4)

    return output


def show_repo_to_seed_plan():
    data = build_repo_to_seed_plan()
    print("\n=== SEED REPO → SEED PLAN v30 ===")
    for plan in data["next_best_integrations"]:
        print(f"\n{plan['name']} score={plan['priority_score']} risk={plan['risk']} adapters={plan['adapters']}")
        for step in plan["steps"][:6]:
            print(f"  - {step}")


if __name__ == "__main__":
    show_repo_to_seed_plan()
