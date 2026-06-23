import json
from datetime import datetime


try:
    from seed_config import SEED_OS_REGISTRY_CACHE_FILE
except Exception:
    SEED_OS_REGISTRY_CACHE_FILE = "seed_os_registry_cache.json"


try:
    from seed_companion_os import append_companion_os_event
    COMPANION_OS_AVAILABLE = True
except Exception:
    COMPANION_OS_AVAILABLE = False


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


COMMAND_REGISTRY = [
    {
        "command": "/help",
        "owner": "core",
        "risk": "read_only",
        "approval": "not_required",
        "description": "Show available Seed commands.",
        "v2_pillars": ["Cockpit", "Safety"],
        "source_repos": []
    },
    {
        "command": "/status",
        "owner": "core",
        "risk": "read_only",
        "approval": "not_required",
        "description": "Show Seed system status.",
        "v2_pillars": ["Safety", "Cockpit"],
        "source_repos": []
    },
    {
        "command": "/hud",
        "owner": "visuals",
        "risk": "read_only",
        "approval": "not_required",
        "description": "Show Seed terminal HUD.",
        "v2_pillars": ["Cockpit", "Presence"],
        "source_repos": ["Open WebUI"]
    },
    {
        "command": "/save",
        "owner": "smart_memory",
        "risk": "write",
        "approval": "user_confirms_memory",
        "description": "Smart memory capture into Seed memory.",
        "v2_pillars": ["Memory", "Continuity"],
        "source_repos": ["Letta", "Khoj", "AnythingLLM"]
    },
    {
        "command": "/semantic-search",
        "owner": "semantic_memory",
        "risk": "read_only",
        "approval": "not_required",
        "description": "Search Seed memory by meaning.",
        "v2_pillars": ["Memory", "Continuity"],
        "source_repos": ["Letta", "Khoj"]
    },
    {
        "command": "/memory-reindex",
        "owner": "semantic_memory",
        "risk": "diagnostic",
        "approval": "not_required",
        "description": "Rebuild semantic memory index.",
        "v2_pillars": ["Memory"],
        "source_repos": ["Letta", "Khoj", "AnythingLLM"]
    },
    {
        "command": "/project",
        "owner": "project_inspector",
        "risk": "read_only",
        "approval": "not_required",
        "description": "Show Seed project report.",
        "v2_pillars": ["Self-improvement"],
        "source_repos": ["Aider", "SWE-agent"]
    },
    {
        "command": "/code-map",
        "owner": "code_map",
        "risk": "read_only",
        "approval": "not_required",
        "description": "Show repo-aware code map.",
        "v2_pillars": ["Self-improvement"],
        "source_repos": ["Aider", "SWE-agent", "mini-SWE-agent"]
    },
    {
        "command": "/code-map-build",
        "owner": "code_map",
        "risk": "diagnostic",
        "approval": "not_required",
        "description": "Build repo-aware code map.",
        "v2_pillars": ["Self-improvement"],
        "source_repos": ["Aider", "SWE-agent", "mini-SWE-agent"]
    },
    {
        "command": "/self-edit",
        "owner": "self_editor",
        "risk": "write",
        "approval": "requires_diff_and_apply_confirmation",
        "description": "Create pending self-edit proposal.",
        "v2_pillars": ["Self-improvement", "Safety"],
        "source_repos": ["Cline", "Aider", "OpenHands"]
    },
    {
        "command": "/self-apply",
        "owner": "self_editor",
        "risk": "write",
        "approval": "exact_apply_confirmation_required",
        "description": "Apply approved self-edit proposal.",
        "v2_pillars": ["Self-improvement", "Safety"],
        "source_repos": ["Cline", "Aider"]
    },
    {
        "command": "/self-rollback",
        "owner": "self_editor",
        "risk": "write",
        "approval": "explicit_user_action",
        "description": "Rollback latest self-edit backup.",
        "v2_pillars": ["Safety", "Self-improvement"],
        "source_repos": ["Cline", "Aider"]
    },
    {
        "command": "/dna",
        "owner": "open_source_dna",
        "risk": "read_only",
        "approval": "not_required",
        "description": "Show open-source DNA status.",
        "v2_pillars": ["Self-improvement"],
        "source_repos": ["all_cloned_repos"]
    },
    {
        "command": "/dna-audit-all",
        "owner": "open_source_dna",
        "risk": "diagnostic",
        "approval": "not_required",
        "description": "Audit cloned repos for Seed inspiration.",
        "v2_pillars": ["Self-improvement"],
        "source_repos": ["all_cloned_repos"]
    },
    {
        "command": "/skills",
        "owner": "skill_os",
        "risk": "read_only",
        "approval": "not_required",
        "description": "Show Seed Skill OS.",
        "v2_pillars": ["Agency", "Safety"],
        "source_repos": ["MCP Servers", "OpenClaw", "OpenHands"]
    },
    {
        "command": "/capability-run",
        "owner": "skill_os",
        "risk": "varies",
        "approval": "depends_on_capability_risk",
        "description": "Run a registered Seed capability.",
        "v2_pillars": ["Agency", "Safety"],
        "source_repos": ["MCP Servers", "Cline"]
    },
    {
        "command": "/companion",
        "owner": "companion_growth",
        "risk": "read_only",
        "approval": "not_required",
        "description": "Show Companion Growth OS.",
        "v2_pillars": ["Growth", "Continuity", "Presence"],
        "source_repos": ["Hermes Agent", "Letta", "OpenClaw"]
    },
    {
        "command": "/companion-pulse",
        "owner": "companion_growth",
        "risk": "diagnostic",
        "approval": "not_required",
        "description": "Generate companion growth pulse.",
        "v2_pillars": ["Growth", "Continuity", "Presence"],
        "source_repos": ["Hermes Agent", "Moltbot AI Assistant"]
    },
    {
        "command": "/ritual-run",
        "owner": "companion_growth",
        "risk": "diagnostic",
        "approval": "not_required",
        "description": "Run selected companion ritual.",
        "v2_pillars": ["Growth", "Presence"],
        "source_repos": ["Moltbot AI Assistant", "OpenClaw"]
    },
    {
        "command": "/presence",
        "owner": "presence_os",
        "risk": "read_only",
        "approval": "not_required",
        "description": "Show Seed symbolic presence state.",
        "v2_pillars": ["Presence"],
        "source_repos": ["Hermes Agent", "Moltbot AI Assistant"]
    },
    {
        "command": "/computer",
        "owner": "computer_awareness",
        "risk": "diagnostic",
        "approval": "not_required",
        "description": "Show local computer/project snapshot.",
        "v2_pillars": ["Agency", "Safety"],
        "source_repos": ["Open Interpreter", "OpenClaw"]
    },
    {
        "command": "/local-shell",
        "owner": "local_control",
        "risk": "diagnostic_or_dangerous",
        "approval": "allowlist_or_exact_phrase",
        "description": "Run safe/approval-gated local shell command.",
        "v2_pillars": ["Agency", "Safety"],
        "source_repos": ["Open Interpreter", "Cline"]
    },
    {
        "command": "/open-app",
        "owner": "local_control",
        "risk": "diagnostic",
        "approval": "allowlisted_apps_only",
        "description": "Open allowlisted app.",
        "v2_pillars": ["Agency", "Presence"],
        "source_repos": ["Open Interpreter", "Moltbot AI Assistant"]
    },
    {
        "command": "/foundry",
        "owner": "evolution_foundry",
        "risk": "read_only",
        "approval": "not_required",
        "description": "Show Evolution Foundry OS.",
        "v2_pillars": ["Self-improvement", "Agency"],
        "source_repos": ["Aider", "SWE-agent", "OpenHands"]
    },
    {
        "command": "/evolve",
        "owner": "evolution_foundry",
        "risk": "diagnostic",
        "approval": "not_required",
        "description": "Generate repo-DNA-based evolution proposals.",
        "v2_pillars": ["Self-improvement", "Growth"],
        "source_repos": ["Aider", "SWE-agent", "OpenHands", "Cline"]
    },
    {
        "command": "/candidate-self-edit-prompt",
        "owner": "evolution_foundry",
        "risk": "write",
        "approval": "autonomy_level_and_user_command_required",
        "description": "Generate self-edit prompt from release candidate.",
        "v2_pillars": ["Self-improvement", "Safety"],
        "source_repos": ["Cline", "Aider"]
    },
    {
        "command": "/events",
        "owner": "event_bus",
        "risk": "read_only",
        "approval": "not_required",
        "description": "Show runtime event stream.",
        "v2_pillars": ["Continuity", "Safety"],
        "source_repos": ["LangGraph", "OpenHands"]
    },
    {
        "command": "/companion-os",
        "owner": "companion_os",
        "risk": "read_only",
        "approval": "not_required",
        "description": "Show Companion OS Alpha state.",
        "v2_pillars": ["Continuity", "Memory", "Growth", "Presence", "Agency", "World", "Safety"],
        "source_repos": ["all_cloned_repos"]
    },
    {
        "command": "/v2-check",
        "owner": "v2_release_gate",
        "risk": "diagnostic",
        "approval": "not_required",
        "description": "Run v2 release gate.",
        "v2_pillars": ["Safety", "Self-improvement", "Cockpit"],
        "source_repos": ["Cline", "Aider", "Open WebUI"]
    }
]


def get_os_command_registry():
    return COMMAND_REGISTRY


def save_registry_cache():
    data = {
        "created_at": now_timestamp(),
        "command_count": len(COMMAND_REGISTRY),
        "commands": COMMAND_REGISTRY
    }

    with open(SEED_OS_REGISTRY_CACHE_FILE, "w") as file:
        json.dump(data, file, indent=4)

    if COMPANION_OS_AVAILABLE:
        try:
            append_companion_os_event(
                "os_registry_cached",
                "OS command registry cached",
                {"command_count": len(COMMAND_REGISTRY)},
                source="os_registry",
                importance=3
            )
        except Exception:
            pass

    return data


def registry_stats():
    owners = {}
    risks = {}
    pillars = {}

    for item in COMMAND_REGISTRY:
        owner = item.get("owner", "unknown")
        risk = item.get("risk", "unknown")

        owners[owner] = owners.get(owner, 0) + 1
        risks[risk] = risks.get(risk, 0) + 1

        for pillar in item.get("v2_pillars", []):
            pillars[pillar] = pillars.get(pillar, 0) + 1

    return {
        "command_count": len(COMMAND_REGISTRY),
        "owners": owners,
        "risks": risks,
        "pillars": pillars
    }


def format_os_registry():
    stats = registry_stats()

    text = "=== SEED OS COMMAND REGISTRY ===\n"
    text += f"Commands: {stats['command_count']}\n\n"

    text += "By owner:\n"
    for owner, count in sorted(stats["owners"].items()):
        text += f"- {owner}: {count}\n"

    text += "\nBy risk:\n"
    for risk, count in sorted(stats["risks"].items()):
        text += f"- {risk}: {count}\n"

    text += "\nBy v2 pillar:\n"
    for pillar, count in sorted(stats["pillars"].items()):
        text += f"- {pillar}: {count}\n"

    return text


def show_os_registry():
    save_registry_cache()
    print("\n" + format_os_registry())


def show_os_command_map():
    print("\n=== OS COMMAND MAP ===")

    for item in COMMAND_REGISTRY:
        print(f"\n{item.get('command')} — {item.get('description')}")
        print(f"Owner: {item.get('owner')}")
        print(f"Risk: {item.get('risk')}")
        print(f"Approval: {item.get('approval')}")
        print(f"V2 pillars: {', '.join(item.get('v2_pillars', []))}")
        print(f"Source repos: {', '.join(item.get('source_repos', []))}")


def find_command(command):
    normalized = command.strip().lower()

    for item in COMMAND_REGISTRY:
        if item.get("command", "").lower() == normalized:
            return item

    return None


def show_os_command_owner(command=None):
    if command is None:
        command = input("Command: ").strip()

    item = find_command(command)

    print("\n=== OS COMMAND OWNER ===")

    if item is None:
        print("Command not found in registry.")
        return

    print(f"Command: {item.get('command')}")
    print(f"Owner: {item.get('owner')}")
    print(f"Risk: {item.get('risk')}")
    print(f"Approval: {item.get('approval')}")
    print(f"Description: {item.get('description')}")
    print(f"V2 pillars: {', '.join(item.get('v2_pillars', []))}")
    print(f"Source repos: {', '.join(item.get('source_repos', []))}")


def show_os_risk_map():
    grouped = {}

    for item in COMMAND_REGISTRY:
        risk = item.get("risk", "unknown")
        grouped.setdefault(risk, []).append(item)

    print("\n=== OS RISK MAP ===")

    for risk, commands in sorted(grouped.items()):
        print(f"\n{risk.upper()}")

        for item in commands:
            print(f"- {item.get('command')} [{item.get('owner')}] — {item.get('approval')}")


def validate_os_registry():
    failures = []

    required = ["command", "owner", "risk", "approval", "description", "v2_pillars", "source_repos"]

    seen = set()

    for item in COMMAND_REGISTRY:
        for key in required:
            if key not in item:
                failures.append(f"{item.get('command', 'unknown')} missing {key}")

        command = item.get("command")

        if command in seen:
            failures.append(f"Duplicate command: {command}")

        seen.add(command)

    return failures


def show_registry_validation():
    failures = validate_os_registry()

    print("\n=== OS REGISTRY VALIDATION ===")

    if not failures:
        print("Registry valid.")
        return

    for failure in failures:
        print(f"- {failure}")


def get_registry_context_for_prompt():
    stats = registry_stats()

    text = "=== OS REGISTRY CONTEXT ===\n"
    text += f"Known commands: {stats['command_count']}\n"

    text += "\nOwners:\n"
    for owner, count in sorted(stats["owners"].items()):
        text += f"- {owner}: {count}\n"

    text += "\nRisk counts:\n"
    for risk, count in sorted(stats["risks"].items()):
        text += f"- {risk}: {count}\n"

    text += """
Registry rule:
Use this registry to understand command ownership, risk, approval style, and v2 pillar coverage.
Do not invent tool powers beyond the registered commands and capabilities.
"""

    return text


if __name__ == "__main__":
    show_os_registry()
    show_registry_validation()
