import json
import os
import signal
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


try:
    from seed_config import SEED_SERVICE_MANAGER_STATE_FILE
except Exception:
    SEED_SERVICE_MANAGER_STATE_FILE = "seed_service_manager_state.json"


SERVICES = {
    "control-plane": {
        "command": [sys.executable, "seed_control_plane_server.py"],
        "url": "http://127.0.0.1:8790",
        "risk": "local_control",
        "description": "Local Seed Control Plane web UI."
    }
}


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def load_state():
    path = Path(SEED_SERVICE_MANAGER_STATE_FILE)
    if not path.exists():
        return {"version": "v4.0.0", "services": {}}
    try:
        return json.loads(path.read_text())
    except Exception:
        return {"version": "v4.0.0", "services": {}}


def save_state(state):
    state["updated_at"] = now_timestamp()
    with open(SEED_SERVICE_MANAGER_STATE_FILE, "w") as file:
        json.dump(state, file, indent=4)
    return state


def pid_alive(pid):
    if not pid:
        return False
    try:
        os.kill(int(pid), 0)
        return True
    except Exception:
        return False


def service_status():
    state = load_state()
    services = {}

    for service_id, spec in SERVICES.items():
        saved = state.get("services", {}).get(service_id, {})
        pid = saved.get("pid")
        services[service_id] = {
            "service_id": service_id,
            "description": spec["description"],
            "url": spec.get("url"),
            "risk": spec["risk"],
            "pid": pid,
            "running": pid_alive(pid),
            "started_at": saved.get("started_at")
        }

    return {
        "ok": True,
        "version": "v4.0.0",
        "services": services
    }


def start_service(service_id):
    if service_id not in SERVICES:
        return {"ok": False, "error": f"Unknown service: {service_id}"}

    current = service_status()["services"][service_id]
    if current["running"]:
        return {"ok": True, "already_running": True, "service": current}

    spec = SERVICES[service_id]
    proc = subprocess.Popen(
        spec["command"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True
    )

    state = load_state()
    state.setdefault("services", {})[service_id] = {
        "pid": proc.pid,
        "started_at": now_timestamp(),
        "command": spec["command"]
    }
    save_state(state)

    try:
        from seed_event_bus import emit_event
        emit_event("service_started", {"service_id": service_id, "pid": proc.pid}, source="service_manager", risk=spec["risk"])
    except Exception:
        pass

    time.sleep(0.7)
    return {"ok": True, "service": service_status()["services"][service_id]}


def stop_service(service_id):
    if service_id not in SERVICES:
        return {"ok": False, "error": f"Unknown service: {service_id}"}

    state = load_state()
    saved = state.get("services", {}).get(service_id, {})
    pid = saved.get("pid")

    if not pid_alive(pid):
        return {"ok": True, "already_stopped": True}

    try:
        os.killpg(os.getpgid(int(pid)), signal.SIGTERM)
    except Exception:
        try:
            os.kill(int(pid), signal.SIGTERM)
        except Exception as error:
            return {"ok": False, "error": str(error)}

    try:
        from seed_event_bus import emit_event
        emit_event("service_stopped", {"service_id": service_id, "pid": pid}, source="service_manager", risk="local_control")
    except Exception:
        pass

    return {"ok": True, "service_id": service_id, "stopped_pid": pid}


def show_service_status():
    print("\n=== SEED SERVICE MANAGER ===")
    print(json.dumps(service_status(), indent=4))


def show_service_start():
    service_id = input("Service id [control-plane]: ").strip() or "control-plane"
    print(json.dumps(start_service(service_id), indent=4))


def show_service_stop():
    service_id = input("Service id [control-plane]: ").strip() or "control-plane"
    print(json.dumps(stop_service(service_id), indent=4))


if __name__ == "__main__":
    show_service_status()
