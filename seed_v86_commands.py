def handle_v86_command(command):
    text = str(command or "").strip()
    cmd = text.split()[0].lower() if text else ""

    mapping = {
        "/v86-check": ("seed_v86_gate", "show_v86_gate"),
        "/v86-status": ("seed_v86_systems", "show_v86_status"),
        "/wake-status": ("seed_wake_word_v86", "show_status"),
    }

    if cmd == "/v86-help":
        print("""
=== SEED v86 WAKE COMMANDS ===
Natural:
- wake status
- start wake listener
- stop wake listener
- wake listen
- wake phrases

Shell:
- python seed_wake_word_v86.py start
- python seed_wake_word_v86.py stop
- python seed_wake_word_v86.py listen
""")
        return "handled"

    if cmd in mapping:
        m, f = mapping[cmd]
        mod = __import__(m, fromlist=[f])
        getattr(mod, f)()
        return "handled"

    return None
