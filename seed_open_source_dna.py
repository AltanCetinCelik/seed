import json
import os
from datetime import datetime

from seed_config import (
    THIRD_PARTY_REPOS_DIR,
    SEED_RESEARCH_DIR,
    OPEN_SOURCE_DNA_FILE,
    OPEN_SOURCE_DNA_REPORT_FILE,
    BORROW_CANDIDATES_FILE,
    DNA_README_CHAR_LIMIT,
    DNA_KEY_FILE_LIMIT,
    DNA_CANDIDATE_LIMIT,
    DNA_CANDIDATE_MAX_FILE_BYTES,
    DNA_CONTEXT_ENABLED
)
from seed_llm import ask_llm


EXPECTED_REPOS = [
    {
        "folder": "letta",
        "name": "Letta",
        "category": "memory",
        "use_for": "long-term agent memory, memory layers, archival recall"
    },
    {
        "folder": "khoj",
        "name": "Khoj",
        "category": "memory",
        "use_for": "second-brain knowledge retrieval and personal search"
    },
    {
        "folder": "anything-llm",
        "name": "AnythingLLM",
        "category": "memory_cockpit",
        "use_for": "workspace-based RAG, local knowledge base, document UX"
    },
    {
        "folder": "SWE-agent",
        "name": "SWE-agent",
        "category": "coding_agent",
        "use_for": "software-engineering agent workflow and repo problem solving"
    },
    {
        "folder": "mini-swe-agent",
        "name": "mini-SWE-agent",
        "category": "coding_agent",
        "use_for": "minimal coding-agent loop and simple harness patterns"
    },
    {
        "folder": "openhands",
        "name": "OpenHands",
        "category": "coding_agent",
        "use_for": "developer-agent control center and task workflow"
    },
    {
        "folder": "openinterpreter",
        "name": "Open Interpreter",
        "category": "local_actions",
        "use_for": "controlled local code/computer action interface ideas"
    },
    {
        "folder": "aider",
        "name": "Aider",
        "category": "coding_agent",
        "use_for": "repo-aware coding assistant, codebase map, terminal coding workflow"
    },
    {
        "folder": "Cline",
        "name": "Cline",
        "category": "coding_agent",
        "use_for": "human-in-the-loop file edits, command execution, and approval workflow"
    },
    {
        "folder": "hermes-agent",
        "name": "Hermes Agent",
        "category": "agent_architecture",
        "use_for": "growing personal agent, skill creation, persistent companion direction"
    },
    {
        "folder": "langgraph",
        "name": "LangGraph",
        "category": "agent_architecture",
        "use_for": "long-running stateful agent orchestration"
    },
    {
        "folder": "servers",
        "name": "MCP Servers",
        "category": "tool_protocol",
        "use_for": "future-proof tool protocol and external-tool connection ideas"
    },
    {
        "folder": "open-webui",
        "name": "Open WebUI",
        "category": "cockpit",
        "use_for": "self-hosted AI cockpit, model UI, RAG/provider panels"
    },
    {
        "folder": "openclaw",
        "name": "OpenClaw",
        "category": "local_companion",
        "use_for": "local assistant skill/gateway ecosystem and integrations"
    },
    {
        "folder": "moltworker",
        "name": "Moltworker",
        "category": "local_companion",
        "use_for": "self-hosted OpenClaw/Moltbot-style implementation"
    },
    {
        "folder": "moltbot-ai-assistant",
        "name": "Moltbot AI Assistant",
        "category": "local_companion",
        "use_for": "related local assistant/integration reference"
    }
]


IGNORED_DIRS = {
    ".git",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    "dist",
    "build",
    ".next",
    ".pytest_cache",
    "target",
    ".cache",
    ".turbo"
}


SOURCE_EXTENSIONS = {
    ".py",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".json",
    ".yaml",
    ".yml",
    ".md",
    ".toml"
}


BORROW_KEYWORDS = [
    "tool",
    "tools",
    "skill",
    "skills",
    "permission",
    "permissions",
    "risk",
    "approval",
    "approve",
    "planner",
    "plan",
    "agent",
    "memory",
    "workspace",
    "vector",
    "embedding",
    "registry",
    "manifest",
    "capability",
    "capabilities",
    "context",
    "sandbox",
    "human-in-the-loop",
    "checkpoint",
    "rollback"
]


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def ensure_research_dir():
    os.makedirs(SEED_RESEARCH_DIR, exist_ok=True)


def read_text_file(path, limit=None):
    try:
        with open(path, "r", errors="ignore") as file:
            text = file.read()
    except FileNotFoundError:
        return ""
    except IsADirectoryError:
        return ""
    except OSError:
        return ""

    if limit is not None:
        return text[:limit]

    return text


def write_json(path, data):
    ensure_research_dir()

    with open(path, "w") as file:
        json.dump(data, file, indent=4)


def read_json(path, default):
    try:
        with open(path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return default
    except json.JSONDecodeError:
        return default


def known_repo_by_folder(folder):
    for repo in EXPECTED_REPOS:
        if repo["folder"].lower() == folder.lower():
            return repo

    return {
        "folder": folder,
        "name": folder,
        "category": "unknown",
        "use_for": "unknown"
    }


def get_repo_path(folder):
    return os.path.join(THIRD_PARTY_REPOS_DIR, folder)


def find_readme(repo_path):
    candidates = [
        "README.md",
        "readme.md",
        "README.rst",
        "README.txt",
        "Readme.md"
    ]

    for candidate in candidates:
        path = os.path.join(repo_path, candidate)

        if os.path.exists(path):
            return candidate

    return None


def find_license(repo_path):
    candidates = [
        "LICENSE",
        "LICENSE.md",
        "LICENSE.txt",
        "license",
        "COPYING",
        "NOTICE"
    ]

    for candidate in candidates:
        path = os.path.join(repo_path, candidate)

        if os.path.exists(path):
            return candidate

    return None


def list_top_level(repo_path):
    try:
        items = sorted(os.listdir(repo_path))
    except FileNotFoundError:
        return []

    return [
        item for item in items
        if item not in IGNORED_DIRS
    ]


def is_interesting_file(file_name):
    lower = file_name.lower()

    interesting_names = [
        "readme",
        "license",
        "agent",
        "tool",
        "skill",
        "memory",
        "planner",
        "registry",
        "sandbox",
        "workspace",
        "mcp",
        "context",
        "config",
        "prompt"
    ]

    for name in interesting_names:
        if name in lower:
            return True

    extension = os.path.splitext(file_name)[1]

    return extension in SOURCE_EXTENSIONS


def list_key_files(repo_path, limit=DNA_KEY_FILE_LIMIT):
    key_files = []

    for root, folders, files in os.walk(repo_path):
        folders[:] = [
            folder for folder in folders
            if folder not in IGNORED_DIRS
        ]

        for file_name in files:
            if not is_interesting_file(file_name):
                continue

            full_path = os.path.join(root, file_name)
            relative_path = os.path.relpath(full_path, repo_path)

            key_files.append(relative_path)

            if len(key_files) >= limit:
                return sorted(key_files)

    return sorted(key_files)


def get_existing_repo_folders():
    if not os.path.exists(THIRD_PARTY_REPOS_DIR):
        return []

    folders = []

    for item in os.listdir(THIRD_PARTY_REPOS_DIR):
        path = os.path.join(THIRD_PARTY_REPOS_DIR, item)

        if os.path.isdir(path):
            folders.append(item)

    return sorted(folders)


def get_repo_scan(folder):
    known = known_repo_by_folder(folder)
    repo_path = get_repo_path(folder)

    exists = os.path.exists(repo_path)

    readme_file = find_readme(repo_path) if exists else None
    license_file = find_license(repo_path) if exists else None

    readme_text = ""
    license_text = ""

    if readme_file is not None:
        readme_text = read_text_file(
            os.path.join(repo_path, readme_file),
            DNA_README_CHAR_LIMIT
        )

    if license_file is not None:
        license_text = read_text_file(
            os.path.join(repo_path, license_file),
            1200
        )

    return {
        "folder": folder,
        "name": known["name"],
        "category": known["category"],
        "use_for": known["use_for"],
        "path": repo_path,
        "exists": exists,
        "readme_file": readme_file,
        "license_file": license_file,
        "license_preview": license_text,
        "top_level": list_top_level(repo_path) if exists else [],
        "key_files": list_key_files(repo_path) if exists else [],
        "readme_excerpt": readme_text
    }


def scan_open_source_dna():
    print("\n=== OPEN-SOURCE DNA SCAN ===")

    ensure_research_dir()

    previous = read_json(
        OPEN_SOURCE_DNA_FILE,
        {
            "audits": {}
        }
    )

    expected_folders = [repo["folder"] for repo in EXPECTED_REPOS]
    actual_folders = get_existing_repo_folders()

    all_folders = []

    for folder in expected_folders:
        if folder not in all_folders:
            all_folders.append(folder)

    for folder in actual_folders:
        if folder not in all_folders:
            all_folders.append(folder)

    repos = []

    for folder in all_folders:
        repo_scan = get_repo_scan(folder)
        repos.append(repo_scan)

        status = "found" if repo_scan["exists"] else "missing"
        print(f"{repo_scan['name']}: {status}")

    data = {
        "created_at": now_timestamp(),
        "third_party_dir": THIRD_PARTY_REPOS_DIR,
        "repo_count": len(repos),
        "found_count": len([repo for repo in repos if repo["exists"]]),
        "repos": repos,
        "audits": previous.get("audits", {}),
        "notes": {
            "purpose": "Seed open-source DNA research index.",
            "rule": "Borrow patterns and small understood code only after license review."
        }
    }

    write_json(OPEN_SOURCE_DNA_FILE, data)

    print(f"\nSaved: {OPEN_SOURCE_DNA_FILE}")
    print(f"Repos found: {data['found_count']} / {data['repo_count']}")

    return data


def load_dna_data():
    data = read_json(OPEN_SOURCE_DNA_FILE, None)

    if data is None:
        data = scan_open_source_dna()

    return data


def find_repo_in_data(repo_query):
    data = load_dna_data()
    repo_query = repo_query.lower().strip()

    for repo in data.get("repos", []):
        if repo_query in repo.get("folder", "").lower():
            return repo

        if repo_query in repo.get("name", "").lower():
            return repo

    return None


def extract_json_object(text):
    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1 or end <= start:
        return None

    possible_json = text[start:end + 1]

    try:
        return json.loads(possible_json)
    except json.JSONDecodeError:
        return None


def build_repo_audit_prompt(repo):
    key_files = "\n".join(repo.get("key_files", [])[:DNA_KEY_FILE_LIMIT])
    top_level = "\n".join(repo.get("top_level", []))
    readme_excerpt = repo.get("readme_excerpt", "")
    license_preview = repo.get("license_preview", "")

    return f"""
You are Seed's open-source DNA auditor.

Seed is a local-first private companion system built by Altan.
Seed has memory, semantic memory, smart memory capture, self-editing with approval gates, an agent kernel, HUD, and local Ollama cognition.

Audit this cloned open-source repo for ideas Seed can borrow.

Repo:
Name: {repo.get('name')}
Folder: {repo.get('folder')}
Category: {repo.get('category')}
Seed intended use: {repo.get('use_for')}
License file: {repo.get('license_file')}

Top-level files:
{top_level}

Key files:
{key_files}

License preview:
{license_preview}

README excerpt:
{readme_excerpt}

Return JSON only.

JSON shape:
{{
  "repo": "repo name",
  "best_use_for_seed": "short answer",
  "patterns_to_borrow": ["pattern 1", "pattern 2"],
  "code_to_study": ["file or module idea 1", "file or module idea 2"],
  "code_to_avoid": ["dangerous or too-complex thing"],
  "memory_lessons": ["lesson"],
  "skill_kernel_lessons": ["lesson"],
  "planner_lessons": ["lesson"],
  "cockpit_lessons": ["lesson"],
  "safety_lessons": ["lesson"],
  "concrete_seed_upgrades": ["upgrade 1", "upgrade 2"],
  "risk_notes": ["risk 1"],
  "license_note": "what to verify before copying code"
}}

Rules:
- Be strict.
- Do not say to copy huge subsystems.
- Prefer small, understandable, Seed-native adaptations.
- Anything that edits files, runs commands, accesses credentials, uses browser/computer control, or integrates external accounts must be approval-gated.
"""


def audit_repo(repo_query, chat_state=None):
    repo = find_repo_in_data(repo_query)

    if repo is None:
        print(f"No repo found for: {repo_query}")
        return None

    if not repo.get("exists"):
        print(f"Repo is missing locally: {repo.get('folder')}")
        return None

    print(f"\n=== DNA AUDIT: {repo.get('name')} ===")
    print("Seed is auditing this repo with the local LLM...")

    prompt = build_repo_audit_prompt(repo)

    response = ask_llm(
        prompt,
        task_type="debug",
        runtime_context=chat_state
    )

    parsed = extract_json_object(response)

    if parsed is None:
        parsed = {
            "repo": repo.get("name"),
            "raw_response": response,
            "parse_warning": "LLM did not return valid JSON."
        }

    data = load_dna_data()

    if "audits" not in data:
        data["audits"] = {}

    data["audits"][repo.get("folder")] = {
        "created_at": now_timestamp(),
        "audit": parsed
    }

    write_json(OPEN_SOURCE_DNA_FILE, data)

    print("Audit saved.")
    print(format_single_audit(repo.get("folder")))

    return parsed


def audit_all_repos(chat_state=None):
    data = load_dna_data()

    print("\n=== FULL OPEN-SOURCE DNA AUDIT ===")
    print("This may take a while because each repo is audited by the local LLM.")

    for repo in data.get("repos", []):
        if not repo.get("exists"):
            continue

        audit_repo(repo.get("folder"), chat_state)

    generate_open_source_report()
    print("\nFull DNA audit complete.")


def format_single_audit(folder):
    data = load_dna_data()
    audits = data.get("audits", {})

    if folder not in audits:
        return f"No audit found for: {folder}"

    audit = audits[folder].get("audit", {})

    text = f"=== DNA AUDIT: {audit.get('repo', folder)} ===\n"

    if "raw_response" in audit:
        text += audit["raw_response"]
        return text

    text += f"Best use for Seed: {audit.get('best_use_for_seed', '')}\n"
    text += f"License note: {audit.get('license_note', '')}\n"

    sections = [
        ("Patterns to borrow", "patterns_to_borrow"),
        ("Code to study", "code_to_study"),
        ("Code to avoid", "code_to_avoid"),
        ("Memory lessons", "memory_lessons"),
        ("Skill kernel lessons", "skill_kernel_lessons"),
        ("Planner lessons", "planner_lessons"),
        ("Cockpit lessons", "cockpit_lessons"),
        ("Safety lessons", "safety_lessons"),
        ("Concrete Seed upgrades", "concrete_seed_upgrades"),
        ("Risk notes", "risk_notes")
    ]

    for title, key in sections:
        text += f"\n{title}:\n"

        items = audit.get(key, [])

        if not items:
            text += "- none\n"
        else:
            for item in items:
                text += f"- {item}\n"

    return text


def format_dna_status():
    data = load_dna_data()
    audits = data.get("audits", {})

    text = "=== OPEN-SOURCE DNA STATUS ===\n"
    text += f"DNA file: {OPEN_SOURCE_DNA_FILE}\n"
    text += f"Report file: {OPEN_SOURCE_DNA_REPORT_FILE}\n"
    text += f"Repos found: {data.get('found_count')} / {data.get('repo_count')}\n"
    text += f"Audits completed: {len(audits)}\n\n"

    for repo in data.get("repos", []):
        status = "found" if repo.get("exists") else "missing"
        audited = "audited" if repo.get("folder") in audits else "not audited"

        text += (
            f"- {repo.get('name')} "
            f"[{repo.get('category')}] "
            f"{status}, {audited}\n"
        )

    return text


def show_dna_status():
    print("\n" + format_dna_status())


def format_repo_dna(repo_query):
    repo = find_repo_in_data(repo_query)

    if repo is None:
        return f"No repo found for: {repo_query}"

    text = f"=== REPO DNA: {repo.get('name')} ===\n"
    text += f"Folder: {repo.get('folder')}\n"
    text += f"Category: {repo.get('category')}\n"
    text += f"Use for: {repo.get('use_for')}\n"
    text += f"Exists: {repo.get('exists')}\n"
    text += f"README: {repo.get('readme_file')}\n"
    text += f"License: {repo.get('license_file')}\n"

    text += "\nTop-level:\n"
    for item in repo.get("top_level", []):
        text += f"- {item}\n"

    text += "\nKey files:\n"
    for item in repo.get("key_files", [])[:60]:
        text += f"- {item}\n"

    text += "\n"
    text += format_single_audit(repo.get("folder"))

    return text


def show_repo_dna(repo_query):
    print("\n" + format_repo_dna(repo_query))


def generate_open_source_report():
    data = load_dna_data()

    report = "# Seed Open-Source DNA Report\n\n"
    report += f"Generated: {now_timestamp()}\n\n"
    report += "## Purpose\n\n"
    report += (
        "This report records what Seed can learn from cloned open-source "
        "agent, memory, coding, cockpit, and local companion projects.\n\n"
    )

    report += "## Repos\n\n"

    for repo in data.get("repos", []):
        report += f"### {repo.get('name')}\n\n"
        report += f"- Folder: `{repo.get('folder')}`\n"
        report += f"- Category: `{repo.get('category')}`\n"
        report += f"- Use for Seed: {repo.get('use_for')}\n"
        report += f"- Exists locally: {repo.get('exists')}\n"
        report += f"- README: {repo.get('readme_file')}\n"
        report += f"- License: {repo.get('license_file')}\n\n"

        audit_record = data.get("audits", {}).get(repo.get("folder"))

        if audit_record is None:
            report += "Audit: not completed yet.\n\n"
            continue

        audit = audit_record.get("audit", {})

        if "raw_response" in audit:
            report += "Audit raw response:\n\n"
            report += audit["raw_response"] + "\n\n"
            continue

        report += f"Best use: {audit.get('best_use_for_seed', '')}\n\n"

        sections = [
            ("Patterns to borrow", "patterns_to_borrow"),
            ("Code to study", "code_to_study"),
            ("Code to avoid", "code_to_avoid"),
            ("Concrete Seed upgrades", "concrete_seed_upgrades"),
            ("Risk notes", "risk_notes"),
            ("License note", "license_note")
        ]

        for title, key in sections:
            report += f"#### {title}\n\n"

            value = audit.get(key, [])

            if isinstance(value, str):
                report += f"- {value}\n\n"
                continue

            if not value:
                report += "- none\n\n"
            else:
                for item in value:
                    report += f"- {item}\n"
                report += "\n"

    ensure_research_dir()

    with open(OPEN_SOURCE_DNA_REPORT_FILE, "w") as file:
        file.write(report)

    print(f"Report written: {OPEN_SOURCE_DNA_REPORT_FILE}")

    return report


def show_dna_report():
    if not os.path.exists(OPEN_SOURCE_DNA_REPORT_FILE):
        generate_open_source_report()

    print(read_text_file(OPEN_SOURCE_DNA_REPORT_FILE))


def format_borrow_map():
    data = load_dna_data()
    audits = data.get("audits", {})

    categories = {}

    for repo in data.get("repos", []):
        category = repo.get("category", "unknown")

        if category not in categories:
            categories[category] = []

        audit_record = audits.get(repo.get("folder"))
        audit = audit_record.get("audit", {}) if audit_record else {}

        categories[category].append({
            "repo": repo,
            "audit": audit
        })

    text = "=== SEED BORROW MAP ===\n"

    for category, items in categories.items():
        text += f"\n## {category}\n"

        for item in items:
            repo = item["repo"]
            audit = item["audit"]

            text += f"\n{repo.get('name')}\n"
            text += f"Use for: {repo.get('use_for')}\n"

            upgrades = audit.get("concrete_seed_upgrades", [])

            if upgrades:
                text += "Candidate upgrades:\n"
                for upgrade in upgrades[:5]:
                    text += f"- {upgrade}\n"
            else:
                text += "Candidate upgrades: audit not done yet.\n"

    return text


def show_borrow_map():
    print("\n" + format_borrow_map())


def file_should_be_scanned(path):
    extension = os.path.splitext(path)[1]

    if extension not in SOURCE_EXTENSIONS:
        return False

    try:
        size = os.path.getsize(path)
    except OSError:
        return False

    if size > DNA_CANDIDATE_MAX_FILE_BYTES:
        return False

    return True


def keyword_hits_for_text(text):
    lowered = text.lower()
    hits = []

    for keyword in BORROW_KEYWORDS:
        if keyword in lowered:
            hits.append(keyword)

    return hits


def build_preview(text, hits, max_lines=12):
    lines = text.splitlines()
    preview_lines = []

    lowered_hits = [hit.lower() for hit in hits]

    for index, line in enumerate(lines, start=1):
        lowered_line = line.lower()

        if any(hit in lowered_line for hit in lowered_hits):
            cleaned = line.strip()

            if cleaned:
                preview_lines.append(f"{index}: {cleaned}")

        if len(preview_lines) >= max_lines:
            break

    return preview_lines


def build_borrow_candidate_index():
    print("\n=== BUILD BORROW CANDIDATE INDEX ===")

    data = load_dna_data()
    candidates = []

    for repo in data.get("repos", []):
        if not repo.get("exists"):
            continue

        repo_path = repo.get("path")

        for root, folders, files in os.walk(repo_path):
            folders[:] = [
                folder for folder in folders
                if folder not in IGNORED_DIRS
            ]

            for file_name in files:
                full_path = os.path.join(root, file_name)

                if not file_should_be_scanned(full_path):
                    continue

                text = read_text_file(full_path)

                hits = keyword_hits_for_text(text)

                if len(hits) < 2:
                    continue

                relative_path = os.path.relpath(full_path, repo_path)
                preview = build_preview(text, hits)

                candidates.append({
                    "repo_folder": repo.get("folder"),
                    "repo_name": repo.get("name"),
                    "category": repo.get("category"),
                    "license_file": repo.get("license_file"),
                    "path": relative_path,
                    "score": len(hits),
                    "keywords": hits,
                    "preview": preview
                })

    candidates.sort(
        key=lambda item: item.get("score", 0),
        reverse=True
    )

    candidates = candidates[:DNA_CANDIDATE_LIMIT]

    output = {
        "created_at": now_timestamp(),
        "candidate_count": len(candidates),
        "candidates": candidates,
        "rule": "Candidates are for study only. Verify license and understand code before borrowing."
    }

    write_json(BORROW_CANDIDATES_FILE, output)

    print(f"Saved: {BORROW_CANDIDATES_FILE}")
    print(f"Candidates: {len(candidates)}")

    return output


def load_borrow_candidates():
    data = read_json(BORROW_CANDIDATES_FILE, None)

    if data is None:
        data = build_borrow_candidate_index()

    return data


def format_borrow_candidates(limit=40):
    data = load_borrow_candidates()
    candidates = data.get("candidates", [])

    text = "=== BORROW CANDIDATES ===\n"
    text += f"Candidate count: {len(candidates)}\n"
    text += "Rule: study only, verify license before copying.\n\n"

    for index, candidate in enumerate(candidates[:limit], start=1):
        text += f"{index}. {candidate.get('repo_name')} / {candidate.get('path')}\n"
        text += f"   Category: {candidate.get('category')}\n"
        text += f"   Score: {candidate.get('score')}\n"
        text += f"   Keywords: {', '.join(candidate.get('keywords', [])[:10])}\n"

        preview = candidate.get("preview", [])

        if preview:
            text += "   Preview:\n"
            for line in preview[:4]:
                text += f"   - {line}\n"

        text += "\n"

    return text


def show_borrow_candidates(limit=40):
    print("\n" + format_borrow_candidates(limit))


def show_borrow_candidate_file(candidate_number):
    data = load_borrow_candidates()
    candidates = data.get("candidates", [])

    try:
        index = int(candidate_number) - 1
    except ValueError:
        print("Invalid candidate number.")
        return

    if index < 0 or index >= len(candidates):
        print("Invalid candidate number.")
        return

    candidate = candidates[index]

    repo_path = get_repo_path(candidate.get("repo_folder"))
    file_path = os.path.join(repo_path, candidate.get("path"))

    print("\n=== BORROW CANDIDATE FILE ===")
    print(f"Repo: {candidate.get('repo_name')}")
    print(f"File: {candidate.get('path')}")
    print(f"License file: {candidate.get('license_file')}")
    print("Rule: study only. Do not copy blindly.\n")

    text = read_text_file(file_path, 12000)
    lines = text.splitlines()

    for line_number, line in enumerate(lines[:220], start=1):
        print(f"{line_number:04d}: {line}")


def get_dna_context_for_prompt(user_prompt):
    if not DNA_CONTEXT_ENABLED:
        return "Open-source DNA context is disabled."

    lowered = user_prompt.lower()

    dna_keywords = [
        "open-source",
        "open source",
        "repo",
        "repos",
        "borrow",
        "hermes",
        "moltbot",
        "openclaw",
        "letta",
        "aider",
        "cline",
        "swe-agent",
        "openhands",
        "skill kernel",
        "planner",
        "cockpit",
        "v1.12",
        "v2.0"
    ]

    if not any(keyword in lowered for keyword in dna_keywords):
        return "No open-source DNA context needed."

    data = load_dna_data()
    audits = data.get("audits", {})

    text = "=== OPEN-SOURCE DNA CONTEXT ===\n"
    text += f"Repos found: {data.get('found_count')} / {data.get('repo_count')}\n"
    text += f"Audits completed: {len(audits)}\n"

    text += "\nResearch repos:\n"
    for repo in data.get("repos", []):
        text += (
            f"- {repo.get('name')} "
            f"[{repo.get('category')}]: "
            f"{repo.get('use_for')}\n"
        )

    text += """
Open-source DNA rule:
Use cloned repositories as inspiration for Seed-native architecture.
Borrow patterns first.
Only borrow code after license review and understanding.
Dangerous automation must stay approval-gated.
"""

    return text