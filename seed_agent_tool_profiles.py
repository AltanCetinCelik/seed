import json
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path


try:
    from seed_config import SEED_AGENT_TOOL_PROFILES_FILE
except Exception:
    SEED_AGENT_TOOL_PROFILES_FILE = "seed_agent_tool_profiles.json"


AGENT_TOOL_PROFILES = [
    {
        "id": "aider",
        "name": "Aider",
        "kind": "coding_assistant",
        "commands": ["aider"],
        "risk": "file_write",
        "approval_required": True,
        "sandbox_required": True,
        "best_for": ["small/medium repo edits", "git-aware code changes"]
    },
    {
        "id": "openhands",
        "name": "OpenHands",
        "kind": "coding_agent",
        "commands": ["openhands"],
        "risk": "file_write_and_shell",
        "approval_required": True,
        "sandbox_required": True,
        "best_for": ["larger coding tasks", "issue solving", "multi-step repo work"]
    },
    {
        "id": "swe_agent",
        "name": "SWE-agent",
        "kind": "coding_agent",
        "commands": ["sweagent", "swe-agent"],
        "risk": "file_write_and_shell",
        "approval_required": True,
        "sandbox_required": True,
        "best_for": ["test-driven bug fixing", "software engineering tasks"]
    },
    {
        "id": "browser_use",
        "name": "browser-use",
        "kind": "browser_agent",
        "commands": ["browser-use"],
        "risk": "external_web_action",
        "approval_required": True,
        "sandbox_required": True,
        "best_for": ["browser automation", "web UI research"]
    },
    {
        "id": "mcp",
        "name": "MCP",
        "kind": "tool_protocol",
        "commands": ["mcp"],
        "risk": "external_tool_access",
        "approval_required": True,
        "sandbox_required": True,
        "best_for": ["tool connectors", "standard tool servers"]
    },
    {
        "id": "pytest",
        "name": "pytest",
        "kind": "test_runner",
        "commands": ["pytest"],
        "risk": "diagnostic",
        "approval_required": False,
        "sandbox_required": False,
        "best_for": ["Python tests"]
    },
    {
        "id": "git",
        "name": "git",
        "kind": "repo_control",
        "commands": ["git"],
        "risk": "read_write",
        "approval_required": True,
        "sandbox_required": True,
        "best_for": ["status", "diff", "branch", "rollback"]
    }
]


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def command_exists(command):
    return shutil.which(command) is not None


def detect_command(commands):
    for command in commands:
        path = shutil.which(command)
        if path:
            return {
                "available": True,
                "command": command,
                "path": path
            }
    return {
        "available": False,
        "command": None,
        "path": None
    }


def scan_local_repos(root=None, limit=80):
    root = Path(root or Path.home() / "Desktop")
    repos = []

    if not root.exists():
        return repos

    for path in root.rglob(".git"):
        repo = path.parent
        if len(repos) >= limit:
            break

        try:
            status = subprocess.run(
                ["git", "-C", str(repo), "status", "--short"],
                capture_output=True,
                text=True,
                timeout=4
            )
            dirty = bool(status.stdout.strip())
        except Exception:
            dirty = None

        repos.append({
            "path": str(repo),
            "name": repo.name,
            "dirty": dirty
        })

    return repos


def build_profiles():
    profiles = []
    for profile in AGENT_TOOL_PROFILES:
        item = dict(profile)
        detection = detect_command(profile.get("commands", []))
        item["available"] = detection["available"]
        item["detected_command"] = detection["command"]
        item["detected_path"] = detection["path"]
        profiles.append(item)
    return profiles


def save_profiles():
    data = {
        "created_at": now_timestamp(),
        "updated_at": now_timestamp(),
        "version": "v2.1.0",
        "profiles": build_profiles(),
        "local_repos": scan_local_repos()
    }

    with open(SEED_AGENT_TOOL_PROFILES_FILE, "w") as file:
        json.dump(data, file, indent=4)

    return data


def load_profiles():
    try:
        with open(SEED_AGENT_TOOL_PROFILES_FILE, "r") as file:
            return json.load(file)
    except Exception:
        return save_profiles()


def agent_tool_profiles_data(refresh=True):
    return save_profiles() if refresh else load_profiles()


def find_profile(profile_id):
    data = agent_tool_profiles_data(refresh=True)
    for profile in data.get("profiles", []):
        if profile.get("id") == profile_id:
            return profile
    return None


def show_agent_tool_profiles():
    data = agent_tool_profiles_data(refresh=True)

    print("\n=== AGENT TOOL PROFILES ===")
    for profile in data.get("profiles", []):
        print(f"\n{profile.get('name')} ({profile.get('id')})")
        print(f"Available: {profile.get('available')} | Command: {profile.get('detected_command')}")
        print(f"Risk: {profile.get('risk')}")
        print(f"Approval required: {profile.get('approval_required')}")
        print(f"Sandbox required: {profile.get('sandbox_required')}")
        print(f"Best for: {', '.join(profile.get('best_for', []))}")

    print("\nLocal repos found:")
    for repo in data.get("local_repos", [])[:30]:
        print(f"- {repo.get('name')}: {repo.get('path')} dirty={repo.get('dirty')}")


def show_agent_install_plan():
    print("\n=== OPTIONAL AGENT TOOL INSTALL PLAN ===")
    print("Do not install everything blindly. Install only what you actually need.")
    print("")
    print("Useful first installs:")
    print("- Aider for direct repo edits:")
    print("  python -m pip install aider-chat")
    print("")
    print("- browser-use for browser automation:")
    print("  python -m pip install browser-use")
    print("")
    print("OpenHands/SWE-agent may need heavier setup. Treat them as separate sandbox projects.")
    print("")
    print("Seed rule:")
    print("- Agent tools can write files or use shell/browser.")
    print("- Seed must ask approval before running them.")
    print("- Use git branch/backups/tests/rollback.")


def get_agent_tool_profiles_context_for_prompt():
    data = agent_tool_profiles_data(refresh=True)
    available = [p for p in data.get("profiles", []) if p.get("available")]
    text = "=== AGENT TOOL PROFILES CONTEXT ===\n"
    text += f"Profiles: {len(data.get('profiles', []))}\n"
    text += f"Available: {', '.join(p.get('id') for p in available) or 'none'}\n"
    text += f"Local repos found: {len(data.get('local_repos', []))}\n"
    text += "Rule: file-writing/shell/browser agents require approval, sandbox, tests, and rollback.\n"
    return text


if __name__ == "__main__":
    show_agent_tool_profiles()
