import os
import json
import difflib
import shutil
import subprocess
import sys
from datetime import datetime

from seed_config import (
    SELF_EDIT_BACKUP_DIR,
    SELF_EDIT_PENDING_FILE,
    SELF_EDIT_ALLOWED_EXTENSIONS,
    SELF_EDIT_PROTECTED_FILES,
    SELF_EDIT_PROTECTED_FOLDERS
)
from seed_llm import ask_llm


def timestamp():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def normalize_edit_path(path):
    path = path.strip()
    path = path.replace("\\", "/")

    if path.startswith("./"):
        path = path[2:]

    return os.path.normpath(path)


def is_safe_edit_path(path, must_exist=True):
    normalized = normalize_edit_path(path)

    if normalized == "":
        return False, "Path cannot be empty."

    if os.path.isabs(normalized):
        return False, "Absolute paths are not allowed."

    if normalized.startswith(".."):
        return False, "Parent directory paths are not allowed."

    parts = normalized.split(os.sep)

    for part in parts:
        if part in SELF_EDIT_PROTECTED_FOLDERS:
            return False, f"Protected folder: {part}"

    file_name = os.path.basename(normalized)

    if file_name in SELF_EDIT_PROTECTED_FILES:
        return False, f"Protected file: {file_name}"

    extension = os.path.splitext(normalized)[1]

    if extension not in SELF_EDIT_ALLOWED_EXTENSIONS:
        return False, f"Extension not allowed: {extension}"

    if must_exist and not os.path.exists(normalized):
        return False, "File does not exist."

    return True, normalized


def get_editable_files():
    editable_files = []

    for root, folders, files in os.walk("."):
        folders[:] = [
            folder for folder in folders
            if folder not in SELF_EDIT_PROTECTED_FOLDERS
        ]

        for file_name in files:
            path = os.path.join(root, file_name)
            normalized = normalize_edit_path(path)

            safe, result = is_safe_edit_path(normalized, must_exist=True)

            if safe:
                editable_files.append(result)

    editable_files.sort()
    return editable_files


def show_editable_files():
    print("\n=== SELF-EDITABLE FILES ===")

    files = get_editable_files()

    if not files:
        print("No editable files found.")
        return

    for number, path in enumerate(files, start=1):
        print(f"{number}. {path}")


def read_text_file(path):
    safe, result = is_safe_edit_path(path, must_exist=True)

    if not safe:
        return None, result

    with open(result, "r") as file:
        return file.read(), result


def show_file_for_edit():
    print("\n=== SELF-READ FILE ===")
    path = input("File path: ")

    content, result = read_text_file(path)

    if content is None:
        print(f"Cannot read file: {result}")
        return

    print(f"\n=== {result} ===")
    print(content)


def extract_revised_file(llm_response):
    start_marker = "<<<SEED_FILE_START>>>"
    end_marker = "<<<SEED_FILE_END>>>"

    if start_marker not in llm_response or end_marker not in llm_response:
        return None

    start_index = llm_response.index(start_marker) + len(start_marker)
    end_index = llm_response.index(end_marker)

    revised = llm_response[start_index:end_index]
    revised = revised.strip("\n")

    return revised + "\n"


def build_edit_prompt(target_path, original_content, instruction):
    return f"""
You are Seed's safe self-editing engine.

You are editing one file in Seed's local project.

Target file:
{target_path}

User instruction:
{instruction}

Rules:
- Return the FULL revised file, not a patch.
- Preserve existing behavior unless the instruction requires a change.
- Do not invent missing imports unless needed.
- Do not delete unrelated functions.
- Do not add explanation outside the markers.
- Do not use markdown fences.
- Put only the full revised file between these exact markers:

<<<SEED_FILE_START>>>
FULL FILE HERE
<<<SEED_FILE_END>>>

Original file:
{original_content}
"""


def save_pending_edit(pending_edit):
    with open(SELF_EDIT_PENDING_FILE, "w") as file:
        json.dump(pending_edit, file, indent=4)


def load_pending_edit():
    try:
        with open(SELF_EDIT_PENDING_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        print("Pending edit file is corrupted.")
        return None


def clear_pending_edit():
    if os.path.exists(SELF_EDIT_PENDING_FILE):
        os.remove(SELF_EDIT_PENDING_FILE)


def create_edit_proposal(runtime_context=None):
    print("\n=== SEED SELF-EDIT PROPOSAL ===")

    target_path = input("Target file: ")
    instruction = input("Edit instruction: ")

    if instruction.strip() == "":
        print("Edit instruction cannot be empty.")
        return

    original_content, safe_path = read_text_file(target_path)

    if original_content is None:
        print(f"Cannot edit file: {safe_path}")
        return

    prompt = build_edit_prompt(
        safe_path,
        original_content,
        instruction
    )

    print("\nSeed is generating an edit proposal...")

    llm_response = ask_llm(
        prompt,
        task_type="code",
        runtime_context=runtime_context
    )

    revised_content = extract_revised_file(llm_response)

    if revised_content is None:
        print("Seed could not produce a valid self-edit proposal.")
        print("The model did not return the required markers.")
        print("\nRaw response preview:")
        print(llm_response[:1000])
        return

    pending_edit = {
        "target_path": safe_path,
        "instruction": instruction,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "original_content": original_content,
        "revised_content": revised_content
    }

    save_pending_edit(pending_edit)

    print("Self-edit proposal created.")
    print("Use /self-diff to review it.")
    print("Use /self-apply to apply it after review.")


def get_pending_diff():
    pending_edit = load_pending_edit()

    if pending_edit is None:
        return None

    original = pending_edit.get("original_content", "")
    revised = pending_edit.get("revised_content", "")
    target_path = pending_edit.get("target_path", "unknown")

    diff_lines = difflib.unified_diff(
        original.splitlines(keepends=True),
        revised.splitlines(keepends=True),
        fromfile=f"{target_path} original",
        tofile=f"{target_path} revised"
    )

    return "".join(diff_lines)


def show_pending_diff():
    print("\n=== SELF-EDIT DIFF ===")

    pending_edit = load_pending_edit()

    if pending_edit is None:
        print("No pending edit.")
        return

    print(f"Target: {pending_edit.get('target_path')}")
    print(f"Instruction: {pending_edit.get('instruction')}")
    print(f"Created: {pending_edit.get('created_at')}")
    print()

    diff = get_pending_diff()

    if diff is None or diff == "":
        print("No differences found.")
        return

    print(diff)


def ensure_backup_folder():
    os.makedirs(SELF_EDIT_BACKUP_DIR, exist_ok=True)


def create_backup(target_path):
    ensure_backup_folder()

    base_name = os.path.basename(target_path)
    backup_name = f"{timestamp()}_{base_name}.bak"
    backup_path = os.path.join(SELF_EDIT_BACKUP_DIR, backup_name)

    shutil.copy2(target_path, backup_path)

    metadata = {
        "backup_path": backup_path,
        "target_path": target_path,
        "created_at": datetime.now().isoformat(timespec="seconds")
    }

    metadata_path = backup_path + ".json"

    with open(metadata_path, "w") as file:
        json.dump(metadata, file, indent=4)

    return backup_path


def apply_pending_edit():
    print("\n=== APPLY SELF-EDIT ===")

    pending_edit = load_pending_edit()

    if pending_edit is None:
        print("No pending edit.")
        return None

    target_path = pending_edit.get("target_path")
    revised_content = pending_edit.get("revised_content")

    safe, result = is_safe_edit_path(target_path, must_exist=True)

    if not safe:
        print(f"Cannot apply edit: {result}")
        return None

    print(f"Target: {target_path}")
    print("This will modify a Seed project file.")
    confirmation = input("Type APPLY to continue: ")

    if confirmation != "APPLY":
        print("Self-edit apply cancelled.")
        return None

    backup_path = create_backup(target_path)

    with open(target_path, "w") as file:
        file.write(revised_content)

    clear_pending_edit()

    print("Self-edit applied.")
    print(f"Backup created: {backup_path}")

    return target_path


def cancel_pending_edit():
    print("\n=== CANCEL SELF-EDIT ===")

    pending_edit = load_pending_edit()

    if pending_edit is None:
        print("No pending edit.")
        return

    clear_pending_edit()
    print("Pending self-edit cancelled.")


def run_python_syntax_check(path=None):
    print("\n=== SELF-EDIT TEST ===")

    if path is None or path.strip() == "":
        pending_edit = load_pending_edit()

        if pending_edit is not None:
            pending_path = pending_edit.get("target_path", "")

            if pending_path.endswith(".py"):
                path = pending_path
            else:
                path = ""

    if path is None:
        path = ""

    path = path.strip()

    if path == "":
        files = [
            file_path for file_path in get_editable_files()
            if file_path.endswith(".py")
        ]
    else:
        safe, result = is_safe_edit_path(path, must_exist=True)

        if not safe:
            print(f"Cannot test file: {result}")
            return False

        if not result.endswith(".py"):
            print("That file is not Python. Checking all Python files instead.")
            files = [
                file_path for file_path in get_editable_files()
                if file_path.endswith(".py")
            ]
        else:
            files = [result]

    if not files:
        print("No Python files to test.")
        return False

    all_ok = True

    for file_path in files:
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", file_path],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print(f"OK: {file_path}")
        else:
            all_ok = False
            print(f"FAILED: {file_path}")
            print(result.stderr)

    if all_ok:
        print("All syntax checks passed.")
    else:
        print("Some syntax checks failed.")

    return all_ok

def get_latest_backup_metadata():
    ensure_backup_folder()

    metadata_files = []

    for file_name in os.listdir(SELF_EDIT_BACKUP_DIR):
        if file_name.endswith(".bak.json"):
            metadata_files.append(os.path.join(SELF_EDIT_BACKUP_DIR, file_name))

    if not metadata_files:
        return None

    metadata_files.sort(key=os.path.getmtime, reverse=True)

    latest_metadata_path = metadata_files[0]

    with open(latest_metadata_path, "r") as file:
        return json.load(file)


def rollback_latest_edit():
    print("\n=== SELF-EDIT ROLLBACK ===")

    metadata = get_latest_backup_metadata()

    if metadata is None:
        print("No edit backups found.")
        return

    backup_path = metadata.get("backup_path")
    target_path = metadata.get("target_path")

    print(f"Latest backup: {backup_path}")
    print(f"Target file: {target_path}")

    confirmation = input("Type ROLLBACK to restore this backup: ")

    if confirmation != "ROLLBACK":
        print("Rollback cancelled.")
        return

    if not os.path.exists(backup_path):
        print("Backup file not found.")
        return

    shutil.copy2(backup_path, target_path)

    print("Rollback complete.")
    print(f"Restored: {target_path}")