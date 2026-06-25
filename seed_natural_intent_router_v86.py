def norm(text):
    return " ".join(str(text or "").strip().lower().split())

def handle_natural_intent_v86(user_message):
    raw = str(user_message or "").strip()
    text = norm(raw)
    if not text or raw.startswith("/"):
        return None

    if any(p in text for p in ["v86 status", "wake status", "wake word status"]):
        from seed_v86_systems import show_v86_status
        show_v86_status()
        return "handled"

    if any(p in text for p in ["start wake listener", "start wake word", "enable wake word", "wake daemon start"]):
        from seed_wake_word_v86 import start_daemon
        print(start_daemon())
        return "handled"

    if any(p in text for p in ["stop wake listener", "stop wake word", "disable wake word", "wake daemon stop"]):
        from seed_wake_word_v86 import stop_daemon
        print(stop_daemon())
        return "handled"

    if any(p in text for p in ["wake listen", "listen for seed", "foreground wake listener"]):
        from seed_wake_word_v86 import listen_loop
        listen_loop()
        return "handled"

    if any(p in text for p in ["wake phrases", "show wake phrases"]):
        from seed_wake_word_v86 import load_settings
        print(load_settings().get("wake_phrases", []))
        return "handled"

    return None
