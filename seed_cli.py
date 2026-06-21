from seed_files import show_seed_core, show_memory_rules, show_first_contact
from seed_memory import add_memory, list_memories, search_memories, delete_memory
from seed_journal import write_journal, read_journal
from seed_status import show_seed_status
from seed_brain import ask_seed, get_context_debug
from seed_memory import add_memory, list_memories, search_memories, delete_memory, save_memory_direct
from seed_brain import ask_seed, get_context_debug, search_memory_context
from seed_memory_tools import list_memories_by_type, show_memory_stats, find_possible_duplicates

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

def talk_to_seed():
    session_history = []

    print("\n=== TALK TO SEED ===")
    print("Type /exit to return to the main menu.")
    print("Type /save to save a memory.")
    print("Type /journal to write a journal entry.")
    print("Type /help to show chat commands.")
    print("Type /debug to show context debug information.")
    print("Type /memories to list Seed memories.")
    print("Type /status to show Seed status.")

    while True:
        user_message = input("\nYou: ")

        if user_message == "":
            print("Message cannot be empty.")
            continue

        if user_message == "/exit":
            print("Leaving Seed chat...")
            break

        if user_message == "/help":
            print("\n=== CHAT COMMANDS ===")
            print("/exit = return to main menu")
            print("/save = save a memory")
            print("/memories = list Seed memories")
            print("/status = show Seed status")
            print("/debug = show context debug information")
            print("/help = show commands")
            print("/search = search relevant memories")
            print("/search = search relevant memories")
            print("/search-type = list memories by type")
            print("/memory-stats = show memory statistics")
            print("/duplicates = find possible duplicate memories")
            continue
        if user_message == "/memories":
            list_memories()
            continue
        if user_message == "/search-type":
            memory_type = input("Memory type: ")
            list_memories_by_type(memory_type)
            continue

        if user_message == "/memory-stats":
            show_memory_stats()
            continue

        if user_message == "/duplicates":
            find_possible_duplicates()
            continue
        if user_message == "/debug":
            debug_query = input("Debug query: ")
            print(get_context_debug(session_history, debug_query))
            continue
        if user_message == "/search":
            search_query = input("Search query: ")
            print("\n=== MEMORY SEARCH RESULTS ===")
            print(search_memory_context(search_query))
            continue

        if user_message == "/status":
            show_seed_status()
            continue
        if user_message == "/journal":
            journal_entry = write_journal()

            if journal_entry is not None:
                session_history.append({
                    "role": "System",
                    "content": f"User wrote this journal entry during this chat session: {journal_entry}"
            })

            continue
        if user_message == "/save":
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

             continue

        print("\nSeed is thinking...")

        answer = ask_seed(user_message, session_history)

        print("\n=== SEED ===")
        print(answer)

        session_history.append({
            "role": "User",
            "content": user_message
        })

        session_history.append({
            "role": "Seed",
            "content": answer
        })


def menu():
    print("\n=== SEED v0.2.9 ===")
    print("1. Show Seed Core")
    print("2. Add Seed Memory")
    print("3. List Seed Memories")
    print("4. Search Seed Memories")
    print("5. Delete Seed Memory")
    print("6. Write Journal Entry")
    print("7. Read Journal Entries")
    print("8. Show Memory Rules")
    print("9. Show First Contact")
    print("10. Talk to Seed")
    print("11. Show Seed Status")
    print("12. Exit")

    choice = input("Enter your choice: ")
    return choice


def main():
    while True:
        choice = menu()

        if choice == "1":
            show_seed_core()

        elif choice == "2":
            add_memory()

        elif choice == "3":
            list_memories()

        elif choice == "4":
            search_memories()

        elif choice == "5":
            delete_memory()

        elif choice == "6":
            write_journal()

        elif choice == "7":
            read_journal()

        elif choice == "8":
            show_memory_rules()

        elif choice == "9":
            show_first_contact()

        elif choice == "10":
            talk_to_seed()

        elif choice == "11":
            show_seed_status()

        elif choice == "12":
            print("Exiting Seed...")
            break

        else:
            print("Invalid choice. Please try again.")


main()