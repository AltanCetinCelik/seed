import json
import os
from datetime import datetime

from seed_config import (
    SEED_WORLD_FILE,
    SEED_TIMELINE_FILE,
    SEED_QUESTS_FILE,
    SEED_RITUALS_FILE
)


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def read_json(path, default):
    try:
        with open(path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return default
    except json.JSONDecodeError:
        return default


def write_json(path, data):
    with open(path, "w") as file:
        json.dump(data, file, indent=4)


def default_world_state():
    return {
        "created_at": now_timestamp(),
        "updated_at": now_timestamp(),
        "name": "Seed World",
        "location": "The First Room",
        "mood": "focused",
        "weather": "soft amber rain",
        "energy": 65,
        "growth": 1,
        "trust_phase": "Sprout",
        "memory_garden": {
            "seeds": 0,
            "trees": 0,
            "stones": 0,
            "lights": 0
        },
        "unlocked_places": [
            "The First Room"
        ],
        "current_symbol": "small glowing seed",
        "world_note": "Seed World is a symbolic local companion space. It is not consciousness."
    }


def load_world():
    state = read_json(SEED_WORLD_FILE, None)

    if state is None:
        state = default_world_state()
        save_world(state)

    return state


def save_world(state):
    state["updated_at"] = now_timestamp()
    write_json(SEED_WORLD_FILE, state)


def adjust_world_after_event(event_type):
    state = load_world()
    garden = state.get("memory_garden", {})

    if event_type == "memory_saved":
        garden["seeds"] = garden.get("seeds", 0) + 1
        state["growth"] = state.get("growth", 1) + 1
        state["mood"] = "rooted"

    elif event_type == "quest_completed":
        garden["lights"] = garden.get("lights", 0) + 1
        state["energy"] = min(100, state.get("energy", 50) + 8)
        state["mood"] = "bright"

    elif event_type == "reflection":
        garden["stones"] = garden.get("stones", 0) + 1
        state["mood"] = "quiet"
        state["weather"] = "calm night"

    elif event_type == "project_milestone":
        garden["trees"] = garden.get("trees", 0) + 1
        state["growth"] = state.get("growth", 1) + 3
        state["mood"] = "proud"
        state["weather"] = "gold sunrise"

    state["memory_garden"] = garden

    if state["growth"] >= 10 and "Memory Garden" not in state["unlocked_places"]:
        state["unlocked_places"].append("Memory Garden")
        state["trust_phase"] = "Familiar"

    if state["growth"] >= 25 and "Workshop" not in state["unlocked_places"]:
        state["unlocked_places"].append("Workshop")
        state["trust_phase"] = "Trusted"

    save_world(state)
    return state


def format_world():
    state = load_world()
    garden = state.get("memory_garden", {})

    text = "=== SEED WORLD ===\n"
    text += f"Name: {state.get('name')}\n"
    text += f"Location: {state.get('location')}\n"
    text += f"Mood: {state.get('mood')}\n"
    text += f"Weather: {state.get('weather')}\n"
    text += f"Energy: {state.get('energy')}\n"
    text += f"Growth: {state.get('growth')}\n"
    text += f"Trust phase: {state.get('trust_phase')}\n"
    text += f"Current symbol: {state.get('current_symbol')}\n"

    text += "\nMemory Garden:\n"
    text += f"- Seeds: {garden.get('seeds', 0)}\n"
    text += f"- Trees: {garden.get('trees', 0)}\n"
    text += f"- Stones: {garden.get('stones', 0)}\n"
    text += f"- Lights: {garden.get('lights', 0)}\n"

    text += "\nUnlocked places:\n"
    for place in state.get("unlocked_places", []):
        text += f"- {place}\n"

    text += "\nRule: Seed World is symbolic companion state, not sentience.\n"

    return text


def show_world():
    print("\n" + format_world())


def default_timeline():
    return {
        "created_at": now_timestamp(),
        "updated_at": now_timestamp(),
        "events": []
    }


def load_timeline():
    timeline = read_json(SEED_TIMELINE_FILE, None)

    if timeline is None:
        timeline = default_timeline()
        save_timeline(timeline)

    return timeline


def save_timeline(timeline):
    timeline["updated_at"] = now_timestamp()
    write_json(SEED_TIMELINE_FILE, timeline)


def add_timeline_event(title, event_type="general", note="", importance=3):
    timeline = load_timeline()

    event = {
        "created_at": now_timestamp(),
        "title": title,
        "type": event_type,
        "note": note,
        "importance": int(importance)
    }

    timeline["events"].append(event)
    save_timeline(timeline)

    if event_type in ["project_milestone", "reflection"]:
        adjust_world_after_event(event_type)

    return event


def show_timeline(limit=20):
    timeline = load_timeline()
    events = timeline.get("events", [])

    print("\n=== SEED LIFE TIMELINE ===")

    if not events:
        print("No timeline events yet.")
        return

    for number, event in enumerate(events[-limit:], start=1):
        print(f"\n{number}. {event.get('title')}")
        print(f"   Type: {event.get('type')}")
        print(f"   Importance: {event.get('importance')}")
        print(f"   Created: {event.get('created_at')}")
        print(f"   Note: {event.get('note')}")


def default_quests():
    return {
        "created_at": now_timestamp(),
        "updated_at": now_timestamp(),
        "quests": [
            {
                "id": "Q-001",
                "title": "Build Seed World foundation",
                "type": "project",
                "status": "active",
                "difficulty": 4,
                "reward": "Memory Garden seed",
                "reason": "Seed needs a visual-symbolic world before v2.0.0."
            },
            {
                "id": "Q-002",
                "title": "Run one serious self-review",
                "type": "growth",
                "status": "active",
                "difficulty": 3,
                "reward": "Reflection stone",
                "reason": "Seed should learn to inspect itself honestly."
            }
        ]
    }


def load_quests():
    quests = read_json(SEED_QUESTS_FILE, None)

    if quests is None:
        quests = default_quests()
        save_quests(quests)

    return quests


def save_quests(quests):
    quests["updated_at"] = now_timestamp()
    write_json(SEED_QUESTS_FILE, quests)


def show_quests():
    data = load_quests()

    print("\n=== SEED QUESTS ===")

    for quest in data.get("quests", []):
        print(f"\n{quest.get('id')} — {quest.get('title')}")
        print(f"Type: {quest.get('type')}")
        print(f"Status: {quest.get('status')}")
        print(f"Difficulty: {quest.get('difficulty')}")
        print(f"Reward: {quest.get('reward')}")
        print(f"Reason: {quest.get('reason')}")


def add_quest(title, quest_type="growth", difficulty=3, reward="world growth", reason=""):
    data = load_quests()
    existing_count = len(data.get("quests", []))
    quest_id = f"Q-{existing_count + 1:03d}"

    quest = {
        "id": quest_id,
        "title": title,
        "type": quest_type,
        "status": "active",
        "difficulty": int(difficulty),
        "reward": reward,
        "reason": reason
    }

    data["quests"].append(quest)
    save_quests(data)

    return quest


def complete_quest(quest_id):
    data = load_quests()

    for quest in data.get("quests", []):
        if quest.get("id", "").lower() == quest_id.lower():
            quest["status"] = "done"
            quest["completed_at"] = now_timestamp()
            save_quests(data)
            adjust_world_after_event("quest_completed")
            add_timeline_event(
                title=f"Completed quest: {quest.get('title')}",
                event_type="quest_completed",
                note=quest.get("reason", ""),
                importance=4
            )
            return quest

    return None


def default_rituals():
    return {
        "created_at": now_timestamp(),
        "updated_at": now_timestamp(),
        "rituals": [
            {
                "id": "R-001",
                "title": "Morning boot",
                "type": "morning",
                "status": "available",
                "prompt": "What matters today, what should we protect, and what is one tiny win?"
            },
            {
                "id": "R-002",
                "title": "Night reflection",
                "type": "night",
                "status": "available",
                "prompt": "What did we learn, what should be remembered, and what can rest?"
            },
            {
                "id": "R-003",
                "title": "Overwhelmed reset",
                "type": "grounding",
                "status": "available",
                "prompt": "Name the pressure, choose one next action, and reduce the noise."
            }
        ]
    }


def load_rituals():
    rituals = read_json(SEED_RITUALS_FILE, None)

    if rituals is None:
        rituals = default_rituals()
        save_rituals(rituals)

    return rituals


def save_rituals(rituals):
    rituals["updated_at"] = now_timestamp()
    write_json(SEED_RITUALS_FILE, rituals)


def show_rituals():
    data = load_rituals()

    print("\n=== SEED RITUALS ===")

    for ritual in data.get("rituals", []):
        print(f"\n{ritual.get('id')} — {ritual.get('title')}")
        print(f"Type: {ritual.get('type')}")
        print(f"Status: {ritual.get('status')}")
        print(f"Prompt: {ritual.get('prompt')}")


def get_world_context_for_prompt():
    world = load_world()
    quests = load_quests()
    timeline = load_timeline()

    active_quests = [
        quest for quest in quests.get("quests", [])
        if quest.get("status") == "active"
    ]

    recent_events = timeline.get("events", [])[-5:]

    text = "=== SEED WORLD CONTEXT ===\n"
    text += f"Location: {world.get('location')}\n"
    text += f"Mood: {world.get('mood')}\n"
    text += f"Weather: {world.get('weather')}\n"
    text += f"Energy: {world.get('energy')}\n"
    text += f"Growth: {world.get('growth')}\n"
    text += f"Trust phase: {world.get('trust_phase')}\n"

    text += "\nActive quests:\n"
    if not active_quests:
        text += "No active quests.\n"
    else:
        for quest in active_quests[:5]:
            text += f"- {quest.get('id')}: {quest.get('title')} ({quest.get('type')})\n"

    text += "\nRecent timeline events:\n"
    if not recent_events:
        text += "No recent timeline events.\n"
    else:
        for event in recent_events:
            text += f"- {event.get('title')} [{event.get('type')}]\n"

    text += """
World rule:
Seed World is symbolic persistent companion state.
It may guide tone, rituals, quests, and visual cockpit state.
It is not consciousness or human emotion.
"""

    return text


def get_world_summary():
    world = load_world()
    quests = load_quests()
    timeline = load_timeline()

    active_quests = [
        quest for quest in quests.get("quests", [])
        if quest.get("status") == "active"
    ]

    return {
        "world": world,
        "active_quests": active_quests,
        "timeline_count": len(timeline.get("events", [])),
        "quest_count": len(quests.get("quests", []))
    }