def handle_v73_command(command):
    text = str(command or "").strip()
    cmd = text.split()[0].lower() if text else ""
    mapping = {
        "/v73-check": ("seed_v73_gate", "show_v73_gate"),
        "/v73-status": ("seed_v73_systems", "show_v73_status"),
        "/express": ("seed_expressive_state_v73", "show_expression"),
        "/memory-actions": ("seed_memory_review_actions_v73", "show_memory_review"),
        "/voice-live": ("seed_voice_live_v73", "show_voice_live_status"),
        "/avatar-panel": ("seed_avatar_panel_v73", "open_avatar_panel"),
        "/action-tasks": ("seed_task_converter_v73", "show_tasks"),
        "/speak-curiosity": ("seed_curiosity_speaker_v73", "say_curiosity"),
    }
    if cmd == "/v73-help":
        print("v73 debug: /v73-check /v73-status /express /memory-actions /voice-live /avatar-panel /action-tasks /speak-curiosity")
        return "handled"
    if cmd in mapping:
        module_name, fn_name = mapping[cmd]
        module = __import__(module_name, fromlist=[fn_name])
        getattr(module, fn_name)()
        return "handled"
    if text.lower().startswith("memory "):
        from seed_memory_review_actions_v73 import handle_memory_action
        return handle_memory_action(text)
    if text.lower().startswith("voice once"):
        from seed_voice_live_v73 import voice_once
        parts = text.split()
        seconds = 5
        if len(parts) >= 3:
            try: seconds = int(parts[2])
            except Exception: pass
        voice_once(seconds)
        return "handled"
    return None
