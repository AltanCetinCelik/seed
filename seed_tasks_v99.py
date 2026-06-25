import json
import time
from datetime import datetime
from pathlib import Path

TASKS = Path("seed_tasks_v99.jsonl")
EVENTS = Path("seed_task_events_v99.jsonl")

def now():
    return datetime.now().isoformat(timespec="seconds")

def write(path, row):
    row.setdefault("created_at", now())
    row.setdefault("version", "v99.1.0")
    with path.open("a") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")

def read(path):
    if not path.exists():
        return []
    out = []
    for line in path.read_text(errors="ignore").splitlines():
        try:
            out.append(json.loads(line))
        except Exception:
            pass
    return out

def create(title, description=""):
    tid = f"task_{int(time.time() * 1000)}"
    row = {"task_id": tid, "title": title, "description": description, "status": "open"}
    write(TASKS, row)
    write(EVENTS, {"task_id": tid, "event": "created", "status": "open"})
    return {"ok": True, "task": row}

def latest_tasks():
    tasks = {t.get("task_id"): dict(t) for t in read(TASKS) if t.get("task_id")}
    for e in read(EVENTS):
        tid = e.get("task_id")
        if tid in tasks:
            tasks[tid]["status"] = e.get("status", tasks[tid].get("status"))
            tasks[tid].setdefault("history", []).append(e)
    return list(tasks.values())

def update(task_id, status, note=""):
    write(EVENTS, {"task_id": task_id, "event": "status", "status": status, "note": note})
    return {"ok": True, "task_id": task_id, "status": status, "note": note}

def status():
    tasks = latest_tasks()
    return {
        "created_at": now(),
        "version": "v99.1.0",
        "ok": True,
        "open": [t for t in tasks if t.get("status") == "open"],
        "done": [t for t in tasks if t.get("status") == "done"],
        "tasks": tasks[-40:],
        "events": read(EVENTS)[-40:],
    }

if __name__ == "__main__":
    import sys
    arg = sys.argv[1] if len(sys.argv) > 1 else "status"
    if arg == "create":
        print(json.dumps(create(sys.argv[2], " ".join(sys.argv[3:])), indent=4, ensure_ascii=False))
    elif arg in {"done", "complete"}:
        print(json.dumps(update(sys.argv[2], "done", " ".join(sys.argv[3:])), indent=4, ensure_ascii=False))
    elif arg in {"fail", "failed"}:
        print(json.dumps(update(sys.argv[2], "failed", " ".join(sys.argv[3:])), indent=4, ensure_ascii=False))
    elif arg == "pause":
        print(json.dumps(update(sys.argv[2], "paused", " ".join(sys.argv[3:])), indent=4, ensure_ascii=False))
    else:
        print(json.dumps(status(), indent=4, ensure_ascii=False))
