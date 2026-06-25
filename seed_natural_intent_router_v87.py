def norm(text):
    return " ".join(str(text or "").strip().lower().split())

def handle_natural_intent_v87(user_message):
    raw = str(user_message or "").strip()
    text = norm(raw)
    if not text or raw.startswith("/"):
        return None

    if any(p in text for p in ["v87 status", "alive companion status"]):
        from seed_v87_systems import show_v87_status
        show_v87_status()
        return "handled"

    if any(p in text for p in ["alive status", "are you alive", "companion status"]):
        from seed_alive_runtime_v87 import show_alive
        show_alive()
        return "handled"

    if any(p in text for p in ["start alive mode", "be alive", "wake and curiosity on", "start companion mode"]):
        from seed_alive_runtime_v87 import start_alive
        start_alive()
        return "handled"

    if any(p in text for p in ["stop alive mode", "stop companion mode"]):
        from seed_alive_runtime_v87 import stop_alive
        stop_alive()
        return "handled"

    if any(p in text for p in ["curiosity status", "show curiosity", "what are you curious about"]):
        from seed_curiosity_life_v87 import show_curiosity
        show_curiosity()
        return "handled"

    if any(p in text for p in ["speak curiosity", "say curiosity", "talk to me first", "say something curious"]):
        from seed_curiosity_life_v87 import speak_curiosity
        print(speak_curiosity(force=True))
        return "handled"

    if any(p in text for p in ["start curiosity loop", "start curious loop"]):
        from seed_curiosity_life_v87 import start_daemon
        print(start_daemon())
        return "handled"

    if any(p in text for p in ["stop curiosity loop", "stop curious loop"]):
        from seed_curiosity_life_v87 import stop_daemon
        print(stop_daemon())
        return "handled"

    if any(p in text for p in ["look at screen", "see my screen", "screen sense", "what can you see"]):
        from seed_senses_v87 import capture_screen
        print(capture_screen())
        return "handled"

    if any(p in text for p in ["sense status", "senses status", "can you see"]):
        from seed_senses_v87 import show_senses
        show_senses()
        return "handled"

    if any(p in text for p in ["wake polish status", "polished wake status"]):
        from seed_wake_word_v861 import show_status
        show_status()
        return "handled"

    if any(p in text for p in ["start polished wake listener", "start better wake listener"]):
        from seed_wake_word_v861 import start_daemon
        print(start_daemon())
        return "handled"

    if any(p in text for p in ["stop polished wake listener", "stop better wake listener"]):
        from seed_wake_word_v861 import stop_daemon
        print(stop_daemon())
        return "handled"

    return None
