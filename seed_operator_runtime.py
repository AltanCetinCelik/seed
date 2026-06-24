import json
from datetime import datetime


try:
    from seed_config import SEED_OPERATOR_RUNTIME_STATE_FILE
except Exception:
    SEED_OPERATOR_RUNTIME_STATE_FILE = "seed_operator_runtime_state.json"


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def run_operator_action(action_id, task=None):
    from seed_execution_policy import evaluate_action

    policy = evaluate_action(action_id)

    if not policy.get("allowed"):
        return {
            "ok": False,
            "action_id": action_id,
            "policy": policy,
            "error": "Policy blocked action."
        }

    if action_id == "gate_matrix":
        from seed_gate_matrix import run_gate_matrix
        data = run_gate_matrix()
    elif action_id == "release_orchestrate":
        from seed_release_orchestrator import run_release_orchestrator
        data = run_release_orchestrator()
    elif action_id == "v40_check":
        from seed_v40_os_gate import run_v40_gate
        data = run_v40_gate()
    elif action_id == "v36_check":
        from seed_v36_integration_gate import run_v36_gate
        data = run_v36_gate()
    elif action_id == "integration_fusion":
        from seed_integration_fusion_engine import build_integration_fusion
        data = build_integration_fusion()
    elif action_id == "repo_dna":
        from seed_repo_dna_engine import build_repo_dna
        data = build_repo_dna()
    elif action_id == "omega_plan":
        from seed_omega_planner import build_omega_plan
        data = build_omega_plan()
    elif action_id == "memory_distill":
        from seed_memory_distiller import build_memory_distill
        data = build_memory_distill()
    elif action_id == "mcp_client_self_test":
        from seed_mcp_client import mcp_client_self_test
        data = mcp_client_self_test()
    elif action_id == "checkpoint_create":
        from seed_patch_rollback import create_checkpoint
        data = create_checkpoint("operator-task-checkpoint", task.get("target_files") if task else None)
    elif action_id == "workflow_runtime_health":
        from seed_workflow_automation import run_workflow
        data = run_workflow("runtime-health")
    elif action_id == "service_start_control_plane":
        from seed_service_manager import start_service
        data = start_service("control-plane")
    elif action_id == "aider_patch_flow_dry_run":
        from seed_aider_patch_flow import create_patch_flow
        target_files = task.get("target_files") or ["seed_fast_voice_context.py"]
        data = create_patch_flow(task.get("title", "Operator Aider dry-run"), target_files, mode="dry_run")
    else:
        return {
            "ok": False,
            "action_id": action_id,
            "policy": policy,
            "error": "No operator handler for this action."
        }

    return {
        "ok": bool(data.get("ok", True)) if isinstance(data, dict) else True,
        "action_id": action_id,
        "policy": policy,
        "data": data
    }


def operator_status():
    from seed_task_os import list_tasks
    from seed_event_bus import event_bus_status
    from seed_capability_graph import build_capability_graph
    from seed_execution_policy import build_policy_manifest

    tasks = list_tasks(limit=100)
    ready = [task for task in tasks["tasks"] if task.get("status") == "ready"]

    status = {
        "created_at": now_timestamp(),
        "version": "v5.0.0",
        "ok": True,
        "manual_tick_only": True,
        "ready_task_count": len(ready),
        "total_task_count": tasks["count"],
        "next_task": ready[0] if ready else None,
        "event_bus": event_bus_status(),
        "capability_graph": {
            "node_count": build_capability_graph().get("node_count"),
            "edge_count": build_capability_graph().get("edge_count")
        },
        "policy": {
            "no_arbitrary_shell": build_policy_manifest().get("no_arbitrary_shell"),
            "no_auto_commit": build_policy_manifest().get("no_auto_commit")
        }
    }

    with open(SEED_OPERATOR_RUNTIME_STATE_FILE, "w") as file:
        json.dump(status, file, indent=4)

    return status


def operator_tick():
    from seed_task_os import next_ready_task, update_task_status

    task = next_ready_task()

    if not task:
        result = {
            "created_at": now_timestamp(),
            "version": "v5.0.0",
            "ok": True,
            "message": "No ready tasks."
        }
        with open(SEED_OPERATOR_RUNTIME_STATE_FILE, "w") as file:
            json.dump(result, file, indent=4)
        return result

    update_task_status(task["id"], "running", "Operator tick started.")
    result = run_operator_action(task.get("action_id"), task=task)

    if result.get("ok"):
        update_task_status(task["id"], "done", "Operator tick completed.")
        final_status = "done"
    else:
        update_task_status(task["id"], "failed", result.get("error"))
        final_status = "failed"

    output = {
        "created_at": now_timestamp(),
        "version": "v5.0.0",
        "ok": result.get("ok"),
        "task": task,
        "task_final_status": final_status,
        "result": result
    }

    with open(SEED_OPERATOR_RUNTIME_STATE_FILE, "w") as file:
        json.dump(output, file, indent=4)

    try:
        from seed_event_bus import emit_event
        emit_event("operator_tick", {"task_id": task["id"], "ok": output["ok"]}, source="operator_runtime", risk="diagnostic")
    except Exception:
        pass

    return output


def show_operator_status():
    print("\n=== SEED OPERATOR RUNTIME ===")
    print(json.dumps(operator_status(), indent=4))


def show_operator_tick():
    print("\n=== SEED OPERATOR TICK ===")
    print(json.dumps(operator_tick(), indent=4))


if __name__ == "__main__":
    show_operator_status()
