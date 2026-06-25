import json
import os
import signal
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

SETTINGS_FILE = Path("seed_wake_context_v91_settings.json")
PID_FILE = Path("seed_wake_context_v91.pid")
STOP_FILE = Path("seed_wake_context_v91.stop")
LOG_FILE = Path("seed_wake_context_v91.log")
STATUS_FILE = Path("seed_wake_context_v91_status.json")

DEFAULTS = {
    "version": "v91.0.0",
    "wake_listen_seconds": 2,
    "followup_seconds": 7,
    "cooldown_seconds": 3,
    "speak_reply": True,
    "open_panel_on_wake": True,
    "wake_phrases": ["wake up seed", "wake up", "hey seed", "ok seed", "okay seed", "seed"],
    "wake_mishears": ["make up", "makeup", "weight up", "wait up", "wake app"],
    "max_words_for_bare_seed": 4
}

def now():
    return datetime.now().isoformat(timespec="seconds")

def load_settings():
    if SETTINGS_FILE.exists():
        try:
            d = DEFAULTS.copy()
            d.update(json.loads(SETTINGS_FILE.read_text(errors="ignore")))
            d["version"] = "v91.0.0"
            return d
        except Exception:
            pass
    SETTINGS_FILE.write_text(json.dumps(DEFAULTS, indent=4, ensure_ascii=False))
    return DEFAULTS.copy()

def write_status(**kw):
    data = {"created_at": now(), "version": "v91.0.0"}
    data.update(kw)
    STATUS_FILE.write_text(json.dumps(data, indent=4, ensure_ascii=False))
    return data

def norm(text):
    import re
    text = str(text or "").lower()
    text = text.replace("wake upp", "wake up")
    text = re.sub(r"[^a-z0-9çğıöşü\s]", " ", text)
    return " ".join(text.split())

def match_wake(text):
    s = load_settings()
    n = norm(text)
    phrases = s.get("wake_phrases", []) + s.get("wake_mishears", [])
    for phrase in sorted(phrases, key=len, reverse=True):
        p = norm(phrase)
        if not p:
            continue
        if n == p or n.startswith(p + " "):
            inline = n[len(p):].strip()
            if p == "seed" and inline == "" and len(n.split()) > int(s.get("max_words_for_bare_seed", 4)):
                continue
            real_phrase = "wake up" if p in [norm(x) for x in s.get("wake_mishears", [])] else phrase
            return True, real_phrase, inline
        if p in n and p != "seed":
            before, after = n.split(p, 1)
            if len(before.split()) <= 3:
                real_phrase = "wake up" if p in [norm(x) for x in s.get("wake_mishears", [])] else phrase
                return True, real_phrase, after.strip()
    return False, None, ""

def record_and_transcribe(seconds):
    audio_path = None
    try:
        from seed_live_voice_v731 import record_audio, transcribe_audio
        audio_path, device = record_audio(seconds)
        transcript = transcribe_audio(audio_path)
        text = (transcript.get("text") or "").strip()
        return {"ok": True, "text": text, "device": device}
    except Exception as e:
        return {"ok": False, "text": "", "error": str(e)}
    finally:
        try:
            if audio_path:
                Path(audio_path).unlink(missing_ok=True)
        except Exception:
            pass

def say(text):
    if not load_settings().get("speak_reply", True):
        return False
    try:
        from seed_voice_v76 import say_with_settings
        return say_with_settings(text)
    except Exception:
        try:
            subprocess.run(["say", str(text)[:900]], timeout=70)
            return True
        except Exception:
            return False

def open_panel():
    if not load_settings().get("open_panel_on_wake", True):
        return False
    try:
        subprocess.Popen(["open", "http://127.0.0.1:8797"])
        return True
    except Exception:
        return False

def ask_contextual(message):
    from seed_contextual_chat_v91 import ask
    return ask(message)

def listen_loop():
    s = load_settings()
    STOP_FILE.unlink(missing_ok=True)
    print("\n=== SEED v91 CONTEXTUAL WAKE LISTENER ===")
    print("Context: Memory Garden + organism state.")
    print("Wake: wake up / make up / hey seed / seed")
    print("Stop: Ctrl+C or python seed_wake_context_v91.py stop")
    write_status(ok=True, running=True, mode="listening")
    try:
        while not STOP_FILE.exists():
            res = record_and_transcribe(int(load_settings().get("wake_listen_seconds", 2)))
            if not res.get("ok"):
                print("[listen-error]", res.get("error"))
                write_status(ok=False, mode="listen_error", error=res.get("error"))
                time.sleep(1)
                continue

            text = res.get("text", "")
            print("[listen]", text or "[empty]")
            matched, phrase, inline = match_wake(text)
            if not matched:
                continue

            print(f"[{now()[11:19]}] WAKE phrase='{phrase}' transcript='{text}' inline='{inline}'")
            open_panel()

            follow = inline
            if not follow:
                print(f"[{now()[11:19]}] Listening for follow-up for {load_settings().get('followup_seconds', 7)}s...")
                res2 = record_and_transcribe(int(load_settings().get("followup_seconds", 7)))
                follow = (res2.get("text") or "").strip()
                print(f"[{now()[11:19]}] Follow-up transcript: {follow or '[empty]'}")

            if follow:
                print(f"[{now()[11:19]}] Thinking with v91 context...")
                answer = ask_contextual(follow)
                reply = answer.get("reply", "")
                print(f"[{now()[11:19]}] Reply ready with {answer.get('model')}: {reply[:180]}")
                write_status(ok=True, mode="replied", wake=text, followup=follow, reply=reply, model=answer.get("model"))
                if reply:
                    say(reply)
            else:
                write_status(ok=True, mode="wake_no_followup", wake=text)

            time.sleep(float(load_settings().get("cooldown_seconds", 3)))
    except KeyboardInterrupt:
        print("\nSeed v91 wake listener stopped.")
        write_status(ok=True, running=False, mode="keyboard_interrupt")
    finally:
        write_status(ok=True, running=False, mode="stopped")

def pid_alive(pid):
    try:
        os.kill(int(pid), 0)
        return True
    except Exception:
        return False

def start_daemon():
    if PID_FILE.exists():
        try:
            pid = int(PID_FILE.read_text().strip())
            if pid_alive(pid):
                return {"ok": True, "already_running": True, "pid": pid}
        except Exception:
            pass
    STOP_FILE.unlink(missing_ok=True)
    log = LOG_FILE.open("a")
    proc = subprocess.Popen([sys.executable, "seed_wake_context_v91.py", "listen"], stdout=log, stderr=log)
    PID_FILE.write_text(str(proc.pid))
    return {"ok": True, "pid": proc.pid, "log": str(LOG_FILE)}

def stop_daemon():
    STOP_FILE.write_text(now())
    pid = None
    stopped = False
    if PID_FILE.exists():
        try:
            pid = int(PID_FILE.read_text().strip())
            if pid_alive(pid):
                os.kill(pid, signal.SIGTERM)
                stopped = True
            PID_FILE.unlink(missing_ok=True)
        except Exception:
            pass
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
    runtime = {}
    if STATUS_FILE.exists():
        try:
            runtime = json.loads(STATUS_FILE.read_text(errors="ignore"))
        except Exception:
            pass
    return {"created_at": now(), "version": "v91.0.0", "ok": True, "pid": pid, "alive": alive, "settings": load_settings(), "runtime": runtime}


# v107 reliable wake override
try:
    from seed_wake_reliability_v107 import match_wake_reliable as _seed_v107_match_wake_reliable

    def match_wake(text):
        return _seed_v107_match_wake_reliable(text)
except Exception:
    pass

if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "status"
    if arg == "listen":
        listen_loop()
    elif arg == "start":
        print(start_daemon())
    elif arg == "stop":
        print(stop_daemon())
    elif arg == "ask":
        msg = " ".join(sys.argv[2:]).strip() or "hello"
        print(json.dumps(ask_contextual(msg), indent=4, ensure_ascii=False))
    elif arg == "test":
        msg = " ".join(sys.argv[2:]).strip() or "make up what are you"
        print({"text": msg, "match": match_wake(msg)})
    elif arg == "status":
        print(json.dumps(wake_status(), indent=4, ensure_ascii=False))
    else:
        print("Commands: listen | start | stop | ask <msg> | test <wake text> | status")
