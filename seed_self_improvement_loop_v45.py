import json
import uuid
from datetime import datetime
from pathlib import Path


LOOP_FILE = Path("seed_self_improvement_loop_v45.json")


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def create_self_improvement_loop(goal, target_files=None):
    target_files = target_files or []
    loop_id = uuid.uuid4().hex[:10]

    try:
        from seed_aider_cockpit_v31 import create_aider_session
        aider = create_aider_session(goal, target_files, mode="dry_run")
    except Exception as error:
        aider = {"ok": False, "error": str(error)}

    try:
        from seed_workflow_runtime_v33 import create_workflow
        workflow = create_workflow(goal)
    except Exception as error:
        workflow = {"ok": False, "error": str(error)}

    loop = {
        "id": loop_id,
        "created_at": now_timestamp(),
        "version": "v45.0.0",
        "ok": True,
        "goal": goal,
        "target_files": target_files,
        "workflow": workflow,
        "aider_session": aider,
        "stages": [
            "memory recall",
            "council review",
            "workflow create",
            "checkpoint",
            "aider dry-run",
            "review",
            "tests",
            "manual approval",
            "real patch",
            "verify",
            "learn"
        ],
        "status": "planned_waiting_for_review"
    }

    LOOP_FILE.write_text(json.dumps(loop, indent=4))
    return loop


def show_self_improve_loop():
    print("\n=== SEED SELF-IMPROVEMENT LOOP v45 ===")
    if LOOP_FILE.exists():
        print(LOOP_FILE.read_text())
    else:
        print("No loop yet. Use /self-improve-new.")


def show_self_improve_new():
    goal = input("Self-improvement goal: ").strip()
    files = input("Target files comma-separated: ").strip()
    target_files = [x.strip() for x in files.split(",") if x.strip()]
    print(json.dumps(create_self_improvement_loop(goal, target_files), indent=4))


if __name__ == "__main__":
    show_self_improve_loop()
