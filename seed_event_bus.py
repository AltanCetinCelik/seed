import json
import os
from datetime import datetime

from seed_config import SEED_EVENTS_FILE, RUNTIME_RECENT_EVENTS_LIMIT


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def emit_event(event_type, title, details=None, source="seed", importance=3):
    if details is None:
        details = {}

    event = {
        "created_at": now_timestamp(),
        "type": event_type,
        "title": title,
        "details": details,
        "source": source,
        "importance": int(importance)
    }

    with open(SEED_EVENTS_FILE, "a") as file:
        file.write(json.dumps(event) + "\n")

    return event


def load_events(limit=None):
    if not os.path.exists(SEED_EVENTS_FILE):
        return []

    events = []

    with open(SEED_EVENTS_FILE, "r") as file:
        for line in file:
            line = line.strip()

            if line == "":
                continue

            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    if limit is not None:
        return events[-limit:]

    return events


def format_events(limit=RUNTIME_RECENT_EVENTS_LIMIT):
    events = load_events(limit)

    text = "=== SEED EVENT STREAM ===\n"

    if not events:
        text += "No runtime events yet.\n"
        return text

    for index, event in enumerate(events, start=1):
        text += f"\n{index}. {event.get('title')}\n"
        text += f"   Type: {event.get('type')}\n"
        text += f"   Source: {event.get('source')}\n"
        text += f"   Importance: {event.get('importance')}\n"
        text += f"   Created: {event.get('created_at')}\n"

    return text


def show_events():
    print("\n" + format_events())


def add_manual_event():
    print("\n=== ADD RUNTIME EVENT ===")

    title = input("Title: ").strip()
    event_type = input("Type: ").strip()
    importance = input("Importance (1-5): ").strip()
    note = input("Note: ").strip()

    if title == "":
        print("Title cannot be empty.")
        return

    try:
        importance_value = int(importance)
    except ValueError:
        importance_value = 3

    event = emit_event(
        event_type=event_type or "manual",
        title=title,
        details={"note": note},
        source="manual",
        importance=importance_value
    )

    print(f"Event added: {event.get('title')}")


def count_events_by_type():
    counts = {}

    for event in load_events():
        event_type = event.get("type", "unknown")

        if event_type not in counts:
            counts[event_type] = 0

        counts[event_type] += 1

    return counts