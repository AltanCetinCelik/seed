from seed_config import RECENT_JOURNAL_LIMIT
JOURNAL_FILE = "seed_journal.txt"

def write_journal():
    entry = input("Journal entry: ")

    if entry == "":
        print("Journal entry cannot be empty.")
        return None

    with open(JOURNAL_FILE, "a") as file:
        file.write(entry + "\n")

    print("Journal entry saved.")
    return entry

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

def get_recent_journal_entries(limit=RECENT_JOURNAL_LIMIT):
    try:
        with open(JOURNAL_FILE, "r") as file:
            lines = file.readlines()

    except FileNotFoundError:
        return "No journal file found."

    if not lines:
        return "No journal entries yet."

    recent_lines = lines[-limit:]

    journal_text = ""

    for number, line in enumerate(recent_lines, start=1):
        journal_text += f"{number}. {line.strip()}\n"

    return journal_text
