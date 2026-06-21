from datetime import datetime
import json



ALLOWED_TYPES = [
    "technical_progress",
    "mistake",
    "reflection",
    "seed_boundary",
    "job_goal",
    "seed_identity",
    "personal_rule"
]
MEMORY_FILE = "seed_memory.json"

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
    if memory_type not in ALLOWED_TYPES:
        print("Invalid memory type.")
        print("Allowed types:")
        for allowed_type in ALLOWED_TYPES:
         print(f"- {allowed_type}")
        return
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
        "importance": importance,
        "created_at": datetime.now().isoformat(timespec="seconds")
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
            f"Importance: {memory['importance']} "
            f"Created at: {memory.get('created_at', 'unknown time')}"
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
            f"Importance: {memory['importance']} "
            f"Created at: {memory.get('created_at', 'unknown time')}"
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

def save_memory_direct(memory_type, content, importance):
    if memory_type not in ALLOWED_TYPES:
        print("Invalid memory type.")
        print("Allowed types:")
        for allowed_type in ALLOWED_TYPES:
            print(f"- {allowed_type}")
        return False

    if content == "":
        print("Memory content cannot be empty.")
        return False

    if importance < 1 or importance > 5:
        print("Importance must be between 1 and 5.")
        return False

    memory = {
        "type": memory_type,
        "content": content,
        "importance": importance,
        "created_at": datetime.now().isoformat(timespec="seconds")
    }

    memories.append(memory)
    save_memories()

    return True