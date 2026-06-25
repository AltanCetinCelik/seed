import json
from datetime import datetime


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


COMMAND_GROUPS = {
    "Natural Companion Phrases": [
        "check yourself",
        "open dashboard",
        "show models",
        "benchmark models",
        "compare Hermes Moltbot OpenClaw",
        "extract memories",
        "save important memories",
        "what should we improve next",
        "show command palette",
    ],
    "Core Debug": [
        "/v60-check",
        "/v50-check",
        "/v45-check",
        "/v30-check",
        "/latency",
        "/quick-gates",
        "/final-gates",
    ],
    "Agent HQ": [
        "/agent-hq",
        "/repo-scoreboard",
        "/repo-to-seed-plan",
        "/adapter-registry",
        "/fusion-lab",
    ],
    "Models": [
        "/model-manager",
        "/model-router",
        "/model-benchmark",
        "/model-role-map",
    ],
    "Work": [
        "/workflow-status",
        "/workflow-new",
        "/workflow-tick",
        "/aider-cockpit",
        "/aider-cockpit-new",
        "/aider-self-improve",
    ],
    "Memory": [
        "/memory-brain",
        "/memory-index-runtime",
        "/memory-search",
        "/memory-auto-extract",
        "/memory-auto-promote",
    ],
    "Presence": [
        "/presence-status",
        "/presence-rituals",
        "/daily-brief",
        "/curiosity",
        "/presence-inbox",
    ],
    "Voice / Browser": [
        "/voice-max",
        "/voice-say",
        "/browser-readonly",
    ],
    "Maintenance": [
        "/task-stats",
        "/task-clean-test",
        "/task-dedupe",
        "/eval-lab",
        "/dust-check",
        "/command-map",
    ],
}


def status_snapshot():
    data = {"created_at": now_timestamp(), "version": "v60.0.0"}

    try:
        from seed_latency_probe import run_latency_probe
        data["latency"] = run_latency_probe()
    except Exception as error:
        data["latency_error"] = str(error)

    try:
        from seed_task_hygiene_v302 import task_stats
        data["tasks"] = task_stats()
    except Exception as error:
        data["task_error"] = str(error)

    try:
        from seed_agent_hq_v30 import build_agent_hq_fast
        hq = build_agent_hq_fast()
        data["agent_hq"] = {
            "agents": hq.get("agent_count"),
            "cache": hq.get("cache_mode"),
        }
    except Exception as error:
        data["agent_hq_error"] = str(error)

    try:
        from seed_model_manager_v60 import build_role_map_from_benchmark
        data["models"] = build_role_map_from_benchmark()
    except Exception as error:
        data["models_error"] = str(error)

    return data


def show_terminal_pro():
    print("\n" + "=" * 68)
    print("SEED TERMINAL PRO — NATURAL COMPANION MODE")
    print("=" * 68)

    snap = status_snapshot()
    latency = snap.get("latency", {}).get("results", {})
    tasks = snap.get("tasks", {})
    hq = snap.get("agent_hq", {})
    models = snap.get("models", {}).get("role_map", {})

    print("Version: v60.0.0")
    print(f"Prompt build: {latency.get('prompt_build_ms')}ms")
    print(f"Fast context: {latency.get('fast_context_ms')}ms")
    print(f"Tasks: total={tasks.get('total')} real_ready={tasks.get('ready_real')} test_ready={tasks.get('ready_test_or_gate')}")
    print(f"Agent HQ: agents={hq.get('agents')} cache={hq.get('cache')}")

    if models:
        print("\nModel Roles:")
        for role, model in models.items():
            print(f"  {role}: {model}")

    print("\nUse Seed naturally. Say things like:")
    for phrase in COMMAND_GROUPS["Natural Companion Phrases"]:
        print(f"  • {phrase}")

    print("\nHidden debug commands are still available when needed:")
    for group, commands in COMMAND_GROUPS.items():
        if group == "Natural Companion Phrases":
            continue
        print(f"\n[{group}]")
        print("  " + "  ".join(commands))

    print("\nTip: normal use = natural language. Debugging = slash commands.")
    print("=" * 68)


if __name__ == "__main__":
    show_terminal_pro()
