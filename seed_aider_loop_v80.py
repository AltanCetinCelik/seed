import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

TASKS_FILE = Path("seed_aider_tasks_v80.json")

def now():
    return datetime.now().isoformat(timespec="seconds")

def load_tasks():
    if TASKS_FILE.exists():
        try:
            return json.loads(TASKS_FILE.read_text(errors="ignore"))
        except Exception:
            pass
    return {"created_at": now(), "version": "v80.0.0", "tasks": []}

def save_tasks(data):
    data["updated_at"] = now()
    TASKS_FILE.write_text(json.dumps(data, indent=4, ensure_ascii=False))
    return data

def aider_info():
    path = shutil.which("aider")
    version = None
    if path:
        try:
            proc = subprocess.run([path, "--version"], capture_output=True, text=True, timeout=20)
            version = (proc.stdout or proc.stderr or "").strip()
        except Exception as e:
            version = f"error: {e}"
    return {"path": path, "version": version}

def create_coding_task(description):
    data = load_tasks()
    item = {
        "id": f"coding_{len(data.get('tasks', []))+1:04d}",
        "created_at": now(),
        "version": "v80.0.0",
        "description": description,
        "status": "planned",
        "plan": [
            "Clarify the target files.",
            "Create a short implementation plan.",
            "Ask Altan for approval before edits.",
            "Use Aider only after approval.",
            "Review diff and run gates/tests.",
            "Suggest commit only after green."
        ],
        "approval_required": True,
    }
    data.setdefault("tasks", []).append(item)
    save_tasks(data)
    return {"ok": True, "task": item}

def aider_summary():
    data = load_tasks()
    info = aider_info()
    return {"created_at": now(), "version": "v80.0.0", "ok": True, "aider": info, "task_count": len(data.get("tasks", []))}

def show_aider():
    print("\n=== SEED v80 AIDER PRODUCTION LOOP ===")
    data = aider_summary()
    print(json.dumps(data, indent=4, ensure_ascii=False))
    tasks = load_tasks().get("tasks", [])[-10:]
    if tasks:
        print("\nCoding tasks:")
        for t in tasks:
            print(f"- {t['id']} [{t['status']}] {t['description'][:180]}")
    print("\nUse: coding task <what to build>")

if __name__ == "__main__":
    show_aider()
