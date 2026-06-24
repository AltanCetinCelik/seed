import json
from datetime import datetime


try:
    from seed_config import SEED_WORLD_AVATAR_FILE
except Exception:
    SEED_WORLD_AVATAR_FILE = "seed_world_avatar_v16.json"


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def build_world_avatar():
    events = []
    tasks = []

    try:
        from seed_event_bus import read_events
        events = read_events(limit=20)
    except Exception:
        pass

    try:
        from seed_task_os import list_tasks
        tasks = list_tasks(limit=30).get("tasks", [])
    except Exception:
        pass

    world = {
        "created_at": now_timestamp(),
        "version": "v20.0.0",
        "ok": True,
        "engine": "Seed World + Avatar Presence v15/v16",
        "world": {
            "memory_garden": {
                "description": "Major memories, milestones, and projects become symbolic places.",
                "seeds": len(events),
                "quests": len(tasks)
            },
            "rooms": [
                {"id": "core", "name": "Seed Core Room", "purpose": "identity, safety, version history"},
                {"id": "workshop", "name": "Builder Workshop", "purpose": "coding, Aider, MCP, gates"},
                {"id": "garden", "name": "Memory Garden", "purpose": "memories, milestones, reflections"},
                {"id": "dashboard", "name": "Control Tower", "purpose": "operator tasks, event bus, services"}
            ]
        },
        "avatar": {
            "state": "ready",
            "mood_visual": "focused",
            "animation_state": "idle",
            "can_speak": False,
            "can_listen_secretly": False,
            "presence_rules": [
                "No fake consciousness claims",
                "Presence is UI/UX only",
                "Altan remains in control"
            ]
        }
    }

    with open(SEED_WORLD_AVATAR_FILE, "w") as file:
        json.dump(world, file, indent=4)

    return world


def show_world_avatar():
    data = build_world_avatar()
    print("\n=== SEED WORLD + AVATAR ===")
    print("Rooms:")
    for room in data["world"]["rooms"]:
        print(f"- {room['name']}: {room['purpose']}")
    print("Avatar:")
    print(json.dumps(data["avatar"], indent=4))


if __name__ == "__main__":
    show_world_avatar()
