import os

from seed_memory import memories, ALLOWED_TYPES


def file_status(filename):
    if os.path.exists(filename):
        return "found"
    else:
        return "missing"


def show_seed_status():
    print("\n=== SEED STATUS ===")
    print("Version: v0.2.9")
    print(f"Core file: {file_status('Seed_Core.md')}")
    print(f"Memory rules file: {file_status('memory_rules.md')}")
    print(f"First contact file: {file_status('first_contact.md')}")
    print(f"Memory file: {file_status('seed_memory.json')}")
    print(f"Journal file: {file_status('seed_journal.txt')}")
    print(f"Number of memories: {len(memories)}")
    print(f"Allowed memory types: {len(ALLOWED_TYPES)}")
    print("LLM: not connected yet")
    print("Mode: local terminal")