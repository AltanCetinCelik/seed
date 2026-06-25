#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys
import re

FILES = {
    "seed_wake_word_v86.py": "\nimport json\nimport os\nimport re\nimport signal\nimport subprocess\nimport sys\nimport time\nfrom datetime import datetime\nfrom pathlib import Path\n\nSETTINGS_FILE = Path(\"seed_wake_word_v86_settings.json\")\nLOG_FILE = Path(\"seed_wake_word_v86.log\")\nEVENTS_FILE = Path(\"seed_wake_word_v86_events.jsonl\")\nPID_FILE = Path(\"seed_wake_word_v86.pid\")\nSTOP_FILE = Path(\"seed_wake_word_v86.stop\")\nSTATUS_FILE = Path(\"seed_wake_word_v86_status.json\")\n\nDEFAULTS = {\n    \"version\": \"v86.0.0\",\n    \"enabled\": True,\n    \"wake_phrases\": [\"seed\", \"hey seed\", \"wake up\", \"wake up seed\", \"okay seed\", \"ok seed\"],\n    \"listen_seconds\": 3,\n    \"cooldown_seconds\": 8,\n    \"empty_backoff_seconds\": 0.4,\n    \"action\": \"open_panel_then_voice\",\n    \"reply_on_wake\": \"I'm here.\",\n    \"open_panel\": True,\n    \"voice_seconds_after_wake\": 8,\n    \"speak_reply\": True,\n    \"max_runtime_minutes\": None\n}\n\ndef now():\n    return datetime.now().isoformat(timespec=\"seconds\")\n\ndef load_settings():\n    if SETTINGS_FILE.exists():\n        try:\n            data = json.loads(SETTINGS_FILE.read_text(errors=\"ignore\"))\n            base = DEFAULTS.copy()\n            base.update(data)\n            return base\n        except Exception:\n            pass\n    SETTINGS_FILE.write_text(json.dumps(DEFAULTS, indent=4, ensure_ascii=False))\n    return DEFAULTS.copy()\n\ndef save_settings(**updates):\n    data = load_settings()\n    data.update(updates)\n    data[\"updated_at\"] = now()\n    SETTINGS_FILE.write_text(json.dumps(data, indent=4, ensure_ascii=False))\n    return data\n\ndef normalize(text):\n    text = str(text or \"\").lower()\n    text = text.replace(\"wake u\", \"wake up\")\n    text = re.sub(r\"[^a-z\u00e7\u011f\u0131\u00f6\u015f\u00fc0-9\\s]\", \" \", text)\n    return \" \".join(text.split())\n\ndef is_wake_phrase(transcript):\n    norm = normalize(transcript)\n    if not norm:\n        return False, None\n    phrases = load_settings().get(\"wake_phrases\", [])\n    for phrase in phrases:\n        p = normalize(phrase)\n        if not p:\n            continue\n        # strict enough to avoid random \"seed\" inside long words, loose enough for whisper sentence output\n        if p == norm or norm.startswith(p + \" \") or (\" \" + p + \" \") in (\" \" + norm + \" \"):\n            return True, phrase\n    return False, None\n\ndef log_event(row):\n    row.setdefault(\"created_at\", now())\n    row.setdefault(\"version\", \"v86.0.0\")\n    with EVENTS_FILE.open(\"a\") as f:\n        f.write(json.dumps(row, ensure_ascii=False) + \"\\n\")\n\ndef write_status(**data):\n    base = {\"created_at\": now(), \"version\": \"v86.0.0\"}\n    base.update(data)\n    STATUS_FILE.write_text(json.dumps(base, indent=4, ensure_ascii=False))\n    return base\n\ndef pid_alive(pid):\n    try:\n        os.kill(int(pid), 0)\n        return True\n    except Exception:\n        return False\n\ndef say(text):\n    try:\n        from seed_voice_v76 import say_with_settings\n        return say_with_settings(text)\n    except Exception:\n        try:\n            say_bin = __import__(\"shutil\").which(\"say\")\n            if say_bin:\n                subprocess.run([say_bin, str(text)[:800]], timeout=45)\n                return True\n        except Exception:\n            pass\n    return False\n\ndef set_avatar(mode, reason):\n    try:\n        from seed_embodied_state_v74 import save_state\n        save_state(mode=mode, mode_reason=reason)\n    except Exception:\n        pass\n\ndef open_seed_panel():\n    try:\n        from seed_runtime_v83 import start_panel\n        return start_panel(open_browser=True)\n    except Exception as e:\n        return {\"ok\": False, \"error\": str(e)}\n\ndef voice_once(seconds):\n    try:\n        from seed_voice_v76 import run_voice2_once\n        return run_voice2_once(seconds=seconds, speak=True)\n    except Exception as e:\n        return {\"ok\": False, \"error\": str(e)}\n\ndef record_and_transcribe(seconds):\n    try:\n        from seed_live_voice_v731 import record_audio, transcribe_audio\n        audio_path, device = record_audio(seconds)\n        transcript = transcribe_audio(audio_path)\n        return {\"ok\": True, \"audio\": str(audio_path), \"device\": device, \"text\": (transcript.get(\"text\") or \"\").strip(), \"raw\": transcript}\n    except Exception as e:\n        return {\"ok\": False, \"error\": str(e), \"text\": \"\"}\n\ndef handle_wake(transcript, phrase):\n    settings = load_settings()\n    set_avatar(\"awake\", f\"Wake phrase heard: {phrase}\")\n    log_event({\"type\": \"wake\", \"phrase\": phrase, \"transcript\": transcript})\n    print(f\"\\n[WAKE] Heard: {transcript!r} matched={phrase!r}\")\n\n    if settings.get(\"speak_reply\", True):\n        say(settings.get(\"reply_on_wake\", \"I'm here.\"))\n\n    panel_result = None\n    if settings.get(\"open_panel\", True):\n        panel_result = open_seed_panel()\n\n    if settings.get(\"action\") in {\"open_panel_then_voice\", \"voice\"}:\n        time.sleep(0.4)\n        return {\n            \"ok\": True,\n            \"woke\": True,\n            \"panel\": panel_result,\n            \"voice\": voice_once(settings.get(\"voice_seconds_after_wake\", 8)),\n        }\n\n    return {\"ok\": True, \"woke\": True, \"panel\": panel_result}\n\ndef listen_loop():\n    settings = load_settings()\n    STOP_FILE.unlink(missing_ok=True)\n    start = time.time()\n    last_wake = 0\n\n    print(\"\\n=== SEED v86 WAKE WORD LISTENER ===\")\n    print(\"Listening for: \" + \", \".join(settings.get(\"wake_phrases\", [])))\n    print(\"Say: Seed / hey Seed / wake up\")\n    print(\"Stop: Ctrl+C or python seed_wake_word_v86.py stop\")\n    write_status(ok=True, running=True, mode=\"listening\", settings=settings)\n\n    while True:\n        if STOP_FILE.exists():\n            print(\"Stop file found. Wake listener stopping.\")\n            break\n\n        settings = load_settings()\n        if not settings.get(\"enabled\", True):\n            write_status(ok=True, running=True, mode=\"disabled\")\n            time.sleep(2)\n            continue\n\n        max_minutes = settings.get(\"max_runtime_minutes\")\n        if max_minutes and (time.time() - start) > max_minutes * 60:\n            print(\"Max runtime reached. Wake listener stopping.\")\n            break\n\n        set_avatar(\"listening\", \"Wake listener is listening for Seed.\")\n        res = record_and_transcribe(int(settings.get(\"listen_seconds\", 3)))\n        text = res.get(\"text\", \"\")\n        print(f\"[listen] {text or '[empty]'}\")\n\n        if not res.get(\"ok\"):\n            log_event({\"type\": \"listen_error\", \"error\": res.get(\"error\")})\n            time.sleep(2)\n            continue\n\n        woke, phrase = is_wake_phrase(text)\n        if woke:\n            if time.time() - last_wake < float(settings.get(\"cooldown_seconds\", 8)):\n                print(\"[wake] ignored due to cooldown\")\n                time.sleep(0.5)\n                continue\n            last_wake = time.time()\n            handle_wake(text, phrase)\n            write_status(ok=True, running=True, mode=\"cooldown\", last_wake=now(), last_transcript=text)\n            time.sleep(float(settings.get(\"cooldown_seconds\", 8)))\n        else:\n            write_status(ok=True, running=True, mode=\"listening\", last_transcript=text)\n            time.sleep(float(settings.get(\"empty_backoff_seconds\", 0.4)))\n\n    set_avatar(\"idle\", \"Wake listener stopped.\")\n    write_status(ok=True, running=False, mode=\"stopped\")\n    return {\"ok\": True, \"stopped\": True}\n\ndef start_daemon():\n    if PID_FILE.exists():\n        try:\n            pid = int(PID_FILE.read_text().strip())\n            if pid_alive(pid):\n                print(f\"Wake listener already running pid={pid}\")\n                return {\"ok\": True, \"already_running\": True, \"pid\": pid}\n        except Exception:\n            pass\n\n    STOP_FILE.unlink(missing_ok=True)\n    log = LOG_FILE.open(\"a\")\n    proc = subprocess.Popen([sys.executable, \"seed_wake_word_v86.py\", \"listen\"], stdout=log, stderr=log)\n    PID_FILE.write_text(str(proc.pid))\n    print(f\"Started Seed wake listener pid={proc.pid}\")\n    print(f\"Log: {LOG_FILE}\")\n    return {\"ok\": True, \"pid\": proc.pid, \"log\": str(LOG_FILE)}\n\ndef stop_daemon():\n    STOP_FILE.write_text(now())\n    stopped = False\n    pid = None\n    if PID_FILE.exists():\n        try:\n            pid = int(PID_FILE.read_text().strip())\n            if pid_alive(pid):\n                os.kill(pid, signal.SIGTERM)\n                stopped = True\n            PID_FILE.unlink(missing_ok=True)\n        except Exception:\n            pass\n    write_status(ok=True, running=False, mode=\"stopped\")\n    print(f\"Wake listener stop requested. pid={pid} stopped={stopped}\")\n    return {\"ok\": True, \"pid\": pid, \"stopped\": stopped}\n\ndef wake_status():\n    pid = None\n    alive = False\n    if PID_FILE.exists():\n        try:\n            pid = int(PID_FILE.read_text().strip())\n            alive = pid_alive(pid)\n        except Exception:\n            pass\n    status = {}\n    if STATUS_FILE.exists():\n        try:\n            status = json.loads(STATUS_FILE.read_text(errors=\"ignore\"))\n        except Exception:\n            pass\n    return {\"created_at\": now(), \"version\": \"v86.0.0\", \"ok\": True, \"pid\": pid, \"alive\": alive, \"settings\": load_settings(), \"runtime_status\": status, \"log\": str(LOG_FILE)}\n\ndef show_status():\n    print(\"\\n=== SEED v86 WAKE WORD STATUS ===\")\n    print(json.dumps(wake_status(), indent=4, ensure_ascii=False))\n\ndef show_help():\n    print(\"\"\"\n=== Seed v86 Wake Word ===\n\nCommands:\npython seed_wake_word_v86.py start\npython seed_wake_word_v86.py stop\npython seed_wake_word_v86.py status\npython seed_wake_word_v86.py listen\npython seed_wake_word_v86.py test \"hey seed\"\npython seed_wake_word_v86.py phrases\npython seed_wake_word_v86.py set-seconds 3\npython seed_wake_word_v86.py set-reply \"I'm here.\"\n\nNatural commands inside Seed:\nwake status\nstart wake listener\nstop wake listener\nwake listen\nwake phrases\n\"\"\")\n\ndef main():\n    arg = sys.argv[1] if len(sys.argv) > 1 else \"status\"\n\n    if arg == \"start\":\n        start_daemon()\n    elif arg == \"stop\":\n        stop_daemon()\n    elif arg == \"listen\":\n        listen_loop()\n    elif arg == \"status\":\n        show_status()\n    elif arg == \"phrases\":\n        print(json.dumps(load_settings().get(\"wake_phrases\", []), indent=4, ensure_ascii=False))\n    elif arg == \"test\":\n        text = \" \".join(sys.argv[2:])\n        print({\"text\": text, \"match\": is_wake_phrase(text)})\n    elif arg == \"set-seconds\":\n        seconds = int(sys.argv[2]) if len(sys.argv) > 2 else 3\n        print(save_settings(listen_seconds=seconds))\n    elif arg == \"set-reply\":\n        reply = \" \".join(sys.argv[2:]) or \"I'm here.\"\n        print(save_settings(reply_on_wake=reply))\n    else:\n        show_help()\n\nif __name__ == \"__main__\":\n    main()\n",
    "seed_v86_systems.py": "\nimport json\nfrom datetime import datetime\nfrom pathlib import Path\n\nSTATE_FILE = Path(\"seed_v86_systems_state.json\")\n\ndef now():\n    return datetime.now().isoformat(timespec=\"seconds\")\n\ndef safe(title, summary, fn):\n    try:\n        data = fn()\n        return {\"title\": title, \"summary\": summary, \"status\": \"ok\" if data.get(\"ok\", True) else \"warning\", \"data\": data}\n    except Exception as e:\n        return {\"title\": title, \"summary\": summary, \"status\": \"error\", \"error\": str(e)}\n\ndef build_v86_state():\n    cards = [\n        safe(\"Wake Word Listener\", \"Say Seed / wake up to open Seed and start voice.\", lambda: __import__(\"seed_wake_word_v86\", fromlist=[\"wake_status\"]).wake_status()),\n        safe(\"Voice 2.0 Base\", \"v76 voice still available.\", lambda: __import__(\"seed_voice_v76\", fromlist=[\"voice2_status\"]).voice2_status()),\n        safe(\"Runtime Base\", \"v83 one-command runtime still available.\", lambda: __import__(\"seed_runtime_v83\", fromlist=[\"runtime_status\"]).runtime_status()),\n        safe(\"v85 Base\", \"v85.3 real-v1 prep gate remains available.\", lambda: __import__(\"seed_v85_gate\", fromlist=[\"run_v85_gate\"]).run_v85_gate()),\n    ]\n    data = {\"created_at\": now(), \"version\": \"v86.0.0\", \"ok\": all(c[\"status\"] != \"error\" for c in cards), \"cards\": cards}\n    STATE_FILE.write_text(json.dumps(data, indent=4, ensure_ascii=False))\n    return data\n\ndef show_v86_status():\n    data = build_v86_state()\n    print(\"\\n=== SEED v86 WAKE WORD STATUS ===\")\n    print(f\"OK: {data['ok']}\")\n    for c in data[\"cards\"]:\n        print(f\"- {c['title']}: {c['status']} \u2014 {c['summary']}\")\n\nif __name__ == \"__main__\":\n    show_v86_status()\n",
    "seed_v86_gate.py": "\nimport json\nimport subprocess\nimport sys\nfrom datetime import datetime\nfrom pathlib import Path\n\nMODULES = [\n    \"seed_wake_word_v86.py\",\n    \"seed_v86_systems.py\",\n    \"seed_v86_gate.py\",\n    \"seed_v86_commands.py\",\n    \"seed_natural_intent_router_v86.py\",\n]\n\ndef now():\n    return datetime.now().isoformat(timespec=\"seconds\")\n\ndef compile_module(module):\n    proc = subprocess.run([sys.executable, \"-m\", \"py_compile\", module], capture_output=True, text=True, timeout=30)\n    return {\"module\": module, \"ok\": proc.returncode == 0, \"stderr\": proc.stderr[-1600:]}\n\ndef run_v86_gate():\n    checks = [compile_module(m) for m in MODULES]\n    modules_ok = all(c[\"ok\"] for c in checks)\n    details = {}\n\n    try:\n        from seed_v86_systems import build_v86_state\n        state = build_v86_state()\n        systems_ok = state.get(\"ok\") is True and len(state.get(\"cards\", [])) >= 4\n        details[\"v86_state\"] = {\"ok\": state.get(\"ok\"), \"cards\": len(state.get(\"cards\", []))}\n    except Exception as e:\n        systems_ok = False\n        details[\"v86_state_error\"] = str(e)\n\n    try:\n        from seed_wake_word_v86 import is_wake_phrase\n        wake_ok = is_wake_phrase(\"hey seed\")[0] is True and is_wake_phrase(\"wake up\")[0] is True\n        details[\"phrase_tests\"] = {\"hey_seed\": is_wake_phrase(\"hey seed\"), \"wake_up\": is_wake_phrase(\"wake up\")}\n    except Exception as e:\n        wake_ok = False\n        details[\"phrase_error\"] = str(e)\n\n    report = {\n        \"created_at\": now(),\n        \"version\": \"v86.0.0\",\n        \"ready\": modules_ok and systems_ok and wake_ok,\n        \"modules_ok\": modules_ok,\n        \"systems_ok\": systems_ok,\n        \"wake_phrase_ok\": wake_ok,\n        \"module_checks\": checks,\n        \"details\": details,\n    }\n    Path(\"seed_v86_gate_report.json\").write_text(json.dumps(report, indent=4, ensure_ascii=False))\n    return report\n\ndef show_v86_gate():\n    r = run_v86_gate()\n    print(\"\\n=== SEED v86 WAKE WORD GATE ===\")\n    print(f\"Ready: {r['ready']}\")\n    print(f\"Modules OK: {r['modules_ok']}\")\n    print(f\"Systems OK: {r['systems_ok']}\")\n    print(f\"Wake Phrase OK: {r['wake_phrase_ok']}\")\n    print(f\"Details: {r['details']}\")\n\nif __name__ == \"__main__\":\n    show_v86_gate()\n",
    "seed_v86_commands.py": "\ndef handle_v86_command(command):\n    text = str(command or \"\").strip()\n    cmd = text.split()[0].lower() if text else \"\"\n\n    mapping = {\n        \"/v86-check\": (\"seed_v86_gate\", \"show_v86_gate\"),\n        \"/v86-status\": (\"seed_v86_systems\", \"show_v86_status\"),\n        \"/wake-status\": (\"seed_wake_word_v86\", \"show_status\"),\n    }\n\n    if cmd == \"/v86-help\":\n        print(\"\"\"\n=== SEED v86 WAKE COMMANDS ===\nNatural:\n- wake status\n- start wake listener\n- stop wake listener\n- wake listen\n- wake phrases\n\nShell:\n- python seed_wake_word_v86.py start\n- python seed_wake_word_v86.py stop\n- python seed_wake_word_v86.py listen\n\"\"\")\n        return \"handled\"\n\n    if cmd in mapping:\n        m, f = mapping[cmd]\n        mod = __import__(m, fromlist=[f])\n        getattr(mod, f)()\n        return \"handled\"\n\n    return None\n",
    "seed_natural_intent_router_v86.py": "\ndef norm(text):\n    return \" \".join(str(text or \"\").strip().lower().split())\n\ndef handle_natural_intent_v86(user_message):\n    raw = str(user_message or \"\").strip()\n    text = norm(raw)\n    if not text or raw.startswith(\"/\"):\n        return None\n\n    if any(p in text for p in [\"v86 status\", \"wake status\", \"wake word status\"]):\n        from seed_v86_systems import show_v86_status\n        show_v86_status()\n        return \"handled\"\n\n    if any(p in text for p in [\"start wake listener\", \"start wake word\", \"enable wake word\", \"wake daemon start\"]):\n        from seed_wake_word_v86 import start_daemon\n        print(start_daemon())\n        return \"handled\"\n\n    if any(p in text for p in [\"stop wake listener\", \"stop wake word\", \"disable wake word\", \"wake daemon stop\"]):\n        from seed_wake_word_v86 import stop_daemon\n        print(stop_daemon())\n        return \"handled\"\n\n    if any(p in text for p in [\"wake listen\", \"listen for seed\", \"foreground wake listener\"]):\n        from seed_wake_word_v86 import listen_loop\n        listen_loop()\n        return \"handled\"\n\n    if any(p in text for p in [\"wake phrases\", \"show wake phrases\"]):\n        from seed_wake_word_v86 import load_settings\n        print(load_settings().get(\"wake_phrases\", []))\n        return \"handled\"\n\n    return None\n",
}

for path, text in FILES.items():
    Path(path).write_text(text.strip() + "\n")
    print("Wrote", path)

# Patch seed_commands.py
p = Path("seed_commands.py")
text = p.read_text(errors="ignore") if p.exists() else "def handle_chat_command(user_message,*args,**kwargs): return None\n"
if "_seed_v86_previous_handle_chat_command" not in text:
    text += """
# v86 Wake word router.
try:
    _seed_v86_previous_handle_chat_command = handle_chat_command

    def handle_chat_command(user_message, *args, **kwargs):
        try:
            from seed_natural_intent_router_v86 import handle_natural_intent_v86
            handled = handle_natural_intent_v86(user_message)
            if handled == "handled":
                return "handled"
        except Exception as error:
            print(f"v86 natural router error: {error}")
            return "handled"

        try:
            from seed_v86_commands import handle_v86_command
            handled = handle_v86_command(user_message)
            if handled == "handled":
                return "handled"
        except Exception as error:
            print(f"v86 command error: {error}")
            return "handled"

        return _seed_v86_previous_handle_chat_command(user_message, *args, **kwargs)

except Exception:
    pass
"""
    p.write_text(text)
    print("Patched seed_commands.py")

# Update config
p = Path("seed_config.py")
text = p.read_text(errors="ignore") if p.exists() else 'SEED_VERSION = "v86.0.0"\n'
text = re.sub(r'^SEED_VERSION\s*=\s*".*?"', 'SEED_VERSION = "v86.0.0"', text, flags=re.M)
if "SEED_V86_WAKE_WORD" not in text:
    text += '\nSEED_V86_WAKE_WORD = True\nSEED_IS_PRIVATE_COMPANION_NOT_PUBLIC_RELEASE = True\n'
p.write_text(text)
print("Updated seed_config.py")

# Docs
p = Path("Seed_Core.md")
text = p.read_text(errors="ignore") if p.exists() else ""
if "Seed v86.0.0 — Wake Word Companion Mode" not in text:
    text += """
## Seed v86.0.0 — Wake Word Companion Mode

Seed is a private companion, not a public release product.

Adds:
- Wake listener for phrases: Seed, hey Seed, wake up, wake up Seed
- Background daemon start/stop/status
- Foreground listen mode
- Opens Seed panel and starts voice after wake phrase
- Voice/Avatar sync through existing v76/v74 systems

Commands:
- python seed_wake_word_v86.py start
- python seed_wake_word_v86.py stop
- python seed_wake_word_v86.py status
- python seed_wake_word_v86.py listen

Natural:
- start wake listener
- stop wake listener
- wake status
- wake listen
"""
p.write_text(text)
print("Updated Seed_Core.md")

# Gitignore
p = Path(".gitignore")
text = p.read_text(errors="ignore") if p.exists() else ""
block = """
# Seed v86 wake-word runtime
seed_wake_word_v86_settings.json
seed_wake_word_v86.log
seed_wake_word_v86_events.jsonl
seed_wake_word_v86.pid
seed_wake_word_v86.stop
seed_wake_word_v86_status.json
seed_v86_systems_state.json
seed_v86_gate_report.json
"""
if "Seed v86 wake-word runtime" not in text:
    text += "\n" + block
p.write_text(text)
print("Updated .gitignore")

# Compile
for m in list(FILES.keys()) + ["seed_commands.py"]:
    proc = subprocess.run([sys.executable, "-m", "py_compile", m], capture_output=True, text=True, timeout=30)
    print("$ python -m py_compile", m)
    if proc.returncode == 0:
        print("OK")
    else:
        print(proc.stderr)
        sys.exit(proc.returncode)

print("\nSeed v86 Wake Word installer complete.")
