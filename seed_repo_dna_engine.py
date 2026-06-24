import ast
import json
import warnings
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path


try:
    from seed_config import SEED_REPO_DNA_FILE
except Exception:
    SEED_REPO_DNA_FILE = "seed_repo_dna.json"


SCAN_EXTENSIONS = {".py", ".md", ".json", ".txt", ".html", ".css", ".js", ".toml", ".yaml", ".yml"}
MAX_PY_PARSE_FILES = 900
MAX_DETAILS_SAMPLE = 30

IGNORE_DIRS = {
    ".git", "__pycache__", ".venv", "venv", "node_modules", "seed_agent_runs",
    ".pytest_cache", ".mypy_cache", ".ruff_cache", ".cache",
    "dist", "build", "site-packages", "backup", "backups",
    "archive", "archives", "vendor", "external_repos", "repos"
}


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def should_skip(path):
    return any(part in IGNORE_DIRS for part in path.parts)


def read_text(path, limit=60000):
    try:
        text = path.read_text(errors="ignore")
        return text[:limit]
    except Exception:
        return ""


def parse_python_file(path):
    text = read_text(path)
    result = {
        "file": str(path),
        "imports": [],
        "functions": [],
        "classes": [],
        "commands": [],
        "routes": [],
        "mentions": Counter()
    }

    lowered = text.lower()
    for key in [
        "voice", "agent", "aider", "mcp", "browser", "memory", "semantic",
        "cockpit", "control plane", "mission", "release", "repair", "skill",
        "ollama", "whisper", "fastapi", "http", "safety", "approval"
    ]:
        if key in lowered:
            result["mentions"][key] += lowered.count(key)

    for line in text.splitlines():
        stripped = line.strip()
        if 'command ==' in stripped and '"/' in stripped:
            try:
                cmd = stripped.split('"/', 1)[1].split('"', 1)[0]
                result["commands"].append("/" + cmd)
            except Exception:
                pass
        if stripped.startswith("@app.") or "add_api_route" in stripped:
            result["routes"].append(stripped[:180])

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", SyntaxWarning)
            tree = ast.parse(text)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for item in node.names:
                    result["imports"].append(item.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    result["imports"].append(node.module.split(".")[0])
            elif isinstance(node, ast.FunctionDef):
                result["functions"].append(node.name)
            elif isinstance(node, ast.AsyncFunctionDef):
                result["functions"].append(node.name)
            elif isinstance(node, ast.ClassDef):
                result["classes"].append(node.name)
    except Exception:
        pass

    result["mentions"] = dict(result["mentions"])
    return result


def build_repo_dna():
    root = Path(".")
    files = []
    py_details = []
    command_counter = Counter()
    import_counter = Counter()
    mention_counter = Counter()
    module_groups = defaultdict(list)

    for path in root.rglob("*"):
        if should_skip(path):
            continue
        if not path.is_file():
            continue
        if path.suffix.lower() not in SCAN_EXTENSIONS:
            continue

        rel = str(path)
        files.append(rel)

        name = path.name.lower()
        if name.startswith("seed_") and path.suffix == ".py":
            if "voice" in name:
                module_groups["voice"].append(rel)
            elif "agent" in name or "aider" in name or "executor" in name:
                module_groups["agents"].append(rel)
            elif "memory" in name or "semantic" in name:
                module_groups["memory"].append(rel)
            elif "cockpit" in name or "control" in name:
                module_groups["ui_control"].append(rel)
            elif "gate" in name or "release" in name:
                module_groups["release"].append(rel)
            elif "skill" in name:
                module_groups["skills"].append(rel)
            elif "repair" in name:
                module_groups["repair"].append(rel)
            else:
                module_groups["core"].append(rel)

        if path.suffix == ".py":
            if len(py_details) >= MAX_PY_PARSE_FILES:
                continue
            detail = parse_python_file(path)
            py_details.append(detail)
            command_counter.update(detail["commands"])
            import_counter.update(detail["imports"])
            mention_counter.update(detail["mentions"])

    dna = {
        "created_at": now_timestamp(),
        "version": "v3.5.0",
        "ok": True,
        "file_count": len(files),
        "python_file_count": len(py_details),
        "module_groups": {k: sorted(v) for k, v in module_groups.items()},
        "top_imports": import_counter.most_common(30),
        "top_mentions": mention_counter.most_common(30),
        "commands": sorted(command_counter.keys()),
        "command_count": len(command_counter.keys()),
        "python_details_sample": py_details[:MAX_DETAILS_SAMPLE],
        "dna_summary": {
            "has_voice": bool(module_groups["voice"]),
            "has_agents": bool(module_groups["agents"]),
            "has_memory": bool(module_groups["memory"]),
            "has_control_plane": bool(module_groups["ui_control"]),
            "has_release_gates": bool(module_groups["release"]),
            "has_skills": bool(module_groups["skills"]),
            "has_repair": bool(module_groups["repair"])
        }
    }

    with open(SEED_REPO_DNA_FILE, "w") as file:
        json.dump(dna, file, indent=4)

    return dna


def repo_dna_context(user_prompt=""):
    dna = build_repo_dna()
    lines = ["=== SEED REPO DNA ==="]
    lines.append(f"Python files: {dna['python_file_count']}")
    lines.append(f"Commands: {dna['command_count']}")
    lines.append("Module groups:")
    for group, items in dna["module_groups"].items():
        lines.append(f"- {group}: {len(items)}")
    return "\n".join(lines)


def show_repo_dna():
    dna = build_repo_dna()

    print("\n=== SEED REPO DNA ===")
    print(f"Files scanned: {dna['file_count']}")
    print(f"Python files: {dna['python_file_count']}")
    print(f"Commands: {dna['command_count']}")

    print("\nModule groups:")
    for group, items in dna["module_groups"].items():
        print(f"- {group}: {len(items)}")

    print("\nTop mentions:")
    for key, count in dna["top_mentions"][:15]:
        print(f"- {key}: {count}")


if __name__ == "__main__":
    show_repo_dna()
