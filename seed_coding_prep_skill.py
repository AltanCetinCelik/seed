import json
import re
from datetime import datetime
from pathlib import Path


RUNS_DIR = Path("seed_agent_runs")


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def slugify(text):
    text = re.sub(r"[^a-zA-Z0-9_-]+", "-", text.strip().lower())
    return text.strip("-")[:60] or "coding-task"


def prepare_coding_task(task, target_repo="."):
    RUNS_DIR.mkdir(exist_ok=True)

    task = task or "Unspecified coding task"
    slug = slugify(task)
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + slug
    run_dir = RUNS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    try:
        from seed_coding_agent_gateway import build_coding_agent_plan
        gateway_plan = build_coding_agent_plan(task)
    except Exception as error:
        gateway_plan = {"error": str(error)}

    try:
        from seed_git_skill import git_summary
        git = git_summary()
    except Exception as error:
        git = {"error": str(error)}

    plan = {
        "created_at": now_timestamp(),
        "version": "v2.5.0",
        "run_id": run_id,
        "task": task,
        "target_repo": target_repo,
        "execution_status": "prepared_only",
        "approval_required_before_execution": True,
        "safe_order": [
            "Review this plan",
            "Confirm target repo",
            "Create or verify backup/branch",
            "Choose coding agent",
            "Run agent only after approval",
            "Run tests",
            "Show diff",
            "Ask before commit",
            "Rollback if broken"
        ],
        "gateway_plan": gateway_plan,
        "git_summary": git
    }

    plan_file = run_dir / "coding_task_plan.json"
    plan_file.write_text(json.dumps(plan, indent=4))

    return {
        "ok": True,
        "run_id": run_id,
        "run_dir": str(run_dir),
        "plan_file": str(plan_file),
        "plan": plan
    }


def run_coding_prep_skill(operation, args=None):
    args = args or {}

    if operation == "prepare":
        return prepare_coding_task(args.get("task", ""), target_repo=args.get("target_repo", "."))

    if operation == "list":
        RUNS_DIR.mkdir(exist_ok=True)
        runs = [p.name for p in sorted(RUNS_DIR.iterdir(), reverse=True) if p.is_dir()]
        return {"ok": True, "runs": runs[:50], "count": len(runs)}

    return {"ok": False, "error": f"Unknown coding prep operation: {operation}"}


if __name__ == "__main__":
    print(prepare_coding_task("test task"))
