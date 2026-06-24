import json
import subprocess
from datetime import datetime


try:
    from seed_config import (
        SEED_CONTROL_ACTION_HISTORY_FILE,
        SEED_CONTROL_ACTION_HEADER_NAME,
        SEED_CONTROL_ACTION_HEADER_VALUE
    )
except Exception:
    SEED_CONTROL_ACTION_HISTORY_FILE = "seed_control_action_history.jsonl"
    SEED_CONTROL_ACTION_HEADER_NAME = "X-Seed-Action"
    SEED_CONTROL_ACTION_HEADER_VALUE = "local-control-plane"


ALLOWLIST = {
    "v50-check": {
        "kind": "subprocess",
        "command": ["python", "seed_v50_operator_gate.py"],
        "risk": "diagnostic"
    },
    "operator-status": {
        "kind": "python",
        "module": "seed_operator_runtime",
        "function": "operator_status",
        "risk": "read_only"
    },
    "operator-tick": {
        "kind": "python",
        "module": "seed_operator_runtime",
        "function": "operator_tick",
        "risk": "diagnostic"
    },
    "capability-graph": {
        "kind": "python",
        "module": "seed_capability_graph",
        "function": "build_capability_graph",
        "risk": "read_only"
    },
    "v40-check": {
        "kind": "subprocess",
        "command": ["python", "seed_v40_os_gate.py"],
        "risk": "diagnostic"
    },
    "runtime-health-workflow": {
        "kind": "python",
        "module": "seed_workflow_automation",
        "function": "run_workflow",
        "risk": "diagnostic"
    },
    "mcp-client-self-test": {
        "kind": "python",
        "module": "seed_mcp_client",
        "function": "mcp_client_self_test",
        "risk": "read_only"
    },
    "memory-distill": {
        "kind": "python",
        "module": "seed_memory_distiller",
        "function": "build_memory_distill",
        "risk": "read_only"
    },
    "v36-check": {
        "kind": "subprocess",
        "command": ["python", "seed_v36_integration_gate.py"],
        "risk": "diagnostic"
    },
    "mcp-manifest": {
        "kind": "python",
        "module": "seed_mcp_skill_manifest",
        "function": "build_mcp_manifest",
        "risk": "read_only"
    },
    "mcp-self-test": {
        "kind": "python",
        "module": "seed_mcp_skill_server",
        "function": "self_test",
        "risk": "read_only"
    },
    "gate-matrix": {
        "kind": "subprocess",
        "command": ["python", "seed_gate_matrix.py"],
        "risk": "diagnostic"
    },
    "release-orchestrate": {
        "kind": "subprocess",
        "command": ["python", "seed_release_orchestrator.py"],
        "risk": "diagnostic"
    },
    "v35-check": {
        "kind": "subprocess",
        "command": ["python", "seed_v35_omega_gate.py"],
        "risk": "diagnostic"
    },
    "repo-dna": {
        "kind": "python",
        "module": "seed_repo_dna_engine",
        "function": "build_repo_dna",
        "risk": "read_only"
    },
    "integration-fusion": {
        "kind": "python",
        "module": "seed_integration_fusion_engine",
        "function": "build_integration_fusion",
        "risk": "read_only"
    },
    "omega-plan": {
        "kind": "python",
        "module": "seed_omega_planner",
        "function": "build_omega_plan",
        "risk": "read_only"
    },
    "self-repair": {
        "kind": "python",
        "module": "seed_self_repair_planner",
        "function": "build_self_repair_plan",
        "risk": "read_only"
    }
}


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def append_history(item):
    with open(SEED_CONTROL_ACTION_HISTORY_FILE, "a") as file:
        file.write(json.dumps(item) + "\n")


def run_allowed_action(action_id):
    if action_id not in ALLOWLIST:
        result = {
            "ok": False,
            "error": f"Action not allowlisted: {action_id}",
            "action_id": action_id
        }
        append_history({**result, "created_at": now_timestamp()})
        return result

    spec = ALLOWLIST[action_id]

    try:
        if spec["kind"] == "subprocess":
            proc = subprocess.run(
                spec["command"],
                capture_output=True,
                text=True,
                timeout=90
            )
            result = {
                "ok": proc.returncode == 0,
                "action_id": action_id,
                "risk": spec["risk"],
                "returncode": proc.returncode,
                "stdout_tail": proc.stdout[-5000:],
                "stderr_tail": proc.stderr[-3000:]
            }
        else:
            module = __import__(spec["module"], fromlist=[spec["function"]])
            fn = getattr(module, spec["function"])
            if action_id == "runtime-health-workflow":
                data = fn("runtime-health")
            else:
                data = fn()
            result = {
                "ok": True,
                "action_id": action_id,
                "risk": spec["risk"],
                "data": data
            }
    except Exception as error:
        result = {
            "ok": False,
            "action_id": action_id,
            "risk": spec.get("risk"),
            "error": str(error)
        }

    append_history({
        "created_at": now_timestamp(),
        "action_id": action_id,
        "ok": result.get("ok"),
        "risk": result.get("risk")
    })

    return result


def validate_action_header(headers):
    try:
        return headers.get(SEED_CONTROL_ACTION_HEADER_NAME) == SEED_CONTROL_ACTION_HEADER_VALUE
    except Exception:
        return False


def action_catalog():
    return {
        "ok": True,
        "version": "v3.5.0",
        "header_required": {
            "name": SEED_CONTROL_ACTION_HEADER_NAME,
            "value": SEED_CONTROL_ACTION_HEADER_VALUE
        },
        "actions": ALLOWLIST,
        "policy": {
            "allowlist_only": True,
            "no_arbitrary_shell": True,
            "no_delete": True,
            "no_auto_commit": True,
            "local_only": True
        }
    }


def show_control_action():
    print(json.dumps(action_catalog(), indent=4))
    action_id = input("Action id: ").strip()
    print(json.dumps(run_allowed_action(action_id), indent=4))


if __name__ == "__main__":
    show_control_action()
