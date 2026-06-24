import json
from datetime import datetime
from pathlib import Path


try:
    from seed_config import SEED_SESSION_TIMELINE_FILE
except Exception:
    SEED_SESSION_TIMELINE_FILE = "seed_session_timeline.json"


SOURCE_PATTERNS = [
    "*history*.jsonl",
    "*trace*.jsonl",
    "seed_transcript_journal.jsonl"
]


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def read_jsonl(path, limit=200):
    items = []
    try:
        with open(path, "r") as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                try:
                    item = json.loads(line)
                except Exception:
                    item = {"raw": line[:500]}
                item["_source_file"] = str(path)
                items.append(item)
    except Exception:
        pass

    return items[-limit:]


def build_session_timeline(limit=120):
    all_items = []

    for pattern in SOURCE_PATTERNS:
        for path in Path(".").glob(pattern):
            if not path.is_file():
                continue
            all_items.extend(read_jsonl(path, limit=limit))

    def sort_key(item):
        return item.get("created_at") or item.get("timestamp") or ""

    all_items = sorted(all_items, key=sort_key)
    all_items = all_items[-limit:]

    timeline = {
        "created_at": now_timestamp(),
        "version": "v3.0.0",
        "ok": True,
        "count": len(all_items),
        "items": all_items
    }

    with open(SEED_SESSION_TIMELINE_FILE, "w") as file:
        json.dump(timeline, file, indent=4)

    return timeline


def timeline_context(user_prompt=""):
    timeline = build_session_timeline(limit=30)
    return (
        "=== SEED SESSION TIMELINE ===\n"
        f"Recent timeline items: {timeline['count']}\n"
        "Use /timeline to inspect recent Seed events.\n"
    )


def show_timeline():
    timeline = build_session_timeline(limit=40)

    print("\n=== SEED SESSION TIMELINE ===")
    print(f"Items: {timeline['count']}")

    for item in timeline["items"][-20:]:
        created = item.get("created_at") or item.get("timestamp") or "unknown-time"
        source = item.get("_source_file", "unknown-source")
        event = item.get("event") or item.get("type") or item.get("command") or item.get("risk") or "event"
        print(f"- {created} [{source}] {event}")


if __name__ == "__main__":
    show_timeline()
