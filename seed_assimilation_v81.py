import json
import re
from datetime import datetime
from pathlib import Path

BACKLOG_FILE = Path("seed_assimilation_backlog_v81.json")
DECISIONS_FILE = Path("seed_assimilation_decisions_v81.jsonl")

def now():
    return datetime.now().isoformat(timespec="seconds")

def read_decisions():
    if not DECISIONS_FILE.exists():
        return []
    rows = []
    for line in DECISIONS_FILE.read_text(errors="ignore").splitlines():
        try:
            rows.append(json.loads(line))
        except Exception:
            pass
    return rows

def decision_map():
    return {r.get("id"): r for r in read_decisions() if r.get("id")}

def write_decision(row):
    with DECISIONS_FILE.open("a") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")

def categorize(text):
    low = str(text).lower()
    if any(w in low for w in ["emotion", "excited", "personality", "feel", "simulating"]):
        return "expression"
    if "voice" in low or "talk" in low or "mic" in low:
        return "voice"
    if "avatar" in low or "panel" in low or "ui" in low:
        return "panel"
    if "memory" in low or "remember" in low:
        return "memory"
    if "curious" in low or "curiosity" in low or "ask" in low:
        return "curiosity"
    if "aider" in low or "coding" in low or "code" in low:
        return "coding"
    if "tool" in low or "permission" in low or "approve" in low:
        return "executor"
    return "general"

def load_friend_advice():
    items = []
    try:
        import seed_friend_advice_ingestor_v72 as advice
        for name in ["load", "load_advice", "load_backlog"]:
            if hasattr(advice, name):
                data = getattr(advice, name)()
                raw = data.get("items") or data.get("advice") or data.get("tasks") or []
                for it in raw:
                    text = it.get("content") or it.get("title") or it.get("body") or str(it)
                    items.append({"source": "friend_advice_v72", "text": text, "raw": it})
                break
    except Exception:
        pass
    return items

def load_repo_patterns():
    items = []
    try:
        from seed_repo_pattern_extractor_v72 import build_repo_patterns
        data = build_repo_patterns()
        for group in data.get("patterns", []):
            label = group.get("label", "repo")
            for task in group.get("seed_native_tasks", []):
                items.append({"source": f"repo_pattern_{label}", "text": task, "raw": group})
    except Exception:
        pass
    return items

def build_backlog():
    raw = []
    raw.extend(load_friend_advice())
    raw.extend(load_repo_patterns())

    # Seed known v1 targets.
    for text in [
        "v82 should add reliability, recovery, rollback, dependency checks, and broken import detection.",
        "v83 should add one-command runtime: seed start.",
        "v84 should add backup, restore, export, delete memory, and private mode.",
        "v85 should be a release candidate with fresh install simulation and docs.",
    ]:
        raw.append({"source": "v1_path", "text": text, "raw": {"type": "planned"}})

    decisions = decision_map()
    items = []
    seen = set()
    for it in raw:
        text = str(it.get("text", "")).strip()
        if not text:
            continue
        key = re.sub(r"\s+", " ", text.lower())[:120]
        if key in seen:
            continue
        seen.add(key)
        item_id = f"assim_{len(items)+1:04d}"
        dec = decisions.get(item_id, {})
        items.append({
            "id": item_id,
            "created_at": now(),
            "version": "v81.0.0",
            "source": it.get("source"),
            "category": categorize(text),
            "text": text,
            "raw": it.get("raw", {}),
            "status": dec.get("action", "pending"),
            "why": "Converted from friend advice, repo pattern, or real-v1 roadmap.",
        })

    data = {"created_at": now(), "version": "v81.0.0", "ok": True, "count": len(items), "items": items}
    BACKLOG_FILE.write_text(json.dumps(data, indent=4, ensure_ascii=False))
    return data

def decide(item_id, action, note=""):
    action = str(action).lower().strip()
    if action not in {"accept", "reject", "later"}:
        action = "later"
    row = {"created_at": now(), "version": "v81.0.0", "id": item_id, "action": action, "note": note}
    write_decision(row)
    return {"ok": True, "decision": row}

def assimilation_summary():
    data = build_backlog()
    items = data.get("items", [])
    return {
        "created_at": now(),
        "version": "v81.0.0",
        "ok": True,
        "count": len(items),
        "pending_count": len([i for i in items if i.get("status") == "pending"]),
        "accepted_count": len([i for i in items if i.get("status") == "accept"]),
        "rejected_count": len([i for i in items if i.get("status") == "reject"]),
        "categories": sorted(set(i.get("category") for i in items)),
    }

def show_assimilation():
    print("\n=== SEED v81 ADVICE + REPO ASSIMILATION ===")
    data = build_backlog()
    print(f"Items: {data['count']}")
    for item in data["items"][:60]:
        print(f"- {item['id']} [{item['category']}/{item['status']}] {item['text'][:220]}")
        print(f"  source: {item['source']}")
    print("\nUse: accept assimilation assim_0001 | reject assimilation assim_0002 | later assimilation assim_0003")

if __name__ == "__main__":
    show_assimilation()
