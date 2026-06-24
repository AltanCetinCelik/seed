import os
from pathlib import Path


try:
    from seed_config import (
        SEED_SKILL_PROJECT_ROOT,
        SEED_SKILL_MAX_READ_BYTES,
        SEED_SKILL_MAX_SEARCH_RESULTS
    )
except Exception:
    SEED_SKILL_PROJECT_ROOT = "."
    SEED_SKILL_MAX_READ_BYTES = 12000
    SEED_SKILL_MAX_SEARCH_RESULTS = 20


TEXT_EXTENSIONS = {
    ".py", ".md", ".txt", ".json", ".yaml", ".yml", ".toml",
    ".html", ".css", ".js", ".ts", ".sh", ".log"
}

SKIP_DIRS = {
    ".git", "__pycache__", ".venv", "venv", "node_modules",
    ".pytest_cache", ".mypy_cache", "dist", "build"
}


def project_root():
    return Path(SEED_SKILL_PROJECT_ROOT).resolve()


def safe_resolve(path_text=""):
    root = project_root()
    target = (root / (path_text or ".")).resolve()

    if root != target and root not in target.parents:
        raise PermissionError("Path escapes Seed project root.")

    return root, target


def path_info(path_text="."):
    root, target = safe_resolve(path_text)
    exists = target.exists()

    return {
        "path": str(target.relative_to(root)) if exists else path_text,
        "exists": exists,
        "is_file": target.is_file() if exists else False,
        "is_dir": target.is_dir() if exists else False,
        "size": target.stat().st_size if exists and target.is_file() else None
    }


def list_dir(path_text=".", limit=200):
    root, target = safe_resolve(path_text)

    if not target.exists():
        return {"ok": False, "error": "Path does not exist.", "items": []}
    if not target.is_dir():
        return {"ok": False, "error": "Path is not a directory.", "items": []}

    items = []
    for item in sorted(target.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))[:limit]:
        if item.name in SKIP_DIRS:
            continue
        rel = str(item.relative_to(root))
        items.append({
            "name": item.name,
            "path": rel,
            "type": "dir" if item.is_dir() else "file",
            "size": item.stat().st_size if item.is_file() else None
        })

    return {
        "ok": True,
        "path": str(target.relative_to(root)),
        "items": items,
        "count": len(items)
    }


def read_file(path_text, max_bytes=None):
    max_bytes = int(max_bytes or SEED_SKILL_MAX_READ_BYTES)
    root, target = safe_resolve(path_text)

    if not target.exists():
        return {"ok": False, "error": "File does not exist.", "path": path_text}
    if not target.is_file():
        return {"ok": False, "error": "Path is not a file.", "path": path_text}

    data = target.read_bytes()[:max_bytes]
    text = data.decode("utf-8", errors="ignore")

    return {
        "ok": True,
        "path": str(target.relative_to(root)),
        "bytes_read": len(data),
        "truncated": target.stat().st_size > max_bytes,
        "text": text
    }


def should_skip(path):
    return bool(set(path.parts).intersection(SKIP_DIRS))


def iter_text_files(root):
    for path in root.rglob("*"):
        if should_skip(path):
            continue
        if path.is_file() and path.suffix.lower() in TEXT_EXTENSIONS:
            yield path


def search_files(query, path_text=".", max_results=None):
    max_results = int(max_results or SEED_SKILL_MAX_SEARCH_RESULTS)
    root, target = safe_resolve(path_text)

    if not target.exists():
        return {"ok": False, "error": "Search path does not exist.", "results": []}

    files = [target] if target.is_file() else list(iter_text_files(target))
    query_lower = (query or "").lower().strip()

    if not query_lower:
        return {"ok": False, "error": "Empty query.", "results": []}

    results = []

    for file_path in files:
        if len(results) >= max_results:
            break

        try:
            text = file_path.read_text(errors="ignore")
        except Exception:
            continue

        lower = text.lower()
        idx = lower.find(query_lower)

        if idx >= 0:
            start = max(0, idx - 180)
            end = min(len(text), idx + 420)
            results.append({
                "path": str(file_path.relative_to(root)),
                "match_index": idx,
                "snippet": text[start:end].replace("\n", " ")
            })

    return {
        "ok": True,
        "query": query,
        "path": str(target.relative_to(root)) if target.exists() else path_text,
        "results": results,
        "count": len(results)
    }


def run_filesystem_skill(operation, args=None):
    args = args or {}

    if operation == "list":
        return list_dir(args.get("path", "."))

    if operation == "read":
        return read_file(args.get("path", ""), max_bytes=args.get("max_bytes"))

    if operation == "search":
        return search_files(
            args.get("query", ""),
            path_text=args.get("path", "."),
            max_results=args.get("max_results")
        )

    if operation == "stat":
        return {"ok": True, "info": path_info(args.get("path", "."))}

    return {"ok": False, "error": f"Unknown filesystem operation: {operation}"}


if __name__ == "__main__":
    print(list_dir("."))
