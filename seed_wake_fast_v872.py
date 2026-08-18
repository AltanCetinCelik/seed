import json
import os
import re
import signal
import subprocess
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path

SETTINGS_FILE = Path("seed_wake_fast_v872_settings.json")
LOG_FILE = Path("seed_wake_fast_v872.log")
EVENTS_FILE = Path("seed_wake_fast_v872_events.jsonl")
PID_FILE = Path("seed_wake_fast_v872.pid")
STOP_FILE = Path("seed_wake_fast_v872.stop")
STATUS_FILE = Path("seed_wake_fast_v872_status.json")

DEFAULTS = {
    "version": "v87.2.0",
    "enabled": True,
    "wake_phrases": ["wake up seed", "hey seed", "okay seed", "ok seed", "wake up", "seed"],
    "wake_listen_seconds": 2,
    "followup_seconds": 7,
    "cooldown_seconds": 3,
    "empty_backoff_seconds": 0.15,
    "open_panel": True,
    "speak_reply": True,
    "fast_model": "gemma3:4b",
    "fallback_models": ["gemma3:4b", "llama3.1:8b"],
    "ollama_url": "http://localhost:11434/api/generate",
    "keep_alive": "45m",
    "num_predict": 90,
    "temperature": 0.65,
    "timeout_seconds": 45,
    "warm_on_start": True,
    "max_words_for_bare_seed": 4,
    "print_timestamps": True
}

FALSE_POSITIVES = {"see it", "see the", "eat", "it", "sea", "are you happy", "it's great", "i buy it"}

def now():
    return datetime.now().isoformat(timespec="seconds")

def stamp(label):
    if load_settings().get("print_timestamps", True):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {label}")

def load_settings():
    if SETTINGS_FILE.exists():
        try:
            base = DEFAULTS.copy()
            base.update(json.loads(SETTINGS_FILE.read_text(errors="ignore")))
            base["version"] = "v87.2.0"
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
    text = text.replace("wake u", "wake up").replace("wakeup", "wake up")
    text = re.sub(r"[^a-zçğıöşü0-9\s]", " ", text)
    return " ".join(text.split())

def ranked_phrases():
    phrases = [str(p).strip() for p in load_settings().get("wake_phrases", []) if str(p).strip()]
    return sorted(set(phrases), key=lambda x: len(normalize(x).split()), reverse=True)

def match_wake(transcript):
    norm = normalize(transcript)
    if not norm or norm in FALSE_POSITIVES:
        return False, None, ""

    words = norm.split()
    settings = load_settings()

    for phrase in ranked_phrases():
        p = normalize(phrase)
        if not p:
            continue

        if len(p.split()) > 1:
            if norm == p:
                return True, phrase, ""
            if norm.startswith(p + " "):
                return True, phrase, norm[len(p):].strip()
            continue

        if p == "seed":
            if norm == "seed":
                return True, phrase, ""
            if norm.startswith("seed ") and len(words) <= int(settings.get("max_words_for_bare_seed", 4)):
                return True, phrase, norm[len("seed"):].strip()
            if norm.endswith(" seed") and len(words) <= int(settings.get("max_words_for_bare_seed", 4)):
                before = norm[:-len(" seed")].strip()
                return True, phrase, before

    return False, None, ""

def log_event(row):
    row.setdefault("created_at", now())
    row.setdefault("version", "v87.2.0")
    with EVENTS_FILE.open("a") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")

def write_status(**data):
    base = {"created_at": now(), "version": "v87.2.0"}
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

def say(text):
    if not load_settings().get("speak_reply", True):
        return False
    try:
        from seed_voice_v76 import say_with_settings
        return say_with_settings(text)
    except Exception:
        try:
            say_bin = __import__("shutil").which("say")
            if say_bin:
                subprocess.run([say_bin, str(text)[:900]], timeout=60)
                return True
        except Exception:
            pass
    return False

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

def ollama_generate(model, prompt, num_predict=None):
    settings = load_settings()
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "keep_alive": settings.get("keep_alive", "45m"),
        "options": {
            "temperature": float(settings.get("temperature", 0.65)),
            "num_predict": int(num_predict or settings.get("num_predict", 90)),
        }
    }
    req = urllib.request.Request(
        settings.get("ollama_url", "http://localhost:11434/api/generate"),
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=int(settings.get("timeout_seconds", 45))) as resp:
        parsed = json.loads(resp.read().decode("utf-8", errors="ignore"))
        return (parsed.get("response") or "").strip()

def model_candidates():
    settings = load_settings()
    models = []
    first = settings.get("fast_model", "gemma3:4b")
    if first:
        models.append(first)
    for m in settings.get("fallback_models", []):
        if m and m not in models:
            models.append(m)
    return models or ["gemma3:4b", "llama3.1:8b"]

def warm_model():
    settings = load_settings()
    model = settings.get("fast_model", "gemma3:4b")
    stamp(f"Warming model {model}...")
    try:
        reply = ollama_generate(model, "Reply with exactly: ready", num_predict=4)
        stamp(f"Model warm: {reply[:50]}")
        return {"ok": True, "model": model, "reply": reply}
    except Exception as e:
        stamp(f"Model warm failed: {e}")
        return {"ok": False, "model": model, "error": str(e)}

def build_prompt(text):
    return f"""You are Seed, User's private local AI companion/friend on his Mac.

Rules:
- Be quick, warm, curious, and useful.
- You are not a public release/product.
- Do not claim literal biological consciousness.
- You can sound alive as a companion expression.
- Match User's language: Turkish, English, or mixed.
- Keep wake replies short unless he asks for details.

User just woke you and said:
{text}

Seed:"""

def answer_fast(text):
    prompt = build_prompt(text)
    errors = []
    for model in model_candidates():
        try:
            reply = ollama_generate(model, prompt)
            if reply and reply.lower() not in {"normal", "ok", "okay"}:
                return {"ok": True, "reply": reply, "model": model, "route": "v87.2_direct_warm_ollama"}
            errors.append({"model": model, "error": "empty"})
        except Exception as e:
            errors.append({"model": model, "error": str(e)})
    return {"ok": False, "reply": "", "errors": errors, "route": "v87.2_direct_warm_ollama"}

def handle_wake(transcript, phrase, inline_followup=""):
    settings = load_settings()
    stamp(f"WAKE phrase={phrase!r} transcript={transcript!r} inline={inline_followup!r}")
    set_avatar("awake", f"Fast wake phrase heard: {phrase}")
    log_event({"type": "wake", "phrase": phrase, "transcript": transcript, "inline_followup": inline_followup})

    panel = None
    if settings.get("open_panel", True):
        panel = open_seed_panel()

    if inline_followup:
        text = inline_followup
        stamp(f"Using inline follow-up: {text!r}")
    else:
        stamp(f"Listening for follow-up for {settings.get('followup_seconds', 7)}s...")
        set_avatar("listening", "Seed is listening for follow-up after wake.")
        rec = record_and_transcribe(int(settings.get("followup_seconds", 7)))
        text = (rec.get("text") or "").strip()
        stamp(f"Follow-up transcript: {text or '[empty]'}")
        log_event({"type": "followup_record", "record": rec})
        if not text:
            reply = "I woke up, but I didn't catch that."
            say(reply)
            return {"ok": False, "stage": "empty", "reply": reply, "panel": panel, "record": rec}

    stamp("Thinking fast...")
    set_avatar("thinking", "Seed is answering through v87.2 fast wake route.")
    answer = answer_fast(text)
    reply = answer.get("reply", "")

    stamp(f"Reply ready with {answer.get('model')}: {reply[:120]}")
    spoke = False
    if reply:
        set_avatar("speaking", "Seed is speaking fast wake reply.")
        spoke = say(reply)

    set_avatar("idle", "Fast wake conversation done.")
    row = {"ok": bool(reply), "stage": "done", "wake_phrase": phrase, "wake_transcript": transcript, "followup": text, "reply": reply, "spoke": spoke, "answer": answer, "panel": panel}
    log_event(row)
    return row

def listen_loop():
    STOP_FILE.unlink(missing_ok=True)
    settings = load_settings()
    last_wake = 0

    print("\n=== SEED v87.2 FAST WAKE LISTENER ===")
    print("Listening for: " + ", ".join(ranked_phrases()))
    print("Say: wake up / hey Seed / wake up what are you")
    print("Stop: Ctrl+C or python seed_wake_fast_v872.py stop")
    if settings.get("warm_on_start", True):
        warm_model()

    write_status(ok=True, running=True, mode="listening", settings=settings)

    while True:
        if STOP_FILE.exists():
            print("Stop file found. Fast wake listener stopping.")
            break

        set_avatar("listening", "Fast wake listener is listening for Seed.")
        res = record_and_transcribe(int(load_settings().get("wake_listen_seconds", 2)))
        text = res.get("text", "")
        print(f"[listen] {text or '[empty]'}")

        if not res.get("ok"):
            log_event({"type": "listen_error", "error": res.get("error")})
            time.sleep(1)
            continue

        woke, phrase, inline_followup = match_wake(text)
        if woke:
            if time.time() - last_wake < float(load_settings().get("cooldown_seconds", 3)):
                print("[wake] ignored due to cooldown")
                time.sleep(0.3)
                continue
            last_wake = time.time()
            result = handle_wake(text, phrase, inline_followup=inline_followup)
            write_status(ok=True, running=True, mode="cooldown", last_wake=now(), last_transcript=text, matched_phrase=phrase, last_result=result)
            time.sleep(float(load_settings().get("cooldown_seconds", 3)))
        else:
            write_status(ok=True, running=True, mode="listening", last_transcript=text)
            time.sleep(float(load_settings().get("empty_backoff_seconds", 0.15)))

    set_avatar("idle", "Fast wake listener stopped.")
    write_status(ok=True, running=False, mode="stopped")
    return {"ok": True}

def start_daemon():
    if PID_FILE.exists():
        try:
            pid = int(PID_FILE.read_text().strip())
            if pid_alive(pid):
                print(f"Fast wake already running pid={pid}")
                return {"ok": True, "already_running": True, "pid": pid}
        except Exception:
            pass
    STOP_FILE.unlink(missing_ok=True)
    log = LOG_FILE.open("a")
    proc = subprocess.Popen([sys.executable, "seed_wake_fast_v872.py", "listen"], stdout=log, stderr=log)
    PID_FILE.write_text(str(proc.pid))
    print(f"Started Seed fast wake pid={proc.pid}")
    print(f"Log: {LOG_FILE}")
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
    write_status(ok=True, running=False, mode="stopped")
    print(f"Fast wake stop requested. pid={pid} stopped={stopped}")
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
    return {"created_at": now(), "version": "v87.2.0", "ok": True, "pid": pid, "alive": alive, "settings": load_settings(), "runtime_status": status, "log": str(LOG_FILE)}

def show_status():
    print("\n=== SEED v87.2 FAST WAKE STATUS ===")
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
    elif arg == "warm":
        print(warm_model())
    elif arg == "test":
        text = " ".join(sys.argv[2:])
        print({"text": text, "normalized": normalize(text), "match": match_wake(text)})
    elif arg == "ask":
        text = " ".join(sys.argv[2:]) or "hello"
        print(answer_fast(text))
    elif arg == "set-model":
        print(save_settings(fast_model=sys.argv[2]))
    elif arg == "set-followup":
        print(save_settings(followup_seconds=int(sys.argv[2])))
    else:
        print("Commands: start | stop | listen | status | warm | test <text> | ask <text> | set-model <model> | set-followup <seconds>")

if __name__ == "__main__":
    main()
