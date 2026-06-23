import ast
import json
import os
from datetime import datetime

from seed_config import SEED_CODE_MAP_FILE, CODE_MAP_IGNORE_DIRS


try:
    from seed_event_bus import emit_event
    EVENT_BUS_AVAILABLE = True
except Exception:
    EVENT_BUS_AVAILABLE = False


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def should_ignore_path(path):
    parts = path.split(os.sep)

    for part in parts:
        if part in CODE_MAP_IGNORE_DIRS:
            return True

    return False


def list_python_files():
    files = []

    for root, folders, file_names in os.walk("."):
        folders[:] = [
            folder for folder in folders
            if folder not in CODE_MAP_IGNORE_DIRS
        ]

        if should_ignore_path(root):
            continue

        for file_name in file_names:
            if not file_name.endswith(".py"):
                continue

            path = os.path.join(root, file_name)
            path = path.replace("./", "", 1)

            if not should_ignore_path(path):
                files.append(path)

    return sorted(files)


def analyze_python_file(path):
    try:
        with open(path, "r") as file:
            source = file.read()
    except OSError:
        return {
            "path": path,
            "error": "could not read file",
            "imports": [],
            "functions": [],
            "classes": [],
            "line_count": 0
        }

    try:
        tree = ast.parse(source)
    except SyntaxError as error:
        return {
            "path": path,
            "error": str(error),
            "imports": [],
            "functions": [],
            "classes": [],
            "line_count": len(source.splitlines())
        }

    imports = []
    functions = []
    classes = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)

        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""

            for alias in node.names:
                imports.append(f"{module}.{alias.name}")

        elif isinstance(node, ast.FunctionDef):
            functions.append(node.name)

        elif isinstance(node, ast.ClassDef):
            classes.append(node.name)

    return {
        "path": path,
        "imports": sorted(set(imports)),
        "functions": sorted(set(functions)),
        "classes": sorted(set(classes)),
        "line_count": len(source.splitlines())
    }


def build_code_map():
    print("\n=== BUILD SEED CODE MAP ===")

    files = list_python_files()
    modules = []

    for path in files:
        modules.append(analyze_python_file(path))

    data = {
        "created_at": now_timestamp(),
        "file_count": len(files),
        "modules": modules
    }

    with open(SEED_CODE_MAP_FILE, "w") as file:
        json.dump(data, file, indent=4)

    if EVENT_BUS_AVAILABLE:
        try:
            emit_event(
                event_type="code_map_built",
                title="Seed code map built",
                details={
                    "file_count": len(files)
                },
                source="code_map",
                importance=5
            )
        except Exception:
            pass

    print(f"Code map saved: {SEED_CODE_MAP_FILE}")
    print(f"Python files: {len(files)}")

    return data


def load_code_map():
    try:
        with open(SEED_CODE_MAP_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return build_code_map()
    except json.JSONDecodeError:
        return build_code_map()


def format_code_map():
    data = load_code_map()

    text = "=== SEED CODE MAP ===\n"
    text += f"Created: {data.get('created_at')}\n"
    text += f"Python files: {data.get('file_count')}\n\n"

    for module in data.get("modules", []):
        text += f"{module.get('path')}\n"

        if "error" in module:
            text += f"  Error: {module.get('error')}\n"
            continue

        functions = module.get("functions", [])
        classes = module.get("classes", [])
        imports = module.get("imports", [])

        text += f"  Lines: {module.get('line_count')}\n"
        text += f"  Functions: {', '.join(functions[:12])}\n"
        text += f"  Classes: {', '.join(classes[:8])}\n"
        text += f"  Imports: {', '.join(imports[:8])}\n\n"

    return text


def show_code_map():
    print("\n" + format_code_map())


def get_code_map_context_for_prompt(user_prompt):
    lowered = user_prompt.lower()

    keywords = [
        "code",
        "module",
        "file",
        "function",
        "self-edit",
        "architecture",
        "refactor",
        "bug",
        "seed code",
        "repo",
        "foundry",
        "evolution"
    ]

    if not any(keyword in lowered for keyword in keywords):
        return "No code map context needed."

    data = load_code_map()

    text = "=== CODE MAP CONTEXT ===\n"
    text += f"Python files: {data.get('file_count')}\n"

    for module in data.get("modules", [])[:40]:
        if "error" in module:
            text += f"- {module.get('path')}: ERROR {module.get('error')}\n"
            continue

        text += (
            f"- {module.get('path')}: "
            f"{len(module.get('functions', []))} functions, "
            f"{len(module.get('classes', []))} classes\n"
        )

    text += """
Code map rule:
Use this for repo-aware answers and self-improvement planning.
Do not claim exact code details beyond the map unless the file has been read.
"""

    return text


def code_map_summary():
    data = load_code_map()

    return {
        "created_at": data.get("created_at"),
        "file_count": data.get("file_count"),
        "modules": [
            {
                "path": module.get("path"),
                "function_count": len(module.get("functions", [])),
                "class_count": len(module.get("classes", [])),
                "line_count": module.get("line_count"),
                "has_error": "error" in module
            }
            for module in data.get("modules", [])
        ]
    }