import json
from datetime import datetime
from pathlib import Path


try:
    from seed_config import SEED_SELF_IMPROVEMENT_LAB_FILE
except Exception:
    SEED_SELF_IMPROVEMENT_LAB_FILE = "seed_self_improvement_lab_v18.json"


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def create_self_improvement_proposal(goal="Improve Seed without breaking core"):
    proposal = {
        "created_at": now_timestamp(),
        "version": "v20.0.0",
        "ok": True,
        "engine": "Seed Self-Improvement Lab v18",
        "goal": goal,
        "pipeline": [
            "create proposal",
            "council review",
            "checkpoint",
            "Aider dry-run",
            "diff review",
            "gate run",
            "approval",
            "real patch",
            "verify",
            "memory distill"
        ],
        "safe_defaults": {
            "dry_run_first": True,
            "one_file_first": True,
            "no_auto_commit": True,
            "rollback_available": True,
            "success_requires_gate": True
        },
        "recommended_first_target": "seed_fast_voice_context.py"
    }

    with open(SEED_SELF_IMPROVEMENT_LAB_FILE, "w") as file:
        json.dump(proposal, file, indent=4)

    return proposal


def show_self_improvement_lab():
    goal = input("Improvement goal: ").strip() or "Improve Seed without breaking core"
    print(json.dumps(create_self_improvement_proposal(goal), indent=4))


if __name__ == "__main__":
    show_self_improvement_lab()
