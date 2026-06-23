import json
import os
import subprocess
from datetime import datetime

from seed_config import (
    SEED_LOCAL_ACTIONS_FILE,
    SEED_PENDING_ACTION_FILE,
    LOCAL_ALLOWED_APPS,
    LOCAL_ALLOWED_FOLDERS,
    LOCAL_SAFE_COMMANDS,
    LOCAL_DIAGNOSTIC_COMMANDS,
    LOCAL_FORBIDDEN_COMMAND_SUBSTRINGS
)
from seed_presence import (
    load_presence_state,
    update_presence_after_action
)


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def expand_path(path):
    return os.path.abspath(os.path.expanduser(path))


def log_action(action):
    with open(SEED_LOCAL_ACTIONS_FILE, "a") as file:
        file.write(json.dumps(action) + "\n")


def load_action_history(limit=30):
    if not os.path.exists(SEED_LOCAL_ACTIONS_FILE):
        return []

    actions = []

    with open(SEED_LOCAL_ACTIONS_FILE, "r") as file:
        for line in file:
            try:
                actions.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    return actions[-limit:]


def save_pending_action(action):
    with open(SEED_PENDING_ACTION_FILE, "w") as file:
        json.dump(action, file, indent=4)


def load_pending_action():
    try:
        with open(SEED_PENDING_ACTION_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        return None


def clear_pending_action():
    if os.path.exists(SEED_PENDING_ACTION_FILE):
        os.remove(SEED_PENDING_ACTION_FILE)


def emergency_lock_is_active():
    state = load_presence_state()
    return bool(state.get("emergency_lock"))


def command_is_forbidden(command):
    lowered = command.lower()

    for forbidden in LOCAL_FORBIDDEN_COMMAND_SUBSTRINGS:
        if forbidden.lower() in lowered:
            return True, forbidden

    return False, None


def command_is_safe(command):
    command = command.strip()

    forbidden, reason = command_is_forbidden(command)

    if forbidden:
        return False, f"Forbidden command substring: {reason}"

    for allowed in LOCAL_SAFE_COMMANDS:
        if command == allowed:
            return True, "Command is in safe allowlist."

    for diagnostic in LOCAL_DIAGNOSTIC_COMMANDS:
        if command == diagnostic:
            return True, "Command is in diagnostic allowlist."

    return False, "Command is not in safe allowlist."


def run_shell_command(command, approved=False):
    if emergency_lock_is_active():
        update_presence_after_action("blocked")
        return {
            "ok": False,
            "message": "Emergency lock is active. Local control is disabled."
        }

    safe, reason = command_is_safe(command)

    if not safe and not approved:
        action = {
            "created_at": now_timestamp(),
            "type": "shell_command",
            "command": command,
            "risk": "approval_required",
            "reason": reason,
            "approval_phrase": "RUN " + command
        }

        save_pending_action(action)
        update_presence_after_action("approval_required")

        return {
            "ok": False,
            "message": "Command requires approval.",
            "reason": reason,
            "approval_phrase": action["approval_phrase"]
        }

    if not safe and approved:
        forbidden, forbidden_reason = command_is_forbidden(command)

        if forbidden:
            update_presence_after_action("blocked")
            return {
                "ok": False,
                "message": f"Command blocked even with approval: {forbidden_reason}"
            }

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=20
        )

        action_log = {
            "created_at": now_timestamp(),
            "type": "shell_command",
            "command": command,
            "approved": approved,
            "returncode": result.returncode,
            "stdout": result.stdout[-5000:],
            "stderr": result.stderr[-5000:]
        }

        log_action(action_log)
        update_presence_after_action("diagnostic")

        return {
            "ok": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout[-5000:],
            "stderr": result.stderr[-5000:]
        }

    except subprocess.TimeoutExpired:
        update_presence_after_action("blocked")
        return {
            "ok": False,
            "message": "Command timed out."
        }


def app_is_allowed(app_name):
    return app_name in LOCAL_ALLOWED_APPS


def open_allowed_app(app_name):
    if emergency_lock_is_active():
        update_presence_after_action("blocked")
        print("Emergency lock is active. Local control is disabled.")
        return

    if not app_is_allowed(app_name):
        print("App is not in allowlist.")
        print("Allowed apps:")
        for app in LOCAL_ALLOWED_APPS:
            print(f"- {app}")
        return

    result = subprocess.run(
        ["open", "-a", app_name],
        capture_output=True,
        text=True
    )

    action = {
        "created_at": now_timestamp(),
        "type": "open_app",
        "app": app_name,
        "returncode": result.returncode,
        "stderr": result.stderr
    }

    log_action(action)
    update_presence_after_action("app_opened")

    if result.returncode == 0:
        print(f"Opened app: {app_name}")
    else:
        print(result.stderr)


def folder_is_allowed(path):
    expanded = expand_path(path)

    for allowed in LOCAL_ALLOWED_FOLDERS:
        allowed_expanded = expand_path(allowed)

        if expanded == allowed_expanded:
            return True

    return False


def open_allowed_folder(path):
    if emergency_lock_is_active():
        update_presence_after_action("blocked")
        print("Emergency lock is active. Local control is disabled.")
        return

    expanded = expand_path(path)

    if not folder_is_allowed(path):
        print("Folder is not in allowlist.")
        print("Allowed folders:")
        for folder in LOCAL_ALLOWED_FOLDERS:
            print(f"- {folder}")
        return

    result = subprocess.run(
        ["open", expanded],
        capture_output=True,
        text=True
    )

    action = {
        "created_at": now_timestamp(),
        "type": "open_folder",
        "path": expanded,
        "returncode": result.returncode,
        "stderr": result.stderr
    }

    log_action(action)
    update_presence_after_action("folder_opened")

    if result.returncode == 0:
        print(f"Opened folder: {expanded}")
    else:
        print(result.stderr)


def approve_pending_action():
    action = load_pending_action()

    if action is None:
        print("No pending local action.")
        return

    print("\n=== APPROVE LOCAL ACTION ===")
    print(f"Type: {action.get('type')}")
    print(f"Command: {action.get('command')}")
    print(f"Reason: {action.get('reason')}")
    print(f"Approval phrase: {action.get('approval_phrase')}")

    phrase = input("Type approval phrase: ")

    if phrase != action.get("approval_phrase"):
        print("Approval phrase did not match.")
        return

    if action.get("type") == "shell_command":
        result = run_shell_command(action.get("command"), approved=True)
        clear_pending_action()
        print(format_command_result(result))
        return

    print("Unknown pending action type.")


def reject_pending_action():
    action = load_pending_action()

    if action is None:
        print("No pending local action.")
        return

    clear_pending_action()
    update_presence_after_action("blocked")
    print("Pending local action rejected.")


def format_command_result(result):
    text = "=== LOCAL COMMAND RESULT ===\n"

    if "message" in result:
        text += result["message"] + "\n"

    if "reason" in result:
        text += "Reason: " + result["reason"] + "\n"

    if "approval_phrase" in result:
        text += "Approval phrase: " + result["approval_phrase"] + "\n"

    if "returncode" in result:
        text += f"Return code: {result.get('returncode')}\n"

    if result.get("stdout"):
        text += "\nSTDOUT:\n"
        text += result.get("stdout") + "\n"

    if result.get("stderr"):
        text += "\nSTDERR:\n"
        text += result.get("stderr") + "\n"

    return text


def run_shell_interactive():
    print("\n=== LOCAL SHELL ACTION ===")
    print("Safe allowlist commands:")
    for command in LOCAL_SAFE_COMMANDS:
        print(f"- {command}")

    command = input("\nCommand: ").strip()

    if command == "":
        print("Command cannot be empty.")
        return

    result = run_shell_command(command)
    print(format_command_result(result))


def open_app_interactive():
    print("\n=== OPEN ALLOWED APP ===")
    print("Allowed apps:")
    for app in LOCAL_ALLOWED_APPS:
        print(f"- {app}")

    app = input("\nApp: ").strip()

    if app == "":
        print("App cannot be empty.")
        return

    open_allowed_app(app)


def open_folder_interactive():
    print("\n=== OPEN ALLOWED FOLDER ===")
    print("Allowed folders:")
    for folder in LOCAL_ALLOWED_FOLDERS:
        print(f"- {folder}")

    folder = input("\nFolder: ").strip()

    if folder == "":
        print("Folder cannot be empty.")
        return

    open_allowed_folder(folder)


def show_pending_action():
    action = load_pending_action()

    print("\n=== PENDING LOCAL ACTION ===")

    if action is None:
        print("No pending local action.")
        return

    print(json.dumps(action, indent=4))


def show_action_history():
    print("\n=== LOCAL ACTION HISTORY ===")

    actions = load_action_history()

    if not actions:
        print("No local actions yet.")
        return

    for action in actions:
        print(f"\n{action.get('created_at')} — {action.get('type')}")
        if "command" in action:
            print(f"Command: {action.get('command')}")
        if "app" in action:
            print(f"App: {action.get('app')}")
        if "path" in action:
            print(f"Path: {action.get('path')}")
        if "returncode" in action:
            print(f"Return code: {action.get('returncode')}")


def format_local_control_status():
    pending = load_pending_action()
    lock = emergency_lock_is_active()

    text = "=== SEED LOCAL CONTROL OS ===\n"
    text += f"Emergency lock: {lock}\n"
    text += f"Pending action: {pending is not None}\n"

    text += "\nAllowed apps:\n"
    for app in LOCAL_ALLOWED_APPS:
        text += f"- {app}\n"

    text += "\nAllowed folders:\n"
    for folder in LOCAL_ALLOWED_FOLDERS:
        text += f"- {folder}\n"

    text += "\nSafe commands:\n"
    for command in LOCAL_SAFE_COMMANDS:
        text += f"- {command}\n"

    text += "\nRule: Unknown or risky commands require approval. Forbidden commands stay blocked.\n"

    return text


def show_local_control_status():
    print("\n" + format_local_control_status())


def get_local_control_context_for_prompt():
    text = format_local_control_status()
    text += """
Local control rule:
Seed can perform limited computer actions through a strict allowlist.
Unknown commands require approval.
Forbidden commands remain blocked.
Seed must never claim it can control the computer beyond these tools.
"""
    return text