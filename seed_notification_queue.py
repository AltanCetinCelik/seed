import json
import uuid
from datetime import datetime
from pathlib import Path


QUEUE_FILE = Path("seed_notification_queue.jsonl")


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def enqueue_notification(message, reason="presence", priority=0.5, source="seed_presence"):
    # Avoid repeating the same pending message again and again.
    for existing in read_notifications(limit=100, status="pending"):
        if (
            existing.get("message") == str(message).strip()
            and existing.get("reason") == reason
        ):
            return existing

    item = {
        "id": uuid.uuid4().hex[:10],
        "created_at": now_timestamp(),
        "version": "v20.3.0",
        "source": source,
        "reason": reason,
        "priority": float(priority),
        "message": str(message).strip(),
        "status": "pending",
        "delivered_at": None
    }

    if not item["message"]:
        return None

    with open(QUEUE_FILE, "a") as file:
        file.write(json.dumps(item) + "\n")

    try:
        from seed_event_bus import emit_event
        emit_event(
            "notification_queued",
            payload={"notification_id": item["id"], "reason": reason},
            source=source,
            risk="read_only"
        )
    except Exception:
        pass

    return item


def read_notifications(limit=50, status=None):
    if not QUEUE_FILE.exists():
        return []

    items = []
    for line in QUEUE_FILE.read_text(errors="ignore").splitlines():
        try:
            item = json.loads(line)
            if status is None or item.get("status") == status:
                items.append(item)
        except Exception:
            pass

    return items[-limit:]


def write_notifications(items):
    with open(QUEUE_FILE, "w") as file:
        for item in items:
            file.write(json.dumps(item) + "\n")


def mark_delivered(notification_id):
    items = read_notifications(limit=100000)
    changed = None

    for item in items:
        if item.get("id") == notification_id:
            item["status"] = "delivered"
            item["delivered_at"] = now_timestamp()
            changed = item
            break

    write_notifications(items)
    return changed


def pop_next_notification():
    pending = sorted(
        read_notifications(limit=100000, status="pending"),
        key=lambda x: (float(x.get("priority", 0)), x.get("created_at", "")),
        reverse=True
    )

    if not pending:
        return None

    item = pending[0]
    mark_delivered(item["id"])
    return item


def pop_next_notification_for_cli():
    item = pop_next_notification()
    if not item:
        return None

    print("\n=== SEED PRESENCE ===")
    print(item["message"])
    print(f"reason={item.get('reason')} priority={item.get('priority')}")
    return item


def show_notification_inbox():
    items = read_notifications(limit=20)
    print("\n=== SEED NOTIFICATION QUEUE ===")

    if not items:
        print("No notifications.")
        return

    for item in items:
        print(f"- [{item.get('status')}] {item.get('reason')} · {item.get('message')}")


if __name__ == "__main__":
    show_notification_inbox()
