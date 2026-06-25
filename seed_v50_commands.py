def handle_v50_command(command):
    cmd = (command or "").strip().split()[0].lower()

    if cmd == "/v50-help":
        print("""
=== SEED v50 COMMANDS — NOTHING LEFT BEHIND ===
/v50-check
/v50-status
/full-update
/update-ledger
/command-map
/dust-check
/repo-notebooks
/memory-bootstrap
/workflow-templates
/system-export
/seed-doctor

Core shortcuts:
/terminal-pro
/control-plane
/v45-check
/v30-check
""")
        return "handled"

    mapping = {
        "/v50-check": ("seed_v50_gate", "show_v50_gate"),
        "/v50-status": ("seed_nothing_left_behind_v50", "show_full_update"),
        "/full-update": ("seed_nothing_left_behind_v50", "show_full_update"),
        "/update-ledger": ("seed_nothing_left_behind_v50", "show_update_ledger"),
        "/command-map": ("seed_nothing_left_behind_v50", "show_command_map"),
        "/dust-check": ("seed_nothing_left_behind_v50", "show_dust_check"),
        "/repo-notebooks": ("seed_nothing_left_behind_v50", "show_repo_notebooks"),
        "/memory-bootstrap": ("seed_nothing_left_behind_v50", "show_memory_bootstrap"),
        "/workflow-templates": ("seed_nothing_left_behind_v50", "show_workflow_templates"),
        "/system-export": ("seed_nothing_left_behind_v50", "show_system_export"),
        "/seed-doctor": ("seed_nothing_left_behind_v50", "show_seed_doctor"),
    }

    if cmd in mapping:
        module_name, function_name = mapping[cmd]
        module = __import__(module_name, fromlist=[function_name])
        getattr(module, function_name)()
        return "handled"

    return None
