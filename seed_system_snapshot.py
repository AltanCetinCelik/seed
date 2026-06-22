import os
import glob
from datetime import datetime

from seed_config import (
    SEED_VERSION,
    MODEL_NAME,
    CHAT_LOG_DIR,
    MEMORY_EMBEDDINGS_FILE
)
from seed_memory import memories, ALLOWED_TYPES
from seed_project_inspector import get_project_files, get_python_modules
from seed_llm import check_ollama_health, get_local_models
from seed_self_editor import load_pending_edit, get_editable_files


def count_memories_by_type():
    counts = {}

    for memory_type in ALLOWED_TYPES:
        counts[memory_type] = 0

    for memory in memories:
        memory_type = memory.get("type", "unknown")

        if memory_type not in counts:
            counts[memory_type] = 0

        counts[memory_type] += 1

    return counts


def get_log_status():
    log_files = glob.glob(os.path.join(CHAT_LOG_DIR, "*.txt"))
    log_files.sort(key=os.path.getmtime, reverse=True)

    latest_log = None

    if log_files:
        latest_log = log_files[0]

    return {
        "log_count": len(log_files),
        "latest_log": latest_log
    }


def get_semantic_status():
    if not os.path.exists(MEMORY_EMBEDDINGS_FILE):
        return {
            "cache_exists": False,
            "cached_items": 0
        }

    try:
        import json

        with open(MEMORY_EMBEDDINGS_FILE, "r") as file:
            cache = json.load(file)

        return {
            "cache_exists": True,
            "cached_items": len(cache.get("items", {}))
        }

    except Exception:
        return {
            "cache_exists": True,
            "cached_items": "unknown/corrupted"
        }


def get_self_edit_status():
    pending_edit = load_pending_edit()
    editable_files = get_editable_files()

    return {
        "pending_edit": pending_edit is not None,
        "pending_edit_target": pending_edit.get("target_path") if pending_edit else None,
        "editable_files": len(editable_files)
    }


def get_system_snapshot():
    project_files = get_project_files()
    python_modules = get_python_modules()
    health = check_ollama_health()
    local_models = get_local_models()
    log_status = get_log_status()
    semantic_status = get_semantic_status()
    self_edit_status = get_self_edit_status()

    return {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "version": SEED_VERSION,
        "default_model": MODEL_NAME,
        "ollama_health": health.get("message"),
        "ollama_ok": health.get("ok"),
        "local_model_count": len(local_models),
        "local_models": local_models,
        "total_memories": len(memories),
        "memories_by_type": count_memories_by_type(),
        "project_file_count": len(project_files),
        "python_module_count": len(python_modules),
        "python_modules": python_modules,
        "log_count": log_status["log_count"],
        "latest_log": log_status["latest_log"],
        "semantic_cache_exists": semantic_status["cache_exists"],
        "semantic_cached_items": semantic_status["cached_items"],
        "pending_self_edit": self_edit_status["pending_edit"],
        "pending_self_edit_target": self_edit_status["pending_edit_target"],
        "editable_files": self_edit_status["editable_files"]
    }


def format_system_snapshot():
    snapshot = get_system_snapshot()

    text = "=== SEED SYSTEM SNAPSHOT ===\n"
    text += f"Created at: {snapshot['created_at']}\n"
    text += f"Version: {snapshot['version']}\n"
    text += f"Default model: {snapshot['default_model']}\n"
    text += f"Ollama health: {snapshot['ollama_health']}\n"
    text += f"Local models: {snapshot['local_model_count']}\n"
    text += f"Total memories: {snapshot['total_memories']}\n"

    text += "\nMemory types:\n"
    for memory_type, count in snapshot["memories_by_type"].items():
        text += f"- {memory_type}: {count}\n"

    text += "\nProject:\n"
    text += f"- Files: {snapshot['project_file_count']}\n"
    text += f"- Python modules: {snapshot['python_module_count']}\n"

    text += "\nSemantic memory:\n"
    text += f"- Cache exists: {snapshot['semantic_cache_exists']}\n"
    text += f"- Cached items: {snapshot['semantic_cached_items']}\n"

    text += "\nSelf-editing:\n"
    text += f"- Editable files: {snapshot['editable_files']}\n"
    text += f"- Pending edit: {snapshot['pending_self_edit']}\n"
    text += f"- Pending target: {snapshot['pending_self_edit_target']}\n"

    text += "\nLogs:\n"
    text += f"- Log count: {snapshot['log_count']}\n"
    text += f"- Latest log: {snapshot['latest_log']}\n"

    text += "\nPython modules:\n"
    for module in snapshot["python_modules"]:
        text += f"- {module}\n"

    return text


def show_system_snapshot():
    print("\n" + format_system_snapshot())