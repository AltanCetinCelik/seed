import hashlib
import json
import os
import shlex
import shutil
import subprocess
from datetime import datetime
from pathlib import Path


try:
    from seed_config import (
        SEED_AIDER_UNLOCK_STATE_FILE,
        SEED_AIDER_UNLOCK_HISTORY_FILE,
        SEED_AIDER_REAL_RUN_PHRASE
    )
except Exception:
    SEED_AIDER_UNLOCK_STATE_FILE = "seed_aider_unlock_state.json"
    SEED_AIDER_UNLOCK_HISTORY_FILE = "seed_aider_unlock_history.jsonl"
    SEED_AIDER_REAL_RUN_PHRASE = "I UNDERSTAND AIDER CAN EDIT FILES"


SAFE_EXTENSIONS = {".py", ".md", ".txt", ".json", ".yaml", ".yml", ".toml", ".html", ".css", ".js", ".ts", ".sh"}


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def append_history(item):
    with open(SEED_AIDER_UNLOCK_HISTORY_FILE, "a") as file:
        file.write(json.dumps(item) + "\n")


def detect_aider_runtime():
    aider = shutil.which("aider")
    version = None
    ok = False

    if aider:
        try:
            result = subprocess.run(["aider", "--version"], capture_output=True, text=True, timeout=10)
            version = (result.stdout or result.stderr).strip()
            ok = result.returncode == 0
        except Exception as error:
            version = str(error)

    return {
        "ok": ok,
        "aider_command": aider,
        "version": version,
        "path": os.environ.get("PATH")
    }


def validate_targets(target_files):
    root = Path(".").resolve()
    valid = []
    invalid = []

    for item in target_files or []:
        path = (root / item).resolve()

        if root != path and root not in path.parents:
            invalid.append({"file": item, "reason": "outside project root"})
            continue

        if not path.exists():
            invalid.append({"file": item, "reason": "missing"})
            continue

        if not path.is_file():
            invalid.append({"file": item, "reason": "not a file"})
            continue

        if path.suffix.lower() not in SAFE_EXTENSIONS:
            invalid.append({"file": item, "reason": f"extension not allowlisted: {path.suffix}"})
            continue

        valid.append(str(path.relative_to(root)))

    return {
        "ok": len(valid) > 0 and not invalid,
        "valid": valid,
        "invalid": invalid
    }


def git_snapshot():
    try:
        from seed_skill_kernel import run_skill
        return {
            "status": run_skill("git", "status"),
            "diff_stat": run_skill("git", "diff_stat")
        }
    except Exception as error:
        return {"ok": False, "error": str(error)}


def make_token(plan_id, task):
    return hashlib.sha256(f"{plan_id}:{task}:{now_timestamp()}".encode()).hexdigest()[:12]


def create_aider_unlock_plan(task, target_files, mode="dry_run"):
    runtime = detect_aider_runtime()
    validation = validate_targets(target_files)

    plan_id = datetime.now().strftime("%Y%m%d_%H%M%S") + "_aider_unlock"
    run_dir = Path("seed_agent_runs") / plan_id
    run_dir.mkdir(parents=True, exist_ok=True)

    prompt_file = run_dir / "AIDER_REAL_TASK.md"
    prompt_file.write_text(
        "# Seed Aider Supervised Task\n\n"
        f"Task:\n{task}\n\n"
        "Hard rules:\n"
        "- Only edit target files listed in the command.\n"
        "- Do not claim Seed is alive/sentient/conscious/human.\n"
        "- Preserve safety gates.\n"
        "- No auto commit.\n"
        "- Prefer minimal patches.\n"
        "- After change, explain tests/diff.\n"
    )

    approval_token = make_token(plan_id, task)

    base_cmd = [
        "aider",
        "--message-file",
        str(prompt_file),
        "--no-auto-commits",
        "--no-dirty-commits",
    ]

    if mode == "dry_run":
        base_cmd.append("--dry-run")

    base_cmd.extend(validation["valid"])

    plan = {
        "created_at": now_timestamp(),
        "version": "v3.6.0",
        "ok": True,
        "plan_id": plan_id,
        "run_dir": str(run_dir),
        "task": task,
        "mode": mode,
        "runtime": runtime,
        "target_validation": validation,
        "approval": {
            "required": True,
            "approved": False,
            "approval_token": approval_token,
            "real_run_phrase_required": mode == "real",
            "real_run_phrase": SEED_AIDER_REAL_RUN_PHRASE if mode == "real" else None
        },
        "git_before": git_snapshot(),
        "command": base_cmd,
        "command_preview": " ".join(shlex.quote(x) for x in base_cmd),
        "status": "planned",
        "can_execute": runtime.get("ok") is True and validation.get("ok") is True
    }

    plan_file = run_dir / "aider_unlock_plan.json"
    plan_file.write_text(json.dumps(plan, indent=4))

    state = {
        "latest_plan_id": plan_id,
        "latest_plan_file": str(plan_file),
        "latest_plan": plan
    }

    with open(SEED_AIDER_UNLOCK_STATE_FILE, "w") as file:
        json.dump(state, file, indent=4)

    append_history({
        "created_at": now_timestamp(),
        "event": "create_plan",
        "plan_id": plan_id,
        "mode": mode,
        "can_execute": plan["can_execute"]
    })

    return plan


def load_latest_plan():
    state_path = Path(SEED_AIDER_UNLOCK_STATE_FILE)
    if not state_path.exists():
        return None

    state = json.loads(state_path.read_text())
    plan_file = Path(state["latest_plan_file"])
    if not plan_file.exists():
        return None

    return json.loads(plan_file.read_text())


def approve_latest_plan(token, real_phrase=None):
    plan = load_latest_plan()
    if not plan:
        return {"ok": False, "error": "No latest Aider unlock plan."}

    if token != plan["approval"]["approval_token"]:
        return {"ok": False, "error": "Invalid approval token."}

    if plan["mode"] == "real" and real_phrase != SEED_AIDER_REAL_RUN_PHRASE:
        return {
            "ok": False,
            "error": "Real-run phrase mismatch.",
            "required_phrase": SEED_AIDER_REAL_RUN_PHRASE
        }

    plan["approval"]["approved"] = True
    plan["approved_at"] = now_timestamp()
    plan["status"] = "approved"

    plan_file = Path(plan["run_dir"]) / "aider_unlock_plan.json"
    plan_file.write_text(json.dumps(plan, indent=4))

    append_history({
        "created_at": now_timestamp(),
        "event": "approve",
        "plan_id": plan["plan_id"],
        "mode": plan["mode"]
    })

    return {"ok": True, "plan_id": plan["plan_id"], "status": "approved"}


def execute_latest_plan():
    plan = load_latest_plan()
    if not plan:
        return {"ok": False, "error": "No latest Aider unlock plan."}

    if not plan["approval"].get("approved"):
        return {"ok": False, "error": "Plan is not approved."}

    if not plan.get("can_execute"):
        return {"ok": False, "error": "Plan cannot execute.", "plan": plan}

    command = plan["command"]
    run_dir = Path(plan["run_dir"])

    before = git_snapshot()

    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=300)
        after = git_snapshot()

        output = {
            "ok": result.returncode == 0,
            "plan_id": plan["plan_id"],
            "mode": plan["mode"],
            "returncode": result.returncode,
            "stdout_tail": result.stdout[-8000:],
            "stderr_tail": result.stderr[-5000:],
            "git_before": before,
            "git_after": after
        }

        (run_dir / "aider_execution_result.json").write_text(json.dumps(output, indent=4))

        plan["status"] = "executed" if output["ok"] else "execution_failed"
        plan["executed_at"] = now_timestamp()
        (run_dir / "aider_unlock_plan.json").write_text(json.dumps(plan, indent=4))

        append_history({
            "created_at": now_timestamp(),
            "event": "execute",
            "plan_id": plan["plan_id"],
            "mode": plan["mode"],
            "ok": output["ok"]
        })

        return output
    except Exception as error:
        return {"ok": False, "error": str(error), "plan_id": plan["plan_id"]}


def show_aider_unlock_status():
    runtime = detect_aider_runtime()
    plan = load_latest_plan()

    print("\n=== SEED AIDER EXECUTION UNLOCK ===")
    print(json.dumps({
        "runtime": runtime,
        "latest_plan": {
            "plan_id": plan.get("plan_id") if plan else None,
            "mode": plan.get("mode") if plan else None,
            "status": plan.get("status") if plan else None,
            "approved": plan.get("approval", {}).get("approved") if plan else None,
            "can_execute": plan.get("can_execute") if plan else None,
            "approval_token": plan.get("approval", {}).get("approval_token") if plan else None,
            "command_preview": plan.get("command_preview") if plan else None
        } if plan else None
    }, indent=4))


def show_aider_unlock_plan():
    task = input("Aider task: ").strip()
    files_raw = input("Target files comma-separated: ").strip()
    mode = input("Mode dry_run or real [dry_run]: ").strip() or "dry_run"
    files = [x.strip() for x in files_raw.split(",") if x.strip()]
    print(json.dumps(create_aider_unlock_plan(task, files, mode=mode), indent=4))


def show_aider_unlock_approve():
    token = input("Approval token: ").strip()
    phrase = input("Real-run phrase if mode=real, else blank: ")
    print(json.dumps(approve_latest_plan(token, real_phrase=phrase or None), indent=4))


def show_aider_unlock_execute():
    print(json.dumps(execute_latest_plan(), indent=4))


if __name__ == "__main__":
    show_aider_unlock_status()
