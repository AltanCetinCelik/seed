import json
import subprocess
from datetime import datetime


MODULES = [
    "seed_nothing_left_behind_v50.py",
    "seed_v50_commands.py",
    "seed_control_plane_ui_v50.py",
    "seed_v50_gate.py",
]


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def compile_module(module):
    proc = subprocess.run(["python", "-m", "py_compile", module], capture_output=True, text=True)
    return {
        "module": module,
        "ok": proc.returncode == 0,
        "stderr": proc.stderr[-2000:],
    }


def run_v50_gate():
    checks = [compile_module(m) for m in MODULES]
    modules_ok = all(c["ok"] for c in checks)

    details = {}

    try:
        from seed_nothing_left_behind_v50 import build_v50_state, dust_check
        state = build_v50_state()
        dust = dust_check()
        systems_ok = state.get("ok") is True
        dust_ok = dust.get("ok") is True
        details["v50_state"] = {
            "ok": state.get("ok"),
            "ledger_count": state.get("ledger", {}).get("count"),
            "commands": state.get("command_map", {}).get("total_commands"),
            "dust_ok": dust.get("ok"),
            "dust": dust.get("dust"),
        }
    except Exception as error:
        systems_ok = False
        dust_ok = False
        details["v50_state_error"] = str(error)

    try:
        from seed_control_plane_server import api_payload
        v50 = api_payload("/api/v50")
        control_plane_ok = bool(v50)
        details["control_plane"] = {"v50_api": bool(v50)}
    except Exception as error:
        control_plane_ok = False
        details["control_plane_error"] = str(error)

    try:
        from seed_v45_total_gate import run_v45_gate
        v45 = run_v45_gate()
        v45_ok = v45.get("ready") is True
        details["v45"] = {"ready": v45.get("ready")}
    except Exception as error:
        v45_ok = False
        details["v45_error"] = str(error)

    ready = modules_ok and systems_ok and dust_ok and control_plane_ok and v45_ok

    report = {
        "created_at": now_timestamp(),
        "version": "v50.0.0",
        "release": "Seed v50.0.0 — Nothing Left Behind Finalization Pack",
        "ready": ready,
        "modules_ok": modules_ok,
        "systems_ok": systems_ok,
        "dust_ok": dust_ok,
        "control_plane_ok": control_plane_ok,
        "v45_ok": v45_ok,
        "module_checks": checks,
        "details": details,
    }

    with open("seed_v50_gate_report.json", "w") as file:
        json.dump(report, file, indent=4)

    return report


def show_v50_gate():
    report = run_v50_gate()
    print("\n=== SEED v50 NOTHING LEFT BEHIND GATE ===")
    print(f"Ready: {report['ready']}")
    print(f"Modules OK: {report['modules_ok']}")
    print(f"Systems OK: {report['systems_ok']}")
    print(f"Dust OK: {report['dust_ok']}")
    print(f"Control Plane OK: {report['control_plane_ok']}")
    print(f"v45 OK: {report['v45_ok']}")
    print("\nDetails:")
    for key, value in report["details"].items():
        print(f"- {key}: {value}")


if __name__ == "__main__":
    show_v50_gate()
