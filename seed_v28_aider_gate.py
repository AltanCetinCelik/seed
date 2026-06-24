import json
import subprocess
from datetime import datetime


try:
    from seed_config import SEED_V28_GATE_REPORT_FILE, V28_REQUIRED_MODULES
except Exception:
    SEED_V28_GATE_REPORT_FILE = "seed_v28_gate_report.json"
    V28_REQUIRED_MODULES = [
        "seed_aider_bridge.py",
        "seed_v28_aider_gate.py"
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


def run_v28_gate():
    module_checks = [compile_module(module) for module in V28_REQUIRED_MODULES]
    modules_ok = all(item["ok"] for item in module_checks)

    detect_ok = False
    install_plan_ok = False
    preflight_ok = False
    plan_ok = False
    context_ok = False
    details = {}

    try:
        from seed_aider_bridge import (
            detect_aider,
            aider_install_plan,
            aider_preflight,
            create_aider_plan,
            aider_bridge_context
        )

        detect = detect_aider()
        detect_ok = "aider_available" in detect and "policy" in detect

        install_plan = aider_install_plan()
        install_plan_ok = len(install_plan.get("recommended_methods", [])) >= 2

        preflight = aider_preflight(
            "Improve Seed voice safely without automatic edits",
            [
                "seed_active_voice_daemon.py",
                "seed_voice_command_bridge.py",
                "seed_fast_voice_context.py"
            ]
        )
        preflight_ok = preflight.get("can_plan") is True and preflight.get("can_execute") is False

        plan = create_aider_plan(
            "v2.8 gate test: prepare Aider plan for Seed voice improvements",
            [
                "seed_active_voice_daemon.py",
                "seed_voice_command_bridge.py",
                "seed_fast_voice_context.py"
            ]
        )
        plan_ok = plan.get("ok") is True and plan.get("manual_only") is True and len(plan.get("valid_target_files", [])) >= 1

        ctx = aider_bridge_context("aider plan")
        context_ok = "AIDER" in ctx.upper() and "locked" in ctx.lower()

        details["detect"] = detect
        details["install_plan_methods"] = [x["method"] for x in install_plan.get("recommended_methods", [])]
        details["preflight"] = {
            "ok": preflight.get("ok"),
            "aider_available": preflight.get("aider_available"),
            "can_plan": preflight.get("can_plan"),
            "can_execute": preflight.get("can_execute")
        }
        details["plan"] = plan
    except Exception as error:
        details["aider_error"] = str(error)

    ready = all([modules_ok, detect_ok, install_plan_ok, preflight_ok, plan_ok, context_ok])

    report = {
        "created_at": now_timestamp(),
        "release": "Seed v2.8.0 — Aider First Executor Bridge",
        "ready": ready,
        "modules_ok": modules_ok,
        "detect_ok": detect_ok,
        "install_plan_ok": install_plan_ok,
        "preflight_ok": preflight_ok,
        "aider_plan_ok": plan_ok,
        "context_ok": context_ok,
        "module_checks": module_checks,
        "details": details
    }

    with open(SEED_V28_GATE_REPORT_FILE, "w") as file:
        json.dump(report, file, indent=4)

    return report


def show_v28_gate():
    report = run_v28_gate()

    print("\n=== SEED v2.8.0 AIDER FIRST EXECUTOR BRIDGE GATE ===")
    print(f"Ready: {report['ready']}")
    print(f"Modules OK: {report['modules_ok']}")
    print(f"Detect OK: {report['detect_ok']}")
    print(f"Install plan OK: {report['install_plan_ok']}")
    print(f"Preflight OK: {report['preflight_ok']}")
    print(f"Aider plan OK: {report['aider_plan_ok']}")
    print(f"Context OK: {report['context_ok']}")

    print("\nModule checks:")
    for item in report["module_checks"]:
        status = "OK" if item["ok"] else "FAIL"
        print(f"- {status}: {item['module']}")
        if item["stderr"] and not item["ok"]:
            print(item["stderr"][:1200])

    print("\nDetails:")
    details = report.get("details", {})
    print(f"- aider available: {details.get('detect', {}).get('aider_available')}")
    print(f"- install methods: {details.get('install_plan_methods')}")
    print(f"- plan: {details.get('plan')}")


if __name__ == "__main__":
    show_v28_gate()
