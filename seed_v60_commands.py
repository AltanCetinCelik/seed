def handle_v60_command(command):
    cmd = (command or "").strip().split()[0].lower()

    mapping = {
        "/v60-check": ("seed_v60_gate", "show_v60_gate"),
        "/v60-status": ("seed_v60_systems", "show_v60_status"),
        "/model-manager": ("seed_model_manager_v60", "show_model_manager"),
        "/model-router": ("seed_model_manager_v60", "show_model_router"),
        "/model-benchmark": ("seed_model_manager_v60", "show_model_benchmark"),
        "/model-role-map": ("seed_model_manager_v60", "show_model_role_map"),
        "/fusion-lab": ("seed_hermes_moltbot_fusion_v60", "show_fusion_lab"),
        "/memory-auto-extract": ("seed_memory_auto_extractor_v60", "show_memory_auto_extract"),
        "/memory-auto-promote": ("seed_memory_auto_extractor_v60", "show_memory_auto_promote"),
        "/presence-rituals": ("seed_presence_rituals_v60", "show_rituals"),
        "/daily-brief": ("seed_presence_rituals_v60", "show_daily_brief"),
        "/palette": ("seed_command_palette_v60", "show_palette"),
        "/aider-self-improve": ("seed_aider_self_improvement_v60", "show_self_improvement_v60"),
        "/aider-self-improve-new": ("seed_aider_self_improvement_v60", "show_self_improvement_new"),
        "/aider-self-improve-approve": ("seed_aider_self_improvement_v60", "show_self_improvement_approve"),
    }

    if cmd == "/v60-help":
        from seed_command_palette_v60 import show_palette
        show_palette()
        print("\nDebug commands still exist, but normal use should be natural language.")
        return "handled"

    if cmd in mapping:
        module_name, function_name = mapping[cmd]
        module = __import__(module_name, fromlist=[function_name])
        getattr(module, function_name)()
        return "handled"

    return None
