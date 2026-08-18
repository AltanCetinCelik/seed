import json
import os
from datetime import datetime


try:
    from seed_config import (
        SEED_DOCUMENT_REGISTRY_FILE,
        DOCUMENT_REGISTRY_SUMMARY_CHAR_LIMIT,
        DOCUMENT_REGISTRY_SEARCH_LIMIT
    )
except Exception:
    SEED_DOCUMENT_REGISTRY_FILE = "seed_document_registry.json"
    DOCUMENT_REGISTRY_SUMMARY_CHAR_LIMIT = 12000
    DOCUMENT_REGISTRY_SEARCH_LIMIT = 12


try:
    from seed_llm import ask_llm
    LLM_AVAILABLE = True
except Exception:
    LLM_AVAILABLE = False


try:
    from seed_companion_os import (
        append_companion_os_event,
        append_companion_os_journal,
        add_companion_os_timeline_event,
        add_memory_garden_artifact
    )
    COMPANION_OS_AVAILABLE = True
except Exception:
    COMPANION_OS_AVAILABLE = False


try:
    from seed_memory_backend import add_layered_memory
    MEMORY_BACKEND_AVAILABLE = True
except Exception:
    MEMORY_BACKEND_AVAILABLE = False


ALLOWED_DOCUMENT_EXTENSIONS = [
    ".txt",
    ".md",
    ".py",
    ".json",
    ".csv",
    ".log"
]


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


def default_registry():
    return {
        "created_at": now_timestamp(),
        "updated_at": now_timestamp(),
        "purpose": (
            "Approved local document registry for Seed. Inspired by Khoj, "
            "AnythingLLM, and LlamaIndex-style knowledge systems."
        ),
        "privacy_rule": (
            "Documents are not registered automatically. User must add them explicitly."
        ),
        "documents": [],
        "counter": 0
    }


def load_registry():
    return load_json(SEED_DOCUMENT_REGISTRY_FILE, default_registry)


def save_registry(registry):
    registry["updated_at"] = now_timestamp()
    save_json(SEED_DOCUMENT_REGISTRY_FILE, registry)


def normalize_path(path):
    return os.path.abspath(os.path.expanduser(path))


def extension_allowed(path):
    _, extension = os.path.splitext(path)
    return extension.lower() in ALLOWED_DOCUMENT_EXTENSIONS


def read_document_text(path, max_chars=None):
    normalized = normalize_path(path)

    if not os.path.exists(normalized):
        return None, "File does not exist."

    if not os.path.isfile(normalized):
        return None, "Path is not a file."

    if not extension_allowed(normalized):
        return None, f"Unsupported extension. Allowed: {', '.join(ALLOWED_DOCUMENT_EXTENSIONS)}"

    try:
        with open(normalized, "r", errors="ignore") as file:
            text = file.read()
    except OSError as error:
        return None, str(error)

    if max_chars is not None:
        text = text[:max_chars]

    return text, None


def document_exists(registry, normalized_path):
    for document in registry.get("documents", []):
        if document.get("path") == normalized_path:
            return True

    return False


def add_document(path, title=None, tags=None, purpose="", privacy_note="user_approved"):
    if tags is None:
        tags = []

    normalized = normalize_path(path)

    text, error = read_document_text(normalized, max_chars=DOCUMENT_REGISTRY_SUMMARY_CHAR_LIMIT)

    if error:
        return {
            "ok": False,
            "message": error
        }

    registry = load_registry()

    if document_exists(registry, normalized):
        return {
            "ok": False,
            "message": "Document already registered."
        }

    registry["counter"] += 1
    document_id = f"DOC-{registry['counter']:03d}"

    if title is None or title.strip() == "":
        title = os.path.basename(normalized)

    document = {
        "id": document_id,
        "created_at": now_timestamp(),
        "updated_at": now_timestamp(),
        "title": title,
        "path": normalized,
        "tags": tags,
        "purpose": purpose,
        "privacy_note": privacy_note,
        "summary": "",
        "last_indexed_at": None,
        "char_count": len(text),
        "status": "registered"
    }

    registry["documents"].append(document)
    save_registry(registry)

    if COMPANION_OS_AVAILABLE:
        try:
            append_companion_os_event(
                "document_registered",
                f"Document registered: {title}",
                {
                    "document_id": document_id,
                    "path": normalized,
                    "tags": tags,
                    "purpose": purpose
                },
                source="document_registry",
                importance=4
            )
        except Exception:
            pass

        try:
            add_companion_os_timeline_event(
                title=f"Document registered: {title}",
                event_type="document",
                note=purpose or normalized,
                importance=3
            )
        except Exception:
            pass

    return {
        "ok": True,
        "document": document
    }


def add_document_interactive():
    print("\n=== ADD DOCUMENT TO SEED REGISTRY ===")
    print("Allowed extensions:", ", ".join(ALLOWED_DOCUMENT_EXTENSIONS))

    path = input("Path: ").strip()
    title = input("Title, optional: ").strip()
    tags_raw = input("Tags, comma-separated: ").strip()
    purpose = input("Purpose: ").strip()
    privacy = input("Privacy note, optional: ").strip()

    if path == "":
        print("Path cannot be empty.")
        return

    tags = [tag.strip() for tag in tags_raw.split(",") if tag.strip()]

    result = add_document(
        path=path,
        title=title or None,
        tags=tags,
        purpose=purpose,
        privacy_note=privacy or "user_approved"
    )

    if result["ok"]:
        print(f"Document registered: {result['document']['id']}")
    else:
        print(result["message"])


def remove_document(document_id):
    registry = load_registry()

    kept = []
    removed = None

    for document in registry.get("documents", []):
        if document.get("id", "").lower() == document_id.lower():
            removed = document
        else:
            kept.append(document)

    if removed is None:
        return {
            "ok": False,
            "message": "Document not found."
        }

    registry["documents"] = kept
    save_registry(registry)

    if COMPANION_OS_AVAILABLE:
        try:
            append_companion_os_event(
                "document_removed",
                f"Document removed: {removed.get('title')}",
                {
                    "document_id": removed.get("id"),
                    "path": removed.get("path")
                },
                source="document_registry",
                importance=3
            )
        except Exception:
            pass

    return {
        "ok": True,
        "document": removed
    }


def remove_document_interactive():
    show_documents()

    document_id = input("\nDocument ID to remove: ").strip()

    if document_id == "":
        print("Document ID cannot be empty.")
        return

    result = remove_document(document_id)

    if result["ok"]:
        print(f"Removed: {result['document']['title']}")
    else:
        print(result["message"])


def find_document(document_id):
    registry = load_registry()

    for document in registry.get("documents", []):
        if document.get("id", "").lower() == document_id.lower():
            return document

    return None


def show_documents():
    registry = load_registry()

    print("\n=== DOCUMENT REGISTRY ===")
    print(f"Documents: {len(registry.get('documents', []))}")
    print(f"Privacy rule: {registry.get('privacy_rule')}")

    if not registry.get("documents"):
        print("No documents registered yet.")
        return

    for document in registry.get("documents", []):
        print(f"\n{document.get('id')} — {document.get('title')}")
        print(f"Path: {document.get('path')}")
        print(f"Tags: {', '.join(document.get('tags', []))}")
        print(f"Purpose: {document.get('purpose')}")
        print(f"Status: {document.get('status')}")
        print(f"Chars: {document.get('char_count')}")
        print(f"Last indexed: {document.get('last_indexed_at')}")


def summarize_document(document_id, chat_state=None):
    document = find_document(document_id)

    if document is None:
        print("Document not found.")
        return None

    text, error = read_document_text(
        document.get("path"),
        max_chars=DOCUMENT_REGISTRY_SUMMARY_CHAR_LIMIT
    )

    if error:
        print(error)
        return None

    if not LLM_AVAILABLE:
        summary = text[:1500]
    else:
        prompt = f"""
You are Seed's Document Registry.

Summarize this user-approved local document for future companion memory.

Document:
ID: {document.get('id')}
Title: {document.get('title')}
Tags: {', '.join(document.get('tags', []))}
Purpose: {document.get('purpose')}
Privacy note: {document.get('privacy_note')}

Text:
{text}

Output:
1. short summary
2. important facts
3. why it may matter to Seed/User
4. suggested memory layer
5. safety/privacy caveat
"""

        summary = ask_llm(prompt, task_type="memory", runtime_context=chat_state)

    registry = load_registry()

    for item in registry.get("documents", []):
        if item.get("id") == document.get("id"):
            item["summary"] = summary
            item["last_indexed_at"] = now_timestamp()
            item["status"] = "summarized"

    save_registry(registry)

    if MEMORY_BACKEND_AVAILABLE:
        try:
            add_layered_memory(
                layer="document",
                content=f"{document.get('title')}: {summary}",
                source="document_registry",
                importance=4,
                tags=document.get("tags", [])
            )
        except Exception:
            pass

    if COMPANION_OS_AVAILABLE:
        try:
            append_companion_os_event(
                "document_summarized",
                f"Document summarized: {document.get('title')}",
                {
                    "document_id": document.get("id"),
                    "title": document.get("title")
                },
                source="document_registry",
                importance=4
            )
        except Exception:
            pass

        try:
            add_memory_garden_artifact(
                name=f"Document: {document.get('title')}",
                meaning=f"Seed registered and summarized this approved document: {document.get('purpose')}",
                artifact_type="document"
            )
        except Exception:
            pass

    print("\n=== DOCUMENT SUMMARY ===")
    print(summary)

    return summary


def summarize_document_interactive(chat_state=None):
    show_documents()

    document_id = input("\nDocument ID to summarize: ").strip()

    if document_id == "":
        print("Document ID cannot be empty.")
        return

    summarize_document(document_id, chat_state=chat_state)


def search_documents(query, limit=DOCUMENT_REGISTRY_SEARCH_LIMIT):
    registry = load_registry()

    query_words = [
        word.lower()
        for word in query.split()
        if len(word.strip()) >= 3
    ]

    results = []

    for document in registry.get("documents", []):
        haystack = json.dumps(document).lower()

        score = 0

        for word in query_words:
            if word in haystack:
                score += 3

        path = document.get("path")
        text, error = read_document_text(path, max_chars=8000)

        if text:
            lowered_text = text.lower()

            for word in query_words:
                if word in lowered_text:
                    score += 1

        if score > 0:
            results.append({
                "score": score,
                "document": document
            })

    results.sort(key=lambda result: result["score"], reverse=True)
    return results[:limit]


def search_documents_interactive():
    query = input("Document search query: ").strip()

    if query == "":
        print("Query cannot be empty.")
        return

    results = search_documents(query)

    print("\n=== DOCUMENT SEARCH ===")

    if not results:
        print("No document matches.")
        return

    for result in results:
        document = result["document"]
        print(f"\nScore {result['score']} | {document.get('id')} — {document.get('title')}")
        print(f"Tags: {', '.join(document.get('tags', []))}")
        print(f"Purpose: {document.get('purpose')}")
        if document.get("summary"):
            print(f"Summary: {document.get('summary')[:700]}")


def show_document_context(query=None):
    registry = load_registry()

    if query:
        results = search_documents(query)
        documents = [result["document"] for result in results]
    else:
        documents = registry.get("documents", [])[-DOCUMENT_REGISTRY_SEARCH_LIMIT:]

    print("\n=== DOCUMENT CONTEXT ===")

    if not documents:
        print("No document context.")
        return

    for document in documents:
        print(f"\n{document.get('id')} — {document.get('title')}")
        print(f"Purpose: {document.get('purpose')}")
        print(f"Tags: {', '.join(document.get('tags', []))}")
        print(f"Summary: {document.get('summary') or 'No summary yet.'}")


def document_context_interactive():
    query = input("Context query, optional: ").strip()

    if query == "":
        query = None

    show_document_context(query)


def get_document_registry_context_for_prompt(user_prompt=""):
    results = search_documents(user_prompt, limit=5) if user_prompt else []
    registry = load_registry()

    text = "=== DOCUMENT REGISTRY CONTEXT ===\n"
    text += f"Registered documents: {len(registry.get('documents', []))}\n"
    text += f"Privacy rule: {registry.get('privacy_rule')}\n"

    if not results:
        text += "No query-matched documents for this prompt.\n"
    else:
        text += "\nRelevant approved documents:\n"

        for result in results:
            document = result["document"]
            text += f"- {document.get('id')} {document.get('title')} | score {result['score']}\n"
            text += f"  Purpose: {document.get('purpose')}\n"
            text += f"  Tags: {', '.join(document.get('tags', []))}\n"
            if document.get("summary"):
                text += f"  Summary: {document.get('summary')[:1000]}\n"

    text += """
Document Registry rule:
Only use documents that User explicitly registered.
Do not claim broad filesystem knowledge.
If a document has no summary, say it needs summarization/indexing first.
"""

    return text


if __name__ == "__main__":
    show_documents()
