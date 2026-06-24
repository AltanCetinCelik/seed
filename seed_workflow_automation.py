import json
import subprocess
from datetime import datetime


try:
    from seed_config import SEED_WORKFLOW_AUTOMATION_STATE_FILE
except Exception:
    SEED_WORKFLOW_AUTOMATION_STATE_FILE = "seed_workflow_automation_state.json"


WORKFLOWS = {
    "release-baseline": [
        {"kind": "python", "module": "seed_patch_rollback", "function": "create_checkpoint", "args": ["release-baseline", None]},
        {"kind": "subprocess", "command": ["python", "seed_v40_os_gate.py"]},
        {"kind": "subprocess", "command": ["python", "seed_v36_integration_gate.py"]},
        {"kind": "subprocess", "command": ["python", "seed_release_orchestrator.py"]}
    ],
    "runtime-health": [
        {"kind": "python", "module": "seed_service_manager", "function": "service_status", "args": []},
        {"kind": "python", "module": "seed_mcp_client", "function": "mcp_client_self_test", "args": []},
        {"kind": "python", "module": "seed_memory_distiller", "function": "build_memory_distill", "args": []}
    ],
    "integration-status": [
        {"kind": "python", "module": "seed_repo_dna_engine", "function": "build_repo_dna", "args": []},
        {"kind": "python", "module": "seed_integration_fusion_engine", "function": "build_integration_fusion", "args": []},
        {"kind": "python", "module": "seed_omega_planner", "function": "build_omega_plan", "args": []}
    ]
}


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def run_step(step):
    if step["kind"] == "subprocess":
        result = subprocess.run(step["command"], capture_output=True, text=True, timeout=120)
        return {
            "ok": result.returncode == 0,
            "kind": "subprocess",
            "command": " ".join(step["command"]),
            "returncode": result.returncode,
            "stdout_tail": result.stdout[-3000:],
            "stderr_tail": result.stderr[-2000:]
        }

    if step["kind"] == "python":
        module = __import__(step["module"], fromlist=[step["function"]])
        fn = getattr(module, step["function"])
        args = step.get("args", [])
        if args is None:
            args = []
        data = fn(*args)
        return {
            "ok": bool(data.get("ok", True)) if isinstance(data, dict) else True,
            "kind": "python",
            "module": step["module"],
            "function": step["function"],
            "data": data
        }

    return {"ok": False, "error": "Unknown step kind"}


def run_workflow(workflow_id):
    if workflow_id not in WORKFLOWS:
        return {"ok": False, "error": f"Unknown workflow: {workflow_id}", "available": list(WORKFLOWS)}

    results = []
    for step in WORKFLOWS[workflow_id]:
        try:
            result = run_step(step)
        except Exception as error:
            result = {"ok": False, "error": str(error), "step": step}
        results.append(result)

        if not result.get("ok"):
            break

    report = {
        "created_at": now_timestamp(),
        "version": "v4.0.0",
        "workflow_id": workflow_id,
        "ok": all(item.get("ok") for item in results),
        "steps": results
    }

    with open(SEED_WORKFLOW_AUTOMATION_STATE_FILE, "w") as file:
        json.dump(report, file, indent=4)

    try:
        from seed_event_bus import emit_event
        emit_event("workflow_run", {"workflow_id": workflow_id, "ok": report["ok"]}, source="workflow", risk="diagnostic")
    except Exception:
        pass

    return report


def workflow_status():
    return {
        "ok": True,
        "version": "v4.0.0",
        "available": list(WORKFLOWS.keys())
    }


def show_workflows():
    print("\n=== SEED WORKFLOWS ===")
    print(json.dumps(workflow_status(), indent=4))


def show_workflow_run():
    workflow_id = input("Workflow id: ").strip()
    print(json.dumps(run_workflow(workflow_id), indent=4))


if __name__ == "__main__":
    show_workflows()
