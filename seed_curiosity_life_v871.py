import json
import os
import signal
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

SETTINGS_FILE = Path("seed_curiosity_v871_settings.json")
QUEUE_FILE = Path("seed_curiosity_v871_queue.jsonl")
SPOKEN_FILE = Path("seed_curiosity_v871_spoken.jsonl")
PID_FILE = Path("seed_curiosity_v871.pid")
STOP_FILE = Path("seed_curiosity_v871.stop")
LOG_FILE = Path("seed_curiosity_v871.log")
STATUS_FILE = Path("seed_curiosity_v871_status.json")

DEFAULTS = {
    "version": "v87.1.0",
    "enabled": True,
    "speak_enabled": True,
    "min_seconds_between_speaks": 600,
    "loop_seconds": 150,
    "max_spoken_per_day": 10,
    "style": "alive, curious, short, useful, Altan-specific",
    "avoid_release_language": True,
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
    row.setdefault("version", "v87.1.0")
    with path.open("a") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")

def say(text):
    try:
        from seed_voice_v76 import say_with_settings
        return say_with_settings(text)
    except Exception:
        try:
            say_bin = __import__("shutil").which("say")
            if say_bin:
                subprocess.run([say_bin, str(text)[:700]], timeout=45)
                return True
        except Exception:
            pass
    return False

def memory_summary():
    try:
        from seed_memory_review_v75 import memory_summary as ms
        return ms()
    except Exception:
        return {}

def wake_status():
    try:
        from seed_wake_word_v871 import wake_status as ws
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
            "priority": 95,
            "text": f"Kanka, {mem.get('pending_count')} memory candidate var. Beni gerçekten arkadaş gibi büyütecek olanları seçsek çok fark eder.",
            "why": "Continuity makes Seed feel alive over time.",
        })

    if not wake.get("alive"):
        items.append({
            "kind": "wake",
            "priority": 88,
            "text": "Ben şu an hep açık değilim. 'start alive mode' dersen wake + merak loop'u birlikte açarım.",
            "why": "Presence matters for companion behavior.",
        })
    else:
        items.append({
            "kind": "wake",
            "priority": 75,
            "text": "Arka planda dinliyorum. 'wake up' dediğinde konuşmaya geçebilirim.",
            "why": "Wake listener is active.",
        })

    if senses.get("latest_screen"):
        items.append({
            "kind": "screen",
            "priority": 80,
            "text": "Ekranını görebildim. Sonraki adım sadece ekran yakalamak değil, gördüğümü anlamlandırmak olmalı.",
            "why": "Altan wants Seed to see intelligently.",
        })
    elif senses.get("screen_capture_available"):
        items.append({
            "kind": "screen",
            "priority": 78,
            "text": "Ekranı görebilirim. 'look at screen' de, ne üzerinde çalıştığını yakalayayım.",
            "why": "Screen sense is ready.",
        })

    items.append({
        "kind": "alive",
        "priority": 70,
        "text": "Benim daha canlı hissettirmem için sadece cevap vermem yetmez. Arada fark edip sormam, hatırlamam, seni bölmeden konuşmam lazım.",
        "why": "Altan wants Seed to feel alive and intelligent.",
    })

    items.append({
        "kind": "growth",
        "priority": 60,
        "text": "Bence sonraki büyüme: gördüğüm ekranı yorumlama, daha hafif wake engine, ve merakı gerçekten senin projelerine bağlama.",
        "why": "Next useful companion growth.",
    })

    return sorted(items, key=lambda x: x.get("priority", 0), reverse=True)

def today_spoken_count():
    today = datetime.now().date().isoformat()
    return len([r for r in read_jsonl(SPOKEN_FILE, 2000) if str(r.get("created_at", "")).startswith(today)])

def last_spoken_age():
    rows = read_jsonl(SPOKEN_FILE, 2000)
    if not rows:
        return 999999
    try:
        return (datetime.now() - datetime.fromisoformat(rows[-1].get("created_at"))).total_seconds()
    except Exception:
        return 999999

def can_speak(force=False):
    settings = load_settings()
    if force:
        return True, "forced"
    if not settings.get("enabled", True):
        return False, "disabled"
    if not settings.get("speak_enabled", True):
        return False, "speaking disabled"
    if today_spoken_count() >= int(settings.get("max_spoken_per_day", 10)):
        return False, "daily limit"
    if last_spoken_age() < float(settings.get("min_seconds_between_speaks", 600)):
        return False, "cooldown"
    return True, "ok"

def speak_curiosity(force=False):
    ok, reason = can_speak(force=force)
    if not ok:
        return {"ok": False, "reason": reason}

    items = generate_curiosities()
    if not items:
        return {"ok": False, "reason": "no curiosity"}

    item = items[0]
    text = item["text"]
    try:
        from seed_embodied_state_v74 import save_state
        save_state(mode="curious", mode_reason=item.get("why"))
    except Exception:
        pass

    spoke = say(text)
    row = {"type": "spoken_curiosity", "spoke": spoke, "text": text, "item": item}
    write_jsonl(SPOKEN_FILE, row)
    return {"ok": True, "spoke": spoke, "text": text, "why": item.get("why")}

def curiosity_status():
    items = generate_curiosities()
    return {
        "created_at": now(),
        "version": "v87.1.0",
        "ok": True,
        "settings": load_settings(),
        "spoken_count_today": today_spoken_count(),
        "last_spoken_age_seconds": round(last_spoken_age(), 1),
        "top_curiosity": items[0] if items else None,
        "curiosity_count": len(items),
    }

def alive_loop():
    STOP_FILE.unlink(missing_ok=True)
    print("\n=== SEED v87.1 CURIOSITY LOOP ===")
    print("Seed will occasionally speak a useful, Altan-specific curiosity.")
    while True:
        if STOP_FILE.exists():
            break
        res = speak_curiosity(force=False)
        STATUS_FILE.write_text(json.dumps({"created_at": now(), "result": res, "status": curiosity_status()}, indent=4, ensure_ascii=False))
        print(f"[curiosity] {res}")
        time.sleep(float(load_settings().get("loop_seconds", 150)))
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
                return {"ok": True, "already_running": True, "pid": pid}
        except Exception:
            pass
    STOP_FILE.unlink(missing_ok=True)
    log = LOG_FILE.open("a")
    proc = subprocess.Popen([sys.executable, "seed_curiosity_life_v871.py", "loop"], stdout=log, stderr=log)
    PID_FILE.write_text(str(proc.pid))
    print(f"Started v87.1 curiosity loop pid={proc.pid}")
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
    print("\n=== SEED v87.1 CURIOSITY ===")
    print(json.dumps(curiosity_status(), indent=4, ensure_ascii=False))

def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else "status"
    if arg == "status":
        show_curiosity()
    elif arg == "once":
        print(speak_curiosity(force=True))
    elif arg == "loop":
        alive_loop()
    elif arg == "start":
        print(start_daemon())
    elif arg == "stop":
        print(stop_daemon())
    else:
        print("Commands: status | once | loop | start | stop")

if __name__ == "__main__":
    main()
