import json
from datetime import datetime


try:
    from seed_config import SEED_AIDER_PATCH_FLOW_STATE_FILE
except Exception:
    SEED_AIDER_PATCH_FLOW_STATE_FILE = "seed_aider_patch_flow_state.json"


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def create_patch_flow(task, target_files, mode="dry_run"):
    from seed_patch_rollback import create_checkpoint
    from seed_aider_execution_unlock import create_aider_unlock_plan

    checkpoint = create_checkpoint("before-aider-patch-flow", target_files)
    aider_plan = create_aider_unlock_plan(task, target_files, mode=mode)

    flow = {
        "created_at": now_timestamp(),
        "version": "v4.0.0",
        "ok": True,
        "task": task,
        "target_files": target_files,
        "mode": mode,
        "checkpoint": checkpoint,
        "aider_plan": aider_plan,
        "next_steps": [
            "Review checkpoint approval token.",
            "Approve Aider plan token.",
            "Execute dry-run first.",
            "Only create real plan after dry-run looks safe.",
            "Use checkpoint restore if patch goes wrong."
        ]
    }

    with open(SEED_AIDER_PATCH_FLOW_STATE_FILE, "w") as file:
        json.dump(flow, file, indent=4)

    return flow


def show_aider_patch_flow():
    task = input("Patch task: ").strip()
    files_raw = input("Target files comma-separated: ").strip()
    mode = input("Mode dry_run or real [dry_run]: ").strip() or "dry_run"
    target_files = [x.strip() for x in files_raw.split(",") if x.strip()]
    print(json.dumps(create_patch_flow(task, target_files, mode), indent=4))


if __name__ == "__main__":
    show_aider_patch_flow()
