import json
import math
import os
from datetime import datetime

from seed_config import (
    MEMORY_EMBEDDINGS_FILE,
    SEMANTIC_MEMORY_TOP_K,
    SEMANTIC_MEMORY_MIN_SIMILARITY,
    SEMANTIC_CONTEXT_ENABLED,
    EMBEDDING_MODEL
)
from seed_memory import memories
from seed_llm import get_embedding


def memory_signature(memory):
    memory_type = memory.get("type", "unknown")
    content = memory.get("content", "")
    created_at = memory.get("created_at", "unknown time")

    return f"{memory_type}|{created_at}|{content}"


def memory_text_for_embedding(memory):
    memory_type = memory.get("type", "unknown")
    content = memory.get("content", "")
    created_at = memory.get("created_at", "unknown time")
    importance = memory.get("importance", 0)

    return (
        f"Memory type: {memory_type}\n"
        f"Content: {content}\n"
        f"Created at: {created_at}\n"
        f"Importance: {importance}"
    )


def load_embedding_cache():
    try:
        with open(MEMORY_EMBEDDINGS_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {
            "model": EMBEDDING_MODEL,
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "items": {}
        }
    except json.JSONDecodeError:
        print("Embedding cache is corrupted. Starting fresh.")
        return {
            "model": EMBEDDING_MODEL,
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "items": {}
        }


def save_embedding_cache(cache):
    with open(MEMORY_EMBEDDINGS_FILE, "w") as file:
        json.dump(cache, file)


def cosine_similarity(vector_a, vector_b):
    if not vector_a or not vector_b:
        return 0.0

    if len(vector_a) != len(vector_b):
        return 0.0

    dot_product = 0.0
    magnitude_a = 0.0
    magnitude_b = 0.0

    for a, b in zip(vector_a, vector_b):
        dot_product += a * b
        magnitude_a += a * a
        magnitude_b += b * b

    if magnitude_a == 0.0 or magnitude_b == 0.0:
        return 0.0

    return dot_product / (math.sqrt(magnitude_a) * math.sqrt(magnitude_b))


def build_memory_embedding_index(force=False):
    print("\n=== MEMORY REINDEX ===")

    cache = load_embedding_cache()

    if cache.get("model") != EMBEDDING_MODEL:
        print("Embedding model changed. Rebuilding cache.")
        cache = {
            "model": EMBEDDING_MODEL,
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "items": {}
        }

    indexed_count = 0
    skipped_count = 0
    failed_count = 0

    for memory in memories:
        signature = memory_signature(memory)

        if not force and signature in cache["items"]:
            skipped_count += 1
            continue

        text = memory_text_for_embedding(memory)
        embedding, error = get_embedding(text)

        if error is not None:
            print(f"Failed to embed memory: {error}")
            failed_count += 1
            continue

        cache["items"][signature] = {
            "embedding": embedding,
            "memory": memory,
            "indexed_at": datetime.now().isoformat(timespec="seconds")
        }

        indexed_count += 1

    save_embedding_cache(cache)

    print(f"Embedding model: {EMBEDDING_MODEL}")
    print(f"Indexed: {indexed_count}")
    print(f"Skipped existing: {skipped_count}")
    print(f"Failed: {failed_count}")
    print(f"Total cache items: {len(cache['items'])}")


def get_semantic_memory_results(query, limit=SEMANTIC_MEMORY_TOP_K):
    cache = load_embedding_cache()

    if not cache.get("items"):
        return [], "Memory embedding cache is empty. Use /memory-reindex first."

    query_embedding, error = get_embedding(query)

    if error is not None:
        return [], error

    results = []

    for signature, item in cache.get("items", {}).items():
        memory_embedding = item.get("embedding", [])
        similarity = cosine_similarity(query_embedding, memory_embedding)

        memory = item.get("memory", {})

        results.append({
            "signature": signature,
            "memory": memory,
            "similarity": similarity
        })

    results.sort(
        key=lambda result: result["similarity"],
        reverse=True
    )

    filtered_results = []

    for result in results:
        if result["similarity"] >= SEMANTIC_MEMORY_MIN_SIMILARITY:
            filtered_results.append(result)

    return filtered_results[:limit], None


def format_semantic_results(query, limit=SEMANTIC_MEMORY_TOP_K):
    results, error = get_semantic_memory_results(query, limit)

    if error is not None:
        return f"Semantic search unavailable: {error}"

    if not results:
        return "No semantic memory matches found."

    text = "=== SEMANTIC MEMORY RESULTS ===\n"
    text += f"Query: {query}\n"
    text += f"Embedding model: {EMBEDDING_MODEL}\n\n"

    for number, result in enumerate(results, start=1):
        memory = result["memory"]

        text += f"{number}. [{memory.get('type', 'unknown')}]\n"
        text += f"Similarity: {result['similarity']:.4f}\n"
        text += f"Content: {memory.get('content', '')}\n"
        text += f"Created: {memory.get('created_at', 'unknown time')}\n"
        text += f"Importance: {memory.get('importance', 0)}\n"
        text += "-" * 40 + "\n"

    return text


def format_semantic_context_for_prompt(user_prompt, limit=SEMANTIC_MEMORY_TOP_K):
    if not SEMANTIC_CONTEXT_ENABLED:
        return "Semantic memory context is disabled."

    results, error = get_semantic_memory_results(user_prompt, limit)

    if error is not None:
        return f"Semantic memory context unavailable: {error}"

    if not results:
        return "No semantic memory matches found."

    text = "=== SEMANTIC MEMORY CONTEXT ===\n"

    for number, result in enumerate(results, start=1):
        memory = result["memory"]

        text += f"{number}. [{memory.get('type', 'unknown')}]\n"
        text += f"Semantic similarity: {result['similarity']:.4f}\n"
        text += f"Content: {memory.get('content', '')}\n"
        text += f"Created: {memory.get('created_at', 'unknown time')}\n"
        text += f"Importance: {memory.get('importance', 0)}\n"
        text += "-" * 40 + "\n"

    text += (
        "\nSemantic memory rule:\n"
        "Use these memories when they are clearly relevant to the user's question. "
        "Do not treat weak semantic matches as guaranteed facts.\n"
    )

    return text


def show_semantic_memory_status():
    print("\n=== SEMANTIC MEMORY STATUS ===")

    cache = load_embedding_cache()
    cache_items = cache.get("items", {})

    print(f"Embedding model: {cache.get('model', EMBEDDING_MODEL)}")
    print(f"Cache file: {MEMORY_EMBEDDINGS_FILE}")
    print(f"Memory count: {len(memories)}")
    print(f"Cached embeddings: {len(cache_items)}")

    if os.path.exists(MEMORY_EMBEDDINGS_FILE):
        print("Cache exists: yes")
    else:
        print("Cache exists: no")