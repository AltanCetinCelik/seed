import hashlib
import json
from datetime import datetime
from pathlib import Path


try:
    from seed_config import SEED_OPERATOR_INBOX_FILE
except Exception:
    SEED_OPERATOR_INBOX_FILE = "seed_operator_inbox.jsonl"


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def capture_inbox_item(text, source="manual", kind="note"):
    item = {
        "created_at": now_timestamp(),
        "version": "v5.0.0",
        "id": hashlib.sha256((text + now_timestamp()).encode()).hexdigest()[:10],
        "kind": kind,
        "source": source,
        "text": text,
        "converted_to_goal": False
    }

    with open(SEED_OPERATOR_INBOX_FILE, "a") as file:
        file.write(json.dumps(item) + "\n")

    return item


def read_inbox(limit=50):
    path = Path(SEED_OPERATOR_INBOX_FILE)
    if not path.exists():
        return []

    items = []
    with open(path, "r") as file:
        for line in file:
            try:
                items.append(json.loads(line))
            except Exception:
                pass

    return items[-limit:]


def show_inbox():
    print("\n=== SEED OPERATOR INBOX ===")
    print(json.dumps({
        "ok": True,
        "items": read_inbox()
    }, indent=4))


def show_inbox_add():
    text = input("Inbox note/goal: ").strip()
    print(json.dumps(capture_inbox_item(text), indent=4))


if __name__ == "__main__":
    show_inbox()
