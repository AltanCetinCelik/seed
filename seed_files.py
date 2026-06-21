def show_seed_core():
    with open("Seed_Core.md", "r") as file:
        content = file.read()

    print("\n=== SEED CORE ===")
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
