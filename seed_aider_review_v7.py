import json
import subprocess
from datetime import datetime
from pathlib import Path


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def git_diff_stat():
    try:
        proc = subprocess.run(["git", "diff", "--stat"], capture_output=True, text=True, timeout=20)
        return proc.stdout
    except Exception as error:
        return str(error)


def create_aider_review(task, target_files):
    from seed_aider_patch_flow import create_patch_flow

    flow = create_patch_flow(task, target_files, mode="dry_run")

    review = {
        "created_at": now_timestamp(),
        "version": "v20.0.0",
        "ok": True,
        "engine": "Seed Aider Patch Review v7",
        "task": task,
        "target_files": target_files,
        "flow": flow,
        "diff_stat_now": git_diff_stat(),
        "review_steps": [
            "checkpoint created",
            "aider dry-run plan created",
            "approve dry-run token",
            "execute dry-run",
            "inspect output",
            "only then create real-run plan",
            "verify with gates",
            "rollback if needed"
        ]
    }

    Path("seed_aider_review_v7.json").write_text(json.dumps(review, indent=4))
    return review


def show_aider_review():
    task = input("Aider review task: ").strip()
    files = input("Target files comma-separated: ").strip()
    target_files = [x.strip() for x in files.split(",") if x.strip()]
    print(json.dumps(create_aider_review(task, target_files), indent=4))


if __name__ == "__main__":
    show_aider_review()
