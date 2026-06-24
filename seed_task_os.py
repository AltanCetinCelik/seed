import hashlib
import json
from datetime import datetime
from pathlib import Path


try:
    from seed_config import SEED_TASK_OS_FILE
except Exception:
    SEED_TASK_OS_FILE = "seed_task_os.json"


STATUSES = ["queued", "ready", "running", "blocked", "done", "failed"]


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def load_task_os():
    path = Path(SEED_TASK_OS_FILE)
    if not path.exists():
        return {
            "created_at": now_timestamp(),
            "version": "v5.0.0",
            "ok": True,
            "tasks": []
        }

    try:
        data = json.loads(path.read_text())
        data.setdefault("tasks", [])
        return data
    except Exception:
        return {
            "created_at": now_timestamp(),
            "version": "v5.0.0",
            "ok": True,
            "tasks": []
        }


def save_task_os(data):
    data["updated_at"] = now_timestamp()
    with open(SEED_TASK_OS_FILE, "w") as file:
        json.dump(data, file, indent=4)
    return data


def task_id_from(title):
    raw = title + now_timestamp()
    return hashlib.sha256(raw.encode()).hexdigest()[:10]


def create_task(title, kind="manual", goal_id=None, priority=5, action_id=None, target_files=None, notes=None):
    data = load_task_os()

    task = {
        "id": task_id_from(title),
        "created_at": now_timestamp(),
        "version": "v5.0.0",
        "title": title,
        "kind": kind,
        "goal_id": goal_id,
        "priority": int(priority),
        "status": "ready",
        "action_id": action_id,
        "target_files": target_files or [],
        "notes": notes or "",
        "events": []
    }

    data["tasks"].append(task)
    save_task_os(data)

    try:
        from seed_event_bus import emit_event
        emit_event("task_created", {"task_id": task["id"], "title": title}, source="task_os", risk="file_write")
    except Exception:
        pass

    return task


def update_task_status(task_id, status, note=None):
    if status not in STATUSES:
        return {"ok": False, "error": f"Invalid status: {status}"}

    data = load_task_os()

    for task in data["tasks"]:
        if task["id"] == task_id:
            task["status"] = status
            task["events"].append({
                "created_at": now_timestamp(),
                "status": status,
                "note": note
            })
            save_task_os(data)
            return {"ok": True, "task": task}

    return {"ok": False, "error": "Task not found."}


def list_tasks(status=None, limit=50):
    data = load_task_os()
    tasks = data.get("tasks", [])

    if status:
        tasks = [task for task in tasks if task.get("status") == status]

    tasks = sorted(tasks, key=lambda x: (x.get("status") != "ready", -int(x.get("priority", 0)), x.get("created_at", "")))

    return {
        "ok": True,
        "version": "v5.0.0",
        "count": len(tasks),
        "tasks": tasks[:limit]
    }


def next_ready_task():
    tasks = list_tasks(status="ready", limit=100)["tasks"]
    if not tasks:
        return None
    return sorted(tasks, key=lambda x: (-int(x.get("priority", 0)), x.get("created_at", "")))[0]


def create_goal_task_set(goal_id, goal_text, actions):
    created = []

    for item in actions:
        task = create_task(
            title=item["title"],
            kind=item.get("kind", "operator_action"),
            goal_id=goal_id,
            priority=item.get("priority", 5),
            action_id=item.get("action_id"),
            target_files=item.get("target_files", []),
            notes=item.get("notes", goal_text)
        )
        created.append(task)

    return created


def show_task_list():
    print("\n=== SEED TASK OS ===")
    print(json.dumps(list_tasks(limit=80), indent=4))


def show_task_create():
    title = input("Task title: ").strip()
    kind = input("Kind [manual]: ").strip() or "manual"
    action_id = input("Action id optional: ").strip() or None
    print(json.dumps(create_task(title, kind=kind, action_id=action_id), indent=4))


def show_task_done():
    task_id = input("Task id: ").strip()
    print(json.dumps(update_task_status(task_id, "done", "Marked done manually."), indent=4))


if __name__ == "__main__":
    show_task_list()
