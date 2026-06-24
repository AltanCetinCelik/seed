import hashlib
import json
from datetime import datetime
from pathlib import Path


try:
    from seed_config import SEED_GOAL_ENGINE_STATE_FILE
except Exception:
    SEED_GOAL_ENGINE_STATE_FILE = "seed_goal_engine_state.json"


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def make_goal_id(goal_text):
    return hashlib.sha256((goal_text + now_timestamp()).encode()).hexdigest()[:10]


def classify_goal(goal_text):
    lowered = goal_text.lower()
    tags = []

    if "voice" in lowered:
        tags.append("voice")
    if "aider" in lowered or "code" in lowered or "patch" in lowered:
        tags.append("coding")
    if "mcp" in lowered or "tool" in lowered:
        tags.append("mcp")
    if "repo" in lowered or "friend" in lowered or "integration" in lowered:
        tags.append("integration")
    if "dashboard" in lowered or "control plane" in lowered or "ui" in lowered:
        tags.append("ui")
    if "memory" in lowered:
        tags.append("memory")

    return tags or ["general"]


def plan_goal(goal_text):
    goal_id = make_goal_id(goal_text)
    tags = classify_goal(goal_text)

    actions = [
        {
            "title": "Create rollback checkpoint before goal work",
            "kind": "operator_action",
            "action_id": "checkpoint_create",
            "priority": 10,
            "notes": "Protect files before work starts."
        },
        {
            "title": "Run runtime health workflow",
            "kind": "operator_action",
            "action_id": "workflow_runtime_health",
            "priority": 9,
            "notes": "Verify v4 runtime before executing goal."
        },
        {
            "title": "Run gate matrix baseline",
            "kind": "operator_action",
            "action_id": "gate_matrix",
            "priority": 8,
            "notes": "Confirm release state before changes."
        }
    ]

    if "integration" in tags or "repo" in tags:
        actions.append({
            "title": "Refresh Repo DNA and integration fusion",
            "kind": "operator_action",
            "action_id": "integration_fusion",
            "priority": 8
        })

    if "voice" in tags:
        actions.append({
            "title": "Prepare Aider dry-run for voice context improvement",
            "kind": "aider_patch_flow",
            "action_id": "aider_patch_flow_dry_run",
            "priority": 8,
            "target_files": ["seed_fast_voice_context.py", "seed_voice_ux_pack.py"],
            "notes": "Dry-run first. No real edit yet."
        })

    if "coding" in tags:
        actions.append({
            "title": "Prepare supervised Aider patch flow",
            "kind": "aider_patch_flow",
            "action_id": "aider_patch_flow_dry_run",
            "priority": 7,
            "target_files": ["seed_fast_voice_context.py"],
            "notes": "One-file dry-run first."
        })

    if "mcp" in tags:
        actions.append({
            "title": "Run MCP client self-test",
            "kind": "operator_action",
            "action_id": "mcp_client_self_test",
            "priority": 8
        })

    if "memory" in tags:
        actions.append({
            "title": "Build memory distill",
            "kind": "operator_action",
            "action_id": "memory_distill",
            "priority": 7
        })

    if "ui" in tags:
        actions.append({
            "title": "Start Control Plane service",
            "kind": "operator_action",
            "action_id": "service_start_control_plane",
            "priority": 6
        })

    actions.append({
        "title": "Run release orchestrator after goal work",
        "kind": "operator_action",
        "action_id": "release_orchestrate",
        "priority": 5
    })

    goal = {
        "created_at": now_timestamp(),
        "version": "v5.0.0",
        "goal_id": goal_id,
        "goal": goal_text,
        "tags": tags,
        "actions": actions,
        "status": "planned"
    }

    with open(SEED_GOAL_ENGINE_STATE_FILE, "w") as file:
        json.dump(goal, file, indent=4)

    try:
        from seed_task_os import create_goal_task_set
        created = create_goal_task_set(goal_id, goal_text, actions)
        goal["created_tasks"] = created
        with open(SEED_GOAL_ENGINE_STATE_FILE, "w") as file:
            json.dump(goal, file, indent=4)
    except Exception as error:
        goal["task_creation_error"] = str(error)

    try:
        from seed_event_bus import emit_event
        emit_event("goal_planned", {"goal_id": goal_id, "tags": tags}, source="goal_engine", risk="file_write")
    except Exception:
        pass

    return goal


def show_goal_plan():
    goal = input("Goal: ").strip()
    print(json.dumps(plan_goal(goal), indent=4))


if __name__ == "__main__":
    show_goal_plan()
