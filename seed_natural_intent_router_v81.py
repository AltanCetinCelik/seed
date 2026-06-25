import re

def norm(text):
    return " ".join(str(text or "").strip().lower().split())

def handle_natural_intent_v81(user_message):
    raw = str(user_message or "").strip()
    text = norm(raw)
    if not text or raw.startswith("/"):
        return None

    if any(p in text for p in ["v81 status", "mega stack status", "v1 alpha status"]):
        from seed_v81_systems import show_v81_status
        show_v81_status()
        return "handled"

    if any(p in text for p in ["v81 self state", "current true version", "what version are you", "true current state"]):
        from seed_self_state_v81 import show_self_state
        show_self_state()
        return "handled"

    if any(p in text for p in ["voice settings", "voice2 status", "voice 2 status"]):
        from seed_voice_v76 import show_voice_settings
        show_voice_settings()
        return "handled"

    if any(p in text for p in ["voice journal", "show voice journal"]):
        from seed_voice_v76 import show_voice_journal
        show_voice_journal()
        return "handled"

    if text.startswith("list voices") or text == "macos voices":
        from seed_voice_v76 import list_macos_voices
        import json
        print("\n=== macOS Voices ===")
        print(json.dumps(list_macos_voices(), indent=4, ensure_ascii=False))
        return "handled"

    m = re.search(r"\bset voice\s+(.+)$", raw, flags=re.I)
    if m:
        from seed_voice_v76 import save_settings
        data = save_settings(macos_voice=m.group(1).strip())
        print("\n=== SEED v76 VOICE SETTING UPDATED ===")
        print(f"macOS voice: {data.get('macos_voice')}")
        return "handled"

    m = re.search(r"\b(?:voice2|voice 2)\s+once\s*(\d{1,2})?\b", text)
    if m:
        from seed_voice_v76 import run_voice2_once
        seconds = int(m.group(1) or 8)
        run_voice2_once(seconds=seconds)
        return "handled"

    if text.startswith("talk mode"):
        from seed_voice_v76 import talk_mode
        m = re.search(r"\b(\d{1,2})\b", text)
        turns = int(m.group(1) or 5)
        talk_mode(max_turns=turns)
        return "handled"

    if any(p in text for p in ["open v77 panel", "open panel 2", "panel 2", "v77 panel"]):
        from seed_panel_v77 import run_panel
        run_panel(True)
        return "handled"

    if any(p in text for p in ["presence check", "proactive check", "what did you notice now"]):
        from seed_proactive_v78 import show_proactive
        show_proactive()
        return "handled"

    if any(p in text for p in ["speak presence", "say presence", "speak proactive"]):
        from seed_proactive_v78 import speak_one
        res = speak_one(force=True)
        print("\n=== SEED v78 SPOKEN PRESENCE ===")
        print(res.get("spoken") or res.get("error"))
        return "handled"

    if any(p in text for p in ["executor status", "permission executor", "actions status"]):
        from seed_permission_executor_v79 import show_executor
        show_executor()
        return "handled"

    m = re.search(r"\bpropose action\s+(.+)$", raw, flags=re.I)
    if m:
        from seed_permission_executor_v79 import propose_action
        res = propose_action(m.group(1).strip(), reason="Proposed from natural command.")
        a = res["action"]
        print("\n=== SEED v79 ACTION PROPOSED ===")
        print(f"{a['id']} [{a['level']}] {a['command']}")
        print(f"safety: {a['safety']}")
        print(f"Run: approve action {a['id']}")
        return "handled"

    m = re.search(r"\bapprove action\s+(action_\d{4})\b", text)
    if m:
        from seed_permission_executor_v79 import approve_and_run
        res = approve_and_run(m.group(1))
        print("\n=== SEED v79 ACTION RESULT ===")
        print(f"ok: {res.get('ok')}")
        result = res.get("result", {})
        if result.get("stdout"):
            print(result["stdout"])
        if result.get("stderr"):
            print(result["stderr"])
        if res.get("error"):
            print(res["error"])
        return "handled"

    if any(p in text for p in ["aider status", "aider loop", "coding loop status"]):
        from seed_aider_loop_v80 import show_aider
        show_aider()
        return "handled"

    m = re.search(r"\bcoding task\s+(.+)$", raw, flags=re.I)
    if m:
        from seed_aider_loop_v80 import create_coding_task
        res = create_coding_task(m.group(1).strip())
        print("\n=== SEED v80 CODING TASK CREATED ===")
        t = res["task"]
        print(f"{t['id']}: {t['description']}")
        print("Approval is required before Aider edits.")
        return "handled"

    if any(p in text for p in ["assimilation backlog", "advice backlog", "repo advice backlog"]):
        from seed_assimilation_v81 import show_assimilation
        show_assimilation()
        return "handled"

    m = re.search(r"\b(accept|reject|later)\s+assimilation\s+(assim_\d{4})\b", text)
    if m:
        from seed_assimilation_v81 import decide
        res = decide(m.group(2), m.group(1))
        print("\n=== SEED v81 ASSIMILATION DECISION ===")
        print(res["decision"])
        return "handled"

    return None
