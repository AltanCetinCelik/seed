import json
import os
import platform
import shlex
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

SETTINGS_FILE = Path("seed_mac_body_v88_settings.json")
LOG_FILE = Path("seed_mac_body_v88_actions.jsonl")
SCREEN_DIR = Path("seed_mac_body_v88_screens")

DEFAULTS = {
    "version": "v88.0.0",
    "mode": "assist",
    "allow_shell": False,
    "shell_timeout_seconds": 45,
    "log_actions": True,
    "require_confirmation_for_shell": True,
    "note": "Seed is User's private Mac body layer. Actions are local, visible, and logged."
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

def log(row):
    row.setdefault("created_at", now())
    row.setdefault("version", "v88.0.0")
    if load_settings().get("log_actions", True):
        with LOG_FILE.open("a") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

def tool(name):
    return shutil.which(name)

def run(cmd, timeout=30):
    log({"type": "run", "cmd": cmd})
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return {"ok": proc.returncode == 0, "returncode": proc.returncode, "stdout": proc.stdout[-4000:], "stderr": proc.stderr[-4000:], "cmd": cmd}

def osascript(script):
    return run(["osascript", "-e", script], timeout=20)

def body_status():
    settings = load_settings()
    return {
        "created_at": now(),
        "version": "v88.0.0",
        "ok": True,
        "platform": platform.platform(),
        "mode": settings.get("mode"),
        "allow_shell": settings.get("allow_shell"),
        "tools": {
            "osascript": tool("osascript"),
            "screencapture": tool("screencapture"),
            "open": tool("open"),
            "say": tool("say"),
            "cliclick": tool("cliclick"),
            "python": sys.executable,
        },
        "permissions_needed": [
            "Accessibility for typing/keyboard automation",
            "Screen Recording for screenshot vision",
            "Microphone for hearing/wake",
            "Automation permissions when macOS asks",
        ],
        "commands": [
            "body status",
            "body permissions",
            "open app Safari",
            "open url https://...",
            "take screenshot",
            "type text <text>",
            "press enter",
            "press command space",
            "body trust on/off",
            "allow shell on/off",
            "run shell <command>",
        ],
    }

def open_permissions(kind="all"):
    urls = {
        "accessibility": "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility",
        "screen": "x-apple.systempreferences:com.apple.preference.security?Privacy_ScreenCapture",
        "microphone": "x-apple.systempreferences:com.apple.preference.security?Privacy_Microphone",
        "automation": "x-apple.systempreferences:com.apple.preference.security?Privacy_Automation",
    }
    opened = []
    targets = urls.items() if kind == "all" else [(kind, urls.get(kind))]
    for k, url in targets:
        if url:
            subprocess.Popen(["open", url])
            opened.append(k)
    return {"ok": True, "opened": opened}

def open_app(app):
    app = str(app).strip()
    if not app:
        return {"ok": False, "error": "empty app"}
    result = run(["open", "-a", app], timeout=20)
    log({"type": "open_app", "app": app, "result": result})
    return result

def open_url(url):
    url = str(url).strip()
    if not url:
        return {"ok": False, "error": "empty url"}
    if not (url.startswith("http://") or url.startswith("https://") or url.startswith("file://")):
        url = "https://" + url
    result = run(["open", url], timeout=20)
    log({"type": "open_url", "url": url, "result": result})
    return result

def screenshot():
    SCREEN_DIR.mkdir(exist_ok=True)
    out = SCREEN_DIR / f"screen_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    if not tool("screencapture"):
        return {"ok": False, "error": "screencapture missing"}
    proc = subprocess.run(["screencapture", "-x", str(out)], capture_output=True, text=True, timeout=30)
    ok = proc.returncode == 0 and out.exists() and out.stat().st_size > 0
    row = {"ok": ok, "file": str(out), "size": out.stat().st_size if out.exists() else 0, "stderr": proc.stderr[-1000:]}
    log({"type": "screenshot", "result": row})
    return row

def speak(text):
    if not tool("say"):
        return {"ok": False, "error": "say missing"}
    proc = subprocess.run(["say", str(text)[:900]], capture_output=True, text=True, timeout=90)
    return {"ok": proc.returncode == 0, "stderr": proc.stderr[-1000:]}

def esc_applescript_text(text):
    return str(text).replace("\\", "\\\\").replace('"', '\\"')

def type_text(text):
    script = f'tell application "System Events" to keystroke "{esc_applescript_text(text)}"'
    result = osascript(script)
    log({"type": "type_text", "text": text, "result": result})
    return result

KEY_CODES = {
    "enter": 36,
    "return": 36,
    "escape": 53,
    "esc": 53,
    "tab": 48,
    "space": 49,
    "delete": 51,
    "backspace": 51,
    "up": 126,
    "down": 125,
    "left": 123,
    "right": 124,
}

def press_key(key):
    key = str(key).lower().strip()
    if key in {"command space", "cmd space"}:
        script = 'tell application "System Events" to key code 49 using command down'
    elif key in {"command c", "cmd c"}:
        script = 'tell application "System Events" to keystroke "c" using command down'
    elif key in {"command v", "cmd v"}:
        script = 'tell application "System Events" to keystroke "v" using command down'
    elif key in {"command tab", "cmd tab"}:
        script = 'tell application "System Events" to key code 48 using command down'
    elif key in KEY_CODES:
        script = f'tell application "System Events" to key code {KEY_CODES[key]}'
    elif len(key) == 1:
        script = f'tell application "System Events" to keystroke "{esc_applescript_text(key)}"'
    else:
        return {"ok": False, "error": f"unknown key: {key}"}
    result = osascript(script)
    log({"type": "press_key", "key": key, "result": result})
    return result

def click_xy(x, y):
    if tool("cliclick"):
        result = run(["cliclick", f"c:{int(x)},{int(y)}"], timeout=10)
        log({"type": "click", "x": x, "y": y, "result": result})
        return result
    return {"ok": False, "error": "cliclick not installed. Install with: brew install cliclick"}

def set_mode(mode):
    mode = str(mode).lower().strip()
    if mode not in {"observe", "assist", "trusted"}:
        return {"ok": False, "error": "mode must be observe, assist, or trusted"}
    return {"ok": True, "settings": save_settings(mode=mode)}

def allow_shell(on):
    return {"ok": True, "settings": save_settings(allow_shell=bool(on))}

def run_shell(command):
    settings = load_settings()
    command = str(command).strip()
    if not command:
        return {"ok": False, "error": "empty command"}
    if not settings.get("allow_shell", False):
        return {"ok": False, "blocked": True, "error": "shell disabled. Run: allow shell on"}
    parts = shlex.split(command)
    proc = subprocess.run(parts, capture_output=True, text=True, timeout=int(settings.get("shell_timeout_seconds", 45)))
    row = {"ok": proc.returncode == 0, "returncode": proc.returncode, "stdout": proc.stdout[-6000:], "stderr": proc.stderr[-6000:], "command": command}
    log({"type": "shell", "command": command, "result": row})
    return row

def show_status():
    print("\n=== SEED v88 MAC BODY STATUS ===")
    print(json.dumps(body_status(), indent=4, ensure_ascii=False))

def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else "status"
    if arg == "status":
        show_status()
    elif arg == "permissions":
        print(open_permissions(sys.argv[2] if len(sys.argv) > 2 else "all"))
    elif arg == "open-app":
        print(open_app(" ".join(sys.argv[2:])))
    elif arg == "open-url":
        print(open_url(" ".join(sys.argv[2:])))
    elif arg == "screenshot":
        print(screenshot())
    elif arg == "speak":
        print(speak(" ".join(sys.argv[2:])))
    elif arg == "type":
        print(type_text(" ".join(sys.argv[2:])))
    elif arg == "press":
        print(press_key(" ".join(sys.argv[2:])))
    elif arg == "click":
        print(click_xy(sys.argv[2], sys.argv[3]))
    elif arg == "mode":
        print(set_mode(sys.argv[2]))
    elif arg == "allow-shell":
        print(allow_shell(sys.argv[2].lower() in {"on", "true", "yes", "1"}))
    elif arg == "shell":
        print(run_shell(" ".join(sys.argv[2:])))
    else:
        print("Commands: status | permissions [all/accessibility/screen/microphone/automation] | open-app <app> | open-url <url> | screenshot | speak <text> | type <text> | press <key> | click x y | mode observe/assist/trusted | allow-shell on/off | shell <cmd>")

if __name__ == "__main__":
    main()
