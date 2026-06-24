import json
from datetime import datetime
from pathlib import Path


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def safe(fn, default):
    try:
        return fn()
    except Exception:
        return default


def read_json(path):
    p = Path(path)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(errors="ignore"))
    except Exception:
        return None


def collect_curiosity_context():
    tasks = safe(
        lambda: __import__("seed_task_os", fromlist=["list_tasks"]).list_tasks(limit=100),
        {"tasks": []}
    )

    events = safe(
        lambda: __import__("seed_event_bus", fromlist=["read_events"]).read_events(limit=30),
        []
    )

    v20 = read_json("seed_v20_sovereign_state.json") or {}
    latency = safe(
        lambda: __import__("seed_latency_probe", fromlist=["run_latency_probe"]).run_latency_probe(),
        {}
    )

    task_items = tasks.get("tasks", []) if isinstance(tasks, dict) else []
    ready_tasks = [t for t in task_items if t.get("status") == "ready"]
    failed_events = [
        e for e in events
        if "fail" in str(e).lower() or "error" in str(e).lower() or "crash" in str(e).lower()
    ]

    return {
        "created_at": now_timestamp(),
        "time_hour": datetime.now().hour,
        "tasks_total": len(task_items),
        "ready_tasks": len(ready_tasks),
        "next_task": ready_tasks[0] if ready_tasks else None,
        "recent_events": events[-10:],
        "failed_event_count": len(failed_events),
        "v20_ok": v20.get("ok"),
        "latency_ok": latency.get("ok"),
        "latency": latency.get("results", {}) if isinstance(latency, dict) else {},
    }


def detect_curiosity_triggers(context):
    triggers = []

    hour = context.get("time_hour")

    if 9 <= hour <= 11:
        triggers.append({
            "id": "morning_ritual",
            "category": "ritual",
            "priority": 0.68,
            "message": "Morning check-in: what are we pushing today — Seed, coding, money, or school?"
        })

    if 21 <= hour <= 23:
        triggers.append({
            "id": "night_reflection",
            "category": "ritual",
            "priority": 0.66,
            "message": "Night reflection: did Seed actually help today, or did we just stack features?"
        })

    if context.get("ready_tasks", 0) >= 5:
        task = context.get("next_task") or {}
        triggers.append({
            "id": "unfinished_operator_tasks",
            "category": "continuity",
            "priority": 0.78,
            "message": f"We have {context.get('ready_tasks')} ready operator tasks. Next one is: {task.get('title')}. Want me to tick it?"
        })

    if context.get("failed_event_count", 0) >= 2:
        triggers.append({
            "id": "repeated_runtime_errors",
            "category": "warning",
            "priority": 0.84,
            "message": "I noticed repeated error-like events. We should stop stacking patches and inspect the root cause."
        })

    if context.get("v20_ok") is True:
        triggers.append({
            "id": "v20_continuity",
            "category": "continuity",
            "priority": 0.70,
            "message": "Seed v20 is installed. The next real step is making Presence Runtime useful: should I watch tasks, errors, or daily goals first?"
        })

    if context.get("latency_ok") is True:
        triggers.append({
            "id": "latency_good",
            "category": "companionship",
            "priority": 0.65,
            "message": "Latency looks healthy now. Want me to use the fast path more aggressively so Seed feels snappier?"
        })

    triggers.append({
        "id": "identity_gap",
        "category": "curiosity",
        "priority": 0.67,
        "message": "When you say you want Seed to feel more present, do you mostly mean asking questions, noticing unfinished work, or taking approved actions?"
    })

    return sorted(triggers, key=lambda x: x["priority"], reverse=True)


def show_curiosity():
    context = collect_curiosity_context()
    triggers = detect_curiosity_triggers(context)

    print("\n=== SEED CURIOSITY ENGINE ===")
    print(f"Detected triggers: {len(triggers)}")
    for trigger in triggers[:8]:
        print(f"- {trigger['category']} · {trigger['priority']}: {trigger['message']}")


if __name__ == "__main__":
    show_curiosity()
