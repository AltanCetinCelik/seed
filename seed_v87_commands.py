def handle_v87_command(command):
    text = str(command or "").strip()
    cmd = text.split()[0].lower() if text else ""

    mapping = {
        "/v87-check": ("seed_v87_gate", "show_v87_gate"),
        "/v87-status": ("seed_v87_systems", "show_v87_status"),
        "/v87-self": ("seed_self_state_v87", "show_self_state"),
        "/alive": ("seed_alive_runtime_v87", "show_alive"),
        "/curiosity": ("seed_curiosity_life_v87", "show_curiosity"),
        "/senses": ("seed_senses_v87", "show_senses"),
        "/wake-polish": ("seed_wake_word_v861", "show_status"),
    }

    if cmd == "/v87-help":
        print("""
=== SEED v87 ALIVE COMPANION COMMANDS ===
Natural:
- v87 status
- alive status
- start alive mode
- stop alive mode
- curiosity status
- speak curiosity
- start curiosity loop
- stop curiosity loop
- look at screen
- sense status
- wake polish status
- start polished wake listener
- stop polished wake listener

Debug:
/v87-check /v87-status /v87-self /alive /curiosity /senses /wake-polish
""")
        return "handled"

    if cmd in mapping:
        m, f = mapping[cmd]
        mod = __import__(m, fromlist=[f])
        getattr(mod, f)()
        return "handled"

    return None
