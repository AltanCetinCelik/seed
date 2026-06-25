import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def _load_tasks():
    try:
        from seed_task_os import load_task_os
        data = load_task_os()
        if isinstance(data, dict):
            return data
    except Exception:
        pass

    path = Path("seed_task_os.json")
    if path.exists():
        try:
            return json.loads(path.read_text(errors="ignore"))
        except Exception:
            pass

    return {"tasks": []}


def _save_tasks(data):
    try:
        from seed_task_os import save_task_os
        return save_task_os(data)
    except Exception:
        pass

    Path("seed_task_os.json").write_text(json.dumps(data, indent=4))
    return data


def classify_task(task):
    title = str(task.get("title", "")).lower()
    notes = str(task.get("notes", "")).lower()
    goal_id = str(task.get("goal_id", "")).lower()

    junk_markers = [
        "gate test",
        "v20 release",
        "v20 self-improvement pipeline",
        "seed v20 release",
        "improve seed voice and aider patch flow safely",
        "create rollback checkpoint before goal work",
        "run runtime health workflow",
        "run gate matrix baseline",
        "run release orchestrator after goal work",
    ]

    if any(marker in title or marker in notes or marker in goal_id for marker in junk_markers):
        return "test_or_gate"

    if task.get("status") in {"done", "failed"}:
        return "closed"

    if task.get("kind") == "operator_action":
        return "operator"

    return "real"


def task_stats():
    data = _load_tasks()
    tasks = data.get("tasks", [])
    counts = defaultdict(int)

    for task in tasks:
        counts[task.get("status", "unknown")] += 1
        counts[f"class:{classify_task(task)}"] += 1

    return {
        "created_at": now_timestamp(),
        "version": "v45.0.0",
        "ok": True,
        "total": len(tasks),
        "counts": dict(counts),
        "ready_real": len([t for t in tasks if t.get("status") == "ready" and classify_task(t) == "real"]),
        "ready_test_or_gate": len([t for t in tasks if t.get("status") == "ready" and classify_task(t) == "test_or_gate"]),
    }


def archive_test_tasks():
    data = _load_tasks()
    changed = 0

    for task in data.get("tasks", []):
        if task.get("status") == "ready" and classify_task(task) == "test_or_gate":
            task["status"] = "archived"
            task.setdefault("events", []).append({
                "created_at": now_timestamp(),
                "event": "archived_by_task_hygiene"
            })
            changed += 1

    _save_tasks(data)

    return {
        "created_at": now_timestamp(),
        "version": "v45.0.0",
        "ok": True,
        "archived": changed,
        "stats": task_stats()
    }


def dedupe_tasks():
    data = _load_tasks()
    seen = set()
    kept = []
    removed = 0

    for task in data.get("tasks", []):
        key = (
            task.get("title"),
            task.get("kind"),
            task.get("goal_id"),
            task.get("action_id"),
            task.get("status"),
        )

        if key in seen and task.get("status") in {"queued", "ready"}:
            removed += 1
            continue

        seen.add(key)
        kept.append(task)

    data["tasks"] = kept
    _save_tasks(data)

    return {
        "created_at": now_timestamp(),
        "version": "v45.0.0",
        "ok": True,
        "removed_duplicates": removed,
        "stats": task_stats()
    }


def reset_demo_tasks():
    archive = archive_test_tasks()
    dedupe = dedupe_tasks()
    return {
        "created_at": now_timestamp(),
        "version": "v45.0.0",
        "ok": True,
        "archive": archive,
        "dedupe": dedupe,
        "stats": task_stats()
    }


def show_task_stats():
    print("\n=== SEED TASK HYGIENE ===")
    print(json.dumps(task_stats(), indent=4))


def show_task_clean_test():
    print("\n=== SEED TASK CLEAN TEST/GATE TASKS ===")
    print(json.dumps(archive_test_tasks(), indent=4))


def show_task_dedupe():
    print("\n=== SEED TASK DEDUPE ===")
    print(json.dumps(dedupe_tasks(), indent=4))


def show_task_reset_demo():
    print("\n=== SEED TASK RESET DEMO ===")
    print(json.dumps(reset_demo_tasks(), indent=4))


if __name__ == "__main__":
    show_task_stats()
