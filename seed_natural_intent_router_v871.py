def norm(text):
    return " ".join(str(text or "").strip().lower().split())

def handle_natural_intent_v871(user_message):
    raw = str(user_message or "").strip()
    text = norm(raw)
    if not text or raw.startswith("/"):
        return None

    if any(p in text for p in ["v87.1 status", "wake conversation status"]):
        from seed_v871_systems import show_v871_status
        show_v871_status()
        return "handled"

    if any(p in text for p in ["start alive mode", "start companion mode", "be alive"]):
        from seed_alive_runtime_v871 import start_alive
        start_alive()
        return "handled"

    if any(p in text for p in ["stop alive mode", "stop companion mode"]):
        from seed_alive_runtime_v871 import stop_alive
        stop_alive()
        return "handled"

    if any(p in text for p in ["start wake listener", "start polished wake listener", "start wake conversation"]):
        from seed_wake_word_v871 import start_daemon
        print(start_daemon())
        return "handled"

    if any(p in text for p in ["stop wake listener", "stop polished wake listener", "stop wake conversation"]):
        from seed_wake_word_v871 import stop_daemon
        print(stop_daemon())
        return "handled"

    if any(p in text for p in ["wake conversation once", "test wake conversation"]):
        from seed_wake_conversation_v871 import wake_conversation_once
        print(wake_conversation_once())
        return "handled"

    if any(p in text for p in ["speak curiosity", "say curiosity", "talk to me first"]):
        from seed_curiosity_life_v871 import speak_curiosity
        print(speak_curiosity(force=True))
        return "handled"

    return None
