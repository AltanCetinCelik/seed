from seed_memory import memories, ALLOWED_TYPES

KEYWORD_ALIASES = {
    "ollama": [
        "ollama",
        "llama",
        "llama3.1",
        "local model",
        "local llm",
        "llm",
        "api",
        "generate",
        "localhost",
        "seed_brain"
    ],
    "journal": [
        "journal",
        "journaling",
        "journaled",
        "entry",
        "entries",
        "reflection",
        "note",
        "notes",
        "seed_journal",
        "write_journal"
    ],
    "memory": [
        "memory",
        "memories",
        "remember",
        "stored",
        "save",
        "saved",
        "saving",
        "seed_memory",
        "json"
    ],
    "debug": [
        "debug",
        "context",
        "inspect",
        "inspection",
        "prompt",
        "retrieval",
        "score",
        "scores"
    ],
    "chat": [
        "chat",
        "session",
        "session_history",
        "talk",
        "conversation",
        "follow-up",
        "temporary"
    ],
    "status": [
        "status",
        "health",
        "version",
        "file status",
        "system status"
    ],
    "refactor": [
        "refactor",
        "refactored",
        "module",
        "modules",
        "structure",
        "split"
    ],   
    "log": [
        "log",
        "logs",
        "logging",
        "chat log",
        "chat logs",
        "conversation log",
        "conversation logs",
        "seed_logs",
        "seed_chat_logger",
        "raw conversation",
        "audit trail"
    ],

    "summary": [
        "summary",
        "summaries",
        "summarize",
        "summarization",
        "session summary",
        "session summaries",
        "seed_session_summarizer",
        "summary-save-memory",
        "summary-save-journal"
    ],

    "project": [
        "project",
        "files",
        "file",
        "modules",
        "module",
        "architecture",
        "structure",
        "codebase",
        "self-inspection",
        "seed_project_inspector"
    ],

    "config": [
        "config",
        "configuration",
        "settings",
        "seed_config",
        "version",
        "model name",
        "ollama url",
        "limits"
    ],
}


def expand_query(query):
    query_lower = query.lower()
    expanded_words = []

    for word in query_lower.split():
        expanded_words.append(word)

    for category, aliases in KEYWORD_ALIASES.items():
        if category in query_lower:
            expanded_words.extend(aliases)

        for alias in aliases:
            if alias in query_lower:
                expanded_words.append(category)
                expanded_words.extend(aliases)

    unique_words = []

    for word in expanded_words:
        if word not in unique_words:
            unique_words.append(word)

    return unique_words


def list_memories_by_type(memory_type):
    if memory_type not in ALLOWED_TYPES:
        print("Invalid memory type.")
        print("Allowed types:")
        for allowed_type in ALLOWED_TYPES:
            print(f"- {allowed_type}")
        return

    matching_memories = []

    for memory in memories:
        if memory.get("type") == memory_type:
            matching_memories.append(memory)

    if not matching_memories:
        print(f"No memories found for type: {memory_type}")
        return

    print(f"\n=== MEMORIES OF TYPE: {memory_type} ===")

    for number, memory in enumerate(matching_memories, start=1):
        print(
            f"{number}. "
            f"{memory.get('content', 'no content')} "
            f"Importance: {memory.get('importance', 'unknown')} "
            f"Created: {memory.get('created_at', 'unknown time')}"
        )


def show_memory_stats():
    print("\n=== MEMORY STATS ===")

    total = len(memories)
    print(f"Total memories: {total}")

    if total == 0:
        return

    print("\nBy type:")

    for memory_type in ALLOWED_TYPES:
        count = 0

        for memory in memories:
            if memory.get("type") == memory_type:
                count += 1

        print(f"- {memory_type}: {count}")

    high_importance_count = 0
    missing_timestamp_count = 0

    for memory in memories:
        if memory.get("importance", 0) == 5:
            high_importance_count += 1

        if "created_at" not in memory:
            missing_timestamp_count += 1

    print(f"\nImportance 5 memories: {high_importance_count}")
    print(f"Memories without timestamp: {missing_timestamp_count}")


def normalize_text(text):
    text = text.lower().strip()

    for symbol in [".", ",", "?", "!", ":", ";", "(", ")", "[", "]", "{", "}", "/", "\\"]:
        text = text.replace(symbol, "")

    return text


def find_possible_duplicates():
    print("\n=== POSSIBLE DUPLICATE MEMORIES ===")

    found_duplicate = False

    for i in range(len(memories)):
        content_a = normalize_text(memories[i].get("content", ""))

        for j in range(i + 1, len(memories)):
            content_b = normalize_text(memories[j].get("content", ""))

            if content_a == "" or content_b == "":
                continue

            if content_a == content_b:
                found_duplicate = True
                print("\nExact duplicate:")
                print(f"{i + 1}. {memories[i].get('content')}")
                print(f"{j + 1}. {memories[j].get('content')}")

            elif content_a in content_b or content_b in content_a:
                found_duplicate = True
                print("\nPossible duplicate:")
                print(f"{i + 1}. {memories[i].get('content')}")
                print(f"{j + 1}. {memories[j].get('content')}")

    if not found_duplicate:
        print("No obvious duplicates found.")
        