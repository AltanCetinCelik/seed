import json
from datetime import datetime
from pathlib import Path


WORLD_FILE = Path("seed_world_ui_v44.json")


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def build_world_ui():
    try:
        from seed_task_hygiene_v302 import task_stats
        tasks = task_stats()
    except Exception:
        tasks = {}

    try:
        from seed_agent_hq_v30 import build_agent_hq_fast
        hq = build_agent_hq_fast()
    except Exception:
        hq = {}

    world = {
        "created_at": now_timestamp(),
        "version": "v45.0.0",
        "ok": True,
        "rooms": [
            {"id": "control_tower", "name": "Control Tower", "unlocked": True, "source": "Control Plane"},
            {"id": "builder_workshop", "name": "Builder Workshop", "unlocked": True, "source": "Aider + Agent HQ"},
            {"id": "memory_garden", "name": "Memory Garden", "unlocked": True, "source": "Memory Brain"},
            {"id": "voice_studio", "name": "Voice Studio", "unlocked": True, "source": "Voice Runtime"},
            {"id": "browser_observatory", "name": "Browser Observatory", "unlocked": True, "source": "Browser Sandbox"},
            {"id": "agent_hq", "name": "Agent HQ", "unlocked": True, "source": "v30"},
        ],
        "avatar": {
            "presence_state": "focused",
            "animation": "idle",
            "can_speak_if_enabled": True,
            "secret_listening": False
        },
        "metrics": {
            "tasks": tasks,
            "agents": hq.get("agent_count")
        }
    }

    WORLD_FILE.write_text(json.dumps(world, indent=4))
    return world


def show_world_ui():
    print("\n=== SEED WORLD UI v44 ===")
    print(json.dumps(build_world_ui(), indent=4))


if __name__ == "__main__":
    show_world_ui()
