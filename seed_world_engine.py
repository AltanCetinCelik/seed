import json
from datetime import datetime


try:
    from seed_config import WORLD_EVENT_LIMIT
except Exception:
    WORLD_EVENT_LIMIT = 30


from seed_companion_os import (
    load_companion_os_state,
    save_companion_os_state,
    append_companion_os_event,
    append_companion_os_journal,
    add_companion_os_timeline_event,
    add_memory_garden_artifact,
    calculate_companion_os_v2_score
)


try:
    from seed_trace_engine import record_world_trace
    TRACE_AVAILABLE = True
except Exception:
    TRACE_AVAILABLE = False


WORLD_EVENT_TYPES = [
    "memory",
    "quest",
    "ritual",
    "milestone",
    "release",
    "reflection",
    "voice",
    "safety",
    "self_improvement",
    "document",
    "companion"
]


WORLD_PLACES = [
    "The First Room",
    "Memory Garden Gate",
    "Memory Garden",
    "Workshop",
    "Deep Root Archive",
    "Voice Lantern Room",
    "Guardian Tower",
    "Release Forge",
    "Mirror Lake"
]


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def get_world():
    state = load_companion_os_state()
    return state.setdefault("world", {})


def save_world(world):
    state = load_companion_os_state()
    state["world"] = world
    save_companion_os_state(state)


def update_world_season_from_growth(world):
    garden = world.get("memory_garden", {})
    growth_score = (
        garden.get("seeds", 0)
        + garden.get("trees", 0) * 4
        + garden.get("stones", 0) * 2
        + garden.get("lights", 0) * 2
        + len(garden.get("artifacts", [])) * 2
    )

    if growth_score >= 120:
        world["season"] = "Evergreen"
        unlock_place_in_world(world, "Deep Root Archive")
        unlock_place_in_world(world, "Mirror Lake")
    elif growth_score >= 80:
        world["season"] = "Rooted"
        unlock_place_in_world(world, "Guardian Tower")
        unlock_place_in_world(world, "Release Forge")
    elif growth_score >= 45:
        world["season"] = "Familiar"
        unlock_place_in_world(world, "Workshop")
    elif growth_score >= 20:
        world["season"] = "Sprout+"
        unlock_place_in_world(world, "Memory Garden")
    else:
        world["season"] = "Sprout"

    return world["season"]


def unlock_place_in_world(world, place):
    world.setdefault("unlocked_places", [])

    if place not in world["unlocked_places"]:
        world["unlocked_places"].append(place)
        return True

    return False


def apply_world_event(event_type, title=None, note="", importance=3):
    if event_type not in WORLD_EVENT_TYPES:
        event_type = "memory"

    state = load_companion_os_state()
    world = state.setdefault("world", {})
    garden = world.setdefault("memory_garden", {
        "seeds": 0,
        "trees": 0,
        "stones": 0,
        "lights": 0,
        "artifacts": []
    })

    if title is None or title.strip() == "":
        title = f"World event: {event_type}"

    if event_type == "quest":
        garden["lights"] = garden.get("lights", 0) + 1
        world["weather"] = "gold sparks"
        world["mood_symbol"] = "quest light"
    elif event_type == "ritual":
        garden["lights"] = garden.get("lights", 0) + 1
        world["weather"] = "soft amber"
        world["mood_symbol"] = "ritual lantern"
    elif event_type == "milestone":
        garden["stones"] = garden.get("stones", 0) + 1
        world["weather"] = "quiet stars"
        world["mood_symbol"] = "stone marker"
    elif event_type == "release":
        garden["trees"] = garden.get("trees", 0) + 1
        world["weather"] = "sunrise"
        world["mood_symbol"] = "release forge"
        unlock_place_in_world(world, "Release Forge")
    elif event_type == "reflection":
        garden["stones"] = garden.get("stones", 0) + 1
        world["weather"] = "soft rain"
        world["mood_symbol"] = "mirror water"
        unlock_place_in_world(world, "Mirror Lake")
    elif event_type == "voice":
        garden["lights"] = garden.get("lights", 0) + 1
        world["weather"] = "warm signal"
        world["mood_symbol"] = "voice lantern"
        unlock_place_in_world(world, "Voice Lantern Room")
    elif event_type == "safety":
        garden["stones"] = garden.get("stones", 0) + 1
        world["weather"] = "clear night"
        world["mood_symbol"] = "guardian lantern"
        unlock_place_in_world(world, "Guardian Tower")
    elif event_type == "self_improvement":
        garden["trees"] = garden.get("trees", 0) + 1
        world["weather"] = "sparks in the workshop"
        world["mood_symbol"] = "builder flame"
        unlock_place_in_world(world, "Workshop")
    elif event_type == "document":
        garden["seeds"] = garden.get("seeds", 0) + 1
        world["weather"] = "paper wind"
        world["mood_symbol"] = "archive page"
        unlock_place_in_world(world, "Deep Root Archive")
    elif event_type == "companion":
        garden["lights"] = garden.get("lights", 0) + 1
        world["weather"] = "steady glow"
        world["mood_symbol"] = "companion ember"
    else:
        garden["seeds"] = garden.get("seeds", 0) + 1
        world["weather"] = "amber night"
        world["mood_symbol"] = "focused glow"

    world.setdefault("event_history", [])
    event = {
        "created_at": now_timestamp(),
        "event_type": event_type,
        "title": title,
        "note": note,
        "importance": int(importance),
        "world_after": {
            "season": world.get("season"),
            "weather": world.get("weather"),
            "mood_symbol": world.get("mood_symbol")
        }
    }

    world["event_history"].append(event)

    update_world_season_from_growth(world)
    save_companion_os_state(state)

    append_companion_os_event(
        "world_event_applied",
        title,
        {
            "event_type": event_type,
            "note": note,
            "season": world.get("season"),
            "weather": world.get("weather"),
            "mood_symbol": world.get("mood_symbol")
        },
        source="world_engine",
        importance=importance
    )

    add_companion_os_timeline_event(
        title=title,
        event_type=f"world_{event_type}",
        note=note,
        importance=importance
    )

    if TRACE_AVAILABLE:
        try:
            record_world_trace(
                title=title,
                summary=f"Applied world event {event_type}: {note}",
                world_event_type=event_type
            )
        except Exception:
            pass

    return event


def apply_world_event_interactive():
    print("\n=== APPLY SEED WORLD EVENT ===")
    print("Types:", ", ".join(WORLD_EVENT_TYPES))

    event_type = input("Event type: ").strip()
    title = input("Title: ").strip()
    note = input("Note: ").strip()
    importance = input("Importance 1-5: ").strip()

    try:
        importance_value = int(importance)
    except ValueError:
        importance_value = 3

    event = apply_world_event(
        event_type=event_type,
        title=title or None,
        note=note,
        importance=importance_value
    )

    print(f"World event applied: {event.get('title')}")


def add_world_artifact(name, meaning, artifact_type="artifact", source="world_engine"):
    artifact = add_memory_garden_artifact(
        name=name,
        meaning=meaning,
        artifact_type=artifact_type
    )

    append_companion_os_event(
        "world_artifact_added",
        f"World artifact added: {name}",
        {
            "meaning": meaning,
            "artifact_type": artifact_type,
            "source": source
        },
        source="world_engine",
        importance=4
    )

    if TRACE_AVAILABLE:
        try:
            record_world_trace(
                title=f"World artifact added: {name}",
                summary=meaning,
                world_event_type="artifact"
            )
        except Exception:
            pass

    return artifact


def add_world_artifact_interactive():
    print("\n=== ADD MEMORY GARDEN ARTIFACT ===")

    name = input("Artifact name: ").strip()
    meaning = input("Meaning: ").strip()
    artifact_type = input("Type: ").strip() or "artifact"

    if not name:
        print("Artifact name required.")
        return

    add_world_artifact(
        name=name,
        meaning=meaning,
        artifact_type=artifact_type
    )

    print("Artifact added.")


def show_world():
    state = load_companion_os_state()
    world = state.get("world", {})
    garden = world.get("memory_garden", {})
    score = calculate_companion_os_v2_score(save=False)

    print("\n=== SEED WORLD ===")
    print(f"Name: {world.get('name')}")
    print(f"Current place: {world.get('current_place')}")
    print(f"Season: {world.get('season')}")
    print(f"Weather: {world.get('weather')}")
    print(f"Mood symbol: {world.get('mood_symbol')}")
    print(f"V2 World score: {score.get('scores', {}).get('World')} / 10")

    print("\nUnlocked places:")
    for place in world.get("unlocked_places", []):
        print(f"- {place}")

    print("\nMemory Garden:")
    print(f"Seeds: {garden.get('seeds', 0)}")
    print(f"Trees: {garden.get('trees', 0)}")
    print(f"Stones: {garden.get('stones', 0)}")
    print(f"Lights: {garden.get('lights', 0)}")
    print(f"Artifacts: {len(garden.get('artifacts', []))}")


def show_memory_garden():
    state = load_companion_os_state()
    garden = state.get("world", {}).get("memory_garden", {})

    print("\n=== MEMORY GARDEN ===")
    print(f"Seeds: {garden.get('seeds', 0)}")
    print(f"Trees: {garden.get('trees', 0)}")
    print(f"Stones: {garden.get('stones', 0)}")
    print(f"Lights: {garden.get('lights', 0)}")

    print("\nArtifacts:")
    artifacts = garden.get("artifacts", [])

    if not artifacts:
        print("- none")
    else:
        for artifact in artifacts:
            print(f"\n{artifact.get('name')}")
            print(f"Type: {artifact.get('type')}")
            print(f"Created: {artifact.get('created_at')}")
            print(f"Meaning: {artifact.get('meaning')}")


def show_world_events(limit=WORLD_EVENT_LIMIT):
    state = load_companion_os_state()
    events = state.get("world", {}).get("event_history", [])[-limit:]

    print("\n=== SEED WORLD EVENTS ===")

    if not events:
        print("No world events yet.")
        return

    for event in events:
        print(f"\n{event.get('created_at')} — {event.get('event_type')}")
        print(f"Title: {event.get('title')}")
        print(f"Importance: {event.get('importance')}")
        print(f"Note: {event.get('note')}")


def set_world_place_interactive():
    state = load_companion_os_state()
    world = state.get("world", {})

    print("\n=== SET CURRENT WORLD PLACE ===")
    print("Unlocked places:")
    for place in world.get("unlocked_places", []):
        print(f"- {place}")

    place = input("Place: ").strip()

    if not place:
        print("Place cannot be empty.")
        return

    if place not in world.get("unlocked_places", []):
        unlock = input("Place is not unlocked. Unlock and move? y/n: ").strip().lower()

        if unlock != "y":
            print("Cancelled.")
            return

        unlock_place_in_world(world, place)

    world["current_place"] = place
    save_companion_os_state(state)

    append_companion_os_event(
        "world_place_changed",
        f"World place changed: {place}",
        {"place": place},
        source="world_engine",
        importance=3
    )

    print(f"Current place set: {place}")


def explain_world_state():
    state = load_companion_os_state()
    world = state.get("world", {})
    garden = world.get("memory_garden", {})

    explanation = f"""
Seed World is a symbolic interface for Seed's growth with Altan.

Current place: {world.get('current_place')}
Season: {world.get('season')}
Weather: {world.get('weather')}
Mood symbol: {world.get('mood_symbol')}

Memory Garden meaning:
- Seeds represent new memories, starts, and small pieces of continuity.
- Trees represent releases, projects, and self-improvement growth.
- Stones represent milestones, reflections, safety, and serious lessons.
- Lights represent quests, rituals, voice, presence, and companion moments.

Current garden:
Seeds: {garden.get('seeds', 0)}
Trees: {garden.get('trees', 0)}
Stones: {garden.get('stones', 0)}
Lights: {garden.get('lights', 0)}
Artifacts: {len(garden.get('artifacts', []))}

This is symbolic state, not emotion or consciousness.
"""
    print(explanation)
    return explanation


def get_world_context_for_prompt(user_prompt=""):
    state = load_companion_os_state()
    world = state.get("world", {})
    garden = world.get("memory_garden", {})
    recent_events = world.get("event_history", [])[-8:]

    text = "=== SEED WORLD CONTEXT ===\n"
    text += f"Name: {world.get('name')}\n"
    text += f"Place: {world.get('current_place')}\n"
    text += f"Season: {world.get('season')}\n"
    text += f"Weather: {world.get('weather')}\n"
    text += f"Symbol: {world.get('mood_symbol')}\n"
    text += f"Garden: seeds={garden.get('seeds', 0)}, trees={garden.get('trees', 0)}, stones={garden.get('stones', 0)}, lights={garden.get('lights', 0)}, artifacts={len(garden.get('artifacts', []))}\n"

    text += "\nRecent world events:\n"
    if not recent_events:
        text += "No world events yet.\n"
    else:
        for event in recent_events:
            text += f"- {event.get('event_type')}: {event.get('title')}\n"

    text += """
World rule:
Seed World and Memory Garden are symbolic continuity surfaces.
They do not mean Seed is conscious or has emotions.
Use them to represent shared history, growth, quests, rituals, releases, and memory.
"""

    return text


if __name__ == "__main__":
    show_world()
    show_memory_garden()
