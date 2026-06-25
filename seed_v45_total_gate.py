import json
import subprocess
from datetime import datetime


MODULES = [
    "seed_task_hygiene_v302.py",
    "seed_aider_cockpit_v31.py",
    "seed_memory_brain_max_v32.py",
    "seed_workflow_runtime_v33.py",
    "seed_mcp_marketplace_max_v34.py",
    "seed_browser_executor_v35.py",
    "seed_voice_runtime_max_v36.py",
    "seed_heavy_agent_sandbox_v37.py",
    "seed_agent_hq_ui_model_v38.py",
    "seed_presence_max_v39.py",
    "seed_eval_lab_v40.py",
    "seed_terminal_pro.py",
    "seed_desktop_packaging_v42.py",
    "seed_multidevice_hub_max_v43.py",
    "seed_world_ui_v44.py",
    "seed_self_improvement_loop_v45.py",
    "seed_control_plane_ui_v45.py",
    "seed_v45_total_systems.py",
    "seed_v45_total_gate.py",
    "seed_v45_commands.py"
]


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def compile_module(module):
    proc = subprocess.run(["python", "-m", "py_compile", module], capture_output=True, text=True)
    return {"module": module, "ok": proc.returncode == 0, "stderr": proc.stderr[-2000:]}


def run_v45_gate():
    checks = [compile_module(m) for m in MODULES]
    modules_ok = all(c["ok"] for c in checks)
    details = {}

    try:
        from seed_v45_total_systems import build_v45_state
        state = build_v45_state()
        systems_ok = state.get("ok") is True and len(state.get("cards", [])) >= 14
        details["systems"] = {"ok": state.get("ok"), "cards": len(state.get("cards", []))}
    except Exception as error:
        systems_ok = False
        details["systems_error"] = str(error)

    try:
        from seed_control_plane_server import api_payload
        v45 = api_payload("/api/v45")
        control_plane_ok = bool(v45)
        details["control_plane"] = {"v45_api": bool(v45)}
    except Exception as error:
        control_plane_ok = False
        details["control_plane_error"] = str(error)

    try:
        from seed_task_hygiene_v302 import task_stats
        stats = task_stats()
        hygiene_ok = stats.get("ok") is True
        details["task_hygiene"] = stats
    except Exception as error:
        hygiene_ok = False
        details["hygiene_error"] = str(error)

    ready = modules_ok and systems_ok and control_plane_ok and hygiene_ok

    report = {
        "created_at": now_timestamp(),
        "version": "v45.0.0",
        "release": "Seed v45.0.0 — Total Systems Implementation MegaPatch",
        "ready": ready,
        "modules_ok": modules_ok,
        "systems_ok": systems_ok,
        "control_plane_ok": control_plane_ok,
        "hygiene_ok": hygiene_ok,
        "module_checks": checks,
        "details": details
    }

    with open("seed_v45_total_gate.json", "w") as file:
        json.dump(report, file, indent=4)

    return report


def show_v45_gate():
    report = run_v45_gate()
    print("\n=== SEED v45 TOTAL SYSTEMS GATE ===")
    print(f"Ready: {report['ready']}")
    print(f"Modules OK: {report['modules_ok']}")
    print(f"Systems OK: {report['systems_ok']}")
    print(f"Control Plane OK: {report['control_plane_ok']}")
    print(f"Hygiene OK: {report['hygiene_ok']}")
    print("\nDetails:")
    for key, value in report["details"].items():
        print(f"- {key}: {value}")


if __name__ == "__main__":
    show_v45_gate()
