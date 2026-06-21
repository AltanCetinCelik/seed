import os
from datetime import datetime

from seed_config import CHAT_LOG_DIR, CHAT_LOG_TAIL_LINES


def ensure_log_folder():
    os.makedirs(CHAT_LOG_DIR, exist_ok=True)


def current_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def filename_timestamp():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def create_chat_log():
    ensure_log_folder()

    filename = f"chat_{filename_timestamp()}.txt"
    log_path = os.path.join(CHAT_LOG_DIR, filename)

    with open(log_path, "w") as file:
        file.write("=== SEED CHAT LOG ===\n")
        file.write(f"Started at: {current_timestamp()}\n")
        file.write("=" * 40 + "\n\n")

    return log_path


def write_log_line(log_path, label, content):
    if log_path is None:
        return

    try:
        with open(log_path, "a") as file:
            file.write(f"[{current_timestamp()}] {label}:\n")
            file.write(f"{content}\n\n")
    except OSError as error:
        print(f"Log error: {error}")


def log_user_message(log_path, message):
    write_log_line(log_path, "USER", message)


def log_seed_answer(log_path, answer):
    write_log_line(log_path, "SEED", answer)


def log_system_event(log_path, event):
    write_log_line(log_path, "SYSTEM", event)


def log_command_event(log_path, command):
    write_log_line(log_path, "COMMAND", command)


def log_developer_note(log_path):
    print("\n=== LOG NOTE ===")
    note = input("Note: ")

    if note == "":
        print("Log note cannot be empty.")
        return

    log_system_event(log_path, f"Developer note: {note}")
    print("Log note saved.")


def show_current_log_path(log_path):
    print("\n=== CURRENT CHAT LOG ===")

    if log_path is None:
        print("No active chat log.")
        return

    print(log_path)


def read_recent_log_lines(log_path, line_count=CHAT_LOG_TAIL_LINES):
    print("\n=== RECENT CHAT LOG ===")

    if log_path is None:
        print("No active chat log.")
        return

    try:
        with open(log_path, "r") as file:
            lines = file.readlines()
    except FileNotFoundError:
        print("Current log file was not found.")
        return

    if not lines:
        print("Log file is empty.")
        return

    recent_lines = lines[-line_count:]

    for line in recent_lines:
        print(line.rstrip())


def close_chat_log(log_path):
    log_system_event(log_path, "Chat session closed.")