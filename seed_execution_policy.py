import json
from datetime import datetime


try:
    from seed_config import SEED_EXECUTION_POLICY_FILE
except Exception:
    SEED_EXECUTION_POLICY_FILE = "seed_execution_policy.json"


RISK_LEVELS = {
    "read_only": {
        "allowed": True,
        "approval_required": False,
        "description": "Reads local state only."
    },
    "diagnostic": {
        "allowed": True,
        "approval_required": False,
        "description": "Runs allowlisted diagnostics/gates."
    },
    "file_write": {
        "allowed": True,
        "approval_required": True,
        "description": "Writes local project state/checkpoints/plans."
    },
    "aider_dry_run": {
        "allowed": True,
        "approval_required": True,
        "description": "Runs Aider dry-run only with target files."
    },
    "aider_real": {
        "allowed": True,
        "approval_required": True,
        "description": "Can edit target files. Requires exact real-run phrase."
    },
    "service_control": {
        "allowed": True,
        "approval_required": False,
        "description": "Start/stop allowlisted local Seed services."
    },
    "external_browser": {
        "allowed": False,
        "approval_required": True,
        "description": "Blocked unless a future browser sandbox handles it."
    },
    "arbitrary_shell": {
        "allowed": False,
        "approval_required": True,
        "description": "Never allowed through Operator Core."
    },
    "delete": {
        "allowed": False,
        "approval_required": True,
        "description": "Delete operations are blocked."
    },
    "auto_commit": {
        "allowed": False,
        "approval_required": True,
        "description": "Auto-commit is blocked."
    }
}


ACTION_POLICIES = {
    "gate_matrix": "diagnostic",
    "release_orchestrate": "diagnostic",
    "v40_check": "diagnostic",
    "v36_check": "diagnostic",
    "v35_check": "diagnostic",
    "repo_dna": "read_only",
    "integration_fusion": "read_only",
    "omega_plan": "read_only",
    "memory_distill": "read_only",
    "mcp_client_self_test": "read_only",
    "checkpoint_create": "file_write",
    "workflow_runtime_health": "diagnostic",
    "aider_patch_flow_dry_run": "aider_dry_run",
    "aider_patch_flow_real": "aider_real",
    "service_start_control_plane": "service_control",
    "service_stop_control_plane": "service_control"
}


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def evaluate_action(action_id, requested_risk=None):
    risk = requested_risk or ACTION_POLICIES.get(action_id, "read_only")
    policy = RISK_LEVELS.get(risk, {
        "allowed": False,
        "approval_required": True,
        "description": "Unknown risk."
    })

    result = {
        "created_at": now_timestamp(),
        "version": "v5.0.0",
        "ok": True,
        "action_id": action_id,
        "risk": risk,
        "allowed": policy["allowed"],
        "approval_required": policy["approval_required"],
        "description": policy["description"],
        "blocked_reason": None if policy["allowed"] else "Policy blocks this action."
    }

    return result


def build_policy_manifest():
    data = {
        "created_at": now_timestamp(),
        "version": "v5.0.0",
        "ok": True,
        "manual_tick_only": True,
        "no_background_autonomy": True,
        "no_arbitrary_shell": True,
        "no_delete": True,
        "no_auto_commit": True,
        "risk_levels": RISK_LEVELS,
        "action_policies": ACTION_POLICIES
    }

    with open(SEED_EXECUTION_POLICY_FILE, "w") as file:
        json.dump(data, file, indent=4)

    return data


def show_policy():
    print("\n=== SEED EXECUTION POLICY ===")
    print(json.dumps(build_policy_manifest(), indent=4))


def show_policy_check():
    action_id = input("Action id: ").strip()
    print(json.dumps(evaluate_action(action_id), indent=4))


if __name__ == "__main__":
    show_policy()
