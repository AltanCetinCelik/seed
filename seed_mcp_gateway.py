import json
import shutil
from datetime import datetime


try:
    from seed_config import SEED_MCP_GATEWAY_STATE_FILE
except Exception:
    SEED_MCP_GATEWAY_STATE_FILE = "seed_mcp_gateway_state.json"


MCP_PROFILES = [
    {
        "id": "filesystem",
        "name": "Filesystem MCP",
        "risk": "file_read_write",
        "approval_required": True,
        "best_for": ["safe local file tool access", "project file operations"]
    },
    {
        "id": "git",
        "name": "Git MCP",
        "risk": "repo_control",
        "approval_required": True,
        "best_for": ["git status", "diffs", "branches", "commit workflows"]
    },
    {
        "id": "browser",
        "name": "Browser MCP",
        "risk": "external_web_action",
        "approval_required": True,
        "best_for": ["web browsing", "page extraction", "browser automation"]
    },
    {
        "id": "github",
        "name": "GitHub MCP",
        "risk": "external_account_action",
        "approval_required": True,
        "best_for": ["issues", "pull requests", "repo metadata"]
    }
]


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def command_exists(command):
    return shutil.which(command) is not None


def mcp_gateway_data():
    data = {
        "created_at": now_timestamp(),
        "version": "v2.2.0",
        "plan_only_by_default": True,
        "commands": {
            "node": command_exists("node"),
            "npm": command_exists("npm"),
            "npx": command_exists("npx"),
            "uv": command_exists("uv"),
            "uvx": command_exists("uvx")
        },
        "profiles": MCP_PROFILES,
        "ready_for_planning": True,
        "ready_for_execution": False,
        "execution_reason": "MCP execution is intentionally disabled until explicit profile config and approval gates are added."
    }

    with open(SEED_MCP_GATEWAY_STATE_FILE, "w") as file:
        json.dump(data, file, indent=4)

    return data


def build_mcp_plan(task):
    lowered = task.lower()
    matches = []

    for profile in MCP_PROFILES:
        blob = json.dumps(profile).lower()
        if any(word in lowered for word in profile.get("best_for", [])) or profile["id"] in lowered or profile["name"].lower() in lowered:
            matches.append(profile)

    if not matches:
        if "file" in lowered or "folder" in lowered:
            matches.append(MCP_PROFILES[0])
        elif "git" in lowered or "repo" in lowered:
            matches.append(MCP_PROFILES[1])
        elif "browser" in lowered or "web" in lowered:
            matches.append(MCP_PROFILES[2])
        elif "github" in lowered:
            matches.append(MCP_PROFILES[3])

    return {
        "created_at": now_timestamp(),
        "task": task,
        "matches": matches,
        "approval_required": True,
        "execution_status": "plan_only",
        "safe_order": [
            "Select MCP profile",
            "Show exact server/config needed",
            "Ask User for approval",
            "Run in sandbox/allowlist mode",
            "Verify result",
            "Log action"
        ]
    }


def show_mcp_gateway():
    data = mcp_gateway_data()
    print("\n=== MCP GATEWAY ===")
    print(f"Ready for planning: {data['ready_for_planning']}")
    print(f"Ready for execution: {data['ready_for_execution']}")
    print("\nCommands:")
    for key, value in data["commands"].items():
        print(f"- {key}: {value}")
    print("\nProfiles:")
    for profile in data["profiles"]:
        print(f"- {profile['name']} ({profile['id']}) risk={profile['risk']}")


def show_mcp_plan():
    task = input("MCP task: ").strip()
    plan = build_mcp_plan(task)
    print(json.dumps(plan, indent=4))


def get_mcp_context():
    data = mcp_gateway_data()
    return (
        "=== MCP GATEWAY CONTEXT ===\n"
        f"Ready for planning: {data['ready_for_planning']}\n"
        f"Ready for execution: {data['ready_for_execution']}\n"
        "Rule: MCP execution stays disabled until explicit config and approval.\n"
    )


if __name__ == "__main__":
    show_mcp_gateway()
