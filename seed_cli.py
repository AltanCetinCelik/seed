from seed_files import show_seed_core, show_memory_rules, show_first_contact
from seed_memory import add_memory, list_memories, search_memories, delete_memory
from seed_journal import write_journal, read_journal
from seed_status import show_seed_status
from seed_brain import ask_seed
from seed_commands import handle_chat_command, handle_memory_suggestion
from seed_config import SEED_VERSION, AUTOSUGGEST_DEFAULT, DEFAULT_CHAT_MODEL
from seed_chat_logger import (
    create_chat_log,
    log_user_message,
    log_seed_answer,
    log_system_event,
    close_chat_log
)
from seed_visuals import show_seed_hud_screen
from seed_personality import show_personality, get_startup_greeting


def talk_to_seed():
    session_history = []
    log_path = create_chat_log()

    chat_state = {
        "autosuggest_enabled": AUTOSUGGEST_DEFAULT,
        "log_path": log_path,
        "last_summary": None,
        "active_model": DEFAULT_CHAT_MODEL,
        "task_models": {},
        "pending_memory_draft": None,
        "pending_agent_plan": None,
        "last_agent_run": None,
        "last_self_review": None,
        "pending_skill_plan": None,
        "last_skill_run": None
}

    print("\n=== TALK TO SEED ===")
    print("Type /help to show chat commands.")
    print("Type /exit to return to the main menu.")
    print(f"Chat log started: {log_path}")

    log_system_event(log_path, "Talk to Seed session started.")

    while True:
        user_message = input("\nYou: ")

        if user_message == "":
            print("Message cannot be empty.")
            continue

        command_result = handle_chat_command(
            user_message,
            session_history,
            chat_state
        )

        if command_result == "exit":
            close_chat_log(log_path)
            break

        if command_result == "handled":
            continue

        log_user_message(log_path, user_message)

        print("\nSeed is thinking...")

        answer = ask_seed(user_message, session_history, chat_state)

        print("\n=== SEED ===")
        print(answer)

        log_seed_answer(log_path, answer)

        session_history.append({
            "role": "User",
            "content": user_message
        })

        session_history.append({
            "role": "Seed",
            "content": answer
        })

        if chat_state["autosuggest_enabled"]:
            handle_memory_suggestion(
                user_message,
                answer,
                session_history,
                chat_state
            )
def menu():
    print(f"\n=== SEED {SEED_VERSION} ===")
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
    print("12. Seed HUD")
    print("13. Show Seed Personality")
    print("14. Exit")

    choice = input("Enter your choice: ")
    return choice


def main():
    while True:
        print(get_startup_greeting())
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
            show_seed_hud_screen()

        elif choice == "13":
            show_personality()

        elif choice == "14":
            print("Goodbye.")
            break


        else:
            print("Invalid choice. Please try again.")


main()