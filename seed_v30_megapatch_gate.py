import json
import subprocess
from datetime import datetime


try:
    from seed_config import SEED_V30_GATE_REPORT_FILE, V30_REQUIRED_MODULES
except Exception:
    SEED_V30_GATE_REPORT_FILE = "seed_v30_megapatch_gate.json"
    V30_REQUIRED_MODULES = [
        "seed_external_adapter_registry.py",
        "seed_repo_pattern_extractor.py",
        "seed_repo_risk_scanner.py",
        "seed_repo_assimilation_engine.py",
        "seed_integration_scoreboard.py",
        "seed_repo_to_seed_planner.py",
        "seed_agent_hq_v30.py",
        "seed_control_plane_ui_v30.py",
        "seed_v30_megapatch_gate.py",
        "seed_v30_commands.py"
    ]


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def compile_module(module):
    proc = subprocess.run(["python", "-m", "py_compile", module], capture_output=True, text=True)
    return {"module": module, "ok": proc.returncode == 0, "stderr": proc.stderr[-2000:]}


def run_v30_gate():
    checks = [compile_module(m) for m in V30_REQUIRED_MODULES]
    modules_ok = all(x["ok"] for x in checks)
    details = {}

    try:
        from seed_external_adapter_registry import build_adapter_registry
        reg = build_adapter_registry()
        registry_ok = reg.get("ok") and len(reg.get("adapters", {})) >= 10
        details["registry"] = {"adapters": len(reg.get("adapters", {}))}
    except Exception as error:
        registry_ok = False
        details["registry_error"] = str(error)

    try:
        from seed_repo_assimilation_engine import build_repo_assimilation_report
        report = build_repo_assimilation_report()
        assimilation_ok = report.get("ok") is True
        details["assimilation"] = {"repo_count": report.get("repo_count")}
    except Exception as error:
        assimilation_ok = False
        details["assimilation_error"] = str(error)

    try:
        from seed_integration_scoreboard import build_integration_scoreboard
        board = build_integration_scoreboard()
        scoreboard_ok = board.get("ok") is True
        details["scoreboard"] = {"repo_count": board.get("repo_count"), "top": len(board.get("top_20", []))}
    except Exception as error:
        scoreboard_ok = False
        details["scoreboard_error"] = str(error)

    try:
        from seed_repo_to_seed_planner import build_repo_to_seed_plan
        plan = build_repo_to_seed_plan()
        planner_ok = plan.get("ok") is True
        details["planner"] = {"plans": len(plan.get("plans", []))}
    except Exception as error:
        planner_ok = False
        details["planner_error"] = str(error)

    try:
        from seed_agent_hq_v30 import build_agent_hq_fast
        hq = build_agent_hq_fast()
        hq_ok = hq.get("ok") is True and hq.get("agent_count", 0) >= 8
        details["agent_hq"] = {"agents": hq.get("agent_count"), "plans": len(hq.get("next_best_integrations", []))}
    except Exception as error:
        hq_ok = False
        details["agent_hq_error"] = str(error)

    try:
        from seed_control_plane_server import api_payload
        v30 = api_payload("/api/v30")
        control_plane_ok = bool(v30)
        details["control_plane"] = {"v30_api": bool(v30)}
    except Exception as error:
        control_plane_ok = False
        details["control_plane_error"] = str(error)

    ready = all([
        modules_ok,
        registry_ok,
        assimilation_ok,
        scoreboard_ok,
        planner_ok,
        hq_ok,
        control_plane_ok
    ])

    report = {
        "created_at": now_timestamp(),
        "release": "Seed v30.0.0 — Repo Assimilation + Agent HQ MegaPatch",
        "ready": ready,
        "modules_ok": modules_ok,
        "registry_ok": registry_ok,
        "assimilation_ok": assimilation_ok,
        "scoreboard_ok": scoreboard_ok,
        "planner_ok": planner_ok,
        "agent_hq_ok": hq_ok,
        "control_plane_ok": control_plane_ok,
        "module_checks": checks,
        "details": details
    }

    with open(SEED_V30_GATE_REPORT_FILE, "w") as file:
        json.dump(report, file, indent=4)

    return report


def show_v30_gate():
    report = run_v30_gate()
    print("\n=== SEED v30.0.0 REPO ASSIMILATION + AGENT HQ GATE ===")
    print(f"Ready: {report['ready']}")
    print(f"Modules OK: {report['modules_ok']}")
    print(f"Registry OK: {report['registry_ok']}")
    print(f"Assimilation OK: {report['assimilation_ok']}")
    print(f"Scoreboard OK: {report['scoreboard_ok']}")
    print(f"Planner OK: {report['planner_ok']}")
    print(f"Agent HQ OK: {report['agent_hq_ok']}")
    print(f"Control Plane OK: {report['control_plane_ok']}")

    print("\nDetails:")
    for key, value in report["details"].items():
        print(f"- {key}: {value}")

    print("\nModule checks:")
    for item in report["module_checks"]:
        status = "OK" if item["ok"] else "FAIL"
        print(f"- {status}: {item['module']}")
        if not item["ok"]:
            print(item["stderr"])


if __name__ == "__main__":
    show_v30_gate()
