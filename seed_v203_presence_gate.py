import json
import subprocess
from datetime import datetime


MODULES = [
    "seed_notification_queue.py",
    "seed_interrupt_policy.py",
    "seed_curiosity_engine.py",
    "seed_presence.py",
    "seed_presence_daemon.py",
    "seed_presence_service.py",
    "seed_presence_commands.py",
    "seed_commands.py",
    "seed_cli.py",
    "seed_control_plane_server.py",
    "seed_control_plane_ui_v20.py"
]


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def compile_module(module):
    proc = subprocess.run(["python", "-m", "py_compile", module], capture_output=True, text=True)
    return {
        "module": module,
        "ok": proc.returncode == 0,
        "stderr": proc.stderr[-2000:]
    }


def run_v203_gate():
    checks = [compile_module(m) for m in MODULES]
    modules_ok = all(c["ok"] for c in checks)
    details = {}

    try:
        from seed_presence import evaluate_presence_once
        tick = evaluate_presence_once(force=True)
        presence_ok = bool(tick.get("should_speak") is True and tick.get("message"))
        details["presence_tick"] = {
            "should_speak": tick.get("should_speak"),
            "reason": tick.get("reason"),
            "message": tick.get("message")
        }
    except Exception as error:
        presence_ok = False
        details["presence_error"] = str(error)

    try:
        from seed_notification_queue import read_notifications
        pending = read_notifications(limit=20, status="pending")
        queue_ok = len(pending) >= 1
        details["pending_notifications"] = len(pending)
    except Exception as error:
        queue_ok = False
        details["queue_error"] = str(error)

    try:
        from seed_curiosity_engine import collect_curiosity_context, detect_curiosity_triggers
        context = collect_curiosity_context()
        triggers = detect_curiosity_triggers(context)
        curiosity_ok = len(triggers) >= 3
        details["curiosity_triggers"] = len(triggers)
    except Exception as error:
        curiosity_ok = False
        details["curiosity_error"] = str(error)

    try:
        from seed_presence_service import service_status
        service = service_status()
        service_ok = "running" in service
        details["service"] = service
    except Exception as error:
        service_ok = False
        details["service_error"] = str(error)

    try:
        from seed_control_plane_server import api_payload, render_home
        presence = api_payload("/api/presence")
        html = render_home()
        control_plane_ok = "Seed Presence Runtime" in html and bool(presence)
        details["control_plane"] = {
            "presence_api": bool(presence),
            "html_has_presence": "Seed Presence Runtime" in html
        }
    except Exception as error:
        control_plane_ok = False
        details["control_plane_error"] = str(error)

    ready = all([modules_ok, presence_ok, queue_ok, curiosity_ok, service_ok, control_plane_ok])

    report = {
        "created_at": now_timestamp(),
        "release": "Seed v20.3.0 — Presence Runtime + Curiosity Loop",
        "ready": ready,
        "modules_ok": modules_ok,
        "presence_ok": presence_ok,
        "queue_ok": queue_ok,
        "curiosity_ok": curiosity_ok,
        "service_ok": service_ok,
        "control_plane_ok": control_plane_ok,
        "module_checks": checks,
        "details": details
    }

    with open("seed_v203_presence_gate.json", "w") as file:
        json.dump(report, file, indent=4)

    return report


def show_v203_gate():
    report = run_v203_gate()
    print("\n=== SEED v20.3 PRESENCE RUNTIME GATE ===")
    print(f"Ready: {report['ready']}")
    print(f"Modules OK: {report['modules_ok']}")
    print(f"Presence OK: {report['presence_ok']}")
    print(f"Queue OK: {report['queue_ok']}")
    print(f"Curiosity OK: {report['curiosity_ok']}")
    print(f"Service OK: {report['service_ok']}")
    print(f"Control Plane OK: {report['control_plane_ok']}")

    print("\nDetails:")
    for key, value in report["details"].items():
        print(f"- {key}: {value}")


if __name__ == "__main__":
    show_v203_gate()
