import os
from seed_config import (
    SEED_VERSION,
    MODEL_NAME,
    SEED_MODE,
    LLM_STATUS,
    MEMORY_SEARCH_LIMIT,
    RECENT_JOURNAL_LIMIT,
    SESSION_HISTORY_LIMIT
)

from seed_memory import memories, ALLOWED_TYPES
from seed_llm import check_ollama_health, get_local_models

def file_status(filename):
    if os.path.exists(filename):
        return "found"
    else:
        return "missing"


def show_seed_status():
    from seed_project_inspector import get_python_modules
    health = check_ollama_health()
    models = get_local_models()


    modules = get_python_modules()
    print(f"Python modules: {len(modules)}")
    print("\n=== SEED STATUS ===")
    print(f"Version: {SEED_VERSION}")
    print(f"Model: {MODEL_NAME}")
    print(f"Mode: {SEED_MODE}")
    print(f"LLM status: {LLM_STATUS}")
    print(f"Memory search limit: {MEMORY_SEARCH_LIMIT}")
    print(f"Recent journal limit: {RECENT_JOURNAL_LIMIT}")
    print(f"Session history limit: {SESSION_HISTORY_LIMIT}")
    print(f"Core file: {file_status('Seed_Core.md')}")
    print(f"Memory rules file: {file_status('memory_rules.md')}")
    print(f"First contact file: {file_status('first_contact.md')}")
    print(f"Memory file: {file_status('seed_memory.json')}")
    print(f"Journal file: {file_status('seed_journal.txt')}")
    print(f"Number of memories: {len(memories)}")
    print(f"Allowed memory types: {len(ALLOWED_TYPES)}")
    print(f"Ollama health: {health['message']}")
    print(f"Local Ollama models: {len(models)}")