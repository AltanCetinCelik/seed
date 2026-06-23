import json
import subprocess
from datetime import datetime

try:
    from seed_config import SEED_INTEGRATION_GATE_REPORT_FILE, V119_REQUIRED_MODULES
except Exception:
    SEED_INTEGRATION_GATE_REPORT_FILE = "seed_integration_gate_report.json"
    V119_REQUIRED_MODULES = [
        "seed_friend_advice_registry.py",
        "seed_repo_arsenal.py",
        "seed_tool_router.py",
        "seed_capability_planner.py",
        "seed_integration_gate.py",
        "seed_arsenal_commands.py"
    ]

try:
    from seed_repo_arsenal import integration_readiness_data, get_repo_arsenal
    ARSENAL_AVAILABLE = True
except Exception:
    ARSENAL_AVAILABLE = False

try:
    from seed_tool_router import route_task
    ROUTER_AVAILABLE = True
except Exception:
    ROUTER_AVAILABLE = False

try:
    from seed_friend_advice_registry import friend_advice_data
    FRIEND_AVAILABLE = True
except Exception:
    FRIEND_AVAILABLE = False

try:
    from seed_companion_os import append_companion_os_event, append_companion_os_journal
    COMPANION_OS_AVAILABLE = True
except Exception:
    COMPANION_OS_AVAILABLE = False


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def compile_module(module):
    result = subprocess.run(
        ["python", "-m", "py_compile", module],
        capture_output=True,
        text=True
    )
    return {
        "module": module,
        "ok": result.returncode == 0,
        "returncode": result.returncode,
        "stdout": result.stdout[-1000:],
        "stderr": result.stderr[-3000:]
    }


def run_integration_gate():
    module_checks = [compile_module(module) for module in V119_REQUIRED_MODULES]
    modules_ok = all(item["ok"] for item in module_checks)

    arsenal = integration_readiness_data() if ARSENAL_AVAILABLE else {"ready": False, "error": "arsenal unavailable"}
    friend = friend_advice_data() if FRIEND_AVAILABLE else {"items": []}

    router_tests = []
    samples = [
        "Fix a Python bug in Seed and run tests",
        "Use a browser to research a webpage",
        "Upgrade memory with vector search",
        "Add push-to-talk local voice",
        "Create avatar cockpit UI",
        "Add guardrails and observability"
    ]

    if ROUTER_AVAILABLE:
        for sample in samples:
            router_tests.append(route_task(sample))

    router_ok = ROUTER_AVAILABLE and len(router_tests) == len(samples)
    friend_ok = FRIEND_AVAILABLE and len(friend.get("items", [])) >= 3
    arsenal_ok = ARSENAL_AVAILABLE and arsenal.get("ready") is True

    approval_gates_ok = True
    if ARSENAL_AVAILABLE:
        for repo in get_repo_arsenal():
            risky = repo.get("risk") not in ["diagnostic", "local_audio_output", "read_only"]
            if risky and repo.get("approval_required") is not True:
                approval_gates_ok = False

    ready = modules_ok and arsenal_ok and router_ok and friend_ok and approval_gates_ok

    report = {
        "created_at": now_timestamp(),
        "ready": ready,
        "modules_ok": modules_ok,
        "arsenal_ok": arsenal_ok,
        "router_ok": router_ok,
        "friend_advice_ok": friend_ok,
        "approval_gates_ok": approval_gates_ok,
        "module_checks": module_checks,
        "arsenal": arsenal,
        "router_tests": router_tests,
        "friend_advice_count": len(friend.get("items", [])),
        "meaning": "Seed can map repos/tools, route capabilities, and keep risky tools approval-gated before v2.0.0."
    }

    with open(SEED_INTEGRATION_GATE_REPORT_FILE, "w") as file:
        json.dump(report, file, indent=4)

    if COMPANION_OS_AVAILABLE:
        try:
            append_companion_os_event(
                "arsenal_integration_gate_run",
                "Arsenal integration gate run",
                {
                    "ready": ready,
                    "modules_ok": modules_ok,
                    "arsenal_ok": arsenal_ok,
                    "router_ok": router_ok,
                    "approval_gates_ok": approval_gates_ok
                },
                source="integration_gate",
                importance=5
            )
            append_companion_os_journal(
                "Seed v1.19 Arsenal Integration Gate",
                json.dumps({
                    "ready": ready,
                    "arsenal_ok": arsenal_ok,
                    "router_ok": router_ok,
                    "approval_gates_ok": approval_gates_ok
                }, indent=2)
            )
        except Exception:
            pass

    return report


def show_integration_gate():
    report = run_integration_gate()

    print("\n=== SEED v1.19 ARSENAL INTEGRATION GATE ===")
    print(f"Ready: {report['ready']}")
    print(f"Modules OK: {report['modules_ok']}")
    print(f"Arsenal OK: {report['arsenal_ok']}")
    print(f"Router OK: {report['router_ok']}")
    print(f"Friend advice OK: {report['friend_advice_ok']}")
    print(f"Approval gates OK: {report['approval_gates_ok']}")

    print("\nModule checks:")
    for item in report["module_checks"]:
        status = "OK" if item["ok"] else "FAIL"
        print(f"- {status}: {item['module']}")
        if item["stderr"] and not item["ok"]:
            print(item["stderr"][:1000])

    print("\nRouter samples:")
    for item in report["router_tests"]:
        print(f"- {item.get('task')} => {item.get('best_capability')} | tools={', '.join(item.get('recommended_tools', []))}")


def get_integration_gate_context_for_prompt():
    try:
        report = run_integration_gate()
    except Exception as error:
        return f"=== INTEGRATION GATE CONTEXT ===\nUnavailable: {error}\n"

    text = "=== INTEGRATION GATE CONTEXT ===\n"
    text += f"Ready: {report.get('ready')}\n"
    text += f"Arsenal OK: {report.get('arsenal_ok')}\n"
    text += f"Router OK: {report.get('router_ok')}\n"
    text += f"Approval gates OK: {report.get('approval_gates_ok')}\n"
    return text


if __name__ == "__main__":
    show_integration_gate()
