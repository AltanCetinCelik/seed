def handle_v81_command(command):
    text = str(command or "").strip()
    parts = text.split()
    cmd = parts[0].lower() if parts else ""

    mapping = {
        "/v81-check": ("seed_v81_gate", "show_v81_gate"),
        "/v81-status": ("seed_v81_systems", "show_v81_status"),
        "/v81-self": ("seed_self_state_v81", "show_self_state"),
        "/voice2": ("seed_voice_v76", "show_voice_settings"),
        "/voice-journal": ("seed_voice_v76", "show_voice_journal"),
        "/presence": ("seed_proactive_v78", "show_proactive"),
        "/executor": ("seed_permission_executor_v79", "show_executor"),
        "/aider-loop": ("seed_aider_loop_v80", "show_aider"),
        "/assimilation": ("seed_assimilation_v81", "show_assimilation"),
    }

    if cmd == "/v81-help":
        print("""
=== SEED v81 COMMANDS ===
Natural:
- v81 status
- v81 self state
- voice settings
- voice journal
- list voices
- set voice Samantha
- voice2 once 8
- talk mode
- open v77 panel
- presence check
- speak presence
- executor status
- propose action git status
- approve action action_0001
- aider status
- coding task <description>
- assimilation backlog
- accept assimilation assim_0001

Debug:
/v81-check /v81-status /v81-self /voice2 /voice-journal /presence /executor /aider-loop /assimilation
""")
        return "handled"

    if cmd in mapping:
        m, f = mapping[cmd]
        mod = __import__(m, fromlist=[f])
        getattr(mod, f)()
        return "handled"

    return None
