import hashlib
import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path


try:
    from seed_config import SEED_CHECKPOINT_DIR, SEED_ROLLBACK_STATE_FILE
except Exception:
    SEED_CHECKPOINT_DIR = "seed_checkpoints"
    SEED_ROLLBACK_STATE_FILE = "seed_rollback_state.json"


SAFE_EXTENSIONS = {".py", ".md", ".json", ".txt", ".yaml", ".yml", ".toml", ".html", ".css", ".js", ".sh"}


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def make_token(checkpoint_id):
    return hashlib.sha256((checkpoint_id + now_timestamp()).encode()).hexdigest()[:12]


def safe_file(path):
    p = Path(path)
    return p.exists() and p.is_file() and p.suffix.lower() in SAFE_EXTENSIONS and ".." not in p.parts


def git_output(args):
    try:
        result = subprocess.run(["git"] + args, capture_output=True, text=True, timeout=20)
        return {
            "ok": result.returncode == 0,
            "stdout": result.stdout[-5000:],
            "stderr": result.stderr[-3000:]
        }
    except Exception as error:
        return {"ok": False, "error": str(error)}


def create_checkpoint(name, files=None):
    checkpoint_id = datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + "".join(ch if ch.isalnum() else "-" for ch in name.lower())[:40]
    root = Path(SEED_CHECKPOINT_DIR) / checkpoint_id
    root.mkdir(parents=True, exist_ok=True)

    selected = []
    invalid = []

    if not files:
        files = [str(p) for p in Path(".").glob("seed_*.py")]

    for item in files:
        if safe_file(item):
            dest = root / item
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, dest)
            selected.append(item)
        else:
            invalid.append(item)

    token = make_token(checkpoint_id)

    state = {
        "created_at": now_timestamp(),
        "version": "v4.0.0",
        "ok": True,
        "checkpoint_id": checkpoint_id,
        "checkpoint_dir": str(root),
        "files": selected,
        "invalid": invalid,
        "approval_token": token,
        "git_status": git_output(["status", "--short"]),
        "git_diff_stat": git_output(["diff", "--stat"])
    }

    (root / "checkpoint.json").write_text(json.dumps(state, indent=4))

    with open(SEED_ROLLBACK_STATE_FILE, "w") as file:
        json.dump({"latest": state}, file, indent=4)

    try:
        from seed_event_bus import emit_event
        emit_event("checkpoint_created", {"checkpoint_id": checkpoint_id, "files": selected}, source="rollback", risk="file_write")
    except Exception:
        pass

    return state


def restore_checkpoint(checkpoint_id, token):
    root = Path(SEED_CHECKPOINT_DIR) / checkpoint_id
    meta = root / "checkpoint.json"

    if not meta.exists():
        return {"ok": False, "error": "Checkpoint metadata not found."}

    data = json.loads(meta.read_text())

    if token != data.get("approval_token"):
        return {"ok": False, "error": "Invalid approval token."}

    restored = []
    for item in data.get("files", []):
        src = root / item
        dst = Path(item)
        if src.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            restored.append(item)

    try:
        from seed_event_bus import emit_event
        emit_event("checkpoint_restored", {"checkpoint_id": checkpoint_id, "files": restored}, source="rollback", risk="file_write")
    except Exception:
        pass

    return {
        "ok": True,
        "checkpoint_id": checkpoint_id,
        "restored": restored
    }


def checkpoint_status():
    base = Path(SEED_CHECKPOINT_DIR)
    checkpoints = []
    if base.exists():
        for meta in base.glob("*/checkpoint.json"):
            try:
                checkpoints.append(json.loads(meta.read_text()))
            except Exception:
                pass

    checkpoints = sorted(checkpoints, key=lambda x: x.get("created_at", ""))
    return {
        "ok": True,
        "version": "v4.0.0",
        "count": len(checkpoints),
        "latest": checkpoints[-1] if checkpoints else None,
        "items": checkpoints[-10:]
    }


def show_checkpoint_create():
    name = input("Checkpoint name: ").strip() or "manual"
    files_raw = input("Files comma-separated, blank=seed_*.py: ").strip()
    files = [x.strip() for x in files_raw.split(",") if x.strip()] if files_raw else None
    print(json.dumps(create_checkpoint(name, files), indent=4))


def show_checkpoint_status():
    print("\n=== SEED CHECKPOINTS ===")
    print(json.dumps(checkpoint_status(), indent=4))


def show_checkpoint_restore():
    checkpoint_id = input("Checkpoint id: ").strip()
    token = input("Approval token: ").strip()
    print(json.dumps(restore_checkpoint(checkpoint_id, token), indent=4))


if __name__ == "__main__":
    show_checkpoint_status()
