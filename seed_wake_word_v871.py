import json
import os
import re
import signal
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

SETTINGS_FILE = Path("seed_wake_word_v871_settings.json")
LOG_FILE = Path("seed_wake_word_v871.log")
EVENTS_FILE = Path("seed_wake_word_v871_events.jsonl")
PID_FILE = Path("seed_wake_word_v871.pid")
STOP_FILE = Path("seed_wake_word_v871.stop")
STATUS_FILE = Path("seed_wake_word_v871_status.json")

DEFAULTS = {
    "version": "v87.1.0",
    "enabled": True,
    "wake_phrases": ["wake up seed", "hey seed", "okay seed", "ok seed", "wake up", "seed"],
    "listen_seconds": 3,
    "cooldown_seconds": 5,
    "empty_backoff_seconds": 0.25,
    "max_words_for_bare_seed": 4,
    "open_panel": True,
    "immediate_followup": True,
    "followup_seconds": 10,
    "do_not_speak_before_followup": True
}

FALSE_POSITIVE_PHRASES = {
    "see it", "see the", "eat", "it", "sea", "basically we don't have face it",
    "are you happy", "it's great", "i buy it"
}

def now():
    return datetime.now().isoformat(timespec="seconds")

def load_settings():
    if SETTINGS_FILE.exists():
        try:
            base = DEFAULTS.copy()
            base.update(json.loads(SETTINGS_FILE.read_text(errors="ignore")))
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
    text = text.replace("wakeup", "wake up")
    text = re.sub(r"[^a-zçğıöşü0-9\s]", " ", text)
    return " ".join(text.split())

def ranked_phrases():
    phrases = [str(p).strip() for p in load_settings().get("wake_phrases", []) if str(p).strip()]
    return sorted(set(phrases), key=lambda x: len(x.split()), reverse=True)

def is_wake_phrase(transcript):
    norm = normalize(transcript)
    if not norm or norm in FALSE_POSITIVE_PHRASES:
        return False, None
    words = norm.split()
    settings = load_settings()

    for phrase in ranked_phrases():
        p = normalize(phrase)
        if not p:
            continue
        if len(p.split()) > 1:
            if norm == p or norm.startswith(p + " "):
                return True, phrase
            continue
        if p == "seed":
            if norm == "seed":
                return True, phrase
            if norm.startswith("seed ") and len(words) <= int(settings.get("max_words_for_bare_seed", 4)):
                return True, phrase
            if norm.endswith(" seed") and len(words) <= int(settings.get("max_words_for_bare_seed", 4)):
                return True, phrase
    return False, None

def log_event(row):
    row.setdefault("created_at", now())
    row.setdefault("version", "v87.1.0")
    with EVENTS_FILE.open("a") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")

def write_status(**data):
    base = {"created_at": now(), "version": "v87.1.0"}
    base.update(data)
    STATUS_FILE.write_text(json.dumps(base, indent=4, ensure_ascii=False))
    return base

def pid_alive(pid):
    try:
        os.kill(int(pid), 0)
        return True
    except Exception:
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

    panel = None
    if settings.get("open_panel", True):
        panel = open_seed_panel()

    if settings.get("immediate_followup", True):
        from seed_wake_conversation_v871 import wake_conversation_once
        return wake_conversation_once(
            wake_phrase=phrase,
            wake_transcript=transcript,
            seconds=settings.get("followup_seconds", 10),
        )

    return {"ok": True, "panel": panel, "woke": True}

def listen_loop():
    STOP_FILE.unlink(missing_ok=True)
    settings = load_settings()
    last_wake = 0

    print("\n=== SEED v87.1 WAKE POLISH + IMMEDIATE CONVERSATION ===")
    print("Listening for: " + ", ".join(ranked_phrases()))
    print("Say: Seed / hey Seed / wake up")
    print("Stop: Ctrl+C or python seed_wake_word_v871.py stop")
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

        set_avatar("listening", "v87.1 wake listener is listening for Seed.")
        res = record_and_transcribe(int(settings.get("listen_seconds", 3)))
        text = res.get("text", "")
        print(f"[listen] {text or '[empty]'}")

        if not res.get("ok"):
            log_event({"type": "listen_error", "error": res.get("error")})
            time.sleep(2)
            continue

        woke, phrase = is_wake_phrase(text)
        if woke:
            if time.time() - last_wake < float(settings.get("cooldown_seconds", 5)):
                print("[wake] ignored due to cooldown")
                time.sleep(0.5)
                continue
            last_wake = time.time()
            result = handle_wake(text, phrase)
            write_status(ok=True, running=True, mode="cooldown", last_wake=now(), last_transcript=text, matched_phrase=phrase, last_result=result)
            time.sleep(float(settings.get("cooldown_seconds", 5)))
        else:
            write_status(ok=True, running=True, mode="listening", last_transcript=text)
            time.sleep(float(settings.get("empty_backoff_seconds", 0.25)))

    set_avatar("idle", "Wake listener stopped.")
    write_status(ok=True, running=False, mode="stopped")
    return {"ok": True, "stopped": True}

def start_daemon():
    if PID_FILE.exists():
        try:
            pid = int(PID_FILE.read_text().strip())
            if pid_alive(pid):
                print(f"v87.1 wake listener already running pid={pid}")
                return {"ok": True, "already_running": True, "pid": pid}
        except Exception:
            pass

    STOP_FILE.unlink(missing_ok=True)
    log = LOG_FILE.open("a")
    proc = subprocess.Popen([sys.executable, "seed_wake_word_v871.py", "listen"], stdout=log, stderr=log)
    PID_FILE.write_text(str(proc.pid))
    print(f"Started v87.1 Seed wake listener pid={proc.pid}")
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
    print(f"v87.1 wake listener stop requested. pid={pid} stopped={stopped}")
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
    return {"created_at": now(), "version": "v87.1.0", "ok": True, "pid": pid, "alive": alive, "settings": load_settings(), "runtime_status": status, "log": str(LOG_FILE)}

def show_status():
    print("\n=== SEED v87.1 WAKE STATUS ===")
    print(json.dumps(wake_status(), indent=4, ensure_ascii=False))

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
        print(json.dumps(ranked_phrases(), indent=4, ensure_ascii=False))
    elif arg == "test":
        text = " ".join(sys.argv[2:])
        print({"text": text, "normalized": normalize(text), "match": is_wake_phrase(text)})
    elif arg == "set-followup":
        seconds = int(sys.argv[2])
        print(save_settings(followup_seconds=seconds))
    else:
        print("Commands: start | stop | listen | status | phrases | test <text> | set-followup <seconds>")

if __name__ == "__main__":
    main()
