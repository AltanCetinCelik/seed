import os

from seed_config import (
    PROJECT_ROOT,
    PROJECT_IGNORED_FOLDERS,
    PROJECT_IGNORED_FILES,
    SEED_VERSION,
    MODEL_NAME,
    OLLAMA_URL
)
from seed_memory import save_memory_direct
from seed_chat_logger import log_system_event


def should_ignore_folder(folder_name):
    return folder_name in PROJECT_IGNORED_FOLDERS


def should_ignore_file(file_name):
    return file_name in PROJECT_IGNORED_FILES


def get_project_files():
    project_files = []

    for root, folders, files in os.walk(PROJECT_ROOT):
        folders[:] = [
            folder for folder in folders
            if not should_ignore_folder(folder)
        ]

        for file_name in files:
            if should_ignore_file(file_name):
                continue

            path = os.path.join(root, file_name)
            project_files.append(path)

    project_files.sort()
    return project_files


def get_python_modules():
    files = get_project_files()

    modules = []

    for path in files:
        if path.endswith(".py"):
            modules.append(path)

    return modules


def count_lines_in_file(path):
    try:
        with open(path, "r") as file:
            return len(file.readlines())
    except UnicodeDecodeError:
        return 0
    except FileNotFoundError:
        return 0


def get_file_report():
    files = get_project_files()

    if not files:
        return "No project files found."

    report = "=== PROJECT FILES ===\n"

    for number, path in enumerate(files, start=1):
        line_count = count_lines_in_file(path)
        report += f"{number}. {path} ({line_count} lines)\n"

    return report


def get_module_report():
    modules = get_python_modules()

    if not modules:
        return "No Python modules found."

    report = "=== PYTHON MODULES ===\n"

    for number, path in enumerate(modules, start=1):
        line_count = count_lines_in_file(path)
        report += f"{number}. {path} ({line_count} lines)\n"

    return report


def describe_known_module(path):
    descriptions = {
        "./seed_cli.py": "Main menu and Talk to Seed chat loop.",
        "./seed_commands.py": "Slash command router for chat mode.",
        "./seed_brain.py": "Prompt builder and Ollama connection.",
        "./seed_memory.py": "JSON memory loading, saving, listing, searching, and deleting.",
        "./seed_memory_tools.py": "Memory search helpers, stats, type filtering, aliases, and duplicate detection.",
        "./seed_memory_suggester.py": "Approved memory suggestion logic.",
        "./seed_journal.py": "Journal writing, reading, and recent journal context.",
        "./seed_files.py": "Markdown file readers for Seed Core and related documents.",
        "./seed_status.py": "Seed status screen.",
        "./seed_config.py": "Central configuration.",
        "./seed_chat_logger.py": "Conversation logging system.",
        "./seed_session_summarizer.py": "Session summary generation and saving."
    }

    return descriptions.get(path, "Project file/module.")


def get_project_report():
    files = get_project_files()
    modules = get_python_modules()

    report = "=== SEED PROJECT REPORT ===\n"
    report += f"Version: {SEED_VERSION}\n"
    report += f"Model: {MODEL_NAME}\n"
    report += f"Ollama URL: {OLLAMA_URL}\n"
    report += f"Total files: {len(files)}\n"
    report += f"Python modules: {len(modules)}\n\n"

    report += "=== MODULE OVERVIEW ===\n"

    for module in modules:
        report += f"- {module}: {describe_known_module(module)}\n"

    report += "\n=== PROJECT LAYERS ===\n"
    report += "- seed_cli.py controls the main user interface.\n"
    report += "- seed_commands.py routes slash commands.\n"
    report += "- seed_brain.py connects Seed to the local LLM.\n"
    report += "- seed_memory.py and seed_memory_tools.py manage long-term memory.\n"
    report += "- seed_journal.py manages journal entries.\n"
    report += "- seed_chat_logger.py stores raw chat logs.\n"
    report += "- seed_session_summarizer.py turns sessions/logs into summaries.\n"
    report += "- seed_config.py centralizes settings.\n"

    return report


def show_project_report():
    print("\n" + get_project_report())


def show_project_files():
    print("\n" + get_file_report())


def show_project_modules():
    print("\n" + get_module_report())


def show_version_info():
    print("\n=== VERSION INFO ===")
    print(f"Seed version: {SEED_VERSION}")
    print(f"Model: {MODEL_NAME}")
    print(f"Ollama URL: {OLLAMA_URL}")


def save_project_report_to_memory(chat_state):
    from seed_config import (
        PROJECT_REPORT_MEMORY_TYPE,
        PROJECT_REPORT_IMPORTANCE
    )

    report = get_project_report()

    print("\n=== PROJECT REPORT MEMORY SAVE ===")
    print(report)

    choice = input("Save this project report to memory? (y/n): ")

    if choice.lower() != "y":
        print("Project report memory save skipped.")
        log_system_event(
            chat_state.get("log_path"),
            "Project report memory save skipped."
        )
        return

    saved = save_memory_direct(
        PROJECT_REPORT_MEMORY_TYPE,
        f"Seed project report: {report}",
        PROJECT_REPORT_IMPORTANCE
    )

    if saved:
        print("Project report saved to memory.")
        log_system_event(
            chat_state.get("log_path"),
            "Project report saved to memory."
        )

def is_project_related_question(user_prompt):
    prompt = user_prompt.lower()

    project_keywords = [
        "file",
        "files",
        "module",
        "modules",
        "project",
        "architecture",
        "structure",
        "codebase",
        "version",
        "your code",
        "your folder",
        "what do you have",
        "what are you made of",
        "seed project",
        "inspect",
        "self-inspection"
    ]

    for keyword in project_keywords:
        if keyword in prompt:
            return True

    return False


def get_project_context_for_prompt(user_prompt):
    from seed_config import PROJECT_CONTEXT_ENABLED, PROJECT_CONTEXT_FILE_LIMIT

    if not PROJECT_CONTEXT_ENABLED:
        return "Project context injection is disabled."

    if not is_project_related_question(user_prompt):
        return "No live project context injected for this prompt."

    files = get_project_files()
    modules = get_python_modules()

    context = "=== LIVE PROJECT CONTEXT ===\n"
    context += f"Seed version: {SEED_VERSION}\n"
    context += f"Model: {MODEL_NAME}\n"
    context += f"Total files found: {len(files)}\n"
    context += f"Python modules found: {len(modules)}\n\n"

    context += "Python modules:\n"
    for module in modules:
        context += f"- {module}: {describe_known_module(module)}\n"

    context += "\nProject files:\n"
    for path in files[:PROJECT_CONTEXT_FILE_LIMIT]:
        context += f"- {path}\n"

    if len(files) > PROJECT_CONTEXT_FILE_LIMIT:
        context += f"...and {len(files) - PROJECT_CONTEXT_FILE_LIMIT} more files.\n"

    context += """
Project context rule:
If the user asks about Seed's files, modules, version, architecture, or project structure,
use this live project context instead of guessing from memory.
"""

    return context