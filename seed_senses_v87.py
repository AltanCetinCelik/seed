import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

SENSE_DIR = Path("seed_senses_v87")
SCREEN_DIR = SENSE_DIR / "screens"
CAMERA_DIR = SENSE_DIR / "camera"
STATE_FILE = Path("seed_senses_v87_state.json")

def now():
    return datetime.now().isoformat(timespec="seconds")

def ensure_dirs():
    SCREEN_DIR.mkdir(parents=True, exist_ok=True)
    CAMERA_DIR.mkdir(parents=True, exist_ok=True)

def tool(path):
    return shutil.which(path)

def capture_screen():
    ensure_dirs()
    out = SCREEN_DIR / f"screen_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    screencapture = tool("screencapture")
    if not screencapture:
        return {"ok": False, "error": "macOS screencapture not found"}
    proc = subprocess.run([screencapture, "-x", str(out)], capture_output=True, text=True, timeout=20)
    ok = proc.returncode == 0 and out.exists()
    row = {"created_at": now(), "version": "v87.0.0", "ok": ok, "file": str(out), "size": out.stat().st_size if out.exists() else 0, "stderr": proc.stderr[-500:]}
    STATE_FILE.write_text(json.dumps(row, indent=4, ensure_ascii=False))
    return row

def capture_camera():
    ensure_dirs()
    out = CAMERA_DIR / f"camera_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    imagesnap = tool("imagesnap")
    if not imagesnap:
        return {"ok": False, "error": "imagesnap not installed. Install later if User wants real webcam capture.", "camera_available": False}
    proc = subprocess.run([imagesnap, str(out)], capture_output=True, text=True, timeout=30)
    ok = proc.returncode == 0 and out.exists()
    return {"created_at": now(), "version": "v87.0.0", "ok": ok, "file": str(out), "size": out.stat().st_size if out.exists() else 0, "stderr": proc.stderr[-500:], "camera_available": True}

def sense_status():
    ensure_dirs()
    return {
        "created_at": now(),
        "version": "v87.0.0",
        "ok": True,
        "screen_capture_available": bool(tool("screencapture")),
        "camera_available": bool(tool("imagesnap")),
        "latest_screen": str(max(SCREEN_DIR.glob("*.png"), key=lambda p: p.stat().st_mtime)) if list(SCREEN_DIR.glob("*.png")) else None,
        "latest_camera": str(max(CAMERA_DIR.glob("*"), key=lambda p: p.stat().st_mtime)) if list(CAMERA_DIR.glob("*")) else None,
        "note": "Screen seeing captures what is on the Mac. Actual vision analysis can be added later.",
    }

def show_senses():
    print("\n=== SEED v87 SENSES ===")
    print(json.dumps(sense_status(), indent=4, ensure_ascii=False))

if __name__ == "__main__":
    show_senses()
