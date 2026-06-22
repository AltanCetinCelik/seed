from seed_config import (
    SUMMARY_MAX_LOG_LINES,
    SUMMARY_MEMORY_TYPE,
    SUMMARY_IMPORTANCE
)
from seed_llm import ask_llm
from seed_memory import save_memory_direct
from seed_journal import write_journal_direct
from seed_chat_logger import log_system_event


def format_session_for_summary(session_history):
    if not session_history:
        return "No current session messages."

    text = ""

    for message in session_history:
        role = message.get("role", "Unknown")
        content = message.get("content", "")

        text += f"{role}: {content}\n"

    return text


def read_log_for_summary(log_path):
    if log_path is None:
        return "No active log file."

    try:
        with open(log_path, "r") as file:
            lines = file.readlines()
    except FileNotFoundError:
        return "Current log file was not found."

    if not lines:
        return "Current log file is empty."

    recent_lines = lines[-SUMMARY_MAX_LOG_LINES:]
    return "".join(recent_lines)


def build_summary_prompt(session_history, log_path):
    session_text = format_session_for_summary(session_history)
    log_text = read_log_for_summary(log_path)

    return f"""
You are Seed.

Create a clean session summary for Altan.

Use the current session history and the current chat log.

Do not invent events.
Do not exaggerate.
Focus on:
- what was built
- what was changed
- bugs/errors encountered
- fixes applied
- important design decisions
- next recommended step

Write it in clear bullet points.

Current session history:
{session_text}

Current chat log:
{log_text}
"""


def generate_session_summary(session_history, log_path, runtime_context=None):
    prompt = build_summary_prompt(session_history, log_path)

    summary = ask_llm(
        prompt,
        task_type="summary",
        runtime_context=runtime_context
    )

    return summary


def show_session_summary(session_history, chat_state):
    log_path = chat_state.get("log_path")
    summary = generate_session_summary(session_history, log_path, chat_state)

    print("\n=== SESSION SUMMARY ===")
    print(summary)

    log_system_event(log_path, "Session summary generated.")

    chat_state["last_summary"] = summary

    return summary


def save_last_summary_to_memory(chat_state):
    summary = chat_state.get("last_summary")

    if summary is None:
        print("No summary found. Use /summary first.")
        return

    print("\n=== SAVE SUMMARY TO MEMORY ===")
    print(summary)

    choice = input("Save this summary as memory? (y/n): ")

    if choice.lower() != "y":
        print("Summary memory save skipped.")
        log_system_event(chat_state.get("log_path"), "Summary memory save skipped.")
        return

    saved = save_memory_direct(
        SUMMARY_MEMORY_TYPE,
        f"Session summary: {summary}",
        SUMMARY_IMPORTANCE
    )

    if saved:
        print("Summary saved to memory.")
        log_system_event(chat_state.get("log_path"), "Summary saved to memory.")


def save_last_summary_to_journal(chat_state):
    summary = chat_state.get("last_summary")

    if summary is None:
        print("No summary found. Use /summary first.")
        return

    print("\n=== SAVE SUMMARY TO JOURNAL ===")
    print(summary)

    choice = input("Save this summary to journal? (y/n): ")

    if choice.lower() != "y":
        print("Summary journal save skipped.")
        log_system_event(chat_state.get("log_path"), "Summary journal save skipped.")
        return

    saved = write_journal_direct(f"Session summary:\n{summary}")

    if saved:
        print("Summary saved to journal.")
        log_system_event(chat_state.get("log_path"), "Summary saved to journal.")