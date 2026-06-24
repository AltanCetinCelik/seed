import json
import subprocess
from datetime import datetime


try:
    from seed_config import SEED_V23_GATE_REPORT_FILE, V23_REQUIRED_MODULES
except Exception:
    SEED_V23_GATE_REPORT_FILE = "seed_v23_gate_report.json"
    V23_REQUIRED_MODULES = [
        "seed_semantic_memory.py",
        "seed_workflow_brain.py",
        "seed_intelligence_context.py",
        "seed_v23_intelligence_gate.py"
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


def run_v23_gate():
    module_checks = [compile_module(module) for module in V23_REQUIRED_MODULES]
    modules_ok = all(item["ok"] for item in module_checks)

    semantic_ok = False
    workflow_ok = False
    context_ok = False
    action_kernel_ok = False

    details = {}

    try:
        from seed_semantic_memory import add_semantic_memory, build_semantic_index, semantic_search
        add_semantic_memory("Seed v2.3.0 test memory: semantic recall should find action kernel and active voice information.", source="v23_gate")
        index = build_semantic_index(".")
        results = semantic_search("action kernel active voice", rebuild=False)
        semantic_ok = index.get("item_count", 0) > 0 and len(results) > 0
        details["semantic"] = {
            "item_count": index.get("item_count"),
            "result_count": len(results),
            "top": results[0] if results else None
        }
    except Exception as error:
        details["semantic_error"] = str(error)

    try:
        from seed_workflow_brain import build_workflow_plan
        plan = build_workflow_plan("open cockpit in browser")
        workflow_ok = plan.get("intent") in ["action", "browser_or_web"] and plan.get("action_candidate") == "open_cockpit"
        details["workflow"] = plan
    except Exception as error:
        details["workflow_error"] = str(error)

    try:
        from seed_intelligence_context import get_intelligence_context_for_prompt
        ctx = get_intelligence_context_for_prompt("what did we build for active voice")
        context_ok = "WORKFLOW BRAIN CONTEXT" in ctx or "SEMANTIC MEMORY CONTEXT" in ctx
        details["context_chars"] = len(ctx)
    except Exception as error:
        details["context_error"] = str(error)

    try:
        from seed_action_kernel import route_action_from_text
        action_id, args = route_action_from_text("open cockpit in browser")
        action_kernel_ok = action_id == "open_cockpit"
        details["action_kernel_route"] = {"action_id": action_id, "args": args}
    except Exception as error:
        details["action_kernel_error"] = str(error)

    ready = all([
        modules_ok,
        semantic_ok,
        workflow_ok,
        context_ok,
        action_kernel_ok
    ])

    report = {
        "created_at": now_timestamp(),
        "release": "Seed v2.3.0 — Real Intelligence Layer",
        "ready": ready,
        "modules_ok": modules_ok,
        "semantic_ok": semantic_ok,
        "workflow_ok": workflow_ok,
        "context_ok": context_ok,
        "action_kernel_ok": action_kernel_ok,
        "module_checks": module_checks,
        "details": details
    }

    with open(SEED_V23_GATE_REPORT_FILE, "w") as file:
        json.dump(report, file, indent=4)

    return report


def show_v23_gate():
    report = run_v23_gate()

    print("\n=== SEED v2.3.0 REAL INTELLIGENCE GATE ===")
    print(f"Ready: {report['ready']}")
    print(f"Modules OK: {report['modules_ok']}")
    print(f"Semantic memory OK: {report['semantic_ok']}")
    print(f"Workflow brain OK: {report['workflow_ok']}")
    print(f"Intelligence context OK: {report['context_ok']}")
    print(f"Action kernel route OK: {report['action_kernel_ok']}")

    print("\nModule checks:")
    for item in report["module_checks"]:
        status = "OK" if item["ok"] else "FAIL"
        print(f"- {status}: {item['module']}")
        if item["stderr"] and not item["ok"]:
            print(item["stderr"][:1200])

    sem = report.get("details", {}).get("semantic", {})
    if sem:
        print(f"\nSemantic index items: {sem.get('item_count')}")
        print(f"Semantic result count: {sem.get('result_count')}")


if __name__ == "__main__":
    show_v23_gate()
