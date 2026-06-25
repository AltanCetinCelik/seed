import json
import os
import re
import signal
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

SETTINGS_FILE = Path("seed_wake_word_v86_settings.json")
LOG_FILE = Path("seed_wake_word_v86.log")
EVENTS_FILE = Path("seed_wake_word_v86_events.jsonl")
PID_FILE = Path("seed_wake_word_v86.pid")
STOP_FILE = Path("seed_wake_word_v86.stop")
STATUS_FILE = Path("seed_wake_word_v86_status.json")

DEFAULTS = {
    "version": "v86.0.0",
    "enabled": True,
    "wake_phrases": ["seed", "hey seed", "wake up", "wake up seed", "okay seed", "ok seed"],
    "listen_seconds": 3,
    "cooldown_seconds": 8,
    "empty_backoff_seconds": 0.4,
    "action": "open_panel_then_voice",
    "reply_on_wake": "I'm here.",
    "open_panel": True,
    "voice_seconds_after_wake": 8,
    "speak_reply": True,
    "max_runtime_minutes": None
}

def now():
    return datetime.now().isoformat(timespec="seconds")

def load_settings():
    if SETTINGS_FILE.exists():
        try:
            data = json.loads(SETTINGS_FILE.read_text(errors="ignore"))
            base = DEFAULTS.copy()
            base.update(data)
            return base
        except Exception:
            pass
    SETTINGS_FILE.write_text(json.dumps(DEFAULTS, indent=4, ensure_ascii=False))
    return DEFAULTS.copy()

def save_settings(**updates):
    data = load_settings()
    data.update(updates)
    data["updated_at"] = now()
    SETTINGS_FILE.write_text(json.dumps(data, indent=4, ensure_ascii=False))
    return data

def normalize(text):
    text = str(text or "").lower()
    text = text.replace("wake u", "wake up")
    text = re.sub(r"[^a-zçğıöşü0-9\s]", " ", text)
    return " ".join(text.split())

def is_wake_phrase(transcript):
    norm = normalize(transcript)
    if not norm:
        return False, None
    phrases = load_settings().get("wake_phrases", [])
    for phrase in phrases:
        p = normalize(phrase)
        if not p:
            continue
        # strict enough to avoid random "seed" inside long words, loose enough for whisper sentence output
        if p == norm or norm.startswith(p + " ") or (" " + p + " ") in (" " + norm + " "):
            return True, phrase
    return False, None

def log_event(row):
    row.setdefault("created_at", now())
    row.setdefault("version", "v86.0.0")
    with EVENTS_FILE.open("a") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")

def write_status(**data):
    base = {"created_at": now(), "version": "v86.0.0"}
    base.update(data)
    STATUS_FILE.write_text(json.dumps(base, indent=4, ensure_ascii=False))
    return base

def pid_alive(pid):
    try:
        os.kill(int(pid), 0)
        return True
    except Exception:
        return False

def say(text):
    try:
        from seed_voice_v76 import say_with_settings
        return say_with_settings(text)
    except Exception:
        try:
            say_bin = __import__("shutil").which("say")
            if say_bin:
                subprocess.run([say_bin, str(text)[:800]], timeout=45)
                return True
        except Exception:
            pass
    return False

def set_avatar(mode, reason):
    try:
        from seed_embodied_state_v74 import save_state
        save_state(mode=mode, mode_reason=reason)
    except Exception:
        pass

def open_seed_panel():
    try:
        from seed_runtime_v83 import start_panel
        return start_panel(open_browser=True)
    except Exception as e:
        return {"ok": False, "error": str(e)}

def voice_once(seconds):
    try:
        from seed_voice_v76 import run_voice2_once
        return run_voice2_once(seconds=seconds, speak=True)
    except Exception as e:
        return {"ok": False, "error": str(e)}

def record_and_transcribe(seconds):
    try:
        from seed_live_voice_v731 import record_audio, transcribe_audio
        audio_path, device = record_audio(seconds)
        transcript = transcribe_audio(audio_path)
        return {"ok": True, "audio": str(audio_path), "device": device, "text": (transcript.get("text") or "").strip(), "raw": transcript}
    except Exception as e:
        return {"ok": False, "error": str(e), "text": ""}

def handle_wake(transcript, phrase):
    settings = load_settings()
    set_avatar("awake", f"Wake phrase heard: {phrase}")
    log_event({"type": "wake", "phrase": phrase, "transcript": transcript})
    print(f"\n[WAKE] Heard: {transcript!r} matched={phrase!r}")

    if settings.get("speak_reply", True):
        say(settings.get("reply_on_wake", "I'm here."))

    panel_result = None
    if settings.get("open_panel", True):
        panel_result = open_seed_panel()

    if settings.get("action") in {"open_panel_then_voice", "voice"}:
        time.sleep(0.4)
        return {
            "ok": True,
            "woke": True,
            "panel": panel_result,
            "voice": voice_once(settings.get("voice_seconds_after_wake", 8)),
        }

    return {"ok": True, "woke": True, "panel": panel_result}

def listen_loop():
    settings = load_settings()
    STOP_FILE.unlink(missing_ok=True)
    start = time.time()
    last_wake = 0

    print("\n=== SEED v86 WAKE WORD LISTENER ===")
    print("Listening for: " + ", ".join(settings.get("wake_phrases", [])))
    print("Say: Seed / hey Seed / wake up")
    print("Stop: Ctrl+C or python seed_wake_word_v86.py stop")
    write_status(ok=True, running=True, mode="listening", settings=settings)

    while True:
        if STOP_FILE.exists():
            print("Stop file found. Wake listener stopping.")
            break

        settings = load_settings()
        if not settings.get("enabled", True):
            write_status(ok=True, running=True, mode="disabled")
            time.sleep(2)
            continue

        max_minutes = settings.get("max_runtime_minutes")
        if max_minutes and (time.time() - start) > max_minutes * 60:
            print("Max runtime reached. Wake listener stopping.")
            break

        set_avatar("listening", "Wake listener is listening for Seed.")
        res = record_and_transcribe(int(settings.get("listen_seconds", 3)))
        text = res.get("text", "")
        print(f"[listen] {text or '[empty]'}")

        if not res.get("ok"):
            log_event({"type": "listen_error", "error": res.get("error")})
            time.sleep(2)
            continue

        woke, phrase = is_wake_phrase(text)
        if woke:
            if time.time() - last_wake < float(settings.get("cooldown_seconds", 8)):
                print("[wake] ignored due to cooldown")
                time.sleep(0.5)
                continue
            last_wake = time.time()
            handle_wake(text, phrase)
            write_status(ok=True, running=True, mode="cooldown", last_wake=now(), last_transcript=text)
            time.sleep(float(settings.get("cooldown_seconds", 8)))
        else:
            write_status(ok=True, running=True, mode="listening", last_transcript=text)
            time.sleep(float(settings.get("empty_backoff_seconds", 0.4)))

    set_avatar("idle", "Wake listener stopped.")
    write_status(ok=True, running=False, mode="stopped")
    return {"ok": True, "stopped": True}

def start_daemon():
    if PID_FILE.exists():
        try:
            pid = int(PID_FILE.read_text().strip())
            if pid_alive(pid):
                print(f"Wake listener already running pid={pid}")
                return {"ok": True, "already_running": True, "pid": pid}
        except Exception:
            pass

    STOP_FILE.unlink(missing_ok=True)
    log = LOG_FILE.open("a")
    proc = subprocess.Popen([sys.executable, "seed_wake_word_v86.py", "listen"], stdout=log, stderr=log)
    PID_FILE.write_text(str(proc.pid))
    print(f"Started Seed wake listener pid={proc.pid}")
    print(f"Log: {LOG_FILE}")
    return {"ok": True, "pid": proc.pid, "log": str(LOG_FILE)}

def stop_daemon():
    STOP_FILE.write_text(now())
    stopped = False
    pid = None
    if PID_FILE.exists():
        try:
            pid = int(PID_FILE.read_text().strip())
            if pid_alive(pid):
                os.kill(pid, signal.SIGTERM)
                stopped = True
            PID_FILE.unlink(missing_ok=True)
        except Exception:
            pass
    write_status(ok=True, running=False, mode="stopped")
    print(f"Wake listener stop requested. pid={pid} stopped={stopped}")
    return {"ok": True, "pid": pid, "stopped": stopped}

def wake_status():
    pid = None
    alive = False
    if PID_FILE.exists():
        try:
            pid = int(PID_FILE.read_text().strip())
            alive = pid_alive(pid)
        except Exception:
            pass
    status = {}
    if STATUS_FILE.exists():
        try:
            status = json.loads(STATUS_FILE.read_text(errors="ignore"))
        except Exception:
            pass
    return {"created_at": now(), "version": "v86.0.0", "ok": True, "pid": pid, "alive": alive, "settings": load_settings(), "runtime_status": status, "log": str(LOG_FILE)}

def show_status():
    print("\n=== SEED v86 WAKE WORD STATUS ===")
    print(json.dumps(wake_status(), indent=4, ensure_ascii=False))

def show_help():
    print("""
=== Seed v86 Wake Word ===

Commands:
python seed_wake_word_v86.py start
python seed_wake_word_v86.py stop
python seed_wake_word_v86.py status
python seed_wake_word_v86.py listen
python seed_wake_word_v86.py test "hey seed"
python seed_wake_word_v86.py phrases
python seed_wake_word_v86.py set-seconds 3
python seed_wake_word_v86.py set-reply "I'm here."

Natural commands inside Seed:
wake status
start wake listener
stop wake listener
wake listen
wake phrases
""")

def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else "status"

    if arg == "start":
        start_daemon()
    elif arg == "stop":
        stop_daemon()
    elif arg == "listen":
        listen_loop()
    elif arg == "status":
        show_status()
    elif arg == "phrases":
        print(json.dumps(load_settings().get("wake_phrases", []), indent=4, ensure_ascii=False))
    elif arg == "test":
        text = " ".join(sys.argv[2:])
        print({"text": text, "match": is_wake_phrase(text)})
    elif arg == "set-seconds":
        seconds = int(sys.argv[2]) if len(sys.argv) > 2 else 3
        print(save_settings(listen_seconds=seconds))
    elif arg == "set-reply":
        reply = " ".join(sys.argv[2:]) or "I'm here."
        print(save_settings(reply_on_wake=reply))
    else:
        show_help()

if __name__ == "__main__":
    main()
