import json
import glob
from datetime import datetime
from pathlib import Path

DECISIONS_FILE = Path("seed_memory_review_decisions_v73.json")
CANDIDATE_KEYS = ["candidates", "items", "pending_items", "memories", "memory_candidates"]

def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")

def load_decisions():
    if DECISIONS_FILE.exists():
        try:
            return json.loads(DECISIONS_FILE.read_text(errors="ignore"))
        except Exception:
            pass
    return {"created_at": now_timestamp(), "version": "v73.0.0", "decisions": []}

def save_decisions(data):
    data["updated_at"] = now_timestamp()
    DECISIONS_FILE.write_text(json.dumps(data, indent=4, ensure_ascii=False))
    return data

def _normalize_candidate(raw, index):
    if isinstance(raw, str):
        text = raw
        cid = f"candidate_{index:04d}"
    elif isinstance(raw, dict):
        cid = str(raw.get("id") or raw.get("candidate_id") or raw.get("key") or f"candidate_{index:04d}")
        text = str(raw.get("content") or raw.get("text") or raw.get("memory") or raw.get("summary") or raw)
    else:
        cid = f"candidate_{index:04d}"
        text = str(raw)
    return {"id": cid, "text": text[:2000]}

def load_candidates():
    candidates = []
    inbox_meta = {}

    try:
        from seed_memory_review_inbox_v64 import build_inbox
        inbox = build_inbox()
        inbox_meta = dict(inbox) if isinstance(inbox, dict) else {"inbox": str(inbox)}
        for key in CANDIDATE_KEYS:
            value = inbox.get(key) if isinstance(inbox, dict) else None
            if isinstance(value, list):
                candidates.extend(value)
                break
    except Exception as error:
        inbox_meta = {"error": str(error)}

    if not candidates:
        for pattern in ["*memory*candidate*.json", "*memory*inbox*.json", "*review*inbox*.json"]:
            for filename in glob.glob(pattern):
                try:
                    data = json.loads(Path(filename).read_text(errors="ignore"))
                    if isinstance(data, list):
                        candidates.extend(data)
                    elif isinstance(data, dict):
                        for key in CANDIDATE_KEYS:
                            if isinstance(data.get(key), list):
                                candidates.extend(data[key])
                                break
                except Exception:
                    pass

    normalized = [_normalize_candidate(x, i + 1) for i, x in enumerate(candidates)]
    return {"created_at": now_timestamp(), "version": "v73.0.0", "ok": True, "count": len(normalized), "candidates": normalized, "inbox_meta": inbox_meta}

def record_decision(candidate_id, decision, note=""):
    data = load_decisions()
    data.setdefault("decisions", []).append({
        "created_at": now_timestamp(),
        "candidate_id": str(candidate_id),
        "decision": decision,
        "note": note
    })
    save_decisions(data)
    return data["decisions"][-1]

def show_memory_review(limit=10):
    data = load_candidates()
    print("\n=== SEED v73 MEMORY REVIEW ACTIONS ===")
    print(f"Candidates visible: {data['count']}")
    pending = data.get("inbox_meta", {}).get("pending")
    if pending is not None:
        print(f"Pending reported by inbox: {pending}")
    if data["count"] == 0:
        print("No candidate list was exposed, but v64 may still report pending count. Use existing 'review memories' too.")
        return "handled"
    for c in data["candidates"][:limit]:
        print(f"- {c['id']}: {c['text'][:220]}")
    print("\nActions: memory save <id> | memory ignore <id> | memory later <id>")
    return "handled"

def handle_memory_action(text):
    parts = str(text or "").strip().split(maxsplit=2)
    if len(parts) < 3 or parts[0].lower() != "memory":
        return None
    action = parts[1].lower()
    cid = parts[2].strip()
    if action not in {"save", "ignore", "later"}:
        return None
    item = record_decision(cid, action)
    print(json.dumps(item, indent=4, ensure_ascii=False))
    return "handled"

if __name__ == "__main__":
    show_memory_review()
