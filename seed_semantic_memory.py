import hashlib
import json
import math
import os
import urllib.request
from datetime import datetime
from pathlib import Path


try:
    from seed_config import (
        SEED_SEMANTIC_MEMORY_FILE,
        SEED_SEMANTIC_INDEX_FILE,
        SEED_OLLAMA_EMBED_MODEL,
        SEED_OLLAMA_EMBED_URL,
        SEED_SEMANTIC_INDEX_MAX_FILES,
        SEED_SEMANTIC_INDEX_MAX_FILE_BYTES,
        SEED_SEMANTIC_SEARCH_RESULTS
    )
except Exception:
    SEED_SEMANTIC_MEMORY_FILE = "seed_semantic_memory.json"
    SEED_SEMANTIC_INDEX_FILE = "seed_semantic_index.json"
    SEED_OLLAMA_EMBED_MODEL = "nomic-embed-text"
    SEED_OLLAMA_EMBED_URL = "http://localhost:11434/api/embeddings"
    SEED_SEMANTIC_INDEX_MAX_FILES = 700
    SEED_SEMANTIC_INDEX_MAX_FILE_BYTES = 300000
    SEED_SEMANTIC_SEARCH_RESULTS = 8


TEXT_EXTENSIONS = {
    ".py", ".md", ".txt", ".json", ".yaml", ".yml", ".toml",
    ".html", ".css", ".js", ".ts", ".sh"
}

SKIP_DIRS = {
    ".git", "__pycache__", ".venv", "venv", "node_modules",
    "seed_agent_runs", ".mypy_cache", ".pytest_cache", "dist", "build"
}


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def safe_load_json(path, default):
    try:
        with open(path, "r") as file:
            return json.load(file)
    except Exception:
        return default() if callable(default) else default


def safe_save_json(path, data):
    with open(path, "w") as file:
        json.dump(data, file, indent=4)


def tokenize(text):
    out = []
    cur = []
    for ch in (text or "").lower():
        if ch.isalnum() or ch in "_-":
            cur.append(ch)
        else:
            if cur:
                out.append("".join(cur))
                cur = []
    if cur:
        out.append("".join(cur))
    return out


def cosine(a, b):
    if not a or not b:
        return 0.0
    n = min(len(a), len(b))
    dot = sum(a[i] * b[i] for i in range(n))
    aa = math.sqrt(sum(x * x for x in a[:n]))
    bb = math.sqrt(sum(x * x for x in b[:n]))
    if aa == 0 or bb == 0:
        return 0.0
    return dot / (aa * bb)


def local_hash_embedding(text, dims=384):
    """
    Safe fallback embedding.
    Not as smart as real embeddings, but stable and dependency-free.
    """
    vec = [0.0] * dims
    tokens = tokenize(text)

    for token in tokens:
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        idx = int.from_bytes(digest[:4], "big") % dims
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        vec[idx] += sign

    norm = math.sqrt(sum(x * x for x in vec))
    if norm:
        vec = [x / norm for x in vec]

    return vec


def ollama_embedding(text):
    payload = json.dumps({
        "model": SEED_OLLAMA_EMBED_MODEL,
        "prompt": text
    }).encode("utf-8")

    request = urllib.request.Request(
        SEED_OLLAMA_EMBED_URL,
        data=payload,
        headers={"Content-Type": "application/json"}
    )

    with urllib.request.urlopen(request, timeout=6) as response:
        data = json.loads(response.read().decode("utf-8"))

    emb = data.get("embedding")
    if not isinstance(emb, list) or not emb:
        raise RuntimeError("Ollama embedding response did not contain embedding.")

    return [float(x) for x in emb]


def embed_text(text):
    try:
        embedding = ollama_embedding(text[:6000])
        return {
            "provider": "ollama",
            "model": SEED_OLLAMA_EMBED_MODEL,
            "embedding": embedding
        }
    except Exception as error:
        return {
            "provider": "local_hash_fallback",
            "model": "hash-384",
            "embedding": local_hash_embedding(text),
            "fallback_reason": str(error)
        }


def default_memory():
    return {
        "created_at": now_timestamp(),
        "updated_at": now_timestamp(),
        "version": "v2.3.0",
        "notes": []
    }


def load_memory():
    return safe_load_json(SEED_SEMANTIC_MEMORY_FILE, default_memory)


def save_memory(data):
    data["updated_at"] = now_timestamp()
    safe_save_json(SEED_SEMANTIC_MEMORY_FILE, data)


def add_semantic_memory(text, source="manual", tags=None):
    memory = load_memory()
    item = {
        "created_at": now_timestamp(),
        "source": source,
        "text": text,
        "tags": tags or []
    }
    memory.setdefault("notes", []).append(item)
    save_memory(memory)
    return item


def should_skip(path):
    return bool(set(path.parts).intersection(SKIP_DIRS))


def iter_indexable_files(root="."):
    root = Path(root).resolve()
    count = 0

    for path in root.rglob("*"):
        if count >= int(SEED_SEMANTIC_INDEX_MAX_FILES):
            break
        if not path.is_file():
            continue
        if should_skip(path):
            continue
        if path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        try:
            size = path.stat().st_size
        except Exception:
            continue
        if size > int(SEED_SEMANTIC_INDEX_MAX_FILE_BYTES):
            continue
        count += 1
        yield path


def read_text(path):
    try:
        return path.read_text(errors="ignore")
    except Exception:
        return ""


def chunk_text(text, size=1800, overlap=250):
    text = text or ""
    chunks = []
    start = 0

    while start < len(text):
        chunk = text[start:start + size]
        if chunk.strip():
            chunks.append(chunk)
        start += max(1, size - overlap)

        if len(chunks) >= 8:
            break

    return chunks


def build_semantic_index(root="."):
    root_path = Path(root).resolve()
    items = []

    memory = load_memory()
    for idx, note in enumerate(memory.get("notes", [])):
        text = note.get("text", "")
        emb = embed_text(text)
        items.append({
            "kind": "semantic_note",
            "path": f"semantic_note_{idx}",
            "title": "Semantic memory note",
            "text": text[:3000],
            "embedding_provider": emb["provider"],
            "embedding_model": emb["model"],
            "embedding": emb["embedding"],
            "source": note.get("source"),
            "created_at": note.get("created_at")
        })

    for path in iter_indexable_files(root_path):
        full_text = read_text(path)
        rel = str(path.relative_to(root_path))

        for i, chunk in enumerate(chunk_text(full_text)):
            emb = embed_text(chunk)
            items.append({
                "kind": "file_chunk",
                "path": rel,
                "chunk": i,
                "title": path.name,
                "text": chunk[:3000],
                "embedding_provider": emb["provider"],
                "embedding_model": emb["model"],
                "embedding": emb["embedding"],
                "mtime": path.stat().st_mtime
            })

    index = {
        "created_at": now_timestamp(),
        "version": "v2.3.0",
        "root": str(root_path),
        "item_count": len(items),
        "items": items
    }

    safe_save_json(SEED_SEMANTIC_INDEX_FILE, index)
    return index


def load_or_build_index(root="."):
    index = safe_load_json(SEED_SEMANTIC_INDEX_FILE, None)
    if not index:
        return build_semantic_index(root)
    return index


def semantic_search(query, root=".", rebuild=False, max_results=None):
    max_results = max_results or int(SEED_SEMANTIC_SEARCH_RESULTS)
    index = build_semantic_index(root) if rebuild else load_or_build_index(root)

    query_emb = embed_text(query)["embedding"]
    query_tokens = set(tokenize(query))

    results = []
    for item in index.get("items", []):
        emb_score = cosine(query_emb, item.get("embedding", []))
        text_lower = item.get("text", "").lower()
        token_score = 0.0

        for token in query_tokens:
            if token in text_lower:
                token_score += 0.04

        score = emb_score + token_score

        if score > 0.05:
            results.append({
                "score": round(score, 4),
                "kind": item.get("kind"),
                "path": item.get("path"),
                "chunk": item.get("chunk"),
                "title": item.get("title"),
                "provider": item.get("embedding_provider"),
                "snippet": item.get("text", "")[:900].replace("\n", " ")
            })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:max_results]


def show_semantic_index():
    print("\n=== SEED SEMANTIC MEMORY INDEX ===")
    index = build_semantic_index(".")
    print(f"Items indexed: {index.get('item_count')}")
    providers = {}
    for item in index.get("items", []):
        providers[item.get("embedding_provider")] = providers.get(item.get("embedding_provider"), 0) + 1
    print("Providers:")
    for key, value in providers.items():
        print(f"- {key}: {value}")


def show_semantic_search():
    query = input("Semantic search query: ").strip()
    results = semantic_search(query, rebuild=False)

    print("\n=== SEMANTIC SEARCH RESULTS ===")
    if not results:
        print("No results.")
        return

    for result in results:
        print(f"\n[{result['score']}] {result['kind']} — {result['path']} chunk={result.get('chunk')} provider={result.get('provider')}")
        print(result["snippet"][:800])


def show_semantic_add():
    text = input("Semantic memory note: ").strip()
    if not text:
        print("No memory added.")
        return

    item = add_semantic_memory(text, source="seed_cli")
    print("\nAdded semantic memory:")
    print(json.dumps(item, indent=4))


def semantic_memory_context(query):
    results = semantic_search(query, rebuild=False, max_results=5)
    text = "=== SEMANTIC MEMORY CONTEXT ===\n"

    if not results:
        return text + "No semantic memory matches.\n"

    for result in results:
        text += f"- {result['path']} score={result['score']}: {result['snippet'][:350]}\n"

    return text


if __name__ == "__main__":
    show_semantic_index()


# Compatibility helpers for Seed brain/context integrations.
def format_semantic_context_for_prompt(user_prompt="", max_results=None):
    """
    Compatibility wrapper expected by seed_brain.py.
    Returns semantic memory context for prompt injection.
    """
    try:
        return semantic_memory_context(user_prompt or "")
    except Exception as error:
        return f"=== SEMANTIC MEMORY CONTEXT ===\nUnavailable: {error}\n"


def get_semantic_context_for_prompt(user_prompt="", max_results=None):
    """
    Alias for future context integrations.
    """
    return format_semantic_context_for_prompt(user_prompt, max_results=max_results)


def retrieve_semantic_context(user_prompt="", max_results=None):
    """
    Alias for retrieval-style integrations.
    """
    return format_semantic_context_for_prompt(user_prompt, max_results=max_results)



# v2.3 compatibility layer for older Seed modules.
# Older modules may expect an embedding cache API. The new semantic index
# stores embeddings inside seed_semantic_index.json, so these wrappers expose
# a safe cache-like view without breaking old imports.

def load_embedding_cache():
    """
    Compatibility wrapper expected by older modules such as seed_visuals.py.
    Returns a cache-like dict derived from the semantic index.
    """
    try:
        index = safe_load_json(SEED_SEMANTIC_INDEX_FILE, None)
        if not index:
            index = load_or_build_index(".")

        cache = {}
        for item in index.get("items", []):
            key = f"{item.get('kind')}::{item.get('path')}::{item.get('chunk', 0)}"
            cache[key] = {
                "provider": item.get("embedding_provider"),
                "model": item.get("embedding_model"),
                "embedding": item.get("embedding", []),
                "title": item.get("title"),
                "path": item.get("path"),
                "kind": item.get("kind")
            }

        return {
            "created_at": index.get("created_at"),
            "version": index.get("version", "v2.3.0"),
            "provider": "semantic_index_compat",
            "cache": cache,
            "count": len(cache),
            "index_file": SEED_SEMANTIC_INDEX_FILE
        }
    except Exception as error:
        return {
            "created_at": now_timestamp(),
            "version": "v2.3.0",
            "provider": "semantic_index_compat",
            "cache": {},
            "count": 0,
            "error": str(error)
        }


def save_embedding_cache(cache):
    """
    Compatibility no-op/save wrapper.
    The v2.3 semantic system writes full indexes through build_semantic_index().
    """
    try:
        data = {
            "created_at": now_timestamp(),
            "version": "v2.3.0",
            "compat_embedding_cache": cache
        }
        safe_save_json(SEED_SEMANTIC_MEMORY_FILE + ".compat_cache.json", data)
        return True
    except Exception:
        return False


def get_embedding_cache_stats():
    cache = load_embedding_cache()
    return {
        "count": cache.get("count", 0),
        "provider": cache.get("provider"),
        "index_file": cache.get("index_file", SEED_SEMANTIC_INDEX_FILE),
        "error": cache.get("error")
    }


def get_text_embedding(text):
    return embed_text(text).get("embedding", [])


def get_embedding(text):
    return get_text_embedding(text)


def embed_text_cached(text):
    return embed_text(text)


def format_semantic_context_for_prompt(user_prompt="", max_results=None):
    """
    Compatibility wrapper expected by seed_brain.py.
    """
    try:
        return semantic_memory_context(user_prompt or "")
    except Exception as error:
        return f"=== SEMANTIC MEMORY CONTEXT ===\nUnavailable: {error}\n"


def get_semantic_context_for_prompt(user_prompt="", max_results=None):
    return format_semantic_context_for_prompt(user_prompt, max_results=max_results)


def retrieve_semantic_context(user_prompt="", max_results=None):
    return format_semantic_context_for_prompt(user_prompt, max_results=max_results)



# v2.3 extended compatibility pack for older Seed modules.
# This keeps older imports working while the new semantic memory engine stays active.

def semantic_memory_status_data():
    try:
        memory = load_memory()
    except Exception:
        memory = {"notes": []}

    try:
        index = safe_load_json(SEED_SEMANTIC_INDEX_FILE, None)
    except Exception:
        index = None

    providers = {}
    item_count = 0

    if index:
        item_count = index.get("item_count", len(index.get("items", [])))
        for item in index.get("items", []):
            provider = item.get("embedding_provider", "unknown")
            providers[provider] = providers.get(provider, 0) + 1

    return {
        "version": "v2.3.0",
        "memory_file": SEED_SEMANTIC_MEMORY_FILE,
        "index_file": SEED_SEMANTIC_INDEX_FILE,
        "notes": len(memory.get("notes", [])),
        "index_exists": bool(index),
        "index_items": item_count,
        "providers": providers,
        "status": "ready" if index else "not_indexed"
    }


def show_semantic_memory_status():
    """
    Compatibility function expected by seed_tool_kernel.py.
    """
    data = semantic_memory_status_data()

    print("\n=== SEMANTIC MEMORY STATUS ===")
    print(f"Status: {data.get('status')}")
    print(f"Memory file: {data.get('memory_file')}")
    print(f"Index file: {data.get('index_file')}")
    print(f"Notes: {data.get('notes')}")
    print(f"Index exists: {data.get('index_exists')}")
    print(f"Index items: {data.get('index_items')}")

    print("\nProviders:")
    for key, value in data.get("providers", {}).items():
        print(f"- {key}: {value}")

    return data


def get_semantic_memory_status():
    return semantic_memory_status_data()


def semantic_memory_status():
    return semantic_memory_status_data()


def rebuild_semantic_memory_index(root="."):
    return build_semantic_index(root)


def rebuild_semantic_index(root="."):
    return build_semantic_index(root)


def show_semantic_memory_index():
    return show_semantic_index()


def show_semantic_memory_search():
    return show_semantic_search()


def add_semantic_memory_note(text, source="compat", tags=None):
    return add_semantic_memory(text, source=source, tags=tags)


def search_semantic_memory(query, root=".", rebuild=False, max_results=None):
    return semantic_search(query, root=root, rebuild=rebuild, max_results=max_results)


def query_semantic_memory(query, root=".", rebuild=False, max_results=None):
    return semantic_search(query, root=root, rebuild=rebuild, max_results=max_results)



# ============================================================
# Seed v2.3 Legacy Semantic Memory API Compatibility Shim
# ============================================================
# Older Seed modules import old function names from seed_semantic_memory.py.
# v2.3 replaced the internals with semantic_search/build_semantic_index.
# These wrappers keep older modules alive without downgrading the new system.

def build_memory_embedding_index(root="."):
    return build_semantic_index(root)


def rebuild_memory_embedding_index(root="."):
    return build_semantic_index(root)


def build_embedding_index(root="."):
    return build_semantic_index(root)


def rebuild_embedding_index(root="."):
    return build_semantic_index(root)


def load_memory_embedding_index(root="."):
    return load_or_build_index(root)


def load_embedding_index(root="."):
    return load_or_build_index(root)


def save_memory_embedding_index(index=None):
    try:
        if index is None:
            index = load_or_build_index(".")
        safe_save_json(SEED_SEMANTIC_INDEX_FILE, index)
        return True
    except Exception:
        return False


def load_semantic_memory():
    return load_memory()


def save_semantic_memory(data):
    return save_memory(data)


def semantic_memory_status_data():
    try:
        memory = load_memory()
    except Exception:
        memory = {"notes": []}

    try:
        index = safe_load_json(SEED_SEMANTIC_INDEX_FILE, None)
    except Exception:
        index = None

    providers = {}
    item_count = 0

    if index:
        item_count = index.get("item_count", len(index.get("items", [])))
        for item in index.get("items", []):
            provider = item.get("embedding_provider", "unknown")
            providers[provider] = providers.get(provider, 0) + 1

    return {
        "version": "v2.3.0",
        "memory_file": SEED_SEMANTIC_MEMORY_FILE,
        "index_file": SEED_SEMANTIC_INDEX_FILE,
        "notes": len(memory.get("notes", [])),
        "index_exists": bool(index),
        "index_items": item_count,
        "providers": providers,
        "status": "ready" if index else "not_indexed"
    }


def show_semantic_memory_status():
    data = semantic_memory_status_data()

    print("\n=== SEMANTIC MEMORY STATUS ===")
    print(f"Status: {data.get('status')}")
    print(f"Memory file: {data.get('memory_file')}")
    print(f"Index file: {data.get('index_file')}")
    print(f"Notes: {data.get('notes')}")
    print(f"Index exists: {data.get('index_exists')}")
    print(f"Index items: {data.get('index_items')}")

    print("\nProviders:")
    for key, value in data.get("providers", {}).items():
        print(f"- {key}: {value}")

    return data


def get_semantic_memory_status():
    return semantic_memory_status_data()


def semantic_memory_status():
    return semantic_memory_status_data()


def load_embedding_cache():
    try:
        index = safe_load_json(SEED_SEMANTIC_INDEX_FILE, None)
        if not index:
            index = load_or_build_index(".")

        cache = {}
        for item in index.get("items", []):
            key = f"{item.get('kind')}::{item.get('path')}::{item.get('chunk', 0)}"
            cache[key] = {
                "provider": item.get("embedding_provider"),
                "model": item.get("embedding_model"),
                "embedding": item.get("embedding", []),
                "title": item.get("title"),
                "path": item.get("path"),
                "kind": item.get("kind")
            }

        return {
            "created_at": index.get("created_at"),
            "version": index.get("version", "v2.3.0"),
            "provider": "semantic_index_compat",
            "cache": cache,
            "count": len(cache),
            "index_file": SEED_SEMANTIC_INDEX_FILE
        }
    except Exception as error:
        return {
            "created_at": now_timestamp(),
            "version": "v2.3.0",
            "provider": "semantic_index_compat",
            "cache": {},
            "count": 0,
            "error": str(error)
        }


def save_embedding_cache(cache):
    try:
        data = {
            "created_at": now_timestamp(),
            "version": "v2.3.0",
            "compat_embedding_cache": cache
        }
        safe_save_json(SEED_SEMANTIC_MEMORY_FILE + ".compat_cache.json", data)
        return True
    except Exception:
        return False


def get_embedding_cache_stats():
    cache = load_embedding_cache()
    return {
        "count": cache.get("count", 0),
        "provider": cache.get("provider"),
        "index_file": cache.get("index_file", SEED_SEMANTIC_INDEX_FILE),
        "error": cache.get("error")
    }


def get_text_embedding(text):
    return embed_text(text).get("embedding", [])


def get_embedding(text):
    return get_text_embedding(text)


def embed_text_cached(text):
    return embed_text(text)


def add_semantic_memory_note(text, source="compat", tags=None):
    return add_semantic_memory(text, source=source, tags=tags)


def add_memory_to_semantic_index(text, source="compat", tags=None):
    item = add_semantic_memory(text, source=source, tags=tags)
    try:
        build_semantic_index(".")
    except Exception:
        pass
    return item


def search_semantic_memory(query, root=".", rebuild=False, max_results=None):
    return semantic_search(query, root=root, rebuild=rebuild, max_results=max_results)


def semantic_memory_search(query, root=".", rebuild=False, max_results=None):
    return semantic_search(query, root=root, rebuild=rebuild, max_results=max_results)


def query_semantic_memory(query, root=".", rebuild=False, max_results=None):
    return semantic_search(query, root=root, rebuild=rebuild, max_results=max_results)


def recall_semantic_memory(query, root=".", rebuild=False, max_results=None):
    return semantic_search(query, root=root, rebuild=rebuild, max_results=max_results)


def search_memory_embeddings(query, root=".", rebuild=False, max_results=None):
    return semantic_search(query, root=root, rebuild=rebuild, max_results=max_results)


def search_memory_embedding_index(query, root=".", rebuild=False, max_results=None):
    return semantic_search(query, root=root, rebuild=rebuild, max_results=max_results)


def format_semantic_context_for_prompt(user_prompt="", max_results=None):
    try:
        return semantic_memory_context(user_prompt or "")
    except Exception as error:
        return f"=== SEMANTIC MEMORY CONTEXT ===\nUnavailable: {error}\n"


def format_semantic_memory_context_for_prompt(user_prompt="", max_results=None):
    return format_semantic_context_for_prompt(user_prompt, max_results=max_results)


def get_semantic_context_for_prompt(user_prompt="", max_results=None):
    return format_semantic_context_for_prompt(user_prompt, max_results=max_results)


def get_semantic_memory_context_for_prompt(user_prompt="", max_results=None):
    return format_semantic_context_for_prompt(user_prompt, max_results=max_results)


def retrieve_semantic_context(user_prompt="", max_results=None):
    return format_semantic_context_for_prompt(user_prompt, max_results=max_results)


def retrieve_semantic_memory_context(user_prompt="", max_results=None):
    return format_semantic_context_for_prompt(user_prompt, max_results=max_results)


def show_semantic_memory_index():
    return show_semantic_index()


def show_semantic_memory_search():
    return show_semantic_search()


def show_semantic_recall():
    return show_semantic_search()


def show_memory_embedding_index():
    return show_semantic_index()


def show_memory_embedding_search():
    return show_semantic_search()


def __getattr__(name):
    """
    Last-resort compatibility fallback.
    Prevents older optional modules from crashing on import when they ask for
    semantic-memory helper names that map to the new v2.3 engine.
    """
    if "status" in name:
        return semantic_memory_status_data

    if "build" in name and ("index" in name or "embedding" in name):
        return build_semantic_index

    if "rebuild" in name and ("index" in name or "embedding" in name):
        return build_semantic_index

    if "load" in name and "cache" in name:
        return load_embedding_cache

    if "save" in name and "cache" in name:
        return save_embedding_cache

    if "embedding" in name and ("get" in name or "text" in name or "embed" in name):
        return get_text_embedding

    if "search" in name or "query" in name or "recall" in name:
        return semantic_search

    if "context" in name or "format" in name:
        return format_semantic_context_for_prompt

    if "add" in name and "memory" in name:
        return add_semantic_memory

    raise AttributeError(f"module 'seed_semantic_memory' has no attribute '{name}'")

