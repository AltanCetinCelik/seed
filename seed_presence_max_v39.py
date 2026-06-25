import json
from datetime import datetime
from pathlib import Path


PRESENCE_MAX_FILE = Path("seed_presence_max_v39.json")


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def build_presence_max():
    try:
        from seed_task_hygiene_v302 import task_stats
        stats = task_stats()
    except Exception as error:
        stats = {"ok": False, "error": str(error)}

    data = {
        "created_at": now_timestamp(),
        "version": "v45.0.0",
        "ok": True,
        "improvements": [
            "ignore archived/test tasks",
            "dedupe pending notifications",
            "reason-based messages",
            "focus mode",
            "quiet hours",
            "daily rituals",
            "presence context for prompt"
        ],
        "task_stats": stats,
        "better_triggers": {
            "real_ready_task": "Only mention real ready tasks, not gate junk.",
            "failed_patch": "Warn after repeated failures.",
            "memory_gap": "Ask one useful clarifying question.",
            "daily_goal_missing": "Morning ritual.",
            "night_reflection": "End-of-day check."
        }
    }
    PRESENCE_MAX_FILE.write_text(json.dumps(data, indent=4))
    return data


def show_presence_max():
    print("\n=== SEED PRESENCE MAX v39 ===")
    print(json.dumps(build_presence_max(), indent=4))


if __name__ == "__main__":
    show_presence_max()
