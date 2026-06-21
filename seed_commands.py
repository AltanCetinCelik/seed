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


def manual_memory_suggestion(session_history):
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


def handle_memory_suggestion(user_message, seed_answer, session_history):
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
    else:
        print("Suggested memory skipped.")


def handle_chat_command(user_message, session_history, chat_state):
    command = user_message.strip().lower()

    if command in ["/exit", "/quit"]:
        print("Leaving Seed chat...")
        return "exit"

    if command in ["/help", "/commands"]:
        show_chat_help()
        return "handled"

    if command == "/autosuggest":
        chat_state["autosuggest_enabled"] = not chat_state["autosuggest_enabled"]

        if chat_state["autosuggest_enabled"]:
            print("Autosuggest is now ON.")
        else:
            print("Autosuggest is now OFF.")

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
        return "handled"

    if command.startswith("/"):
        print("Unknown command. Type /help to see available commands.")
        return "handled"

    return "normal"