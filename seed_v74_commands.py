def handle_v74_command(command):
    text=str(command or "").strip(); cmd=text.split()[0].lower() if text else ""
    mapping={"/v74-check":("seed_v74_gate","show_v74_gate"),"/v74-status":("seed_v74_systems","show_v74_status"),"/embodied-state":("seed_embodied_state_v74","show_embodied_state"),"/avatar-panel-state":("seed_avatar_panel_v74","show_avatar_panel"),"/memory-actions":("seed_memory_actions_v74","show_memory_actions"),"/action-tasks":("seed_action_tasks_v74","show_action_tasks")}
    if cmd=="/v74-help":
        print("v74: /v74-check /v74-status /embodied-state /avatar-panel-state /memory-actions /action-tasks. Natural: v74 status, open avatar panel, embodied panel, memory actions, action tasks.")
        return "handled"
    if cmd in mapping:
        m,f=mapping[cmd]; mod=__import__(m,fromlist=[f]); getattr(mod,f)(); return "handled"
    return None
