import json

MEMORY_FILE = "seed_memory.json"
JOURNAL_FILE = "seed_journal.txt"


def load_memories():
    try:
        with open(MEMORY_FILE, "r") as file:
            return json.load(file)

    except FileNotFoundError:
        print("Seed memory file not found. Starting with empty memory.")
        return []

    except json.JSONDecodeError:
        print("Seed memory file is empty or broken. Starting with empty memory.")
        return []
def save_memories():
    with open(MEMORY_FILE, "w") as file:
        json.dump(memories, file, indent=4)
memories = load_memories()

def add_memory():
    memory_type = input("Memory type: ")
    content = input("Content: ")

    if content == "":
        print("Memory content cannot be empty.")
        return

    try:
        importance = int(input("Importance (1-5): "))
    except ValueError:
        print("Invalid importance. Please enter a number between 1 and 5.")
        return

    if importance < 1 or importance > 5:
        print("Importance must be between 1 and 5.")
        return

    memory = {
        "type": memory_type,
        "content": content,
        "importance": importance
    }

    memories.append(memory)
    save_memories()

    print("Seed memory added.")

def list_memories():
    if not memories:
        print("No Seed memories found.")
        return

    print("\n=== SEED MEMORIES ===")

    for number, memory in enumerate(memories, start=1):
        print(
            f"{number}. "
            f"[{memory['type']}] "
            f"{memory['content']} "
            f"Importance: {memory['importance']}"
        )

def search_memories():
    if not memories:
        print("No Seed memories found.")
        return

    search_type = input("Enter memory type to search: ")

    found_memories = []

    for memory in memories:
        if memory["type"] == search_type:
            found_memories.append(memory)

    if not found_memories:
        print("No matching Seed memories found.")
        return

    print("\n=== SEARCH RESULTS ===")

    for number, memory in enumerate(found_memories, start=1):
        print(
            f"{number}. "
            f"[{memory['type']}] "
            f"{memory['content']} "
            f"Importance: {memory['importance']}"
        )
def delete_memory():
    if not memories:
        print("No Seed memories to delete.")
        return

    list_memories()

    try:
        delete_number = int(input("Enter the number of the memory to delete: "))
    except ValueError:
        print("Invalid number. Please enter a valid memory number.")
        return

    delete_index = delete_number - 1

    if delete_index < 0 or delete_index >= len(memories):
        print("Invalid memory number.")
        return

    confirm = input("Type DELETE to confirm: ")

    if confirm == "DELETE":
        deleted_memory = memories.pop(delete_index)
        save_memories()
        print(f"Deleted Seed memory: {deleted_memory['content']}")
    else:
        print("Delete cancelled.")

def write_journal():
    entry = input("Journal entry: ")

    if entry == "":
        print("Journal entry cannot be empty.")
        return

    with open(JOURNAL_FILE, "a") as file:
        file.write(entry + "\n")

    print("Journal entry saved.")

def read_journal():
    try:
        with open(JOURNAL_FILE, "r") as file:
            content = file.read()

    except FileNotFoundError:
        print("Seed journal file not found.")
        return

    if content == "":
        print("No journal entries found.")
        return

    print("\n=== SEED JOURNAL ===")
    print(content)

def show_memory_rules():
    with open("memory_rules.md", "r") as file:
        content = file.read()

    print("\n=== MEMORY RULES ===")
    print(content)

def show_first_contact():
    with open("first_contact.md", "r") as file:
        content = file.read()

    print("\n=== FIRST CONTACT ===")
    print(content)

def menu():
    print("\n=== SEED v0.1 ===")
    print("1. Show Seed Core")
    print("2. Add Seed Memory")
    print("3. List Seed Memories")
    print("4. Search Seed Memories")
    print("5. Delete Seed Memory")
    print("6. Write Journal Entry")
    print("7. Read Journal Entries")
    print("8. Show Memory Rules")
    print("9. Show First Contact")
    print("10. Exit")

    choice = input("Enter your choice: ")
    return choice

def show_seed_core():
    with open("Seed_Core.md", "r") as file:
        content = file.read()
        print(content)

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
            print("Exiting Seed...")
            break

        else:
            print("Invalid choice. Please try again.")


main()




