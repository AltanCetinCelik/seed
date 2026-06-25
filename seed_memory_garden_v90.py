import json
import re
from datetime import datetime
from pathlib import Path

STATE_FILE = Path("seed_memory_garden_v90_state.json")
MEMORIES_FILE = Path("seed_memory_garden_v90_memories.jsonl")
ARCHIVE_FILE = Path("seed_memory_garden_v90_archive.jsonl")
SETTINGS_FILE = Path("seed_memory_garden_v90_settings.json")

DEFAULTS = {
    "version": "v90.0.0",
    "auto_archive_startup_notes": True,
    "auto_archive_low_value_notes": True,
    "min_importance_candidate": 75,
    "min_importance_auto_promote": 92,
    "max_candidate_cards": 25,
    "memory_context_limit": 12,
    "note_source_file": "seed_organism_notes_v89.jsonl",
    "no_raw_media_rule": True
}

LOW_VALUE_PATTERNS = [
    "organism mode started",
    "seed organism mode started",
    "stores notes only",
    "terminal window",
    "command prompt",
    "active window",
    "safari webpage",
    "firefox window",
    "browser is showing",
    "person of interest",
    "episode",
    "watching show",
    "webpage with a login prompt"
]

HIGH_VALUE_HINTS = [
    "decided", "wants", "prefers", "important", "todo", "next", "bug", "fixed",
    "permission", "working", "green", "failed", "project", "seed", "memory",
    "mac body", "organism", "wake", "avatar", "vision", "hearing"
]

def now():
    return datetime.now().isoformat(timespec="seconds")

def load_settings():
    if SETTINGS_FILE.exists():
        try:
            d = DEFAULTS.copy()
            d.update(json.loads(SETTINGS_FILE.read_text(errors="ignore")))
            d["version"] = "v90.0.0"
            return d
        except Exception:
            pass
    SETTINGS_FILE.write_text(json.dumps(DEFAULTS, indent=4, ensure_ascii=False))
    return DEFAULTS.copy()

def write_jsonl(path, row):
    row.setdefault("created_at", now())
    row.setdefault("version", "v90.0.0")
    with path.open("a") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")

def read_jsonl(path, limit=5000):
    if not Path(path).exists():
        return []
    rows = []
    for line in Path(path).read_text(errors="ignore").splitlines()[-limit:]:
        try:
            rows.append(json.loads(line))
        except Exception:
            pass
    return rows

def norm(text):
    text = re.sub(r"[^a-z0-9çğıöşü\s]", " ", str(text or "").lower())
    return " ".join(text.split())

def note_id(note):
    return str(note.get("id") or note.get("created_at") or "")

def is_low_value(note):
    summary = norm(note.get("summary", ""))
    source = note.get("source", "")
    if source == "organism" and "organism mode started" in summary:
        return True
    return any(p in summary for p in LOW_VALUE_PATTERNS)

def has_high_value_hint(note):
    s = norm(note.get("summary", ""))
    tags = " ".join([norm(t) for t in note.get("tags", [])])
    return any(h in s or h in tags for h in HIGH_VALUE_HINTS)

def memory_type_for(note):
    s = norm(note.get("summary", ""))
    tags = " ".join([norm(t) for t in note.get("tags", [])])
    if "prefers" in s or "wants" in s or "likes" in s:
        return "preference"
    if "bug" in s or "failed" in s or "fixed" in s or "permission" in s:
        return "technical_state"
    if "green" in s or "working" in s or "ready true" in s:
        return "milestone"
    if "todo" in s or "next" in s:
        return "open_loop"
    if "seed" in s or "organism" in s or "mac body" in s or "wake" in s:
        return "project_context"
    if "vision" in tags or "hearing" in tags:
        return "observation"
    return "general"

def reviewed_ids():
    ids = set()
    for row in read_jsonl(MEMORIES_FILE):
        ids.add(str(row.get("source_note_id", "")))
    for row in read_jsonl(ARCHIVE_FILE):
        ids.add(str(row.get("source_note_id", "")))
    return ids

def load_notes():
    settings = load_settings()
    return read_jsonl(settings.get("note_source_file", "seed_organism_notes_v89.jsonl"))

def classify_note(note):
    settings = load_settings()
    importance = int(note.get("importance", 0) or 0)
    low = is_low_value(note)
    high_hint = has_high_value_hint(note)
    source = note.get("source", "unknown")
    summary = str(note.get("summary", "")).strip()

    if not summary:
        return {"action": "archive", "reason": "empty_summary", "score": 0}

    if low:
        return {"action": "archive", "reason": "low_value_or_startup_note", "score": min(importance, 35)}

    score = importance
    if high_hint:
        score += 12
    if source in {"hearing", "vision"}:
        score += 2
    score = min(score, 100)

    if score >= int(settings.get("min_importance_auto_promote", 92)):
        return {"action": "promote", "reason": "high_importance", "score": score}

    if score >= int(settings.get("min_importance_candidate", 75)):
        return {"action": "candidate", "reason": "review_candidate", "score": score}

    return {"action": "ignore", "reason": "not_important_enough", "score": score}

def note_to_memory(note, decision=None):
    decision = decision or classify_note(note)
    return {
        "memory_id": "mem_" + note_id(note).replace("note_", ""),
        "source_note_id": note_id(note),
        "memory_type": memory_type_for(note),
        "summary": str(note.get("summary", "")).strip(),
        "importance": int(note.get("importance", 0) or 0),
        "score": decision.get("score"),
        "tags": note.get("tags", []),
        "metadata": note.get("metadata", {}),
        "created_from_note_at": note.get("created_at"),
        "raw_audio_saved": False,
        "raw_screenshot_saved": False,
        "raw_transcript_saved": False,
        "note_only_mode": True
    }

def digest_notes(apply=False):
    ids = reviewed_ids()
    notes = load_notes()
    cards = []
    promoted = 0
    archived = 0

    for note in notes:
        nid = note_id(note)
        if not nid or nid in ids:
            continue
        decision = classify_note(note)
        card = {"note_id": nid, "decision": decision, "source": note.get("source"), "summary": note.get("summary"), "importance": note.get("importance"), "tags": note.get("tags", [])}
        cards.append(card)

        if apply and decision["action"] == "promote":
            write_jsonl(MEMORIES_FILE, note_to_memory(note, decision))
            promoted += 1
        elif apply and decision["action"] in {"archive", "ignore"}:
            write_jsonl(ARCHIVE_FILE, {"source_note_id": nid, "reason": decision["reason"], "summary": note.get("summary"), "decision": decision})
            archived += 1

    state = {"created_at": now(), "version": "v90.0.0", "ok": True, "apply": apply, "promoted": promoted, "archived": archived, "cards": cards[:int(load_settings().get("max_candidate_cards", 25))], "unreviewed_count": len(cards)}
    STATE_FILE.write_text(json.dumps(state, indent=4, ensure_ascii=False))
    return state

def promote_note(note_id_value):
    notes = load_notes()
    target = None
    for note in notes:
        if note_id(note) == str(note_id_value):
            target = note
            break
    if not target:
        return {"ok": False, "error": "note not found", "note_id": note_id_value}
    mem = note_to_memory(target, {"score": 100, "reason": "manual_promote"})
    write_jsonl(MEMORIES_FILE, mem)
    return {"ok": True, "promoted": mem}

def promote_latest_candidate():
    state = digest_notes(apply=False)
    for card in state["cards"]:
        if card["decision"]["action"] in {"candidate", "promote"}:
            return promote_note(card["note_id"])
    return {"ok": False, "error": "no candidate found"}

def archive_note(note_id_value, reason="manual_archive"):
    write_jsonl(ARCHIVE_FILE, {"source_note_id": str(note_id_value), "reason": reason})
    return {"ok": True, "archived": str(note_id_value), "reason": reason}

def memories(limit=20):
    return read_jsonl(MEMORIES_FILE, limit)

def garden_context(limit=None):
    limit = int(limit or load_settings().get("memory_context_limit", 12))
    rows = memories(limit)
    if not rows:
        return "Seed Memory Garden: no promoted memories yet."
    lines = ["Seed Memory Garden promoted memories:"]
    for r in rows[-limit:]:
        lines.append(f"- [{r.get('memory_type')}] {r.get('summary')}")
    return "\n".join(lines)

def daily_summary():
    mems = memories(50)
    notes = load_notes()[-50:]
    recent = mems[-12:] if mems else notes[-12:]
    if not recent:
        return {"ok": True, "summary": "No meaningful notes yet."}
    bullets = []
    for r in recent:
        s = str(r.get("summary", "")).strip()
        if s:
            bullets.append("- " + s)
    return {"ok": True, "summary": "Seed day summary:\n" + "\n".join(bullets[-12:])}

def status():
    notes = load_notes()
    mems = memories(5000)
    archived = read_jsonl(ARCHIVE_FILE, 5000)
    unreviewed = [n for n in notes if note_id(n) not in reviewed_ids()]
    data = {
        "created_at": now(),
        "version": "v90.0.0",
        "ok": True,
        "notes_total": len(notes),
        "memories_total": len(mems),
        "archived_total": len(archived),
        "unreviewed_total": len(unreviewed),
        "settings": load_settings(),
        "latest_memories": mems[-5:]
    }
    STATE_FILE.write_text(json.dumps(data, indent=4, ensure_ascii=False))
    return data

def show_status():
    print("\n=== SEED v90 MEMORY GARDEN STATUS ===")
    print(json.dumps(status(), indent=4, ensure_ascii=False))

def show_review(apply=False):
    print("\n=== SEED v90 MEMORY GARDEN REVIEW ===")
    print(json.dumps(digest_notes(apply=apply), indent=4, ensure_ascii=False))

def show_memories(limit=20):
    print("\n=== SEED v90 PROMOTED MEMORIES ===")
    print(json.dumps(memories(limit), indent=4, ensure_ascii=False))

# v90.1.1 memory summary override: do not summarize archived low-value notes.
def daily_summary():
    """Summarize only promoted memories or meaningful unreviewed candidates.
    Archived low-value notes must not appear in the daily summary."""
    archived_ids = {str(r.get("source_note_id", "")) for r in read_jsonl(ARCHIVE_FILE, 5000)}

    mems = memories(50)
    if mems:
        bullets = []
        for r in mems[-12:]:
            s = str(r.get("summary", "")).strip()
            if s:
                bullets.append("- " + s)
        if bullets:
            return {"ok": True, "summary": "Seed day summary:\n" + "\n".join(bullets[-12:])}

    meaningful = []
    for note in load_notes()[-80:]:
        nid = note_id(note)
        if nid in archived_ids:
            continue
        decision = classify_note(note)
        if decision.get("action") in {"candidate", "promote"}:
            s = str(note.get("summary", "")).strip()
            if s:
                meaningful.append("- " + s)

    if meaningful:
        return {"ok": True, "summary": "Seed day summary candidates:\n" + "\n".join(meaningful[-12:])}

    return {"ok": True, "summary": "Seed day summary: no meaningful promoted memories yet."}

if __name__ == "__main__":
    import sys
    arg = sys.argv[1] if len(sys.argv) > 1 else "status"
    if arg == "status":
        show_status()
    elif arg == "review":
        show_review(apply=False)
    elif arg == "digest":
        show_review(apply=True)
    elif arg == "memories":
        show_memories(int(sys.argv[2]) if len(sys.argv) > 2 else 20)
    elif arg == "promote":
        print(promote_note(sys.argv[2]))
    elif arg == "promote-latest":
        print(promote_latest_candidate())
    elif arg == "archive":
        print(archive_note(sys.argv[2], "manual_archive"))
    elif arg == "summary":
        print(daily_summary()["summary"])
    elif arg == "context":
        print(garden_context())
    else:
        print("Commands: status | review | digest | memories [n] | promote <note_id> | promote-latest | archive <note_id> | summary | context")
