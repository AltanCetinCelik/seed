import json
from datetime import datetime
from pathlib import Path

SETTINGS_FILE = Path("seed_companion_context_v91_settings.json")
STATE_FILE = Path("seed_companion_context_v91_state.json")
MEMORIES_FILE = Path("seed_memory_garden_v90_memories.jsonl")
NOTES_FILE = Path("seed_organism_notes_v89.jsonl")

DEFAULTS = {
    "version": "v91.0.0",
    "memory_limit": 12,
    "note_limit": 6,
    "max_context_chars": 3500,
    "include_note_only_rule": True,
    "bootstrap_seed_milestone": True
}

BASELINE_MEMORY_ID = "mem_seed_v91_baseline_green"

BASELINE_MEMORY = {
    "memory_id": BASELINE_MEMORY_ID,
    "source_note_id": "manual_v91_baseline",
    "memory_type": "milestone",
    "summary": "Seed baseline on User's Mac is green through v90.1.1: v88 Mac Body works, keyboard control works after Accessibility permission, v89 organism avatar/hearing/vision works in note-only mode, v89.2 filters low-value notes, and v90 Memory Garden archives junk with no promoted memories yet.",
    "importance": 96,
    "score": 100,
    "tags": ["seed", "milestone", "mac_body", "organism", "memory_garden", "v91_baseline"],
    "metadata": {"created_by": "seed_v91_context_bootstrap"},
    "created_from_note_at": None,
    "raw_audio_saved": False,
    "raw_screenshot_saved": False,
    "raw_transcript_saved": False,
    "note_only_mode": True
}

def now():
    return datetime.now().isoformat(timespec="seconds")

def load_settings():
    if SETTINGS_FILE.exists():
        try:
            d = DEFAULTS.copy()
            d.update(json.loads(SETTINGS_FILE.read_text(errors="ignore")))
            d["version"] = "v91.0.0"
            return d
        except Exception:
            pass
    SETTINGS_FILE.write_text(json.dumps(DEFAULTS, indent=4, ensure_ascii=False))
    return DEFAULTS.copy()

def read_jsonl(path, limit=5000):
    path = Path(path)
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(errors="ignore").splitlines()[-limit:]:
        try:
            rows.append(json.loads(line))
        except Exception:
            pass
    return rows

def append_jsonl(path, row):
    row.setdefault("created_at", now())
    row.setdefault("version", "v91.0.0")
    with Path(path).open("a") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")

def ensure_baseline_memory():
    settings = load_settings()
    if not settings.get("bootstrap_seed_milestone", True):
        return {"ok": True, "created": False, "disabled": True}

    for row in read_jsonl(MEMORIES_FILE):
        if row.get("memory_id") == BASELINE_MEMORY_ID:
            return {"ok": True, "created": False, "memory_id": BASELINE_MEMORY_ID}

    append_jsonl(MEMORIES_FILE, BASELINE_MEMORY.copy())
    return {"ok": True, "created": True, "memory_id": BASELINE_MEMORY_ID}

def promoted_memories(limit=None):
    limit = int(limit or load_settings().get("memory_limit", 12))
    return read_jsonl(MEMORIES_FILE, limit)

def recent_notes(limit=None):
    limit = int(limit or load_settings().get("note_limit", 6))
    rows = read_jsonl(NOTES_FILE, 5000)
    useful = []
    for row in rows:
        if row.get("source") == "organism":
            continue
        if row.get("raw_audio_saved") or row.get("raw_screenshot_saved") or row.get("raw_transcript_saved"):
            continue
        summary = str(row.get("summary", "")).strip()
        if summary:
            useful.append(row)
    return useful[-limit:]

def status():
    ensure = ensure_baseline_memory()
    mems = promoted_memories()
    notes = recent_notes()
    data = {
        "created_at": now(),
        "version": "v91.0.0",
        "ok": True,
        "baseline_memory": ensure,
        "memory_count": len(read_jsonl(MEMORIES_FILE, 5000)),
        "context_memories": len(mems),
        "recent_notes": len(notes),
        "settings": load_settings()
    }
    STATE_FILE.write_text(json.dumps(data, indent=4, ensure_ascii=False))
    return data

def build_context_text(max_chars=None):
    ensure_baseline_memory()
    settings = load_settings()
    max_chars = int(max_chars or settings.get("max_context_chars", 3500))

    mems = promoted_memories(settings.get("memory_limit", 12))
    notes = recent_notes(settings.get("note_limit", 6))

    lines = []
    lines.append("SEED COMPANION CONTEXT v91")
    lines.append("Identity: Seed is User's private local companion/friend, not a public product.")
    lines.append("Tone: natural, direct, helpful; Turkish if User uses Turkish; do not over-explain.")
    lines.append("Reality: Seed is not literally biologically alive; it can act organism-like through senses, memory, avatar, curiosity, and Mac body.")
    if settings.get("include_note_only_rule", True):
        lines.append("Privacy rule: raw audio, raw screenshots, and raw transcripts should not be saved. Store only important notes/memories.")

    if mems:
        lines.append("\nPROMOTED MEMORIES:")
        for m in mems[-int(settings.get("memory_limit", 12)):]:
            mt = m.get("memory_type", "memory")
            summary = str(m.get("summary", "")).strip()
            if summary:
                lines.append(f"- [{mt}] {summary}")
    else:
        lines.append("\nPROMOTED MEMORIES: none yet.")

    if notes:
        lines.append("\nRECENT NOTE-ONLY OBSERVATIONS:")
        for n in notes[-int(settings.get("note_limit", 6)):]:
            src = n.get("source", "note")
            summary = str(n.get("summary", "")).strip()
            if summary:
                lines.append(f"- [{src}] {summary}")

    text = "\n".join(lines)
    if len(text) > max_chars:
        text = text[:max_chars-160] + "\n...[context trimmed]"
    return text

def show_status():
    print("\n=== SEED v91 COMPANION CONTEXT STATUS ===")
    print(json.dumps(status(), indent=4, ensure_ascii=False))

def show_context():
    print(build_context_text())

if __name__ == "__main__":
    import sys
    arg = sys.argv[1] if len(sys.argv) > 1 else "status"
    if arg == "status":
        show_status()
    elif arg == "context":
        show_context()
    elif arg == "bootstrap":
        print(ensure_baseline_memory())
    else:
        print("Commands: status | context | bootstrap")
