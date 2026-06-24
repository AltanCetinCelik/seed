import json
import subprocess
from datetime import datetime


try:
    from seed_config import SEED_V26_GATE_REPORT_FILE, V26_REQUIRED_MODULES
except Exception:
    SEED_V26_GATE_REPORT_FILE = "seed_v26_gate_report.json"
    V26_REQUIRED_MODULES = [
        "seed_agent_run_lifecycle.py",
        "seed_agent_operator_console.py",
        "seed_v26_agent_gate.py"
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


def run_v26_gate():
    module_checks = [compile_module(module) for module in V26_REQUIRED_MODULES]
    modules_ok = all(item["ok"] for item in module_checks)

    lifecycle_ok = False
    approval_ok = False
    execution_guard_ok = False
    operator_ok = False
    details = {}

    try:
        from seed_agent_run_lifecycle import (
            create_agent_run,
            approve_agent_run,
            execute_supervised_agent_run,
            list_agent_runs,
            detect_agent_tools
        )

        created = create_agent_run("v2.6 gate test: inspect repo safely with supervised agent lifecycle")
        lifecycle_ok = created.get("ok") is True and created.get("approval_token")

        blocked = execute_supervised_agent_run(created["run_id"])
        execution_guard_ok = blocked.get("ok") is False and "not approved" in blocked.get("error", "").lower()

        approved = approve_agent_run(created["run_id"], created["approval_token"])
        executed = execute_supervised_agent_run(created["run_id"])
        approval_ok = approved.get("ok") is True and executed.get("ok") is True

        details["created_run"] = created
        details["blocked_before_approval"] = blocked
        details["approved"] = approved
        details["executed_after_approval"] = {
            "ok": executed.get("ok"),
            "status": executed.get("status"),
            "external_agent_locked": executed.get("external_agent_locked")
        }
        details["runs_count"] = list_agent_runs().get("count")
        details["detected_tools"] = detect_agent_tools()
    except Exception as error:
        details["lifecycle_error"] = str(error)

    try:
        from seed_agent_operator_console import agent_operator_home
        home = agent_operator_home()
        operator_ok = home.get("ok") is True and "commands" in home
        details["operator_home"] = home
    except Exception as error:
        details["operator_error"] = str(error)

    ready = all([modules_ok, lifecycle_ok, approval_ok, execution_guard_ok, operator_ok])

    report = {
        "created_at": now_timestamp(),
        "release": "Seed v2.6.0 — Supervised Agent Execution Layer",
        "ready": ready,
        "modules_ok": modules_ok,
        "lifecycle_ok": lifecycle_ok,
        "approval_ok": approval_ok,
        "execution_guard_ok": execution_guard_ok,
        "operator_ok": operator_ok,
        "module_checks": module_checks,
        "details": details
    }

    with open(SEED_V26_GATE_REPORT_FILE, "w") as file:
        json.dump(report, file, indent=4)

    return report


def show_v26_gate():
    report = run_v26_gate()

    print("\n=== SEED v2.6.0 SUPERVISED AGENT EXECUTION GATE ===")
    print(f"Ready: {report['ready']}")
    print(f"Modules OK: {report['modules_ok']}")
    print(f"Lifecycle OK: {report['lifecycle_ok']}")
    print(f"Approval OK: {report['approval_ok']}")
    print(f"Execution guard OK: {report['execution_guard_ok']}")
    print(f"Operator OK: {report['operator_ok']}")

    print("\nModule checks:")
    for item in report["module_checks"]:
        status = "OK" if item["ok"] else "FAIL"
        print(f"- {status}: {item['module']}")
        if item["stderr"] and not item["ok"]:
            print(item["stderr"][:1200])

    created = report.get("details", {}).get("created_run", {})
    if created:
        print(f"\nCreated test run: {created.get('run_id')}")
        print(f"Approval token: {created.get('approval_token')}")


if __name__ == "__main__":
    show_v26_gate()
