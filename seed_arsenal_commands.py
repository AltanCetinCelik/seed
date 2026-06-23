def print_arsenal_help():
    print("/repo-arsenal = show known repo/tool arsenal")
    print("/tool-arsenal = same as repo arsenal")
    print("/repo-map = show arsenal categories")
    print("/repo-search = search arsenal")
    print("/tool-route = route task to best tool/capability")
    print("/capability-match = build capability plan")
    print("/sandbox-plan = build sandbox/approval plan")
    print("/integration-readiness = show arsenal readiness")
    print("/integration-gate = run v1.19 arsenal integration gate")
    print("/friend-advice = show friend advice registry")
    print("/friend-advice-search = search friend advice")


def handle_arsenal_command(command, chat_state=None):
    command = command.strip()

    if command == "/repo-arsenal" or command == "/tool-arsenal":
        from seed_repo_arsenal import show_repo_arsenal
        show_repo_arsenal()
        return "handled"

    if command == "/repo-map":
        from seed_repo_arsenal import show_repo_map
        show_repo_map()
        return "handled"

    if command == "/repo-search":
        from seed_repo_arsenal import search_arsenal_interactive
        search_arsenal_interactive()
        return "handled"

    if command == "/tool-route":
        from seed_tool_router import show_tool_route
        show_tool_route()
        return "handled"

    if command == "/capability-match":
        from seed_capability_planner import show_capability_match
        show_capability_match()
        return "handled"

    if command == "/sandbox-plan":
        from seed_capability_planner import show_sandbox_plan
        show_sandbox_plan()
        return "handled"

    if command == "/integration-readiness":
        from seed_repo_arsenal import show_integration_readiness
        show_integration_readiness()
        return "handled"

    if command == "/integration-gate":
        from seed_integration_gate import show_integration_gate
        show_integration_gate()
        return "handled"

    if command == "/friend-advice":
        from seed_friend_advice_registry import show_friend_advice
        show_friend_advice()
        return "handled"

    if command == "/friend-advice-search":
        from seed_friend_advice_registry import search_friend_advice_interactive
        search_friend_advice_interactive()
        return "handled"

    return None
