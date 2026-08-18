import json, subprocess, time, re
from datetime import datetime, timedelta
from pathlib import Path

NOTES_FILE = Path("seed_organism_notes_v89.jsonl")
QUESTIONS_FILE = Path("seed_organism_questions_v89.jsonl")
SETTINGS_FILE = Path("seed_organism_notes_v89_settings.json")

DEFAULTS = {
    "version": "v89.2.0",
    "max_notes": 1200,
    "ask_enabled": True,
    "min_importance_to_ask": 88,
    "min_seconds_between_questions": 1200,
    "speak_questions": True,
    "store_raw_audio": False,
    "store_raw_screenshots": False,
    "store_raw_transcripts": False,
    "note_only_mode": True,
    "reject_prompt_leak": True,
    "dedupe_minutes": 12,
    "reject_generic_questions": True,
    "reject_low_value_vision": True
}

BAD_TEXT = [
    "return only json",
    "inspect this temporary screenshot",
    "importance 0-100",
    "summary, question, tags",
    "user wants no screenshots saved",
    "seed ambient vision filter",
    "seed ambient hearing filter",
    "store no private raw image data",
    "user strauss"
]

GENERIC_QUESTIONS = {
    "what is user doing",
    "what is user doing?",
    "what is user doing on the mac",
    "what is user doing on the mac?",
    "what is the output of the command",
    "what is the output of the command?"
}

def now():
    return datetime.now().isoformat(timespec="seconds")

def settings():
    if SETTINGS_FILE.exists():
        try:
            d = DEFAULTS.copy()
            d.update(json.loads(SETTINGS_FILE.read_text(errors="ignore")))
            d["version"] = "v89.2.0"
            return d
        except Exception:
            pass
    SETTINGS_FILE.write_text(json.dumps(DEFAULTS, indent=4, ensure_ascii=False))
    return DEFAULTS.copy()

def norm(s):
    s = re.sub(r"[^a-z0-9çğıöşü\s]", " ", str(s or "").lower())
    return " ".join(s.split())

def is_bad_text(text):
    s = norm(text)
    return any(x in s for x in BAD_TEXT)

def is_generic_question(question):
    q = norm(question)
    return (not q) or q in {norm(x) for x in GENERIC_QUESTIONS} or is_bad_text(q)

def is_low_value_vision(summary, metadata=None):
    s = norm(summary)
    metadata = metadata or {}
    app = norm((metadata.get("active_window") or {}).get("app", ""))
    title = norm((metadata.get("active_window") or {}).get("title", ""))

    low_patterns = [
        "active screen changed",
        "active window",
        "using terminal app to run a script",
        "using the terminal app to run a script",
        "terminal window shows the output",
        "running a shell terminal",
        "displaying a command prompt",
        "using safari to access a webpage",
        "browser is showing a webpage",
        "webpage with a login prompt",
    ]

    if any(p in s for p in low_patterns):
        return True

    # Watching entertainment is a valid observation, but not worth long-term note unless asked.
    if any(x in s for x in ["person of interest", "episode", "show", "movie", "netflix", "youtube video"]):
        return True

    if app in {"safari", "firefox"} and len(s.split()) < 22:
        return True

    return False

def write(path, row):
    row.setdefault("created_at", now())
    row.setdefault("version", "v89.2.0")
    with path.open("a") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")

def read(path, limit=200):
    if not path.exists():
        return []
    out = []
    for line in path.read_text(errors="ignore").splitlines()[-limit:]:
        try:
            out.append(json.loads(line))
        except Exception:
            pass
    return out

def parse_dt(s):
    try:
        return datetime.fromisoformat(str(s))
    except Exception:
        return None

def recent_duplicate(source, summary, metadata=None):
    metadata = metadata or {}
    s = norm(summary)
    active = metadata.get("active_window") or {}
    key = (norm(active.get("app", "")), norm(active.get("title", "")))
    cutoff = datetime.now() - timedelta(minutes=float(settings().get("dedupe_minutes", 12)))

    for row in read(NOTES_FILE, 300):
        if row.get("source") != source:
            continue
        dt = parse_dt(row.get("created_at"))
        if dt and dt < cutoff:
            continue
        old = norm(row.get("summary", ""))
        old_active = (row.get("metadata") or {}).get("active_window") or {}
        old_key = (norm(old_active.get("app", "")), norm(old_active.get("title", "")))

        if s and old and (s == old or s in old or old in s):
            return True
        if key != ("", "") and key == old_key and source == "vision":
            return True
    return False

def trim():
    max_notes = int(settings().get("max_notes", 1200))
    if NOTES_FILE.exists():
        lines = NOTES_FILE.read_text(errors="ignore").splitlines()
        if len(lines) > max_notes:
            NOTES_FILE.write_text("\n".join(lines[-max_notes:]) + "\n")

def say(txt):
    if not settings().get("speak_questions", True):
        return False
    try:
        from seed_voice_v76 import say_with_settings
        return say_with_settings(txt)
    except Exception:
        try:
            import shutil
            b = shutil.which("say")
            if b:
                subprocess.run([b, str(txt)[:800]], timeout=60)
                return True
        except Exception:
            pass
    return False

def last_question_age():
    q = read(QUESTIONS_FILE, 1000)
    if not q:
        return 999999
    dt = parse_dt(q[-1].get("created_at"))
    if not dt:
        return 999999
    return (datetime.now() - dt).total_seconds()

def maybe_ask(note):
    s = settings()
    if not s.get("ask_enabled", True):
        return {"asked": False, "reason": "disabled"}
    if int(note.get("importance", 0)) < int(s.get("min_importance_to_ask", 88)):
        return {"asked": False, "reason": "importance"}
    if last_question_age() < float(s.get("min_seconds_between_questions", 1200)):
        return {"asked": False, "reason": "cooldown"}

    q = (note.get("question") or "").strip()
    if is_generic_question(q):
        return {"asked": False, "reason": "generic_or_bad_question"}

    try:
        from seed_avatar_v89 import set_avatar_state
        set_avatar_state(mode="curious", emotion="curious", message=q, hearing=False, seeing=False, thinking=False, speaking=False)
    except Exception:
        pass

    spoke = say(q)
    write(QUESTIONS_FILE, {"note_id": note.get("id"), "question": q, "spoke": spoke})
    return {"asked": True, "spoke": spoke, "question": q}

def add_note(source, summary, importance=50, question="", tags=None, metadata=None):
    metadata = metadata or {}
    cleaned = str(summary or "").strip()[:1200]

    if not cleaned or is_bad_text(cleaned):
        return {"ok": False, "blocked": True, "reason": "bad_or_empty_summary", "source": source}

    if source == "vision" and settings().get("reject_low_value_vision", True) and is_low_value_vision(cleaned, metadata):
        return {"ok": False, "blocked": True, "reason": "low_value_vision_note", "source": source, "summary": cleaned[:160]}

    if recent_duplicate(source, cleaned, metadata):
        return {"ok": False, "blocked": True, "reason": "recent_duplicate", "source": source, "summary": cleaned[:160]}

    q = "" if is_generic_question(question) else str(question or "").strip()[:500]

    note = {
        "id": f"note_{int(time.time()*1000)}",
        "source": source,
        "summary": cleaned,
        "importance": int(importance),
        "question": q,
        "tags": tags or [],
        "metadata": metadata,
        "raw_audio_saved": False,
        "raw_screenshot_saved": False,
        "raw_transcript_saved": False,
        "note_only_mode": True
    }
    write(NOTES_FILE, note)
    trim()

    try:
        from seed_avatar_v89 import set_avatar_state
        set_avatar_state(mode="noting", emotion="attentive", message=note["summary"], last_note=note, hearing=False, seeing=False, thinking=False, speaking=False)
    except Exception:
        pass

    return {"ok": True, "note": note, "ask": maybe_ask(note)}

def clean_bad_notes():
    if not NOTES_FILE.exists():
        return {"ok": True, "removed": 0, "kept": 0}
    kept, removed = [], 0
    seen = set()
    for line in NOTES_FILE.read_text(errors="ignore").splitlines():
        try:
            row = json.loads(line)
        except Exception:
            continue
        metadata = row.get("metadata") or {}
        key = (row.get("source"), norm(row.get("summary")), norm((metadata.get("active_window") or {}).get("app","")), norm((metadata.get("active_window") or {}).get("title","")))
        bad = (
            is_bad_text(row.get("summary", "")) or
            is_bad_text(row.get("question", "")) or
            (row.get("source") == "vision" and is_low_value_vision(row.get("summary", ""), metadata)) or
            key in seen
        )
        if bad:
            removed += 1
        else:
            row["question"] = "" if is_generic_question(row.get("question", "")) else row.get("question", "")
            kept.append(row)
            seen.add(key)
    NOTES_FILE.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in kept) + ("\n" if kept else ""))
    return {"ok": True, "removed": removed, "kept": len(kept)}

def latest_notes(limit=10):
    return read(NOTES_FILE, limit)

def note_stats():
    rows = read(NOTES_FILE, 5000)
    by = {}
    for r in rows:
        by[r.get("source", "unknown")] = by.get(r.get("source", "unknown"), 0) + 1
    return {"created_at": now(), "version": "v89.2.0", "ok": True, "count": len(rows), "by_source": by, "latest": rows[-5:], "settings": settings()}

def show_notes(n=10):
    print(json.dumps(latest_notes(n), indent=4, ensure_ascii=False))

def show_stats():
    print(json.dumps(note_stats(), indent=4, ensure_ascii=False))

if __name__ == "__main__":
    import sys
    a = sys.argv[1] if len(sys.argv) > 1 else "stats"
    if a == "latest":
        show_notes(int(sys.argv[2]) if len(sys.argv) > 2 else 10)
    elif a == "add":
        print(add_note("manual", " ".join(sys.argv[2:]) or "manual note", 60))
    elif a == "clean":
        print(clean_bad_notes())
    else:
        show_stats()
