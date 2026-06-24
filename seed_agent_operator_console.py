import json


def agent_operator_home():
    try:
        from seed_agent_run_lifecycle import list_agent_runs, detect_agent_tools
        runs = list_agent_runs(limit=10)
        tools = detect_agent_tools()
    except Exception as error:
        return {
            "ok": False,
            "error": str(error)
        }

    available_tools = [
        name for name, data in tools.items()
        if data.get("available")
    ]

    return {
        "ok": True,
        "version": "v2.6.0",
        "title": "Seed Agent Operator Console",
        "available_agent_tools": available_tools,
        "recent_runs": runs.get("runs", []),
        "rules": [
            "supervised only",
            "approval token required",
            "safe internal execution first",
            "external agents locked by default",
            "no auto-edit",
            "no auto-commit"
        ],
        "commands": [
            "/agent-tools-real",
            "/agent-run-create",
            "/agent-run-list",
            "/agent-run-show",
            "/agent-run-approve",
            "/agent-run-execute"
        ]
    }


def show_agent_operator_home():
    print("\n=== SEED AGENT OPERATOR CONSOLE ===")
    print(json.dumps(agent_operator_home(), indent=4))


def agent_operator_context(user_prompt=""):
    home = agent_operator_home()
    if not home.get("ok"):
        return f"=== AGENT OPERATOR CONSOLE ===\nUnavailable: {home.get('error')}\n"

    return (
        "=== AGENT OPERATOR CONSOLE ===\n"
        f"Available agent tools: {', '.join(home.get('available_agent_tools', [])) or 'none'}\n"
        f"Recent runs: {len(home.get('recent_runs', []))}\n"
        "Rules: approval token required, no auto-edit, no auto-commit, external agents locked by default.\n"
    )


if __name__ == "__main__":
    show_agent_operator_home()
