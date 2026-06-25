import json
import subprocess
from datetime import datetime
from pathlib import Path

REGISTRY = Path("seed_tool_registry_v97.json")
LOG = Path("seed_tool_calls_v97.jsonl")

DEFAULT_TOOLS = {
    "git.status": {"risk": "observe", "description": "Read-only git status."},
    "shell.pwd": {"risk": "observe", "description": "Read-only current working directory."},
    "mac.screenshot": {"risk": "safe", "description": "Temporary screenshot through Mac Body."},
    "mac.open_url": {"risk": "safe", "description": "Open URL."},
    "mac.open_app": {"risk": "safe", "description": "Open macOS app."},
}

def now():
    return datetime.now().isoformat(timespec="seconds")

def registry():
    if REGISTRY.exists():
        try:
            d = DEFAULT_TOOLS.copy()
            d.update(json.loads(REGISTRY.read_text(errors="ignore")))
            return d
        except Exception:
            pass
    REGISTRY.write_text(json.dumps(DEFAULT_TOOLS, indent=4, ensure_ascii=False))
    return DEFAULT_TOOLS.copy()

def log(row):
    row.setdefault("created_at", now())
    row.setdefault("version", "v97.1.0")
    with LOG.open("a") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")

def call(tool, arg="", approved=False):
    reg = registry()
    if tool not in reg:
        result = {"ok": False, "error": "unknown_tool", "tool": tool}
        log(result)
        return result

    try:
        from seed_safety_ledger_v94 import decision
        dec = decision("tool " + tool, target=arg, approved=approved)
        if not dec.get("allowed"):
            result = {"ok": False, "blocked": True, "decision": dec}
            log({"tool": tool, "arg": arg, "result": result})
            return result
    except Exception as e:
        dec = {"error": str(e)}

    try:
        if tool == "git.status":
            p = subprocess.run(["git", "status", "--short"], capture_output=True, text=True, timeout=20)
            result = {"ok": p.returncode == 0, "stdout": p.stdout, "stderr": p.stderr}
        elif tool == "shell.pwd":
            p = subprocess.run(["pwd"], capture_output=True, text=True, timeout=5)
            result = {"ok": p.returncode == 0, "stdout": p.stdout.strip(), "stderr": p.stderr}
        elif tool.startswith("mac."):
            import seed_mac_body_v88 as body
            if tool == "mac.screenshot":
                result = body.screenshot()
            elif tool == "mac.open_url":
                result = body.open_url(arg)
            elif tool == "mac.open_app":
                result = body.open_app(arg)
            else:
                result = {"ok": False, "error": "no_runner"}
        else:
            result = {"ok": False, "error": "registered_but_no_runner"}
    except Exception as e:
        result = {"ok": False, "error": str(e)}

    log({"tool": tool, "arg": arg, "decision": dec, "result": result})
    return result

def status():
    return {"created_at": now(), "version": "v97.1.0", "ok": True, "tools": registry()}

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 2 and sys.argv[1] == "call":
        print(json.dumps(call(sys.argv[2], " ".join(x for x in sys.argv[3:] if x != "--yes"), "--yes" in sys.argv), indent=4, ensure_ascii=False))
    else:
        print(json.dumps(status(), indent=4, ensure_ascii=False))
