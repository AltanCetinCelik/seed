import json
import re
from pathlib import Path
from datetime import datetime

INDEX = Path("seed_private_rag_v104_index.jsonl")
SETTINGS = Path("seed_private_rag_v104_settings.json")

DEFAULTS = {
    "version": "v104.1.0",
    "roots": ["."],
    "max_file_kb": 180,
    "extensions": [".py", ".md", ".txt", ".json"],
    "exclude_dirs": [
        ".git", "__pycache__", "node_modules", ".venv", "venv",
        "third_party_repos", "seed_checkpoints", "seed_private_backup",
        "seed_mac_body_v88_screens", "seed_ambient_vision_v89_temp"
    ],
    "exclude_files": [
        "seed_private_rag_v104_index.jsonl",
        "seed_trace_v95.jsonl",
        "seed_errors_v95.jsonl",
        "seed_actions_v95.jsonl",
        "seed_tool_calls_v97.jsonl",
    ],
}

def now():
    return datetime.now().isoformat(timespec="seconds")

def settings():
    if SETTINGS.exists():
        try:
            old = json.loads(SETTINGS.read_text(errors="ignore"))
            d = DEFAULTS.copy()
            d.update(old)
            # force safer/focused excludes even if old settings existed
            d["version"] = "v104.1.0"
            d["exclude_dirs"] = sorted(set(DEFAULTS["exclude_dirs"]) | set(old.get("exclude_dirs", [])))
            d["exclude_files"] = sorted(set(DEFAULTS["exclude_files"]) | set(old.get("exclude_files", [])))
            SETTINGS.write_text(json.dumps(d, indent=4, ensure_ascii=False))
            return d
        except Exception:
            pass
    SETTINGS.write_text(json.dumps(DEFAULTS, indent=4, ensure_ascii=False))
    return DEFAULTS.copy()

def excluded(path):
    s = settings()
    parts = set(Path(path).parts)
    if parts.intersection(set(s["exclude_dirs"])):
        return True
    if Path(path).name in set(s["exclude_files"]):
        return True
    return False

def allowed(path):
    p = Path(path)
    s = settings()
    if excluded(p):
        return False
    try:
        return p.is_file() and p.suffix in set(s["extensions"]) and p.stat().st_size <= int(s["max_file_kb"]) * 1024
    except Exception:
        return False

def index():
    s = settings()
    rows = []
    for root in s["roots"]:
        for p in Path(root).rglob("*"):
            try:
                if allowed(p):
                    rows.append({
                        "path": str(p),
                        "size": p.stat().st_size,
                        "preview": p.read_text(errors="ignore")[:1500],
                        "indexed_at": now(),
                    })
            except Exception:
                pass
    INDEX.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + ("\n" if rows else ""))
    return {"ok": True, "indexed": len(rows), "version": "v104.1.0"}

def rows():
    if not INDEX.exists():
        return []
    out = []
    for line in INDEX.read_text(errors="ignore").splitlines():
        try:
            out.append(json.loads(line))
        except Exception:
            pass
    return out

def search(query):
    terms = [x for x in re.sub(r"[^a-z0-9çğıöşü\s]", " ", query.lower()).split() if len(x) > 1]
    hits = []
    for r in rows():
        hay = (r["path"] + " " + r.get("preview", "")).lower()
        score = sum(hay.count(t) for t in terms)
        if score:
            hits.append({"score": score, "path": r["path"], "preview": r.get("preview", "")[:450]})
    return sorted(hits, key=lambda x: x["score"], reverse=True)[:20]

def status():
    return {"created_at": now(), "version": "v104.1.0", "ok": True, "indexed": len(rows()), "settings": settings()}

if __name__ == "__main__":
    import sys
    arg = sys.argv[1] if len(sys.argv) > 1 else "status"
    if arg == "index":
        print(json.dumps(index(), indent=4, ensure_ascii=False))
    elif arg == "search":
        print(json.dumps(search(" ".join(sys.argv[2:])), indent=4, ensure_ascii=False))
    else:
        print(json.dumps(status(), indent=4, ensure_ascii=False))
