import json
import shutil
import zipfile
from datetime import datetime
from pathlib import Path

BACKUP_DIR = Path("seed_backups_v84")
EXPORT_DIR = Path("seed_exports_v84")
FORGET_LOG = Path("seed_forget_log_v84.jsonl")

EXCLUDE_DIRS = {".git", "__pycache__", "seed_voice_recordings_v731", "seed_backups_v84", "node_modules", ".venv", "venv"}
EXCLUDE_SUFFIXES = {".pyc", ".wav", ".mp3", ".mp4", ".mov"}

def now():
    return datetime.now().isoformat(timespec="seconds")

def ensure_dirs():
    BACKUP_DIR.mkdir(exist_ok=True)
    EXPORT_DIR.mkdir(exist_ok=True)

def should_skip(path):
    parts = set(path.parts)
    if parts & EXCLUDE_DIRS:
        return True
    if path.suffix.lower() in EXCLUDE_SUFFIXES:
        return True
    return False

def backup_project(label="manual"):
    ensure_dirs()
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = BACKUP_DIR / f"seed_backup_{stamp}_{label}.zip"
    count = 0
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for p in Path(".").rglob("*"):
            if p.is_file() and not should_skip(p):
                z.write(p, p.as_posix())
                count += 1
    meta = {"created_at": now(), "version": "v84.0.0", "ok": True, "file": str(out), "files": count}
    (BACKUP_DIR / f"{out.stem}.json").write_text(json.dumps(meta, indent=4))
    return meta

def list_backups():
    ensure_dirs()
    items = []
    for p in sorted(BACKUP_DIR.glob("seed_backup_*.zip")):
        items.append({"file": str(p), "size_mb": round(p.stat().st_size / (1024*1024), 2), "created": datetime.fromtimestamp(p.stat().st_mtime).isoformat(timespec="seconds")})
    return {"ok": True, "count": len(items), "items": items[-20:]}

def export_memory():
    ensure_dirs()
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_out = EXPORT_DIR / f"seed_memory_export_{stamp}.json"
    txt_out = EXPORT_DIR / f"seed_memory_export_{stamp}.txt"

    data = {}
    for file in ["seed_long_term_memory_v75.json", "seed_memory_decisions_v75.jsonl", "seed_self_state_v85.json", "seed_self_state_v81.json"]:
        p = Path(file)
        if p.exists():
            if p.suffix == ".json":
                try:
                    data[file] = json.loads(p.read_text(errors="ignore"))
                except Exception:
                    data[file] = p.read_text(errors="ignore")
            else:
                data[file] = p.read_text(errors="ignore").splitlines()

    json_out.write_text(json.dumps({"created_at": now(), "version": "v84.0.0", "data": data}, indent=4, ensure_ascii=False))

    lines = [f"Seed memory export {now()}", ""]
    mem = data.get("seed_long_term_memory_v75.json", {}).get("memories", []) if isinstance(data.get("seed_long_term_memory_v75.json"), dict) else []
    for item in mem:
        lines.append(f"- {item.get('id')}: {item.get('text')}")
    txt_out.write_text("\n".join(lines))
    return {"ok": True, "json": str(json_out), "txt": str(txt_out), "memory_count": len(mem)}

def forget_keyword(keyword):
    keyword = str(keyword or "").strip()
    if not keyword:
        return {"ok": False, "error": "empty keyword"}
    p = Path("seed_long_term_memory_v75.json")
    if not p.exists():
        return {"ok": False, "error": "memory file not found"}

    data = json.loads(p.read_text(errors="ignore"))
    before = data.get("memories", [])
    kept, removed = [], []
    for item in before:
        if keyword.lower() in str(item.get("text", "")).lower():
            removed.append(item)
        else:
            kept.append(item)
    data["memories"] = kept
    data["updated_at"] = now()
    p.write_text(json.dumps(data, indent=4, ensure_ascii=False))

    with FORGET_LOG.open("a") as f:
        f.write(json.dumps({"created_at": now(), "version": "v84.0.0", "keyword": keyword, "removed": removed}, ensure_ascii=False) + "\n")

    return {"ok": True, "keyword": keyword, "removed_count": len(removed), "kept_count": len(kept)}

def cleanup_voice_logs():
    # Non-destructive by default: only counts.
    files = list(Path(".").glob("seed_voice_recordings_v731/*.wav"))
    return {"ok": True, "recording_count": len(files), "note": "Non-destructive. Delete manually or add destructive cleanup later."}

def privacy_status():
    ensure_dirs()
    exported = list(EXPORT_DIR.glob("*"))
    backups = list(BACKUP_DIR.glob("*.zip"))
    memory_file = Path("seed_long_term_memory_v75.json")
    memory_count = 0
    if memory_file.exists():
        try:
            memory_count = len(json.loads(memory_file.read_text(errors="ignore")).get("memories", []))
        except Exception:
            pass
    return {
        "created_at": now(),
        "version": "v84.0.0",
        "ok": True,
        "backup_count": len(backups),
        "export_count": len(exported),
        "memory_count": memory_count,
        "forget_log_exists": FORGET_LOG.exists(),
        "dirs": {"backups": str(BACKUP_DIR), "exports": str(EXPORT_DIR)},
    }

def show_privacy():
    print("\n=== SEED v84 BACKUP / PRIVACY / EXPORT ===")
    print(json.dumps(privacy_status(), indent=4, ensure_ascii=False))
    print("\nCommands:")
    print("backup seed")
    print("list backups")
    print("export memory")
    print("forget memory <keyword>")

if __name__ == "__main__":
    show_privacy()
