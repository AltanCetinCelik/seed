import json
from datetime import datetime
from pathlib import Path


try:
    from seed_config import SEED_EVENT_BUS_FILE
except Exception:
    SEED_EVENT_BUS_FILE = "seed_event_bus.jsonl"


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def emit_event(event_type, payload=None, source="seed", risk="read_only"):
    item = {
        "created_at": now_timestamp(),
        "version": "v4.0.0",
        "source": source,
        "type": event_type,
        "risk": risk,
        "payload": payload or {}
    }

    with open(SEED_EVENT_BUS_FILE, "a") as file:
        file.write(json.dumps(item) + "\n")

    return item


def read_events(limit=50, event_type=None):
    path = Path(SEED_EVENT_BUS_FILE)
    if not path.exists():
        return []

    items = []
    with open(path, "r") as file:
        for line in file:
            try:
                item = json.loads(line)
                if event_type and item.get("type") != event_type:
                    continue
                items.append(item)
            except Exception:
                pass

    return items[-limit:]


def event_bus_status():
    events = read_events(limit=100)
    counts = {}

    for item in events:
        counts[item.get("type", "unknown")] = counts.get(item.get("type", "unknown"), 0) + 1

    return {
        "ok": True,
        "version": "v4.0.0",
        "event_count_sample": len(events),
        "recent_counts": counts,
        "recent": events[-10:]
    }


def show_event_bus():
    print("\n=== SEED EVENT BUS ===")
    print(json.dumps(event_bus_status(), indent=4))


if __name__ == "__main__":
    show_event_bus()

# v4.0 compatibility aliases for older Seed command imports.
def show_events():
    return show_event_bus()


def add_manual_event():
    event_type = input("Event type: ").strip() or "manual_event"
    payload_text = input("Payload/note: ").strip()

    event = emit_event(
        event_type,
        payload={"note": payload_text},
        source="manual",
        risk="read_only"
    )

    print("\n=== MANUAL EVENT ADDED ===")
    print(json.dumps(event, indent=4))
    return event
