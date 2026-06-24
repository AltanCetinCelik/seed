import json
import os
from datetime import datetime
from pathlib import Path


try:
    from seed_config import (
        SEED_CAPABILITY_MEMORY_FILE,
        SEED_CAPABILITY_MEMORY_INDEX_FILE,
        SEED_MEMORY_INDEX_MAX_FILES,
        SEED_MEMORY_INDEX_MAX_FILE_BYTES,
        SEED_MEMORY_SEARCH_MAX_RESULTS
    )
except Exception:
    SEED_CAPABILITY_MEMORY_FILE = "seed_capability_memory.json"
    SEED_CAPABILITY_MEMORY_INDEX_FILE = "seed_capability_memory_index.json"
    SEED_MEMORY_INDEX_MAX_FILES = 500
    SEED_MEMORY_INDEX_MAX_FILE_BYTES = 250000
    SEED_MEMORY_SEARCH_MAX_RESULTS = 8


TEXT_EXTENSIONS = {
    ".py", ".md", ".txt", ".json", ".yaml", ".yml", ".toml",
    ".html", ".css", ".js", ".ts", ".sh"
}

SKIP_DIRS = {
    ".git", "__pycache__", ".venv", "venv", "node_modules",
    "seed_agent_runs", ".mypy_cache", ".pytest_cache",
    "seed_private_backup", "dist", "build"
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
    current = []
    for ch in (text or "").lower():
        if ch.isalnum() or ch in "_-":
            current.append(ch)
        else:
            if current:
                out.append("".join(current))
                current = []
    if current:
        out.append("".join(current))
    return out


def default_memory():
    return {
        "created_at": now_timestamp(),
        "updated_at": now_timestamp(),
        "version": "v2.2.0",
        "notes": []
    }


def load_memory():
    return safe_load_json(SEED_CAPABILITY_MEMORY_FILE, default_memory)


def save_memory(data):
    data["updated_at"] = now_timestamp()
    safe_save_json(SEED_CAPABILITY_MEMORY_FILE, data)


def add_memory_note(text, source="manual", tags=None):
    data = load_memory()
    note = {
        "created_at": now_timestamp(),
        "source": source,
        "text": text,
        "tags": tags or []
    }
    data.setdefault("notes", []).append(note)
    save_memory(data)
    return note


def should_skip_path(path):
    parts = set(path.parts)
    return bool(parts.intersection(SKIP_DIRS))


def iter_indexable_files(root="."):
    root = Path(root).resolve()
    count = 0

    for path in root.rglob("*"):
        if count >= int(SEED_MEMORY_INDEX_MAX_FILES):
            break

        if not path.is_file():
            continue

        if should_skip_path(path):
            continue

        if path.suffix.lower() not in TEXT_EXTENSIONS:
            continue

        try:
            size = path.stat().st_size
        except Exception:
            continue

        if size > int(SEED_MEMORY_INDEX_MAX_FILE_BYTES):
            continue

        count += 1
        yield path


def read_text_file(path):
    try:
        return path.read_text(errors="ignore")
    except Exception:
        try:
            return path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return ""


def build_memory_index(root="."):
    items = []
    root_path = Path(root).resolve()

    # Manual capability memory notes.
    memory = load_memory()
    for idx, note in enumerate(memory.get("notes", [])):
        text = note.get("text", "")
        items.append({
            "kind": "manual_memory",
            "path": f"memory_note_{idx}",
            "title": "Manual capability memory",
            "text": text[:2000],
            "tokens": tokenize(text),
            "created_at": note.get("created_at"),
            "source": note.get("source")
        })

    # Repo/document text files.
    for path in iter_indexable_files(root_path):
        text = read_text_file(path)
        if not text.strip():
            continue

        rel = str(path.relative_to(root_path))
        title = path.name

        items.append({
            "kind": "file",
            "path": rel,
            "title": title,
            "text": text[:4000],
            "tokens": tokenize(text[:12000]),
            "mtime": path.stat().st_mtime
        })

    index = {
        "created_at": now_timestamp(),
        "version": "v2.2.0",
        "root": str(root_path),
        "item_count": len(items),
        "items": items
    }

    safe_save_json(SEED_CAPABILITY_MEMORY_INDEX_FILE, index)
    return index


def load_or_build_index(root="."):
    index = safe_load_json(SEED_CAPABILITY_MEMORY_INDEX_FILE, None)
    if not index:
        return build_memory_index(root)
    return index


def search_memory(query, root=".", max_results=None, rebuild=False):
    max_results = max_results or int(SEED_MEMORY_SEARCH_MAX_RESULTS)
    index = build_memory_index(root) if rebuild else load_or_build_index(root)

    query_tokens = tokenize(query)
    if not query_tokens:
        return []

    results = []

    for item in index.get("items", []):
        tokens = item.get("tokens", [])
        token_set = set(tokens)
        score = 0

        for q in query_tokens:
            if q in token_set:
                score += 5
            score += sum(1 for t in tokens if q in t and q != t)

        text_lower = item.get("text", "").lower()
        if query.lower() in text_lower:
            score += 10

        if score > 0:
            snippet = item.get("text", "")[:800].replace("\n", " ")
            results.append({
                "score": score,
                "kind": item.get("kind"),
                "path": item.get("path"),
                "title": item.get("title"),
                "snippet": snippet
            })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:max_results]


def show_memory_index():
    index = build_memory_index(".")
    print("\n=== SEED CAPABILITY MEMORY INDEX ===")
    print(f"Items indexed: {index.get('item_count')}")
    print(f"Root: {index.get('root')}")
    print(f"Index file: {SEED_CAPABILITY_MEMORY_INDEX_FILE}")


def show_memory_search():
    query = input("Search Seed memory/repo/docs: ").strip()
    results = search_memory(query, rebuild=False)

    print("\n=== MEMORY / REPO SEARCH ===")
    if not results:
        print("No results.")
        return

    for result in results:
        print(f"\n[{result['score']}] {result['kind']} — {result['path']}")
        print(result["snippet"][:700])


def show_memory_add():
    text = input("Memory note to add: ").strip()
    if not text:
        print("No memory added.")
        return

    note = add_memory_note(text, source="seed_cli")
    print("\nAdded memory note:")
    print(json.dumps(note, indent=4))


def memory_context(query):
    results = search_memory(query, rebuild=False, max_results=5)
    text = "=== CAPABILITY MEMORY CONTEXT ===\n"
    if not results:
        text += "No relevant local memory results.\n"
        return text

    for result in results:
        text += f"- {result['kind']} {result['path']} score={result['score']}: {result['snippet'][:250]}\n"
    return text


if __name__ == "__main__":
    show_memory_index()
