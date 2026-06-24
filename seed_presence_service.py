import json
import os
import signal
import subprocess
import sys
from datetime import datetime
from pathlib import Path


PID_FILE = Path("seed_presence_daemon.pid")
LOG_FILE = Path("seed_presence_daemon.log")


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def is_running(pid):
    try:
        os.kill(pid, 0)
        return True
    except Exception:
        return False


def service_status():
    pid = None
    running = False

    if PID_FILE.exists():
        try:
            pid = int(PID_FILE.read_text().strip())
            running = is_running(pid)
        except Exception:
            pid = None

    return {
        "created_at": now_timestamp(),
        "version": "v20.3.0",
        "pid": pid,
        "running": running,
        "pid_file": str(PID_FILE),
        "log_file": str(LOG_FILE)
    }


def start_service(interval=300):
    status = service_status()
    if status["running"]:
        return {**status, "started": False, "note": "Presence daemon already running."}

    log = open(LOG_FILE, "a")
    proc = subprocess.Popen(
        [sys.executable, "seed_presence_daemon.py", "--interval", str(interval)],
        stdout=log,
        stderr=log,
        start_new_session=True
    )

    PID_FILE.write_text(str(proc.pid))

    return {
        "created_at": now_timestamp(),
        "version": "v20.3.0",
        "started": True,
        "pid": proc.pid,
        "running": True,
        "log_file": str(LOG_FILE)
    }


def stop_service():
    status = service_status()
    pid = status.get("pid")

    if not pid or not status.get("running"):
        return {**status, "stopped": False, "note": "Presence daemon not running."}

    os.kill(pid, signal.SIGTERM)

    try:
        PID_FILE.unlink()
    except Exception:
        pass

    return {
        "created_at": now_timestamp(),
        "version": "v20.3.0",
        "stopped": True,
        "pid": pid,
        "running": False
    }


def show_presence_service():
    print("\n=== SEED PRESENCE SERVICE ===")
    print(json.dumps(service_status(), indent=4))


if __name__ == "__main__":
    show_presence_service()
