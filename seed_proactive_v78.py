import json
import time
from datetime import datetime
from pathlib import Path

QUEUE_FILE = Path("seed_proactive_queue_v78.jsonl")
LOG_FILE = Path("seed_proactive_log_v78.jsonl")
STATE_FILE = Path("seed_proactive_state_v78.json")

def now():
    return datetime.now().isoformat(timespec="seconds")

def load_policy():
    try:
        from seed_presence_policy_v72 import load_policy as lp
        return lp()
    except Exception:
        return {
            "spam": {"allow_proactive_presence": True, "min_minutes_between_proactive_messages": 45, "max_unprompted_messages_per_day": 6, "store_in_inbox_when_not_speaking": True},
            "curiosity": {"allowed": True},
            "life_advice": {"allowed": True, "require_relevance": True}
        }

def read_jsonl(path, limit=1000):
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(errors="ignore").splitlines()[-limit:]:
        try:
            rows.append(json.loads(line))
        except Exception:
            pass
    return rows

def write_jsonl(path, row):
    with path.open("a") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")

def generate_notices():
    notices = []

    try:
        from seed_memory_review_v75 import memory_summary
        mem = memory_summary()
        if mem.get("pending_count", 0):
            notices.append({
                "category": "memory",
                "urgency": "high",
                "title": "Memory review is waiting",
                "body": f"{mem.get('pending_count')} memory candidates are pending. Saving the right ones improves continuity.",
                "why": "Seed noticed real v75 memory review state.",
            })
    except Exception:
        pass

    try:
        from seed_assimilation_v81 import assimilation_summary
        a = assimilation_summary()
        if a.get("pending_count", 0):
            notices.append({
                "category": "assimilation",
                "urgency": "normal",
                "title": "Advice/repo backlog can be turned into features",
                "body": f"{a.get('pending_count')} assimilation items are pending.",
                "why": "Seed noticed friend advice and repo patterns waiting for accept/reject.",
            })
    except Exception:
        pass

    try:
        from seed_voice_v76 import voice2_status
        v = voice2_status()
        if v.get("ok"):
            notices.append({
                "category": "voice",
                "urgency": "normal",
                "title": "Voice 2.0 is available",
                "body": "Voice settings, journal, retries, and talk mode are ready to test.",
                "why": "Seed noticed v76 voice tools are installed.",
            })
    except Exception:
        pass

    notices.append({
        "category": "v1",
        "urgency": "normal",
        "title": "Real v1 path is narrowing",
        "body": "After v81, the biggest remaining systems are recovery, one-command runtime, backup/privacy, and release candidate hardening.",
        "why": "This is relevant to Altan's current Seed v1 goal.",
    })

    return notices

def enqueue_notices():
    notices = generate_notices()
    for i, n in enumerate(notices, start=1):
        row = {"id": f"notice_{int(time.time())}_{i}", "created_at": now(), "version": "v78.0.0", "status": "queued", **n}
        write_jsonl(QUEUE_FILE, row)
    STATE_FILE.write_text(json.dumps({"created_at": now(), "version": "v78.0.0", "ok": True, "queued": len(notices)}, indent=4))
    return {"ok": True, "queued": len(notices), "items": notices}

def proactive_summary():
    return {"created_at": now(), "version": "v78.0.0", "ok": True, "queue_count": len(read_jsonl(QUEUE_FILE)), "spoken_count": len(read_jsonl(LOG_FILE)), "policy": load_policy()}

def speak_one(force=False):
    policy = load_policy()
    if not force and not policy.get("spam", {}).get("allow_proactive_presence", True):
        return {"ok": False, "error": "proactive disabled by policy"}

    queue = read_jsonl(QUEUE_FILE, 200)
    if not queue:
        enqueue_notices()
        queue = read_jsonl(QUEUE_FILE, 200)

    item = None
    for q in queue:
        if q.get("status") == "queued":
            item = q
            break

    if not item:
        return {"ok": False, "error": "no queued proactive notices"}

    text = f"{item.get('title')}. {item.get('body')}"
    try:
        from seed_voice_v76 import say_with_settings
        say_with_settings(text)
    except Exception:
        pass

    row = {"created_at": now(), "version": "v78.0.0", "spoken": text, "notice": item}
    write_jsonl(LOG_FILE, row)
    return {"ok": True, "spoken": text, "why": item.get("why"), "item": item}

def show_proactive():
    print("\n=== SEED v78 PROACTIVE PRESENCE ===")
    data = enqueue_notices()
    print(f"Queued: {data['queued']}")
    for n in data["items"]:
        print(f"- [{n['category']}/{n['urgency']}] {n['title']}")
        print(f"  {n['body']}")
        print(f"  why: {n['why']}")

if __name__ == "__main__":
    show_proactive()
