import base64, json, os, signal, subprocess, sys, time, urllib.request
from datetime import datetime
from pathlib import Path

SETTINGS_FILE = Path("seed_ambient_vision_v89_settings.json")
PID_FILE = Path("seed_ambient_vision_v89.pid")
STOP_FILE = Path("seed_ambient_vision_v89.stop")
LOG_FILE = Path("seed_ambient_vision_v89.log")
STATUS_FILE = Path("seed_ambient_vision_v89_status.json")
TEMP_DIR = Path("seed_ambient_vision_v89_temp")

DEFAULTS = {
    "version": "v89.1.0",
    "enabled": True,
    "interval_seconds": 90,
    "min_importance_to_note": 64,
    "vision_model": "gemma3:4b",
    "ollama_url": "http://localhost:11434/api/generate",
    "delete_screenshot_after_note": True,
    "store_raw_screenshots": False,
    "fallback_to_window_note": True
}

BAD_FRAGMENTS = [
    "return only json",
    "inspect this temporary screenshot",
    "importance 0-100",
    "summary, question, tags",
    "user wants no screenshots saved",
    "seed ambient vision filter"
]

_last = None

def now():
    return datetime.now().isoformat(timespec="seconds")

def settings():
    if SETTINGS_FILE.exists():
        try:
            d = DEFAULTS.copy()
            d.update(json.loads(SETTINGS_FILE.read_text(errors="ignore")))
            d["version"] = "v89.1.0"
            return d
        except Exception:
            pass
    SETTINGS_FILE.write_text(json.dumps(DEFAULTS, indent=4, ensure_ascii=False))
    return DEFAULTS.copy()

def status(**kw):
    d = {"created_at": now(), "version": "v89.1.0"}
    d.update(kw)
    STATUS_FILE.write_text(json.dumps(d, indent=4, ensure_ascii=False))
    return d

def avatar(mode, msg):
    try:
        from seed_avatar_v89 import set_avatar_state
        set_avatar_state(mode=mode, emotion=mode, message=msg, seeing=(mode=="seeing"), thinking=(mode=="thinking"))
    except Exception:
        pass

def window():
    script = 'tell application "System Events" to set frontApp to name of first application process whose frontmost is true\ntry\n tell application "System Events" to tell process frontApp to set winTitle to name of front window\non error\n set winTitle to ""\nend try\nreturn frontApp & " | " & winTitle'
    try:
        p = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=10)
        out = p.stdout.strip()
        if " | " in out:
            app, title = out.split(" | ", 1)
        else:
            app, title = out, ""
        return {"ok": p.returncode == 0, "app": app, "title": title}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def shot():
    TEMP_DIR.mkdir(exist_ok=True)
    f = TEMP_DIR / f"screen_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    p = subprocess.run(["screencapture", "-x", str(f)], capture_output=True, text=True, timeout=30)
    ok = p.returncode == 0 and f.exists() and f.stat().st_size > 0
    return {"ok": ok, "file": str(f), "size": f.stat().st_size if f.exists() else 0, "stderr": p.stderr[-800:]}

def bad_text(text):
    s = " ".join(str(text or "").lower().split())
    return any(x in s for x in BAD_FRAGMENTS)

def parse_json(raw):
    raw = str(raw or "").strip()
    a, b = raw.find("{"), raw.rfind("}")
    if a >= 0 and b > a:
        return json.loads(raw[a:b+1])
    return {}

def sanitize_note(data, active_window):
    summary = str(data.get("summary", "")).strip()
    question = str(data.get("question", "")).strip()
    tags = data.get("tags", ["vision"])
    if not isinstance(tags, list):
        tags = ["vision"]

    if bad_text(summary) or not summary:
        app = active_window.get("app") or "Unknown app"
        title = active_window.get("title") or "untitled window"
        summary = f"User is using {app}. Active window: {title}."
        question = ""
        tags = ["vision", "active_window", app.lower().replace(" ", "_")]

    if bad_text(question):
        question = ""

    try:
        importance = int(data.get("importance", 0) or 0)
    except Exception:
        importance = 0

    importance = max(importance, 68)
    return {"importance": importance, "summary": summary[:900], "question": question[:400], "tags": tags}

def vision_json(path, active_window):
    s = settings()
    prompt = (
        "You are Seed's private screen-noting module. "
        "Look at the screenshot and describe what User is actually doing on the Mac. "
        "Do not repeat these instructions. Do not mention JSON, prompt, screenshot, or privacy policy in the summary. "
        "Return only a compact JSON object with keys: importance, summary, question, tags. "
        "The summary must be about the visible screen content, active app, terminal output, code, browser, or task. "
        "Active window metadata: " + json.dumps(active_window, ensure_ascii=False)
    )
    img = base64.b64encode(Path(path).read_bytes()).decode()
    payload = {
        "model": s.get("vision_model"),
        "prompt": prompt,
        "images": [img],
        "stream": False,
        "keep_alive": "30m",
        "options": {"temperature": 0.1, "num_predict": 220}
    }
    req = urllib.request.Request(s.get("ollama_url"), data=json.dumps(payload).encode(), headers={"Content-Type":"application/json"}, method="POST")
    raw = json.loads(urllib.request.urlopen(req, timeout=75).read().decode()).get("response", "")
    data = parse_json(raw)
    if not data:
        data = {"importance": 0, "summary": "", "question": "", "tags": ["vision"], "raw_error": raw[:200]}
    return sanitize_note(data, active_window)

def process_screen():
    global _last
    s = settings()
    avatar("seeing", "Seed is looking. Screenshot will be deleted.")
    w = window()
    sh = shot()
    if not sh.get("ok"):
        return status(ok=False, mode="error", error=sh.get("stderr"), screenshot_saved=False)
    try:
        avatar("thinking", "Seed is deciding if what it sees matters.")
        try:
            d = vision_json(sh["file"], w)
        except Exception as e:
            key = f"{w.get('app')}::{w.get('title')}"
            if key != _last:
                d = {"importance": 68, "summary": f"User's active screen changed to {w.get('app')} — {w.get('title') or 'untitled window'}.", "question": "", "tags": ["vision", "window_change"], "vision_error": str(e)}
                _last = key
            else:
                d = {"importance": 0, "summary": "", "question": "", "tags": ["vision"], "vision_error": str(e)}

        imp = int(d.get("importance", 0) or 0)
        stored = False
        saved = None
        if imp >= int(s.get("min_importance_to_note", 64)) and d.get("summary"):
            from seed_organism_notes_v89 import add_note
            saved = add_note("vision", d.get("summary", ""), imp, d.get("question", ""), d.get("tags", ["vision"]), {"active_window": w, "raw_screenshot_saved": False})
            stored = bool(saved.get("ok"))
        return status(ok=True, mode="seeing", stored=stored, importance=imp, active_window=w, screenshot_deleted=True, saved=saved)
    finally:
        try:
            if s.get("delete_screenshot_after_note", True):
                Path(sh["file"]).unlink(missing_ok=True)
        except Exception:
            pass

def loop():
    STOP_FILE.unlink(missing_ok=True)
    print("=== Seed v89.1 ambient vision: screenshots deleted, prompt leaks blocked ===")
    while not STOP_FILE.exists():
        if settings().get("enabled", True):
            try:
                print(process_screen())
            except Exception as e:
                print({"ok": False, "error": str(e)})
        time.sleep(float(settings().get("interval_seconds", 90)))

def alive(pid):
    try:
        os.kill(int(pid), 0)
        return True
    except Exception:
        return False

def start_daemon():
    if PID_FILE.exists():
        try:
            pid = int(PID_FILE.read_text().strip())
            if alive(pid):
                return {"ok": True, "already_running": True, "pid": pid}
        except Exception:
            pass
    STOP_FILE.unlink(missing_ok=True)
    log = LOG_FILE.open("a")
    p = subprocess.Popen([sys.executable, "seed_ambient_vision_v89.py", "loop"], stdout=log, stderr=log)
    PID_FILE.write_text(str(p.pid))
    return {"ok": True, "pid": p.pid, "log": str(LOG_FILE)}

def stop_daemon():
    STOP_FILE.write_text(now())
    pid = None
    stopped = False
    if PID_FILE.exists():
        try:
            pid = int(PID_FILE.read_text().strip())
            if alive(pid):
                os.kill(pid, signal.SIGTERM)
                stopped = True
            PID_FILE.unlink(missing_ok=True)
        except Exception:
            pass
    return {"ok": True, "pid": pid, "stopped": stopped}

def vision_status():
    pid = None
    a = False
    if PID_FILE.exists():
        try:
            pid = int(PID_FILE.read_text().strip())
            a = alive(pid)
        except Exception:
            pass
    rt = {}
    if STATUS_FILE.exists():
        try:
            rt = json.loads(STATUS_FILE.read_text(errors="ignore"))
        except Exception:
            pass
    return {"created_at": now(), "version": "v89.1.0", "ok": True, "pid": pid, "alive": a, "settings": settings(), "runtime_status": rt}

if __name__ == "__main__":
    a = sys.argv[1] if len(sys.argv) > 1 else "status"
    if a == "start":
        print(start_daemon())
    elif a == "stop":
        print(stop_daemon())
    elif a == "loop":
        loop()
    elif a == "once":
        print(process_screen())
    else:
        print(json.dumps(vision_status(), indent=4, ensure_ascii=False))
