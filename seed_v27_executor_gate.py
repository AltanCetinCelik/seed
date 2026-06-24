import json
import subprocess
from datetime import datetime


try:
    from seed_config import SEED_V27_GATE_REPORT_FILE, V27_REQUIRED_MODULES
except Exception:
    SEED_V27_GATE_REPORT_FILE = "seed_v27_gate_report.json"
    V27_REQUIRED_MODULES = [
        "seed_external_executor_bridge.py",
        "seed_repo_doctor.py",
        "seed_voice_upgrade_planner.py",
        "seed_v27_executor_gate.py"
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


def run_v27_gate():
    module_checks = [compile_module(module) for module in V27_REQUIRED_MODULES]
    modules_ok = all(item["ok"] for item in module_checks)

    executor_ok = False
    plan_ok = False
    repo_doctor_ok = False
    voice_plan_ok = False
    action_route_ok = False
    details = {}

    try:
        from seed_external_executor_bridge import detect_executors, create_executor_plan
        state = detect_executors()
        executor_ok = "python" in state.get("registry", {}) and "git" in state.get("registry", {})
        plan = create_executor_plan("v2.7 gate test: improve Seed voice safely without automatic edits")
        plan_ok = plan.get("ok") is True and plan.get("manual_only") is True
        details["executor_available"] = [k for k, v in state["registry"].items() if v["available"]]
        details["executor_plan"] = plan
    except Exception as error:
        details["executor_error"] = str(error)

    try:
        from seed_repo_doctor import run_repo_doctor
        report = run_repo_doctor()
        repo_doctor_ok = report.get("ok") is True
        details["repo_doctor_findings"] = report.get("findings", [])
    except Exception as error:
        details["repo_doctor_error"] = str(error)

    try:
        from seed_voice_upgrade_planner import build_voice_upgrade_plan
        voice = build_voice_upgrade_plan()
        voice_plan_ok = voice.get("ok") is True and len(voice.get("next_upgrades", [])) >= 4
        details["voice_recommended_next_patch"] = voice.get("recommended_next_patch")
    except Exception as error:
        details["voice_plan_error"] = str(error)

    try:
        from seed_action_kernel import route_action_from_text
        action_id, args = route_action_from_text("run repo doctor")
        action_route_ok = action_id in ["repo_doctor", "run_skill", None]
        details["action_route_probe"] = {"action_id": action_id, "args": args}
    except Exception as error:
        details["action_route_error"] = str(error)

    ready = all([modules_ok, executor_ok, plan_ok, repo_doctor_ok, voice_plan_ok, action_route_ok])

    report = {
        "created_at": now_timestamp(),
        "release": "Seed v2.7.0 — Executor Bridge + Repo Doctor + Voice Upgrade Planner",
        "ready": ready,
        "modules_ok": modules_ok,
        "executor_registry_ok": executor_ok,
        "executor_plan_ok": plan_ok,
        "repo_doctor_ok": repo_doctor_ok,
        "voice_upgrade_plan_ok": voice_plan_ok,
        "action_route_ok": action_route_ok,
        "module_checks": module_checks,
        "details": details
    }

    with open(SEED_V27_GATE_REPORT_FILE, "w") as file:
        json.dump(report, file, indent=4)

    return report


def show_v27_gate():
    report = run_v27_gate()

    print("\n=== SEED v2.7.0 EXECUTOR BRIDGE GATE ===")
    print(f"Ready: {report['ready']}")
    print(f"Modules OK: {report['modules_ok']}")
    print(f"Executor registry OK: {report['executor_registry_ok']}")
    print(f"Executor plan OK: {report['executor_plan_ok']}")
    print(f"Repo Doctor OK: {report['repo_doctor_ok']}")
    print(f"Voice upgrade plan OK: {report['voice_upgrade_plan_ok']}")
    print(f"Action route OK: {report['action_route_ok']}")

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
    show_v27_gate()
