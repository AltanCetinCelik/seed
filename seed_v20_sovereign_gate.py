import json
import subprocess
from datetime import datetime


try:
    from seed_config import SEED_V20_GATE_REPORT_FILE, V20_REQUIRED_MODULES
except Exception:
    SEED_V20_GATE_REPORT_FILE = "seed_v20_gate_report.json"
    V20_REQUIRED_MODULES = [
        "seed_memory_engine_v2.py",
        "seed_voice_runtime_v6.py",
        "seed_workflow_graph_v9.py",
        "seed_browser_sandbox_v10.py",
        "seed_mcp_marketplace_v11.py",
        "seed_openhands_sandbox_v12.py",
        "seed_project_life_os_v14.py",
        "seed_world_avatar_v16.py",
        "seed_agent_council_v17.py",
        "seed_self_improvement_lab_v18.py",
        "seed_multidevice_hub_v19.py",
        "seed_v20_sovereign_os.py",
        "seed_control_plane_ui_v20.py",
        "seed_v20_sovereign_gate.py"
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


def run_v20_gate():
    module_checks = [compile_module(module) for module in V20_REQUIRED_MODULES]
    modules_ok = all(item["ok"] for item in module_checks)
    details = {}

    try:
        from seed_v20_sovereign_os import build_v20_state
        state = build_v20_state()
        sovereign_ok = state.get("ok") is True and len(state.get("major_capabilities", [])) >= 12
        details["v20_state"] = {
            "ok": state.get("ok"),
            "capabilities": len(state.get("major_capabilities", [])),
            "modules": len(state.get("modules", {}))
        }
    except Exception as error:
        sovereign_ok = False
        details["v20_error"] = str(error)

    try:
        from seed_control_plane_server import render_home, api_payload
        html = render_home()
        bundle = api_payload("/api/home-bundle")
        control_plane_ok = "Seed v20 Sovereign Companion OS" in html and "v20" in bundle
        details["control_plane"] = {
            "html_chars": len(html),
            "has_v20_bundle": "v20" in bundle
        }
    except Exception as error:
        control_plane_ok = False
        details["control_plane_error"] = str(error)

    try:
        from seed_memory_engine_v2 import build_memory_v2
        from seed_voice_runtime_v6 import build_voice_runtime
        from seed_mcp_marketplace_v11 import build_mcp_marketplace
        subsystem_ok = all([
            build_memory_v2().get("ok"),
            build_voice_runtime().get("ok"),
            build_mcp_marketplace().get("ok")
        ])
    except Exception as error:
        subsystem_ok = False
        details["subsystem_error"] = str(error)

    ready = all([modules_ok, sovereign_ok, control_plane_ok, subsystem_ok])

    report = {
        "created_at": now_timestamp(),
        "release": "Seed v20.0.0 — Sovereign Companion OS MegaCore",
        "ready": ready,
        "modules_ok": modules_ok,
        "sovereign_os_ok": sovereign_ok,
        "control_plane_v20_ok": control_plane_ok,
        "subsystems_ok": subsystem_ok,
        "module_checks": module_checks,
        "details": details
    }

    with open(SEED_V20_GATE_REPORT_FILE, "w") as file:
        json.dump(report, file, indent=4)

    return report


def show_v20_gate():
    report = run_v20_gate()

    print("\n=== SEED v20.0.0 SOVEREIGN COMPANION OS GATE ===")
    print(f"Ready: {report['ready']}")
    print(f"Modules OK: {report['modules_ok']}")
    print(f"Sovereign OS OK: {report['sovereign_os_ok']}")
    print(f"Control Plane v20 OK: {report['control_plane_v20_ok']}")
    print(f"Subsystems OK: {report['subsystems_ok']}")

    print("\nModule checks:")
    for item in report["module_checks"]:
        status = "OK" if item["ok"] else "FAIL"
        print(f"- {status}: {item['module']}")
        if item["stderr"] and not item["ok"]:
            print(item["stderr"][:1000])


if __name__ == "__main__":
    show_v20_gate()
