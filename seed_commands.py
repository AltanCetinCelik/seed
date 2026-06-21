from seed_files import show_seed_core, show_memory_rules, show_first_contact
from seed_memory import (
    list_memories,
    delete_memory,
    save_memory_direct
)
from seed_journal import write_journal, read_journal
from seed_status import show_seed_status
from seed_brain import get_context_debug, search_memory_context
from seed_memory_tools import (
    list_memories_by_type,
    show_memory_stats,
    find_possible_duplicates
)
from seed_memory_suggester import suggest_memory
from seed_config import LOG_COMMAND_EVENTS
from seed_chat_logger import (
    log_system_event,
    log_command_event,
    log_developer_note,
    show_current_log_path,
    read_recent_log_lines
)
from seed_session_summarizer import (
    show_session_summary,
    save_last_summary_to_memory,
    save_last_summary_to_journal
)
from seed_project_inspector import (
    show_project_report,
    show_project_files,
    show_project_modules,
    show_version_info,
    save_project_report_to_memory
)


def show_chat_help():
    print("\n=== CHAT COMMANDS ===")
    print("/help or /commands = show commands")
    print("/exit or /quit = return to main menu")
    print("/save = manually save a memory")
    print("/suggest = manually generate a memory suggestion")
    print("/autosuggest = toggle automatic memory suggestions on/off")
    print("/memories = list Seed memories")
    print("/search = search relevant memories")
    print("/search-type = list memories by type")
    print("/memory-stats or /stats = show memory statistics")
    print("/duplicates = find possible duplicate memories")
    print("/forget = delete memory by number")
    print("/journal = write a journal entry")
    print("/journal-read = read journal entries")
    print("/core = show Seed Core")
    print("/rules = show Memory Rules")
    print("/first-contact = show First Contact")
    print("/status = show Seed status")
    print("/debug = show current prompt context")
    print("/clear-session = clear temporary chat history")
    print("/config = show Seed configuration")
    print("/log = show current chat log path")
    print("/log-note = write a note into current chat log")
    print("/log-read = read recent lines from current chat log")
    print("/summary = summarize current chat session")
    print("/summary-save-memory = save last summary to memory")
    print("/summary-save-journal = save last summary to journal")
    print("/project = show Seed project report")
    print("/files = show project files")
    print("/modules = show Python modules")
    print("/version = show Seed version info")
    print("/project-save-memory = save project report to memory")


def save_memory_from_chat():
    print("\n=== SAVE MEMORY FROM CHAT ===")

    memory_type = input("Memory type: ")
    content = input("Content: ")

    try:
        importance = int(input("Importance (1-5): "))
    except ValueError:
        print("Invalid importance. Please enter a number between 1 and 5.")
        return None

    saved = save_memory_direct(memory_type, content, importance)

    if saved:
        print("Memory saved from chat.")
        return {
            "type": memory_type,
            "content": content,
            "importance": importance
        }

    return None


def manual_memory_suggestion(session_history, chat_state):
    print("\n=== MANUAL MEMORY SUGGESTION ===")

    user_message = input("What happened / what did we do?: ")

    if user_message == "":
        print("Suggestion input cannot be empty.")
        return

    seed_answer = "Manual suggestion requested by user."

    suggestion = suggest_memory(user_message, seed_answer)

    if suggestion is None:
        print("No suggestion generated.")
        return

    print("\n=== SUGGESTED MEMORY ===")
    print(f"Type: {suggestion['type']}")
    print(f"Content: {suggestion['content']}")
    print(f"Importance: {suggestion['importance']}")

    choice = input("Save this memory? (y/n): ")

    if choice.lower() == "y":
        saved = save_memory_direct(
            suggestion["type"],
            suggestion["content"],
            suggestion["importance"]
        )

        if saved:
            print("Suggested memory saved.")
            log_system_event(
                chat_state.get("log_path"),
                (
                    f"Manually approved suggested memory: "
                    f"[{suggestion['type']}] "
                    f"{suggestion['content']} "
                    f"Importance: {suggestion['importance']}"
                )
            )

            session_history.append({
                "role": "System",
                "content": (
                    f"User manually approved and saved suggested memory: "
                    f"[{suggestion['type']}] "
                    f"{suggestion['content']} "
                    f"Importance: {suggestion['importance']}"
                )
            })
    else:
        print("Suggested memory skipped.")
        log_system_event(
            chat_state.get("log_path"),
            "Manual suggested memory skipped."
        )


def handle_memory_suggestion(user_message, seed_answer, session_history, chat_state=None):
    suggestion = suggest_memory(user_message, seed_answer)

    if suggestion is None:
        return

    print("\n=== SUGGESTED MEMORY ===")
    print(f"Type: {suggestion['type']}")
    print(f"Content: {suggestion['content']}")
    print(f"Importance: {suggestion['importance']}")

    choice = input("Save this memory? (y/n): ")

    if choice.lower() == "y":
        saved = save_memory_direct(
            suggestion["type"],
            suggestion["content"],
            suggestion["importance"]
        )

        if saved:
            print("Suggested memory saved.")

            session_history.append({
                "role": "System",
                "content": (
                    f"User approved and saved suggested memory: "
                    f"[{suggestion['type']}] "
                    f"{suggestion['content']} "
                    f"Importance: {suggestion['importance']}"
                )
            })

            if chat_state is not None:
                log_path = chat_state.get("log_path")
                log_system_event(
                    log_path,
                    (
                        f"Approved suggested memory: "
                        f"[{suggestion['type']}] "
                        f"{suggestion['content']} "
                        f"Importance: {suggestion['importance']}"
                    )
                )
    else:
        print("Suggested memory skipped.")

        if chat_state is not None:
            log_path = chat_state.get("log_path")
            log_system_event(log_path, "Suggested memory skipped.")


def handle_chat_command(user_message, session_history, chat_state):
    command = user_message.strip().lower()
    log_path = chat_state.get("log_path")

    if command.startswith("/") and LOG_COMMAND_EVENTS:
        log_command_event(log_path, command)

    if command in ["/exit", "/quit"]:
        print("Leaving Seed chat...")
        return "exit"
    if command == "/config":
        show_config()
        return "handled"

    if command in ["/help", "/commands"]:
        show_chat_help()
        return "handled"

    if command == "/autosuggest":
        chat_state["autosuggest_enabled"] = not chat_state["autosuggest_enabled"]

        if chat_state["autosuggest_enabled"]:
            print("Autosuggest is now ON.")
        else:
            print("Autosuggest is now OFF.")
        log_system_event(
            log_path,
            f"Autosuggest set to {chat_state['autosuggest_enabled']}"
        )

        return "handled"

    if command == "/save":
        saved_memory = save_memory_from_chat()

        if saved_memory is not None:
            session_history.append({
                "role": "System",
                "content": (
                    f"User just saved a long-term memory: "
                    f"[{saved_memory['type']}] "
                    f"{saved_memory['content']} "
                    f"Importance: {saved_memory['importance']}"
                )
            })
            log_system_event(
                log_path,
                (
                    f"Manual memory saved: "
                    f"[{saved_memory['type']}] "
                    f"{saved_memory['content']} "
                    f"Importance: {saved_memory['importance']}"
                )
            )

        return "handled"

    if command == "/suggest":
        manual_memory_suggestion(session_history)
        return "handled"

    if command == "/memories":
        list_memories()
        return "handled"

    if command == "/search":
        search_query = input("Search query: ")
        print("\n=== MEMORY SEARCH RESULTS ===")
        print(search_memory_context(search_query))
        return "handled"

    if command == "/search-type":
        memory_type = input("Memory type: ")
        list_memories_by_type(memory_type)
        return "handled"

    if command in ["/memory-stats", "/stats"]:
        show_memory_stats()
        return "handled"

    if command == "/duplicates":
        find_possible_duplicates()
        return "handled"

    if command == "/forget":
        print("\n=== FORGET MEMORY FROM CHAT ===")
        delete_memory()
        log_system_event(log_path, "Forget memory command used.")
        return "handled"

    if command == "/journal":
        journal_entry = write_journal()

        if journal_entry is not None:
            session_history.append({
                "role": "System",
                "content": (
                    f"User wrote this journal entry during this chat session: "
                    f"{journal_entry}"
                )
            })
            log_system_event(
                    log_path,
                    f"Journal entry written: {journal_entry}"
                )

        return "handled"

    if command == "/journal-read":
        read_journal()
        return "handled"

    if command == "/core":
        show_seed_core()
        return "handled"

    if command == "/rules":
        show_memory_rules()
        return "handled"

    if command == "/first-contact":
        show_first_contact()
        return "handled"
    
    if command == "/summary":
        show_session_summary(session_history, chat_state)
        return "handled"

    if command == "/summary-save-memory":
        save_last_summary_to_memory(chat_state)
        return "handled"

    if command == "/summary-save-journal":
        save_last_summary_to_journal(chat_state)
        return "handled"
    
    if command == "/log":
        show_current_log_path(log_path)
        return "handled"

    if command == "/log-note":
        log_developer_note(log_path)
        return "handled"

    if command == "/log-read":
        read_recent_log_lines(log_path)
        return "handled"


    if command == "/project":
        show_project_report()
        return "handled"

    if command == "/files":
        show_project_files()
        return "handled"

    if command == "/modules":
        show_project_modules()
        return "handled"

    if command == "/version":
        show_version_info()
        return "handled"

    if command == "/project-save-memory":
        save_project_report_to_memory(chat_state)
        return "handled"

    if command == "/status":
        show_seed_status()
        return "handled"

    if command == "/debug":
        debug_query = input("Debug query: ")
        print(get_context_debug(session_history, debug_query))
        return "handled"

    if command == "/clear-session":
        session_history.clear()
        print("Temporary session history cleared.")
        log_system_event(log_path, "Temporary session history cleared.")
        return "handled"

    if command.startswith("/"):
        print("Unknown command. Type /help to see available commands.")
        return "handled"

    return "normal"

def show_config():
    from seed_config import (
        SEED_VERSION,
        MODEL_NAME,
        OLLAMA_URL,
        MEMORY_SEARCH_LIMIT,
        RECENT_JOURNAL_LIMIT,
        SESSION_HISTORY_LIMIT,
        AUTOSUGGEST_DEFAULT,
        SEED_MODE
    )

    print("\n=== SEED CONFIG ===")
    print(f"Version: {SEED_VERSION}")
    print(f"Model: {MODEL_NAME}")
    print(f"Ollama URL: {OLLAMA_URL}")
    print(f"Memory search limit: {MEMORY_SEARCH_LIMIT}")
    print(f"Recent journal limit: {RECENT_JOURNAL_LIMIT}")
    print(f"Session history limit: {SESSION_HISTORY_LIMIT}")
    print(f"Autosuggest default: {AUTOSUGGEST_DEFAULT}")
    print(f"Mode: {SEED_MODE}")