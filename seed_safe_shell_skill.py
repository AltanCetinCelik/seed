import subprocess


try:
    from seed_config import SEED_SKILL_SAFE_TIMEOUT_SECONDS
except Exception:
    SEED_SKILL_SAFE_TIMEOUT_SECONDS = 12


SAFE_COMMANDS = {
    "python_version": ["python", "--version"],
    "disk_usage": ["df", "-h", "."],
    "compile_core": [
        "python", "-m", "py_compile",
        "seed_skill_kernel.py",
        "seed_action_kernel.py",
        "seed_semantic_memory.py",
        "seed_voice_command_bridge.py"
    ],
    "compile_v25": [
        "python", "-m", "py_compile",
        "seed_skill_kernel.py",
        "seed_filesystem_skill.py",
        "seed_git_skill.py",
        "seed_repo_inspection_skill.py",
        "seed_safe_shell_skill.py",
        "seed_browser_skill.py",
        "seed_coding_prep_skill.py",
        "seed_v25_skill_gate.py"
    ]
}


def run_safe_command(command_id):
    if command_id not in SAFE_COMMANDS:
        return {
            "ok": False,
            "error": "Command is not whitelisted.",
            "command_id": command_id
        }

    command = SAFE_COMMANDS[command_id]
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=int(SEED_SKILL_SAFE_TIMEOUT_SECONDS)
    )

    return {
        "ok": result.returncode == 0,
        "command_id": command_id,
        "command": command,
        "returncode": result.returncode,
        "stdout": result.stdout[-8000:],
        "stderr": result.stderr[-4000:]
    }


def run_diagnostic():
    results = []
    for command_id in ["python_version", "disk_usage", "compile_v25"]:
        try:
            results.append(run_safe_command(command_id))
        except Exception as error:
            results.append({
                "ok": False,
                "command_id": command_id,
                "error": str(error)
            })

    return {
        "ok": all(item.get("ok") for item in results),
        "results": results
    }


def run_safe_shell_skill(operation, args=None):
    args = args or {}

    if operation == "diagnostic":
        return run_diagnostic()

    if operation == "run":
        return run_safe_command(args.get("command_id", ""))

    if operation == "list":
        return {
            "ok": True,
            "commands": sorted(SAFE_COMMANDS.keys())
        }

    return {"ok": False, "error": f"Unknown safe shell operation: {operation}"}


if __name__ == "__main__":
    print(run_diagnostic())
