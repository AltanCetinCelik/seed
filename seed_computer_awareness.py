import json
import os
import platform
import shutil
import subprocess
from datetime import datetime

from seed_config import SEED_COMPUTER_SNAPSHOT_FILE
from seed_presence import update_presence_after_action


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def safe_run(command, timeout=6):
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        return {
            "command": command,
            "returncode": result.returncode,
            "stdout": result.stdout[-3000:],
            "stderr": result.stderr[-3000:]
        }

    except subprocess.TimeoutExpired:
        return {
            "command": command,
            "returncode": None,
            "stdout": "",
            "stderr": "Command timed out."
        }


def get_git_status():
    if not os.path.exists(".git"):
        return "Not a git repository."

    result = safe_run("git status --short", timeout=8)

    if result["returncode"] != 0:
        return result["stderr"] or "git status failed"

    output = result["stdout"].strip()

    if output == "":
        return "clean"

    return output


def get_python_version():
    result = safe_run("python --version", timeout=5)

    if result["stdout"].strip():
        return result["stdout"].strip()

    return result["stderr"].strip()


def get_ollama_models():
    result = safe_run("ollama list", timeout=8)

    if result["returncode"] != 0:
        return result["stderr"] or "ollama list failed"

    return result["stdout"][-3000:]


def get_disk_summary():
    total, used, free = shutil.disk_usage(".")

    gb = 1024 * 1024 * 1024

    return {
        "total_gb": round(total / gb, 2),
        "used_gb": round(used / gb, 2),
        "free_gb": round(free / gb, 2)
    }


def build_computer_snapshot():
    snapshot = {
        "created_at": now_timestamp(),
        "system": {
            "platform": platform.platform(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python": get_python_version()
        },
        "project": {
            "cwd": os.getcwd(),
            "git_status": get_git_status()
        },
        "ollama": {
            "models": get_ollama_models()
        },
        "disk": get_disk_summary()
    }

    with open(SEED_COMPUTER_SNAPSHOT_FILE, "w") as file:
        json.dump(snapshot, file, indent=4)

    update_presence_after_action("diagnostic")

    return snapshot


def load_computer_snapshot():
    try:
        with open(SEED_COMPUTER_SNAPSHOT_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return build_computer_snapshot()
    except json.JSONDecodeError:
        return build_computer_snapshot()


def format_computer_snapshot():
    snapshot = load_computer_snapshot()

    text = "=== SEED COMPUTER AWARENESS ===\n"
    text += f"Created: {snapshot.get('created_at')}\n"

    system = snapshot.get("system", {})
    project = snapshot.get("project", {})
    disk = snapshot.get("disk", {})

    text += "\nSystem:\n"
    text += f"- Platform: {system.get('platform')}\n"
    text += f"- Machine: {system.get('machine')}\n"
    text += f"- Processor: {system.get('processor')}\n"
    text += f"- Python: {system.get('python')}\n"

    text += "\nProject:\n"
    text += f"- CWD: {project.get('cwd')}\n"
    text += f"- Git status: {project.get('git_status')}\n"

    text += "\nDisk:\n"
    text += f"- Total GB: {disk.get('total_gb')}\n"
    text += f"- Used GB: {disk.get('used_gb')}\n"
    text += f"- Free GB: {disk.get('free_gb')}\n"

    text += "\nOllama models:\n"
    text += snapshot.get("ollama", {}).get("models", "")

    return text


def show_computer_snapshot():
    print("\n" + format_computer_snapshot())


def refresh_computer_snapshot():
    build_computer_snapshot()
    show_computer_snapshot()


def get_computer_context_for_prompt():
    snapshot = load_computer_snapshot()

    text = "=== COMPUTER CONTEXT ===\n"
    text += f"Platform: {snapshot.get('system', {}).get('platform')}\n"
    text += f"Python: {snapshot.get('system', {}).get('python')}\n"
    text += f"CWD: {snapshot.get('project', {}).get('cwd')}\n"
    text += f"Git status: {snapshot.get('project', {}).get('git_status')}\n"
    text += f"Disk free GB: {snapshot.get('disk', {}).get('free_gb')}\n"
    text += """
Computer awareness rule:
Seed may use this snapshot to understand the local machine/project state.
Seed must not claim it can see the screen or access files that were not inspected.
"""
    return text