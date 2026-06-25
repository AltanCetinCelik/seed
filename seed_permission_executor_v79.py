import json
import shlex
import subprocess
from datetime import datetime
from pathlib import Path

ACTIONS_FILE = Path("seed_permission_actions_v79.json")
HISTORY_FILE = Path("seed_permission_history_v79.jsonl")

SAFE_PREFIXES = [
    ["git", "status"],
    ["pwd"],
    ["ls"],
    ["python", "seed_v81_gate.py"],
    ["python", "seed_v75_gate.py"],
    ["python", "seed_v74_gate.py"],
    ["python", "seed_v731_gate.py"],
]

def now():
    return datetime.now().isoformat(timespec="seconds")

def load_actions():
    if ACTIONS_FILE.exists():
        try:
            return json.loads(ACTIONS_FILE.read_text(errors="ignore"))
        except Exception:
            pass
    return {"created_at": now(), "version": "v79.0.0", "actions": []}

def save_actions(data):
    data["updated_at"] = now()
    ACTIONS_FILE.write_text(json.dumps(data, indent=4, ensure_ascii=False))
    return data

def action_id(n):
    return f"action_{n:04d}"

def is_safe_command(command):
    try:
        parts = shlex.split(command)
    except Exception:
        return False, "cannot parse command"
    for prefix in SAFE_PREFIXES:
        if parts[:len(prefix)] == prefix:
            return True, "safe whitelisted command"
    return False, "not in safe whitelist; needs future higher-level approval system"

def propose_action(command, reason="", level="safe"):
    data = load_actions()
    ok, why = is_safe_command(command)
    item = {
        "id": action_id(len(data.get("actions", [])) + 1),
        "created_at": now(),
        "version": "v79.0.0",
        "command": command,
        "reason": reason,
        "level": "safe" if ok else "needs_manual_review",
        "safety": why,
        "status": "proposed",
    }
    data.setdefault("actions", []).append(item)
    save_actions(data)
    return {"ok": True, "action": item}

def approve_and_run(action_id_value):
    data = load_actions()
    target = None
    for item in data.get("actions", []):
        if item.get("id") == action_id_value:
            target = item
            break
    if not target:
        return {"ok": False, "error": "action not found"}

    ok, why = is_safe_command(target.get("command", ""))
    if not ok:
        target["status"] = "blocked"
        target["blocked_reason"] = why
        save_actions(data)
        return {"ok": False, "error": why, "action": target}

    target["status"] = "approved_running"
    target["approved_at"] = now()
    save_actions(data)

    parts = shlex.split(target["command"])
    proc = subprocess.run(parts, capture_output=True, text=True, timeout=60)
    result = {
        "created_at": now(),
        "version": "v79.0.0",
        "action_id": target["id"],
        "command": target["command"],
        "returncode": proc.returncode,
        "stdout": proc.stdout[-5000:],
        "stderr": proc.stderr[-5000:],
    }

    with HISTORY_FILE.open("a") as f:
        f.write(json.dumps(result, ensure_ascii=False) + "\n")

    target["status"] = "done" if proc.returncode == 0 else "failed"
    target["last_result"] = result
    save_actions(data)
    return {"ok": proc.returncode == 0, "action": target, "result": result}

def executor_summary():
    data = load_actions()
    return {"created_at": now(), "version": "v79.0.0", "ok": True, "actions": len(data.get("actions", [])), "safe_prefixes": SAFE_PREFIXES}

def show_executor():
    print("\n=== SEED v79 PERMISSION EXECUTOR ===")
    data = load_actions()
    print(f"Actions: {len(data.get('actions', []))}")
    for item in data.get("actions", [])[-20:]:
        print(f"- {item['id']} [{item.get('status')}/{item.get('level')}] {item.get('command')}")
        print(f"  why: {item.get('reason','')}")
    print("\nExamples:")
    print("propose action git status")
    print("approve action action_0001")

if __name__ == "__main__":
    show_executor()
