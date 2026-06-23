import json
import os
from datetime import datetime


try:
    from seed_config import (
        SEED_MEMORY_BACKEND_STATE_FILE,
        MEMORY_BACKEND_ACTIVE,
        MEMORY_BACKEND_VECTOR_READY,
        MEMORY_BACKEND_DOCUMENT_READY
    )
except Exception:
    SEED_MEMORY_BACKEND_STATE_FILE = "seed_memory_backend_state.json"
    MEMORY_BACKEND_ACTIVE = "json_semantic"
    MEMORY_BACKEND_VECTOR_READY = True
    MEMORY_BACKEND_DOCUMENT_READY = True


try:
    from seed_memory import memories
    OLD_MEMORY_AVAILABLE = True
except Exception:
    memories = []
    OLD_MEMORY_AVAILABLE = False


try:
    from seed_semantic_memory import show_semantic_memory_status
    SEMANTIC_AVAILABLE = True
except Exception:
    SEMANTIC_AVAILABLE = False


try:
    from seed_companion_os import (
        load_companion_os_state,
        save_companion_os_state,
        append_companion_os_event,
        append_companion_os_journal
    )
    COMPANION_OS_AVAILABLE = True
except Exception:
    COMPANION_OS_AVAILABLE = False


MEMORY_BACKEND_TIERS = {
    "json": {
        "status": "active",
        "meaning": "Plain local JSON memory. Simple, private, reliable."
    },
    "semantic": {
        "status": "active_if_seed_semantic_memory_exists",
        "meaning": "Meaning-based memory retrieval using local embeddings."
    },
    "document_registry": {
        "status": "active_after_section_4",
        "meaning": "Approved local documents with summaries, tags, and search."
    },
    "vector_future": {
        "status": "prepared_not_installed",
        "meaning": "Future Qdrant/Chroma/pgvector/LanceDB-style backend."
    },
    "mem0_future": {
        "status": "prepared_not_installed",
        "meaning": "Future Mem0-style lifecycle, preferences, user memory extraction."
    },
    "rag_future": {
        "status": "prepared_not_installed",
        "meaning": "Future LlamaIndex/AnythingLLM/Khoj-style retrieval pipeline."
    }
}


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def load_json(path, default):
    try:
        with open(path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return default() if callable(default) else default
    except json.JSONDecodeError:
        return default() if callable(default) else default


def save_json(path, data):
    with open(path, "w") as file:
        json.dump(data, file, indent=4)


def default_backend_state():
    return {
        "created_at": now_timestamp(),
        "updated_at": now_timestamp(),
        "active_backend": MEMORY_BACKEND_ACTIVE,
        "vector_ready": MEMORY_BACKEND_VECTOR_READY,
        "document_ready": MEMORY_BACKEND_DOCUMENT_READY,
        "tiers": MEMORY_BACKEND_TIERS,
        "migration_notes": [
            "Seed currently uses local JSON memory plus semantic memory.",
            "Companion OS adds layered memory and timeline continuity.",
            "Document Registry prepares Seed for Khoj/AnythingLLM/LlamaIndex-style context.",
            "Vector backends are prepared as future slots, not installed yet."
        ],
        "future_backends": {
            "qdrant": {
                "status": "not_installed",
                "use": "large vector memory/search backend"
            },
            "chroma": {
                "status": "not_installed",
                "use": "local vector store option"
            },
            "pgvector": {
                "status": "not_installed",
                "use": "Postgres-backed vector search"
            },
            "lancedb": {
                "status": "not_installed",
                "use": "local embedded vector database"
            },
            "mem0": {
                "status": "not_installed",
                "use": "memory lifecycle and user preference memory"
            }
        }
    }


def load_backend_state():
    return load_json(SEED_MEMORY_BACKEND_STATE_FILE, default_backend_state)


def save_backend_state(state):
    state["updated_at"] = now_timestamp()
    save_json(SEED_MEMORY_BACKEND_STATE_FILE, state)


def initialize_memory_backend():
    state = load_backend_state()
    save_backend_state(state)

    if COMPANION_OS_AVAILABLE:
        try:
            append_companion_os_event(
                "memory_backend_initialized",
                "Memory Backend prepared",
                {
                    "active_backend": state.get("active_backend"),
                    "vector_ready": state.get("vector_ready"),
                    "document_ready": state.get("document_ready")
                },
                source="memory_backend",
                importance=4
            )
        except Exception:
            pass

    print("Memory backend initialized.")
    return state


def memory_backend_stats():
    state = load_backend_state()

    old_memory_count = len(memories) if OLD_MEMORY_AVAILABLE else 0

    companion_layer_counts = {}

    if COMPANION_OS_AVAILABLE:
        try:
            os_state = load_companion_os_state()
            layers = os_state.get("memory", {}).get("layers", {})

            for layer_name, items in layers.items():
                companion_layer_counts[layer_name] = len(items)
        except Exception:
            companion_layer_counts = {}

    return {
        "active_backend": state.get("active_backend"),
        "old_memory_available": OLD_MEMORY_AVAILABLE,
        "old_memory_count": old_memory_count,
        "semantic_available": SEMANTIC_AVAILABLE,
        "companion_os_available": COMPANION_OS_AVAILABLE,
        "companion_layer_counts": companion_layer_counts,
        "vector_ready": state.get("vector_ready"),
        "document_ready": state.get("document_ready"),
        "future_backends": state.get("future_backends", {})
    }


def format_memory_backend_status():
    stats = memory_backend_stats()
    state = load_backend_state()

    text = "=== SEED MEMORY BACKEND ===\n"
    text += f"Active backend: {stats['active_backend']}\n"
    text += f"Old memory available: {stats['old_memory_available']}\n"
    text += f"Old memory count: {stats['old_memory_count']}\n"
    text += f"Semantic memory available: {stats['semantic_available']}\n"
    text += f"Companion OS available: {stats['companion_os_available']}\n"
    text += f"Vector-ready slot: {stats['vector_ready']}\n"
    text += f"Document-ready slot: {stats['document_ready']}\n"

    text += "\nCompanion OS layer counts:\n"
    if not stats["companion_layer_counts"]:
        text += "- none yet\n"
    else:
        for layer, count in sorted(stats["companion_layer_counts"].items()):
            text += f"- {layer}: {count}\n"

    text += "\nBackend tiers:\n"
    for tier, data in state.get("tiers", {}).items():
        text += f"- {tier}: {data.get('status')} — {data.get('meaning')}\n"

    text += "\nFuture backends:\n"
    for backend, data in state.get("future_backends", {}).items():
        text += f"- {backend}: {data.get('status')} — {data.get('use')}\n"

    return text


def show_memory_backend_status():
    print("\n" + format_memory_backend_status())


def set_active_backend_interactive():
    state = load_backend_state()

    print("\n=== SET ACTIVE MEMORY BACKEND ===")
    print("Available practical choices now:")
    print("- json")
    print("- json_semantic")
    print("- companion_os_layers")
    print("- document_registry")

    backend = input("Backend: ").strip()

    if backend == "":
        print("Backend cannot be empty.")
        return

    state["active_backend"] = backend
    save_backend_state(state)

    if COMPANION_OS_AVAILABLE:
        try:
            append_companion_os_event(
                "memory_backend_changed",
                f"Memory backend changed to {backend}",
                {"backend": backend},
                source="memory_backend",
                importance=3
            )
        except Exception:
            pass

    print(f"Active backend set: {backend}")


def add_layered_memory(layer, content, source="memory_backend", importance=3, tags=None):
    if tags is None:
        tags = []

    if not COMPANION_OS_AVAILABLE:
        return {
            "ok": False,
            "message": "Companion OS unavailable."
        }

    os_state = load_companion_os_state()
    layers = os_state.setdefault("memory", {}).setdefault("layers", {})

    layers.setdefault(layer, [])

    item = {
        "created_at": now_timestamp(),
        "layer": layer,
        "source": source,
        "content": content,
        "importance": int(importance),
        "tags": tags
    }

    layers[layer].append(item)
    save_companion_os_state(os_state)

    append_companion_os_event(
        "layered_memory_added",
        f"Layered memory added to {layer}",
        {
            "source": source,
            "importance": importance,
            "tags": tags
        },
        source="memory_backend",
        importance=importance
    )

    return {
        "ok": True,
        "item": item
    }


def add_layered_memory_interactive():
    print("\n=== ADD COMPANION OS LAYERED MEMORY ===")
    print("Layers: core, project, relationship, timeline, ritual, quest, identity_mirror, world, document")

    layer = input("Layer: ").strip()
    content = input("Content: ").strip()
    importance = input("Importance 1-5: ").strip()
    tags_raw = input("Tags, comma-separated: ").strip()

    if not layer or not content:
        print("Layer and content are required.")
        return

    try:
        importance_value = int(importance)
    except ValueError:
        importance_value = 3

    tags = [tag.strip() for tag in tags_raw.split(",") if tag.strip()]

    result = add_layered_memory(
        layer=layer,
        content=content,
        source="manual",
        importance=importance_value,
        tags=tags
    )

    if result["ok"]:
        print("Layered memory added.")
    else:
        print(result["message"])


def search_layered_memory(query, limit=12):
    if not COMPANION_OS_AVAILABLE:
        return []

    os_state = load_companion_os_state()
    layers = os_state.get("memory", {}).get("layers", {})

    query_words = [
        word.lower()
        for word in query.split()
        if len(word.strip()) >= 3
    ]

    results = []

    for layer_name, items in layers.items():
        for item in items:
            haystack = json.dumps(item).lower()
            score = item.get("importance", 1)

            for word in query_words:
                if word in haystack:
                    score += 3

            if score > item.get("importance", 1):
                results.append({
                    "score": score,
                    "layer": layer_name,
                    "item": item
                })

    results.sort(key=lambda result: result["score"], reverse=True)
    return results[:limit]


def search_layered_memory_interactive():
    query = input("Layered memory search query: ").strip()

    if query == "":
        print("Query cannot be empty.")
        return

    results = search_layered_memory(query)

    print("\n=== LAYERED MEMORY SEARCH ===")

    if not results:
        print("No matches.")
        return

    for result in results:
        item = result["item"]
        print(f"\nScore {result['score']} | Layer: {result['layer']}")
        print(f"Created: {item.get('created_at')}")
        print(f"Source: {item.get('source')}")
        print(f"Importance: {item.get('importance')}")
        print(f"Content: {item.get('content')}")


def get_memory_backend_context_for_prompt():
    text = format_memory_backend_status()
    text += """
Memory Backend rule:
Seed currently uses local JSON, semantic memory, Companion OS layers, and Document Registry.
Vector backends such as Qdrant/Chroma/pgvector/LanceDB are future slots, not active unless explicitly installed.
Do not claim a vector database is active unless the backend state says so.
"""
    return text


if __name__ == "__main__":
    initialize_memory_backend()
    show_memory_backend_status()
