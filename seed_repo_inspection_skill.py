import ast
from pathlib import Path


SKIP_DIRS = {".git", "__pycache__", ".venv", "venv", "node_modules", ".pytest_cache"}


def should_skip(path):
    return bool(set(path.parts).intersection(SKIP_DIRS))


def python_files(limit=300):
    files = []
    for path in Path(".").resolve().rglob("*.py"):
        if should_skip(path):
            continue
        files.append(path)
        if len(files) >= limit:
            break
    return files


def repo_summary():
    py_files = python_files()
    modules = [str(p.relative_to(Path(".").resolve())) for p in py_files]

    important = [
        p for p in modules
        if any(x in p for x in [
            "seed_action", "seed_skill", "seed_semantic", "seed_voice",
            "seed_v2", "seed_v23", "seed_v24", "seed_cockpit"
        ])
    ]

    return {
        "ok": True,
        "python_file_count": len(py_files),
        "important_modules": important[:80],
        "sample_modules": modules[:80]
    }


def import_graph(limit=200):
    root = Path(".").resolve()
    graph = {}

    for path in python_files(limit):
        rel = str(path.relative_to(root))
        try:
            tree = ast.parse(path.read_text(errors="ignore"))
        except Exception:
            continue

        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)

        graph[rel] = sorted(set(imports))[:80]

    return {
        "ok": True,
        "file_count": len(graph),
        "graph": graph
    }


def find_todos(limit=80):
    root = Path(".").resolve()
    results = []

    for path in python_files(500):
        try:
            lines = path.read_text(errors="ignore").splitlines()
        except Exception:
            continue

        for number, line in enumerate(lines, start=1):
            lower = line.lower()
            if "todo" in lower or "fixme" in lower or "hack" in lower:
                results.append({
                    "path": str(path.relative_to(root)),
                    "line": number,
                    "text": line.strip()
                })
                if len(results) >= limit:
                    return {"ok": True, "results": results, "count": len(results)}

    return {"ok": True, "results": results, "count": len(results)}


def inspect_module(path_text):
    path = Path(path_text)
    if not path.exists() or not path.is_file():
        return {"ok": False, "error": "Module file not found.", "path": path_text}

    try:
        tree = ast.parse(path.read_text(errors="ignore"))
    except Exception as error:
        return {"ok": False, "error": str(error), "path": path_text}

    functions = []
    classes = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            functions.append(node.name)
        elif isinstance(node, ast.ClassDef):
            classes.append(node.name)

    return {
        "ok": True,
        "path": path_text,
        "functions": functions[:120],
        "classes": classes[:80],
        "function_count": len(functions),
        "class_count": len(classes)
    }


def run_repo_skill(operation, args=None):
    args = args or {}

    if operation == "summary":
        return repo_summary()

    if operation == "imports":
        return import_graph(limit=args.get("limit", 200))

    if operation == "todos":
        return find_todos(limit=args.get("limit", 80))

    if operation == "inspect":
        return inspect_module(args.get("path", ""))

    return {"ok": False, "error": f"Unknown repo inspection operation: {operation}"}


if __name__ == "__main__":
    print(repo_summary())
