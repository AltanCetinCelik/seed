import hashlib
import json
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path


try:
    from seed_config import (
        SEED_AIDER_BRIDGE_STATE_FILE,
        SEED_AIDER_BRIDGE_HISTORY_FILE,
        SEED_AIDER_RUNS_DIR,
        SEED_AIDER_EXECUTION_LOCKED
    )
except Exception:
    SEED_AIDER_BRIDGE_STATE_FILE = "seed_aider_bridge_state.json"
    SEED_AIDER_BRIDGE_HISTORY_FILE = "seed_aider_bridge_history.jsonl"
    SEED_AIDER_RUNS_DIR = "seed_agent_runs"
    SEED_AIDER_EXECUTION_LOCKED = True


SAFE_TARGET_EXTENSIONS = {
    ".py", ".md", ".txt", ".json", ".yaml", ".yml", ".toml",
    ".html", ".css", ".js", ".ts", ".sh"
}


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def safe_slug(text, max_len=70):
    out = []
    for ch in (text or "").lower():
        if ch.isalnum():
            out.append(ch)
        elif ch in " _-":
            out.append("-")
    slug = "".join(out).strip("-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug[:max_len] or "aider-task"


def save_json(path, data):
    with open(path, "w") as file:
        json.dump(data, file, indent=4)


def append_history(item):
    try:
        with open(SEED_AIDER_BRIDGE_HISTORY_FILE, "a") as file:
            file.write(json.dumps(item) + "\n")
    except Exception:
        pass


def detect_aider():
    command = shutil.which("aider")
    python_module_available = False

    try:
        result = subprocess.run(
            ["python", "-m", "aider", "--version"],
            capture_output=True,
            text=True,
            timeout=8
        )
        python_module_available = result.returncode == 0
        module_version_output = (result.stdout or result.stderr).strip()
    except Exception as error:
        module_version_output = str(error)

    version_output = None
    if command:
        try:
            result = subprocess.run(
                ["aider", "--version"],
                capture_output=True,
                text=True,
                timeout=8
            )
            version_output = (result.stdout or result.stderr).strip()
        except Exception as error:
            version_output = str(error)

    state = {
        "created_at": now_timestamp(),
        "version": "v2.8.0",
        "aider_command": command,
        "aider_available": bool(command) or python_module_available,
        "python_module_available": python_module_available,
        "command_version_output": version_output,
        "module_version_output": module_version_output,
        "policy": {
            "no_auto_install": True,
            "no_auto_execute": True,
            "execution_locked": bool(SEED_AIDER_EXECUTION_LOCKED),
            "manual_commands_only": True,
            "approval_required": True,
            "target_files_required": True
        }
    }

    save_json(SEED_AIDER_BRIDGE_STATE_FILE, state)
    append_history({
        "created_at": now_timestamp(),
        "event": "detect_aider",
        "available": state["aider_available"],
        "command": command
    })

    return state


def aider_install_plan():
    """
    Install plan only. Does not execute install commands.
    Official docs recommend uv or pipx style isolated installs.
    """
    plan = {
        "created_at": now_timestamp(),
        "version": "v2.8.0",
        "status": "manual_install_plan_only",
        "recommended_methods": [
            {
                "method": "uv",
                "commands": [
                    "python -m pip install uv",
                    "uv tool install --force --python python3.12 --with pip aider-chat@latest"
                ],
                "why": "Isolated tool install; avoids breaking Seed's Python environment."
            },
            {
                "method": "pipx",
                "commands": [
                    "python -m pip install pipx",
                    "python -m pipx ensurepath",
                    "pipx install aider-chat"
                ],
                "why": "Isolated CLI install."
            }
        ],
        "do_not_use_inside_seed_auto": True,
        "note": "Run install manually in terminal only if User approves."
    }
    return plan


def git_status_snapshot():
    try:
        from seed_skill_kernel import run_skill
        return run_skill("git", "status")
    except Exception as error:
        return {"ok": False, "error": str(error)}


def validate_target_files(files):
    root = Path(".").resolve()
    valid = []
    invalid = []

    for file_name in files or []:
        if not file_name:
            continue

        path = (root / file_name).resolve()

        if root != path and root not in path.parents:
            invalid.append({
                "file": file_name,
                "reason": "escapes project root"
            })
            continue

        if not path.exists():
            invalid.append({
                "file": file_name,
                "reason": "does not exist"
            })
            continue

        if not path.is_file():
            invalid.append({
                "file": file_name,
                "reason": "not a file"
            })
            continue

        if path.suffix.lower() not in SAFE_TARGET_EXTENSIONS:
            invalid.append({
                "file": file_name,
                "reason": f"extension not allowlisted: {path.suffix}"
            })
            continue

        valid.append(str(path.relative_to(root)))

    return {
        "ok": len(valid) > 0 and len(invalid) == 0,
        "valid": valid,
        "invalid": invalid
    }


def choose_suggested_files(task):
    lowered = (task or "").lower()
    candidates = []

    if "voice" in lowered:
        candidates += [
            "seed_active_voice_daemon.py",
            "seed_voice_command_bridge.py",
            "seed_fast_voice_context.py",
            "seed_voice_quality_router.py"
        ]

    if "skill" in lowered:
        candidates += [
            "seed_skill_kernel.py",
            "seed_filesystem_skill.py",
            "seed_git_skill.py"
        ]

    if "agent" in lowered or "aider" in lowered:
        candidates += [
            "seed_agent_run_lifecycle.py",
            "seed_external_executor_bridge.py",
            "seed_aider_bridge.py"
        ]

    if "cockpit" in lowered:
        candidates += [
            "seed_cockpit_browser_action.py",
            "seed_companion_cockpit.py"
        ]

    if not candidates:
        candidates = [
            "seed_brain.py",
            "seed_commands.py",
            "seed_config.py"
        ]

    existing = []
    for file_name in candidates:
        if Path(file_name).exists():
            existing.append(file_name)

    return existing


def make_approval_token(plan_id, task):
    digest = hashlib.sha256(f"{plan_id}:{task}:{now_timestamp()}".encode("utf-8")).hexdigest()
    return digest[:12]


def create_aider_plan(task, target_files=None):
    detect = detect_aider()
    target_files = target_files or choose_suggested_files(task)
    validation = validate_target_files(target_files)

    runs_dir = Path(SEED_AIDER_RUNS_DIR)
    runs_dir.mkdir(exist_ok=True)

    plan_id = datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + safe_slug(task)
    plan_dir = runs_dir / plan_id
    plan_dir.mkdir(parents=True, exist_ok=True)

    approval_token = make_approval_token(plan_id, task)

    prompt_file = plan_dir / "AIDER_TASK.md"
    prompt_file.write_text(
        "# Seed Aider Task\n\n"
        f"Task:\n\n{task}\n\n"
        "Rules:\n"
        "- Do not broad edit.\n"
        "- Only target listed files.\n"
        "- Preserve Seed safety rules.\n"
        "- No fake sentience or consciousness claims.\n"
        "- No auto-commit.\n"
        "- Show diff and tests after edits.\n"
    )

    valid_files = validation["valid"]

    command_preview = []
    if detect["aider_command"]:
        command_preview = [
            "aider",
            "--message-file",
            str(prompt_file),
        ] + valid_files
    elif detect["python_module_available"]:
        command_preview = [
            "python",
            "-m",
            "aider",
            "--message-file",
            str(prompt_file),
        ] + valid_files
    else:
        command_preview = []

    plan = {
        "created_at": now_timestamp(),
        "version": "v2.8.0",
        "plan_id": plan_id,
        "task": task,
        "status": "planned_locked",
        "aider_detect": detect,
        "install_plan_if_missing": aider_install_plan() if not detect["aider_available"] else None,
        "target_files": target_files,
        "target_validation": validation,
        "git_status": git_status_snapshot(),
        "approval": {
            "required": True,
            "approved": False,
            "approval_token": approval_token
        },
        "execution": {
            "locked": True,
            "can_execute_now": False,
            "reason": "v2.8 creates Aider plans but does not run file-editing Aider commands automatically.",
            "manual_command_preview": command_preview
        },
        "safe_order": [
            "Review target files",
            "Review git status",
            "Install Aider manually if missing",
            "Approve exact command",
            "Run only on selected target files",
            "Run tests",
            "Review diff",
            "Commit only after approval"
        ]
    }

    plan_file = plan_dir / "aider_plan.json"
    plan_file.write_text(json.dumps(plan, indent=4))

    preview_file = plan_dir / "AIDER_COMMAND_PREVIEW.sh"
    preview_text = "#!/bin/sh\n# Manual preview only. Do not run unless approved.\n"
    if command_preview:
        preview_text += " ".join(f'"{x}"' if " " in x else x for x in command_preview) + "\n"
    else:
        preview_text += "# Aider is not installed. See aider_plan.json install_plan_if_missing.\n"
    preview_file.write_text(preview_text)

    append_history({
        "created_at": now_timestamp(),
        "event": "create_aider_plan",
        "plan_id": plan_id,
        "aider_available": detect["aider_available"],
        "valid_files": valid_files
    })

    return {
        "ok": True,
        "plan_id": plan_id,
        "plan_dir": str(plan_dir),
        "plan_file": str(plan_file),
        "prompt_file": str(prompt_file),
        "preview_file": str(preview_file),
        "aider_available": detect["aider_available"],
        "valid_target_files": valid_files,
        "invalid_target_files": validation["invalid"],
        "approval_token": approval_token,
        "manual_only": True
    }


def aider_preflight(task, target_files=None):
    detect = detect_aider()
    target_files = target_files or choose_suggested_files(task)
    validation = validate_target_files(target_files)
    git_status = git_status_snapshot()

    ok = validation["ok"]

    return {
        "ok": ok,
        "aider_available": detect["aider_available"],
        "aider_detect": detect,
        "target_validation": validation,
        "git_status": git_status,
        "install_plan_if_missing": aider_install_plan() if not detect["aider_available"] else None,
        "can_plan": True,
        "can_execute": False,
        "execution_reason": "Execution remains locked in v2.8."
    }


def show_aider_status():
    print("\n=== SEED AIDER BRIDGE STATUS ===")
    print(json.dumps(detect_aider(), indent=4))


def show_aider_install_plan():
    print("\n=== SEED AIDER INSTALL PLAN ===")
    print(json.dumps(aider_install_plan(), indent=4))


def show_aider_preflight():
    task = input("Aider task: ").strip()
    files_raw = input("Target files comma-separated or blank for auto: ").strip()
    files = [x.strip() for x in files_raw.split(",") if x.strip()] if files_raw else None
    print(json.dumps(aider_preflight(task, files), indent=4))


def show_aider_plan():
    task = input("Aider task: ").strip()
    files_raw = input("Target files comma-separated or blank for auto: ").strip()
    files = [x.strip() for x in files_raw.split(",") if x.strip()] if files_raw else None
    print(json.dumps(create_aider_plan(task, files), indent=4))


def aider_bridge_context(user_prompt=""):
    detect = detect_aider()
    return (
        "=== SEED v2.8 AIDER FIRST EXECUTOR BRIDGE ===\n"
        f"Aider available: {detect['aider_available']}\n"
        "Seed can create Aider preflight checks and manual-only Aider plans.\n"
        "Aider execution remains locked by default because it can edit files.\n"
        "Rules: target files required, approval token required, no auto-commit, no blind install.\n"
    )


if __name__ == "__main__":
    show_aider_status()
