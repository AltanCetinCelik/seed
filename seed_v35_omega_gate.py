import json
import subprocess
from datetime import datetime


try:
    from seed_config import SEED_V35_GATE_REPORT_FILE, V35_REQUIRED_MODULES
except Exception:
    SEED_V35_GATE_REPORT_FILE = "seed_v35_gate_report.json"
    V35_REQUIRED_MODULES = [
        "seed_repo_dna_engine.py",
        "seed_integration_fusion_engine.py",
        "seed_omega_planner.py",
        "seed_control_plane_actions.py",
        "seed_voice_one_shot.py",
        "seed_control_plane_ui_omega.py",
        "seed_v35_omega_gate.py"
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


def run_v35_gate():
    module_checks = [compile_module(module) for module in V35_REQUIRED_MODULES]
    modules_ok = all(item["ok"] for item in module_checks)

    repo_dna_ok = False
    fusion_ok = False
    omega_ok = False
    actions_ok = False
    voice_one_shot_ok = False
    ui_ok = False
    server_ok = False
    details = {}

    try:
        from seed_repo_dna_engine import build_repo_dna
        dna = build_repo_dna()
        repo_dna_ok = dna.get("ok") is True and dna.get("python_file_count", 0) > 50
        details["repo_dna"] = {"python_files": dna.get("python_file_count"), "commands": dna.get("command_count")}
    except Exception as error:
        details["repo_dna_error"] = str(error)

    try:
        from seed_integration_fusion_engine import build_integration_fusion
        fusion = build_integration_fusion()
        fusion_ok = fusion.get("ok") is True and fusion.get("candidate_count", 0) >= 10
        details["top_integrations"] = [x.get("name") for x in fusion.get("top_10", [])[:5]]
    except Exception as error:
        details["fusion_error"] = str(error)

    try:
        from seed_omega_planner import build_omega_plan
        plan = build_omega_plan()
        omega_ok = plan.get("ok") is True and "waves" in plan
        details["next_big_build"] = plan.get("next_big_build")
    except Exception as error:
        details["omega_error"] = str(error)

    try:
        from seed_control_plane_actions import action_catalog, run_allowed_action
        catalog = action_catalog()
        result = run_allowed_action("repo-dna")
        actions_ok = catalog.get("ok") is True and result.get("ok") is True
        details["control_action_count"] = len(catalog.get("actions", {}))
    except Exception as error:
        details["actions_error"] = str(error)

    try:
        from seed_voice_one_shot import one_shot_response
        result = one_shot_response("open the control plane")
        voice_one_shot_ok = result.get("intent") == "control_plane" and result.get("executed") is False
        details["voice_one_shot"] = result
    except Exception as error:
        details["voice_one_shot_error"] = str(error)

    try:
        from seed_control_plane_ui_omega import render_control_plane_ui
        bundle = {
            "mission": {"health": {"test": True}, "next_actions": ["test action"]},
            "status": {"system": {"python": "test", "machine": "test", "platform": "test"}},
            "commands": {"groups": {"release": ["/v35-check"], "mission": ["/mission-control"], "agents": [], "aider": [], "voice": [], "skills": []}},
            "voice": {"no_secret_always_listening": True, "recent_transcripts": [], "next_voice_patch": []},
            "agents": {"runs": []},
            "aider": {"aider_available": False, "aider_command": None, "policy": {"execution_locked": True}},
            "apps": {"tools": {"python": {"available": True}}},
            "timeline": {"items": []},
            "integration_fusion": {"top_10": [], "candidate_count": 0},
            "omega_plan": {"waves": {}, "next_big_build": "test"},
            "repo_dna": {"python_file_count": 1, "command_count": 1},
            "control_actions": {"actions": {"repo-dna": {}}}
        }
        html = render_control_plane_ui(bundle)
        ui_ok = "Omega Integration" in html and "Seed Control" in html
        details["ui_chars"] = len(html)
    except Exception as error:
        details["ui_error"] = str(error)

    try:
        from seed_control_plane_server import render_home, api_payload
        html = render_home()
        bundle = api_payload("/api/home-bundle")
        server_ok = "Omega Integration" in html and isinstance(bundle, dict)
        details["server_html_chars"] = len(html)
    except Exception as error:
        details["server_error"] = str(error)

    ready = all([modules_ok, repo_dna_ok, fusion_ok, omega_ok, actions_ok, voice_one_shot_ok, ui_ok, server_ok])

    report = {
        "created_at": now_timestamp(),
        "release": "Seed v3.5.0 — Omega Integration Pack",
        "ready": ready,
        "modules_ok": modules_ok,
        "repo_dna_ok": repo_dna_ok,
        "fusion_ok": fusion_ok,
        "omega_plan_ok": omega_ok,
        "control_actions_ok": actions_ok,
        "voice_one_shot_ok": voice_one_shot_ok,
        "ui_ok": ui_ok,
        "server_ok": server_ok,
        "module_checks": module_checks,
        "details": details
    }

    with open(SEED_V35_GATE_REPORT_FILE, "w") as file:
        json.dump(report, file, indent=4)

    return report


def show_v35_gate():
    report = run_v35_gate()

    print("\n=== SEED v3.5.0 OMEGA INTEGRATION PACK GATE ===")
    print(f"Ready: {report['ready']}")
    print(f"Modules OK: {report['modules_ok']}")
    print(f"Repo DNA OK: {report['repo_dna_ok']}")
    print(f"Fusion OK: {report['fusion_ok']}")
    print(f"Omega Plan OK: {report['omega_plan_ok']}")
    print(f"Control Actions OK: {report['control_actions_ok']}")
    print(f"Voice One-Shot OK: {report['voice_one_shot_ok']}")
    print(f"UI OK: {report['ui_ok']}")
    print(f"Server OK: {report['server_ok']}")

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
    show_v35_gate()
