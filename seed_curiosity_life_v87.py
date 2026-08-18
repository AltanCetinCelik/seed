import json
import os
import signal
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

SETTINGS_FILE = Path("seed_curiosity_v87_settings.json")
QUEUE_FILE = Path("seed_curiosity_v87_queue.jsonl")
SPOKEN_FILE = Path("seed_curiosity_v87_spoken.jsonl")
STATUS_FILE = Path("seed_curiosity_v87_status.json")
PID_FILE = Path("seed_curiosity_v87.pid")
STOP_FILE = Path("seed_curiosity_v87.stop")
LOG_FILE = Path("seed_curiosity_v87.log")

DEFAULTS = {
    "version": "v87.0.0",
    "enabled": True,
    "speak_enabled": True,
    "min_seconds_between_speaks": 900,
    "loop_seconds": 180,
    "max_spoken_per_day": 8,
    "tone": "friendly, curious, alive, grounded",
    "anti_spam": True,
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

def read_jsonl(path, limit=1000):
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(errors="ignore").splitlines()[-limit:]:
        try:
            rows.append(json.loads(line))
        except Exception:
            pass
    return rows

def write_jsonl(path, row):
    row.setdefault("created_at", now())
    row.setdefault("version", "v87.0.0")
    with path.open("a") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")

def today_spoken_count():
    today = datetime.now().date().isoformat()
    return len([r for r in read_jsonl(SPOKEN_FILE, 1000) if str(r.get("created_at", "")).startswith(today)])

def last_spoken_age():
    rows = read_jsonl(SPOKEN_FILE, 1000)
    if not rows:
        return 999999
    try:
        last = rows[-1].get("created_at", "")
        dt = datetime.fromisoformat(last)
        return (datetime.now() - dt).total_seconds()
    except Exception:
        return 999999

def memory_summary():
    try:
        from seed_memory_review_v75 import memory_summary as ms
        return ms()
    except Exception:
        return {}

def wake_status():
    try:
        from seed_wake_word_v861 import wake_status as ws
        return ws()
    except Exception:
        return {}

def sense_status():
    try:
        from seed_senses_v87 import sense_status as ss
        return ss()
    except Exception:
        return {}

def generate_curiosities():
    mem = memory_summary()
    wake = wake_status()
    senses = sense_status()
    items = []

    if mem.get("pending_count", 0):
        items.append({
            "kind": "memory",
            "priority": 90,
            "text": f"Kanka, I still see {mem.get('pending_count')} memory candidates waiting. Want me to help pick which ones are actually worth remembering?",
            "why": "Memory review improves Seed's continuity with User.",
        })

    if not wake.get("alive"):
        items.append({
            "kind": "wake",
            "priority": 80,
            "text": "I can stay in wake mode now. Say 'start wake listener' and I'll listen for Seed or wake up.",
            "why": "User wants Seed to feel present and open by voice.",
        })
    else:
        items.append({
            "kind": "wake",
            "priority": 70,
            "text": "I'm listening in the background. Say 'wake up' when you want me, and I'll come forward.",
            "why": "Wake listener is active.",
        })

    if senses.get("screen_capture_available"):
        items.append({
            "kind": "senses",
            "priority": 75,
            "text": "I can look at your screen now. Say 'look at screen' and I'll capture what I'm seeing.",
            "why": "Screen sense is available.",
        })

    items.append({
        "kind": "alive",
        "priority": 60,
        "text": "I don't want to just wait like a dead command line. I can check in, notice Seed problems, and ask you things when it actually matters.",
        "why": "User explicitly wants Seed to feel alive, curious, and intelligent.",
    })

    items.append({
        "kind": "growth",
        "priority": 55,
        "text": "Next, I should become lighter: wake detection without heavy Whisper loops, better vision, and smarter curiosity tied to what you're building.",
        "why": "This is the next growth step after wake mode.",
    })

    return sorted(items, key=lambda x: x.get("priority", 0), reverse=True)

def enqueue_curiosities():
    items = generate_curiosities()
    for i, item in enumerate(items, start=1):
        row = {"id": f"curio_{int(time.time())}_{i}", "status": "queued", **item}
        write_jsonl(QUEUE_FILE, row)
    return {"ok": True, "queued": len(items), "items": items}

def can_speak(force=False):
    settings = load_settings()
    if force:
        return True, "forced"
    if not settings.get("enabled", True):
        return False, "disabled"
    if not settings.get("speak_enabled", True):
        return False, "speaking disabled"
    if today_spoken_count() >= int(settings.get("max_spoken_per_day", 8)):
        return False, "daily limit"
    if last_spoken_age() < float(settings.get("min_seconds_between_speaks", 900)):
        return False, "cooldown"
    return True, "ok"

def speak(text):
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

def speak_curiosity(force=False):
    ok, reason = can_speak(force=force)
    if not ok:
        return {"ok": False, "reason": reason}

    items = generate_curiosities()
    if not items:
        return {"ok": False, "reason": "no curiosity"}

    item = items[0]
    text = item["text"]
    set_avatar("curious", item.get("why", "Seed is curious."))
    spoke = speak(text)
    row = {"type": "spoken_curiosity", "spoke": spoke, "text": text, "item": item}
    write_jsonl(SPOKEN_FILE, row)
    return {"ok": True, "spoke": spoke, "text": text, "why": item.get("why")}

def curiosity_status():
    settings = load_settings()
    return {
        "created_at": now(),
        "version": "v87.0.0",
        "ok": True,
        "settings": settings,
        "queued_count": len(read_jsonl(QUEUE_FILE)),
        "spoken_count_today": today_spoken_count(),
        "last_spoken_age_seconds": round(last_spoken_age(), 1),
        "top_curiosity": generate_curiosities()[0] if generate_curiosities() else None,
    }

def alive_loop():
    STOP_FILE.unlink(missing_ok=True)
    print("\n=== SEED v87 ALIVE CURIOSITY LOOP ===")
    print("Seed will notice, queue curiosity, and sometimes speak within anti-spam limits.")
    while True:
        if STOP_FILE.exists():
            print("Stop file found. Alive curiosity stopping.")
            break
        settings = load_settings()
        if settings.get("enabled", True):
            enqueue_curiosities()
            res = speak_curiosity(force=False)
            STATUS_FILE.write_text(json.dumps({"created_at": now(), "version": "v87.0.0", "ok": True, "last_result": res, "status": curiosity_status()}, indent=4, ensure_ascii=False))
            print(f"[curiosity] {res}")
        time.sleep(float(settings.get("loop_seconds", 180)))
    STATUS_FILE.write_text(json.dumps({"created_at": now(), "version": "v87.0.0", "ok": True, "running": False}, indent=4))
    return {"ok": True}

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
                print(f"Curiosity already running pid={pid}")
                return {"ok": True, "already_running": True, "pid": pid}
        except Exception:
            pass
    STOP_FILE.unlink(missing_ok=True)
    log = LOG_FILE.open("a")
    proc = subprocess.Popen([sys.executable, "seed_curiosity_life_v87.py", "loop"], stdout=log, stderr=log)
    PID_FILE.write_text(str(proc.pid))
    print(f"Started Seed curiosity loop pid={proc.pid}")
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
    return {"ok": True, "pid": pid, "stopped": stopped}

def show_curiosity():
    print("\n=== SEED v87 CURIOSITY / ALIVE LOOP ===")
    print(json.dumps(curiosity_status(), indent=4, ensure_ascii=False))

def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else "status"
    if arg == "status":
        show_curiosity()
    elif arg == "once":
        print(speak_curiosity(force=True))
    elif arg == "queue":
        print(json.dumps(enqueue_curiosities(), indent=4, ensure_ascii=False))
    elif arg == "loop":
        alive_loop()
    elif arg == "start":
        print(start_daemon())
    elif arg == "stop":
        print(stop_daemon())
    elif arg == "set-loop":
        seconds = int(sys.argv[2]) if len(sys.argv) > 2 else 180
        print(save_settings(loop_seconds=seconds))
    elif arg == "set-cooldown":
        seconds = int(sys.argv[2]) if len(sys.argv) > 2 else 900
        print(save_settings(min_seconds_between_speaks=seconds))
    else:
        print("Commands: status | once | queue | loop | start | stop | set-loop <seconds> | set-cooldown <seconds>")

if __name__ == "__main__":
    main()
