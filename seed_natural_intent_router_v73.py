def norm(x):
    return " ".join(str(x or "").strip().lower().split())

# v73.1 voice once precedence
try:
    from seed_live_voice_v731 import handle_voice_command_v731
except Exception:
    handle_voice_command_v731 = None

def handle_natural_intent_v73(user_message):
    raw = str(user_message or "").strip()
    text = norm(raw)
    if not text or raw.startswith("/"):
        return None
    if any(p in text for p in ["v73 status", "action presence status", "next big update status"]):
        from seed_v73_systems import show_v73_status
        return show_v73_status()
    if any(p in text for p in ["express", "show excitement", "simulated excitement", "celebrate"]):
        from seed_expressive_state_v73 import show_expression
        show_expression("success")
        return "handled"
    if any(p in text for p in ["memory actions", "review memory actions", "show top memories", "memory review actions"]):
        from seed_memory_review_actions_v73 import show_memory_review
        return show_memory_review()
    if any(p in text for p in ["open avatar panel", "avatar panel", "visual avatar"]):
        from seed_avatar_panel_v73 import open_avatar_panel
        return open_avatar_panel()
    if any(p in text for p in ["action tasks", "convert tasks", "repo tasks", "advice tasks"]):
        from seed_task_converter_v73 import show_tasks
        return show_tasks()
    if any(p in text for p in ["speak curiosity", "say curiosity", "tell me what you noticed aloud"]):
        from seed_curiosity_speaker_v73 import say_curiosity
        return say_curiosity()
    if any(p in text for p in ["voice live", "live voice", "voice once", "test voice"]):
        from seed_voice_live_v73 import show_voice_live_status
        show_voice_live_status()
        print("To record: type 'voice once' or 'voice once 8'.")
        return "handled"
    return None
