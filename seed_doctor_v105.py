import json
import shutil
import socket
import subprocess
from datetime import datetime
from pathlib import Path

OPTIONAL_CHECKS = {"panel_8797", "avatar_8798"}

def now():
    return datetime.now().isoformat(timespec="seconds")

def port_open(port):
    s = socket.socket()
    s.settimeout(0.25)
    try:
        s.connect(("127.0.0.1", int(port)))
        s.close()
        return True
    except Exception:
        return False

def command_ok(name):
    return {"ok": bool(shutil.which(name)), "path": shutil.which(name), "required": True}

def diagnose():
    checks = {
        "ollama": command_ok("ollama"),
        "osascript": command_ok("osascript"),
        "screencapture": command_ok("screencapture"),
        "say": command_ok("say"),
        "git": command_ok("git"),
        "avatar_8798": {"ok": port_open(8798), "required": False, "note": "Optional. Green only when avatar server is running."},
        "panel_8797": {"ok": port_open(8797), "required": False, "note": "Optional legacy panel. v106 dashboard uses port 8806."},
        "dashboard_8806": {"ok": port_open(8806), "required": False, "note": "Optional. Green only when dashboard is running."},
    }
    required_ok = all(v.get("ok") for v in checks.values() if v.get("required", True))
    optional_down = [k for k, v in checks.items() if not v.get("required", True) and not v.get("ok")]
    return {
        "created_at": now(),
        "version": "v105.1.0",
        "ok": required_ok,
        "required_ok": required_ok,
        "optional_down": optional_down,
        "checks": checks,
    }

def heal():
    actions = []
    if not port_open(8806) and Path("seed_dashboard_v106.py").exists():
        try:
            p = subprocess.run(["python", "seed_dashboard_v106.py", "start"], capture_output=True, text=True, timeout=20)
            actions.append({"start_dashboard": {"ok": p.returncode == 0, "stdout": p.stdout[-1000:], "stderr": p.stderr[-1000:]}})
        except Exception as e:
            actions.append({"start_dashboard": {"ok": False, "error": str(e)}})
    return {"created_at": now(), "version": "v105.1.0", "ok": True, "actions": actions, "after": diagnose()}

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "heal":
        print(json.dumps(heal(), indent=4, ensure_ascii=False))
    else:
        print(json.dumps(diagnose(), indent=4, ensure_ascii=False))
