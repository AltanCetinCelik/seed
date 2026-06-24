import json
import subprocess
from datetime import datetime


try:
    from seed_config import SEED_V50_GATE_REPORT_FILE, V50_REQUIRED_MODULES
except Exception:
    SEED_V50_GATE_REPORT_FILE = "seed_v50_gate_report.json"
    V50_REQUIRED_MODULES = [
        "seed_execution_policy.py",
        "seed_capability_graph.py",
        "seed_task_os.py",
        "seed_goal_engine.py",
        "seed_operator_inbox.py",
        "seed_operator_runtime.py",
        "seed_control_plane_ui_v5.py",
        "seed_v50_operator_gate.py"
    ]


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def compile_module(module):
    result = subprocess.run(["python", "-m", "py_compile", module], capture_output=True, text=True)
    return {"module": module, "ok": result.returncode == 0, "stderr": result.stderr[-2500:]}


def run_v50_gate():
    module_checks = [compile_module(module) for module in V50_REQUIRED_MODULES]
    modules_ok = all(x["ok"] for x in module_checks)
    details = {}

    try:
        from seed_execution_policy import build_policy_manifest, evaluate_action
        policy = build_policy_manifest()
        eval_result = evaluate_action("aider_patch_flow_real")
        policy_ok = policy.get("ok") is True and eval_result.get("approval_required") is True
        details["policy"] = {"no_shell": policy.get("no_arbitrary_shell"), "real_aider_approval": eval_result.get("approval_required")}
    except Exception as error:
        policy_ok = False
        details["policy_error"] = str(error)

    try:
        from seed_capability_graph import build_capability_graph, route_intent
        graph = build_capability_graph()
        route = route_intent("improve voice with aider")
        capability_ok = graph.get("node_count", 0) > 10 and route.get("intent") in ["voice", "coding"]
        details["capability_graph"] = {"nodes": graph.get("node_count"), "edges": graph.get("edge_count"), "route": route}
    except Exception as error:
        capability_ok = False
        details["capability_error"] = str(error)

    try:
        from seed_goal_engine import plan_goal
        goal = plan_goal("Improve Seed voice and Aider patch flow safely")
        goal_ok = goal.get("goal_id") and len(goal.get("created_tasks", [])) >= 4
        details["goal"] = {"goal_id": goal.get("goal_id"), "tasks": len(goal.get("created_tasks", []))}
    except Exception as error:
        goal_ok = False
        details["goal_error"] = str(error)

    try:
        from seed_task_os import list_tasks, next_ready_task
        tasks = list_tasks(limit=100)
        task_ok = tasks.get("count", 0) >= 1 and next_ready_task() is not None
        details["tasks"] = {"count": tasks.get("count"), "next": next_ready_task()}
    except Exception as error:
        task_ok = False
        details["task_error"] = str(error)

    try:
        from seed_operator_inbox import capture_inbox_item, read_inbox
        capture_inbox_item("v5 gate inbox probe", source="v50_gate", kind="probe")
        inbox_ok = len(read_inbox(limit=10)) >= 1
        details["inbox_count"] = len(read_inbox(limit=10))
    except Exception as error:
        inbox_ok = False
        details["inbox_error"] = str(error)

    try:
        from seed_operator_runtime import operator_status
        status = operator_status()
        runtime_ok = status.get("ok") is True and status.get("manual_tick_only") is True
        details["operator"] = {"ready": status.get("ready_task_count"), "total": status.get("total_task_count")}
    except Exception as error:
        runtime_ok = False
        details["runtime_error"] = str(error)

    try:
        from seed_control_plane_server import render_home, api_payload
        html = render_home()
        bundle = api_payload("/api/home-bundle")
        ui_ok = "Seed v5 Operator Core" in html and "operator" in bundle
        details["control_plane"] = {"html_chars": len(html), "has_operator_bundle": "operator" in bundle}
    except Exception as error:
        ui_ok = False
        details["ui_error"] = str(error)

    ready = all([modules_ok, policy_ok, capability_ok, goal_ok, task_ok, inbox_ok, runtime_ok, ui_ok])

    report = {
        "created_at": now_timestamp(),
        "release": "Seed v5.0.0 — Autonomous Operator Core",
        "ready": ready,
        "modules_ok": modules_ok,
        "policy_ok": policy_ok,
        "capability_graph_ok": capability_ok,
        "goal_engine_ok": goal_ok,
        "task_os_ok": task_ok,
        "operator_inbox_ok": inbox_ok,
        "operator_runtime_ok": runtime_ok,
        "control_plane_v5_ok": ui_ok,
        "module_checks": module_checks,
        "details": details
    }

    with open(SEED_V50_GATE_REPORT_FILE, "w") as file:
        json.dump(report, file, indent=4)

    return report


def show_v50_gate():
    report = run_v50_gate()

    print("\n=== SEED v5.0.0 AUTONOMOUS OPERATOR CORE GATE ===")
    print(f"Ready: {report['ready']}")
    print(f"Modules OK: {report['modules_ok']}")
    print(f"Policy OK: {report['policy_ok']}")
    print(f"Capability Graph OK: {report['capability_graph_ok']}")
    print(f"Goal Engine OK: {report['goal_engine_ok']}")
    print(f"Task OS OK: {report['task_os_ok']}")
    print(f"Operator Inbox OK: {report['operator_inbox_ok']}")
    print(f"Operator Runtime OK: {report['operator_runtime_ok']}")
    print(f"Control Plane v5 OK: {report['control_plane_v5_ok']}")

    print("\nModule checks:")
    for item in report["module_checks"]:
        status = "OK" if item["ok"] else "FAIL"
        print(f"- {status}: {item['module']}")
        if item["stderr"] and not item["ok"]:
            print(item["stderr"][:1000])


if __name__ == "__main__":
    show_v50_gate()
