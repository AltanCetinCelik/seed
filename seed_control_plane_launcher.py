import json
import subprocess
import sys
import time
import webbrowser
from datetime import datetime
from pathlib import Path


try:
    from seed_config import (
        SEED_CONTROL_PLANE_HOST,
        SEED_CONTROL_PLANE_PORT,
        SEED_CONTROL_PLANE_URL,
        SEED_CONTROL_PLANE_STATE_FILE
    )
except Exception:
    SEED_CONTROL_PLANE_HOST = "127.0.0.1"
    SEED_CONTROL_PLANE_PORT = 8790
    SEED_CONTROL_PLANE_URL = "http://127.0.0.1:8790"
    SEED_CONTROL_PLANE_STATE_FILE = "seed_control_plane_state.json"


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def save_state(data):
    with open(SEED_CONTROL_PLANE_STATE_FILE, "w") as file:
        json.dump(data, file, indent=4)


def control_plane_status():
    state = {
        "created_at": now_timestamp(),
        "version": "v3.0.0",
        "url": SEED_CONTROL_PLANE_URL,
        "host": SEED_CONTROL_PLANE_HOST,
        "port": SEED_CONTROL_PLANE_PORT,
        "local_only": True,
        "read_only_default": True,
        "manual_start": True
    }
    save_state(state)
    return state


def start_control_plane_background(open_browser=True):
    process = subprocess.Popen(
        [sys.executable, "seed_control_plane_server.py"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True
    )

    state = control_plane_status()
    state["pid"] = process.pid
    state["started_at"] = now_timestamp()
    save_state(state)

    time.sleep(1)

    if open_browser:
        webbrowser.open(SEED_CONTROL_PLANE_URL)

    return state


def show_control_plane_status():
    print("\n=== SEED CONTROL PLANE STATUS ===")
    print(json.dumps(control_plane_status(), indent=4))


def show_control_plane_open():
    print("\n=== STARTING SEED CONTROL PLANE ===")
    state = start_control_plane_background(open_browser=True)
    print(json.dumps(state, indent=4))


def control_plane_context(user_prompt=""):
    return (
        "=== SEED v3.0 CONTROL PLANE ===\n"
        f"Local URL: {SEED_CONTROL_PLANE_URL}\n"
        "Local-only, read-only by default, no remote bind, no auto-execute.\n"
        "Use /control-plane-open to start the dashboard.\n"
    )


if __name__ == "__main__":
    show_control_plane_open()
