import json
import subprocess
from datetime import datetime


try:
    from seed_config import SEED_V30_GATE_REPORT_FILE, V30_REQUIRED_MODULES
except Exception:
    SEED_V30_GATE_REPORT_FILE = "seed_v30_gate_report.json"
    V30_REQUIRED_MODULES = [
        "seed_gate_matrix.py",
        "seed_runtime_supervisor.py",
        "seed_session_timeline.py",
        "seed_command_center.py",
        "seed_control_plane_ui.py",
        "seed_control_plane_server.py",
        "seed_control_plane_launcher.py",
        "seed_v30_control_gate.py"
    ]


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def compile_module(module):
    result = subprocess.run(["python", "-m", "py_compile", module], capture_output=True, text=True)
    return {
        "module": module,
        "ok": result.returncode == 0,
        "stderr": result.stderr[-3000:]
    }


def run_v30_gate():
    module_checks = [compile_module(module) for module in V30_REQUIRED_MODULES]
    modules_ok = all(item["ok"] for item in module_checks)

    gate_matrix_ok = False
    runtime_ok = False
    timeline_ok = False
    command_center_ok = False
    control_plane_ok = False
    launcher_ok = False
    details = {}

    try:
        from seed_gate_matrix import gate_matrix_context
        ctx = gate_matrix_context()
        gate_matrix_ok = "GATE MATRIX" in ctx
        details["gate_matrix_context_chars"] = len(ctx)
    except Exception as error:
        details["gate_matrix_error"] = str(error)

    try:
        from seed_runtime_supervisor import runtime_supervisor_snapshot
        snap = runtime_supervisor_snapshot()
        runtime_ok = "tools" in snap and "files" in snap
        details["runtime_ok"] = snap.get("ok")
    except Exception as error:
        details["runtime_error"] = str(error)

    try:
        from seed_session_timeline import build_session_timeline
        timeline = build_session_timeline(limit=20)
        timeline_ok = timeline.get("ok") is True and "items" in timeline
        details["timeline_count"] = timeline.get("count")
    except Exception as error:
        details["timeline_error"] = str(error)

    try:
        from seed_command_center import build_command_center
        center = build_command_center()
        command_center_ok = center.get("ok") is True and center.get("total_commands", 0) >= 30
        details["total_commands"] = center.get("total_commands")
    except Exception as error:
        details["command_center_error"] = str(error)

    try:
        from seed_control_plane_server import render_home, api_payload
        html = render_home()
        payload = api_payload("/api/status")
        control_plane_ok = "Seed Control Plane" in html and isinstance(payload, dict)
        details["control_plane_html_chars"] = len(html)
    except Exception as error:
        details["control_plane_error"] = str(error)

    try:
        from seed_control_plane_launcher import control_plane_status
        state = control_plane_status()
        launcher_ok = state.get("local_only") is True and "url" in state
        details["control_plane_url"] = state.get("url")
    except Exception as error:
        details["launcher_error"] = str(error)

    ready = all([
        modules_ok,
        gate_matrix_ok,
        runtime_ok,
        timeline_ok,
        command_center_ok,
        control_plane_ok,
        launcher_ok
    ])

    report = {
        "created_at": now_timestamp(),
        "release": "Seed v3.0.0 — Jarvis Control Plane + Local Command Center",
        "ready": ready,
        "modules_ok": modules_ok,
        "gate_matrix_ok": gate_matrix_ok,
        "runtime_supervisor_ok": runtime_ok,
        "timeline_ok": timeline_ok,
        "command_center_ok": command_center_ok,
        "control_plane_ok": control_plane_ok,
        "launcher_ok": launcher_ok,
        "module_checks": module_checks,
        "details": details
    }

    with open(SEED_V30_GATE_REPORT_FILE, "w") as file:
        json.dump(report, file, indent=4)

    return report


def show_v30_gate():
    report = run_v30_gate()

    print("\n=== SEED v3.0.0 JARVIS CONTROL PLANE GATE ===")
    print(f"Ready: {report['ready']}")
    print(f"Modules OK: {report['modules_ok']}")
    print(f"Gate Matrix OK: {report['gate_matrix_ok']}")
    print(f"Runtime Supervisor OK: {report['runtime_supervisor_ok']}")
    print(f"Timeline OK: {report['timeline_ok']}")
    print(f"Command Center OK: {report['command_center_ok']}")
    print(f"Control Plane OK: {report['control_plane_ok']}")
    print(f"Launcher OK: {report['launcher_ok']}")

    print("\nModule checks:")
    for item in report["module_checks"]:
        status = "OK" if item["ok"] else "FAIL"
        print(f"- {status}: {item['module']}")
        if item["stderr"] and not item["ok"]:
            print(item["stderr"][:1200])

    print("\nDetails:")
    for key, value in report.get("details", {}).items():
        print(f"- {key}: {value}")


if __name__ == "__main__":
    show_v30_gate()
