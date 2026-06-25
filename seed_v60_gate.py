import json
import subprocess
from datetime import datetime


MODULES = [
    "seed_model_manager_v60.py",
    "seed_hermes_moltbot_fusion_v60.py",
    "seed_memory_auto_extractor_v60.py",
    "seed_presence_rituals_v60.py",
    "seed_command_palette_v60.py",
    "seed_aider_self_improvement_v60.py",
    "seed_natural_intent_router_v60.py",
    "seed_control_plane_ui_v60.py",
    "seed_v60_systems.py",
    "seed_v60_gate.py",
    "seed_v60_commands.py",
]


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def compile_module(module):
    proc = subprocess.run(["python", "-m", "py_compile", module], capture_output=True, text=True)
    return {"module": module, "ok": proc.returncode == 0, "stderr": proc.stderr[-2000:]}


def run_v60_gate():
    checks = [compile_module(m) for m in MODULES]
    modules_ok = all(c["ok"] for c in checks)
    details = {}

    try:
        from seed_v60_systems import build_v60_state
        state = build_v60_state()
        systems_ok = state.get("ok") is True and len(state.get("cards", [])) >= 8
        details["v60_state"] = {"ok": state.get("ok"), "cards": len(state.get("cards", []))}
    except Exception as error:
        systems_ok = False
        details["v60_state_error"] = str(error)

    try:
        from seed_control_plane_server import api_payload
        v60 = api_payload("/api/v60")
        control_plane_ok = bool(v60)
        details["control_plane"] = {"v60_api": bool(v60)}
    except Exception as error:
        control_plane_ok = False
        details["control_plane_error"] = str(error)

    try:
        from seed_v50_gate import run_v50_gate
        v50 = run_v50_gate()
        v50_ok = v50.get("ready") is True
        details["v50"] = {"ready": v50.get("ready")}
    except Exception as error:
        v50_ok = False
        details["v50_error"] = str(error)

    ready = modules_ok and systems_ok and control_plane_ok and v50_ok

    report = {
        "created_at": now_timestamp(),
        "version": "v60.0.0",
        "release": "Seed v60.0.0 — Real Intelligence + Natural UX Fusion",
        "ready": ready,
        "modules_ok": modules_ok,
        "systems_ok": systems_ok,
        "control_plane_ok": control_plane_ok,
        "v50_ok": v50_ok,
        "module_checks": checks,
        "details": details,
    }

    with open("seed_v60_gate_report.json", "w") as file:
        json.dump(report, file, indent=4)

    return report


def show_v60_gate():
    report = run_v60_gate()
    print("\n=== SEED v60 REAL INTELLIGENCE + UX FUSION GATE ===")
    print(f"Ready: {report['ready']}")
    print(f"Modules OK: {report['modules_ok']}")
    print(f"Systems OK: {report['systems_ok']}")
    print(f"Control Plane OK: {report['control_plane_ok']}")
    print(f"v50 OK: {report['v50_ok']}")
    print("\nDetails:")
    for key, value in report["details"].items():
        print(f"- {key}: {value}")


if __name__ == "__main__":
    show_v60_gate()
