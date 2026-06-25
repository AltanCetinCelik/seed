def handle_v30_command(command):
    cmd = (command or "").strip().split()[0].lower()

    if cmd == "/v30-help":
        print("""
=== SEED v30 COMMANDS ===
/v30-check
/agent-hq
/repo-assimilate
/repo-scoreboard
/repo-patterns
/repo-risks
/adapter-registry
/repo-to-seed-plan
""")
        return "handled"

    if cmd == "/v30-check":
        from seed_v30_megapatch_gate import show_v30_gate
        show_v30_gate()
        return "handled"

    if cmd == "/agent-hq":
        from seed_agent_hq_v30 import show_agent_hq_fast
        show_agent_hq_fast()
        return "handled"

    if cmd == "/repo-assimilate":
        from seed_repo_assimilation_engine import show_repo_assimilation
        show_repo_assimilation()
        return "handled"

    if cmd == "/repo-scoreboard":
        from seed_integration_scoreboard import show_scoreboard
        show_scoreboard()
        return "handled"

    if cmd == "/adapter-registry":
        from seed_external_adapter_registry import show_adapter_registry
        show_adapter_registry()
        return "handled"

    if cmd == "/repo-to-seed-plan":
        from seed_repo_to_seed_planner import show_repo_to_seed_plan
        show_repo_to_seed_plan()
        return "handled"

    if cmd == "/repo-patterns":
        from seed_repo_assimilation_engine import discover_repos
        from seed_repo_pattern_extractor import extract_repo_patterns
        repos = discover_repos()
        print("\n=== SEED REPO PATTERNS ===")
        for repo in repos[:25]:
            data = extract_repo_patterns(repo)
            print(f"- {data['name']}: {data['patterns']} docs={data['docs_found']}")
        return "handled"

    if cmd == "/repo-risks":
        from seed_repo_assimilation_engine import discover_repos
        from seed_repo_risk_scanner import scan_repo_risks
        repos = discover_repos()
        print("\n=== SEED REPO RISKS ===")
        for repo in repos[:25]:
            data = scan_repo_risks(repo)
            print(f"- {data['name']}: risk={data['risk_level']} score={data['risk_score']} totals={data['risk_totals']}")
        return "handled"

    return None
