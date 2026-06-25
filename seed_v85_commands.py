def handle_v85_command(command):
    text = str(command or "").strip()
    parts = text.split()
    cmd = parts[0].lower() if parts else ""

    mapping = {
        "/v85-check": ("seed_v85_gate", "show_v85_gate"),
        "/v85-status": ("seed_v85_systems", "show_v85_status"),
        "/v85-self": ("seed_self_state_v85", "show_self_state"),
        "/recovery": ("seed_recovery_v82", "show_recovery"),
        "/runtime": ("seed_runtime_v83", "show_runtime"),
        "/privacy": ("seed_privacy_backup_v84", "show_privacy"),
        "/release-candidate": ("seed_release_candidate_v85", "show_release_candidate"),
    }

    if cmd == "/v85-help":
        print("""
=== SEED v85 COMMANDS ===
Natural:
- v85 status
- v85 self state
- recovery check
- mark green checkpoint
- recovery notes
- runtime status
- seed start
- stop seed runtime
- backup seed
- list backups
- export memory
- forget memory <keyword>
- privacy status
- release candidate
- full release candidate

Debug:
/v85-check /v85-status /v85-self /recovery /runtime /privacy /release-candidate
""")
        return "handled"

    if cmd in mapping:
        m, f = mapping[cmd]
        mod = __import__(m, fromlist=[f])
        getattr(mod, f)()
        return "handled"

    return None
