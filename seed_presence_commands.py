def handle_presence_command(command):
    cmd = (command or "").strip().split()[0].lower()

    if cmd == "/presence-help":
        print("""
=== SEED PRESENCE COMMANDS ===
/presence-status
/presence-on
/presence-off
/focus-on
/focus-off
/curiosity
/presence-tick
/presence-force
/presence-inbox
/presence-pop
/presence-service
/presence-start
/presence-stop
""")
        return "handled"

    if cmd == "/presence-status":
        from seed_presence import show_presence_status
        show_presence_status()
        return "handled"

    if cmd == "/presence-on":
        from seed_interrupt_policy import set_presence_enabled, show_interrupt_policy
        set_presence_enabled(True)
        show_interrupt_policy()
        return "handled"

    if cmd == "/presence-off":
        from seed_interrupt_policy import set_presence_enabled, show_interrupt_policy
        set_presence_enabled(False)
        show_interrupt_policy()
        return "handled"

    if cmd == "/focus-on":
        from seed_interrupt_policy import set_focus_mode, show_interrupt_policy
        set_focus_mode(True)
        show_interrupt_policy()
        return "handled"

    if cmd == "/focus-off":
        from seed_interrupt_policy import set_focus_mode, show_interrupt_policy
        set_focus_mode(False)
        show_interrupt_policy()
        return "handled"

    if cmd == "/curiosity":
        from seed_curiosity_engine import show_curiosity
        show_curiosity()
        return "handled"

    if cmd == "/presence-tick":
        from seed_presence import show_presence_tick
        show_presence_tick(force=False)
        return "handled"

    if cmd == "/presence-force":
        from seed_presence import show_presence_tick
        show_presence_tick(force=True)
        return "handled"

    if cmd == "/presence-inbox":
        from seed_notification_queue import show_notification_inbox
        show_notification_inbox()
        return "handled"

    if cmd == "/presence-pop":
        from seed_notification_queue import pop_next_notification_for_cli
        item = pop_next_notification_for_cli()
        if not item:
            print("No pending presence notifications.")
        return "handled"

    if cmd == "/presence-service":
        from seed_presence_service import show_presence_service
        show_presence_service()
        return "handled"

    if cmd == "/presence-start":
        from seed_presence_service import start_service
        import json
        print(json.dumps(start_service(), indent=4))
        return "handled"

    if cmd == "/presence-stop":
        from seed_presence_service import stop_service
        import json
        print(json.dumps(stop_service(), indent=4))
        return "handled"

    return None
