import json
from datetime import datetime
from pathlib import Path

NOTES_FILE = Path("seed_organism_notes_v89.jsonl")
STATE = Path("seed_vision_v98_state.json")
AMBIENT_STATUS_FILE = Path("seed_ambient_vision_v89_status.json")

LOW_VALUE_SELF_TEST = [
    "seed_vision_v98.py once",
    "run a script named `seed_vision_v98.py once`",
    "terminal application to run a script",
    "osascript ◂ python seed_vision_v98.py once",
]

def now():
    return datetime.now().isoformat(timespec="seconds")

def is_low_value_self_test(summary):
    s = str(summary or "").lower()
    return any(p.lower() in s for p in LOW_VALUE_SELF_TEST)

def remove_note(note_id):
    if not note_id or not NOTES_FILE.exists():
        return False
    kept = []
    removed = False
    for line in NOTES_FILE.read_text(errors="ignore").splitlines():
        try:
            row = json.loads(line)
            rid = row.get("id") or row.get("note_id")
            if rid == note_id:
                removed = True
                continue
        except Exception:
            pass
        kept.append(line)
    if removed:
        NOTES_FILE.write_text("\n".join(kept) + ("\n" if kept else ""))
    return removed

def cleanup_existing():
    if not NOTES_FILE.exists():
        return {"ok": True, "removed": 0}
    kept = []
    removed = 0
    for line in NOTES_FILE.read_text(errors="ignore").splitlines():
        keep = True
        try:
            row = json.loads(line)
            if row.get("source") == "vision" and is_low_value_self_test(row.get("summary", "")):
                keep = False
                removed += 1
        except Exception:
            pass
        if keep:
            kept.append(line)
    if removed:
        NOTES_FILE.write_text("\n".join(kept) + ("\n" if kept else ""))
    return {"ok": True, "removed": removed}

def sanitize_runtime_status(runtime_status):
    if not isinstance(runtime_status, dict):
        return runtime_status
    saved = runtime_status.get("saved", {})
    note = saved.get("note", {}) if isinstance(saved, dict) else {}
    summary = note.get("summary", "") or saved.get("summary", "")
    if is_low_value_self_test(summary):
        cleaned = dict(runtime_status)
        cleaned["stored"] = False
        cleaned["stale_display_cleaned"] = True
        cleaned["saved"] = {
            "ok": False,
            "blocked": True,
            "reason": "stale_low_value_terminal_self_test_display",
            "summary": summary,
            "raw_note_removed": True,
        }
        return cleaned
    return runtime_status

def once():
    cleanup = cleanup_existing()
    try:
        from seed_ambient_vision_v89 import process_screen
        result = process_screen()
        saved = result.get("saved", {}) if isinstance(result, dict) else {}
        note = saved.get("note", {}) if isinstance(saved, dict) else {}
        summary = note.get("summary", "")
        if saved.get("ok") and is_low_value_self_test(summary):
            nid = note.get("id") or note.get("note_id")
            removed = remove_note(nid)
            result["stored"] = False
            result["saved"] = {
                "ok": False,
                "blocked": True,
                "reason": "low_value_terminal_self_test",
                "removed_note": removed,
                "note_id": nid,
                "summary": summary,
            }
        data = {
            "created_at": now(),
            "version": "v98.2.0",
            "ok": True,
            "result": result,
            "privacy": "note_only_screenshot_deleted",
            "cleanup": cleanup,
        }
    except Exception as e:
        data = {"created_at": now(), "version": "v98.2.0", "ok": False, "error": str(e), "cleanup": cleanup}
    STATE.write_text(json.dumps(data, indent=4, ensure_ascii=False))
    return data

def status():
    cleanup = cleanup_existing()
    try:
        from seed_ambient_vision_v89 import vision_status
        ambient = vision_status()
    except Exception as e:
        ambient = {"ok": False, "error": str(e)}
    if isinstance(ambient, dict) and isinstance(ambient.get("runtime_status"), dict):
        ambient["runtime_status"] = sanitize_runtime_status(ambient["runtime_status"])
    return {
        "created_at": now(),
        "version": "v98.2.0",
        "ok": True,
        "ambient_vision": ambient,
        "cleanup": cleanup,
        "capabilities": ["observe", "temporary screenshot", "note-only", "filter low-value", "hide stale terminal self-test runtime display"],
    }

if __name__ == "__main__":
    import sys
    arg = sys.argv[1] if len(sys.argv) > 1 else "status"
    if arg == "once":
        print(json.dumps(once(), indent=4, ensure_ascii=False))
    elif arg == "cleanup":
        print(json.dumps(cleanup_existing(), indent=4, ensure_ascii=False))
    else:
        print(json.dumps(status(), indent=4, ensure_ascii=False))
