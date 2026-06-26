import json, os, shutil, sys, glob
from pathlib import Path
from datetime import datetime

VERSION = "v137.1.0"
REPORT = Path("seed_log_optimizer_v1371_report.json")
EVENTS = Path("seed_log_optimizer_v1371_events.jsonl")
ARCHIVE_DIR = Path("seed_log_archive_v1371")

PATTERNS = [
    "*events.jsonl", "*.log", "seed_full_outputs_v1371/*.json",
    "seed_companion_v137_inbox.jsonl", "seed_companion_v137_events.jsonl"
]

def now():
    return datetime.now().isoformat(timespec="seconds")

def event(row):
    row.setdefault("created_at", now())
    row.setdefault("version", VERSION)
    with EVENTS.open("a") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row

def candidates():
    out = []
    for pat in PATTERNS:
        for p in glob.glob(pat):
            path = Path(p)
            if not path.is_file():
                continue
            if path.name in {EVENTS.name, REPORT.name}:
                continue
            try:
                out.append({"path": str(path), "bytes": path.stat().st_size, "lines": len(path.read_text(errors="ignore").splitlines()) if path.stat().st_size < 8_000_000 else None})
            except Exception:
                out.append({"path": str(path), "bytes": path.stat().st_size, "lines": None})
    return sorted(out, key=lambda x: x["bytes"], reverse=True)

def trim_file(path, keep_lines=700, archive=True):
    path = Path(path)
    if not path.exists() or not path.is_file():
        return {"ok": False, "path": str(path), "error": "missing"}
    txt = path.read_text(errors="ignore")
    lines = txt.splitlines()
    before = {"bytes": path.stat().st_size, "lines": len(lines)}
    if len(lines) <= keep_lines:
        return {"ok": True, "path": str(path), "unchanged": True, "before": before, "after": before}
    archive_path = None
    if archive:
        ARCHIVE_DIR.mkdir(exist_ok=True)
        archive_path = ARCHIVE_DIR / (path.name + "." + datetime.now().strftime("%Y%m%d_%H%M%S") + ".bak")
        shutil.copy2(path, archive_path)
    path.write_text("\n".join(lines[-keep_lines:]) + "\n")
    after = {"bytes": path.stat().st_size, "lines": len(path.read_text(errors="ignore").splitlines())}
    return {"ok": True, "path": str(path), "before": before, "after": after, "archive": str(archive_path) if archive_path else None}

def optimize(keep_lines=700, min_bytes=250_000, apply=False):
    rows = candidates()
    actions = []
    for c in rows:
        if c["bytes"] >= min_bytes or (c.get("lines") or 0) > keep_lines * 2:
            if apply:
                actions.append(trim_file(c["path"], keep_lines=keep_lines, archive=True))
            else:
                actions.append({"ok": True, "dry_run": True, "path": c["path"], "bytes": c["bytes"], "lines": c.get("lines")})
    report = {"created_at": now(), "version": VERSION, "ok": True, "apply": apply, "candidate_count": len(rows), "action_count": len(actions), "actions": actions}
    REPORT.write_text(json.dumps(report, indent=4, ensure_ascii=False))
    event({"event": "optimize", "apply": apply, "action_count": len(actions)})
    return report

def status():
    rows = candidates()
    total = sum(x["bytes"] for x in rows)
    return {"created_at": now(), "version": VERSION, "ok": True, "file_count": len(rows), "total_bytes": total, "largest": rows[:12]}

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "apply":
        print(json.dumps(optimize(apply=True), indent=4, ensure_ascii=False))
    elif cmd in {"dry-run", "plan"}:
        print(json.dumps(optimize(apply=False), indent=4, ensure_ascii=False))
    else:
        print(json.dumps(status(), indent=4, ensure_ascii=False))
