import json
import os
from datetime import datetime

from seed_config import (
    SEED_SKILLS_DIR,
    SKILL_CONTEXT_ENABLED
)


DEFAULT_SKILL_MANIFESTS = [
    {
        "id": "memory",
        "name": "Memory Skill",
        "category": "memory",
        "inspired_by": ["Letta", "Khoj", "AnythingLLM"],
        "purpose": "Manage Seed's long-term, semantic, and smart captured memories.",
        "risk": "read_only",
        "approval_rule": "Saving or deleting memories requires user approval.",
        "capabilities": [
            {
                "id": "memory.stats",
                "name": "Memory statistics",
                "risk": "read_only",
                "tool": "memory_stats",
                "description": "Show memory counts and type distribution."
            },
            {
                "id": "memory.duplicates",
                "name": "Memory duplicate scan",
                "risk": "read_only",
                "tool": "memory_duplicates",
                "description": "Find possible duplicate memories."
            },
            {
                "id": "memory.semantic_status",
                "name": "Semantic memory status",
                "risk": "read_only",
                "tool": "semantic_memory_status",
                "description": "Show semantic memory cache and embedding status."
            },
            {
                "id": "memory.smart_capture",
                "name": "Smart memory capture",
                "risk": "write",
                "command": "/save <text>",
                "description": "Infer type, content, and importance from natural memory text."
            }
        ]
    },
    {
        "id": "self_edit",
        "name": "Self-Edit Skill",
        "category": "self_modification",
        "inspired_by": ["Cline", "Aider", "SWE-agent", "mini-SWE-agent"],
        "purpose": "Let Seed safely inspect, propose, apply, test, and roll back edits.",
        "risk": "dangerous",
        "approval_rule": "File modification requires diff review and exact APPLY confirmation.",
        "capabilities": [
            {
                "id": "self_edit.status",
                "name": "Editable files status",
                "risk": "read_only",
                "tool": "self_edit_status",
                "description": "Show files Seed is allowed to edit."
            },
            {
                "id": "self_edit.syntax_test",
                "name": "Python syntax test",
                "risk": "diagnostic",
                "tool": "self_test",
                "description": "Run Python syntax checks."
            },
            {
                "id": "self_edit.propose",
                "name": "Propose file edit",
                "risk": "dangerous",
                "command": "/self-edit",
                "description": "Create a pending self-edit proposal."
            },
            {
                "id": "self_edit.diff",
                "name": "Show edit diff",
                "risk": "read_only",
                "command": "/self-diff",
                "description": "Show the pending self-edit diff."
            },
            {
                "id": "self_edit.apply",
                "name": "Apply edit",
                "risk": "dangerous",
                "command": "/self-apply",
                "description": "Apply pending edit after exact approval."
            }
        ]
    },
    {
        "id": "project",
        "name": "Project Skill",
        "category": "project_introspection",
        "inspired_by": ["Aider", "SWE-agent", "OpenHands"],
        "purpose": "Inspect Seed's own project files, modules, and architecture.",
        "risk": "read_only",
        "approval_rule": "Project inspection is read-only.",
        "capabilities": [
            {
                "id": "project.report",
                "name": "Project report",
                "risk": "read_only",
                "tool": "project_report",
                "description": "Show Seed architecture report."
            },
            {
                "id": "project.files",
                "name": "Project files",
                "risk": "read_only",
                "tool": "project_files",
                "description": "List Seed project files."
            },
            {
                "id": "project.modules",
                "name": "Project modules",
                "risk": "read_only",
                "tool": "project_modules",
                "description": "List Seed Python modules."
            }
        ]
    },
    {
        "id": "llm",
        "name": "LLM Skill",
        "category": "cognition",
        "inspired_by": ["Open WebUI", "AnythingLLM", "OpenClaw"],
        "purpose": "Manage local model/cognition status and task routing.",
        "risk": "read_only",
        "approval_rule": "Model changes are user-controlled.",
        "capabilities": [
            {
                "id": "llm.status",
                "name": "LLM status",
                "risk": "read_only",
                "tool": "llm_status",
                "description": "Show Ollama and task-model status."
            }
        ]
    },
    {
        "id": "dna",
        "name": "Open-Source DNA Skill",
        "category": "research",
        "inspired_by": [
            "Hermes Agent",
            "Letta",
            "Aider",
            "Cline",
            "OpenHands",
            "OpenClaw",
            "LangGraph",
            "MCP Servers"
        ],
        "purpose": "Study cloned open-source repos and convert lessons into Seed-native architecture.",
        "risk": "read_only",
        "approval_rule": "Borrowing code requires license review and explicit approval.",
        "capabilities": [
            {
                "id": "dna.status",
                "name": "DNA status",
                "risk": "read_only",
                "tool": "open_source_dna_status",
                "description": "Show open-source DNA research status."
            },
            {
                "id": "dna.borrow_map",
                "name": "Borrow map",
                "risk": "read_only",
                "tool": "open_source_borrow_map",
                "description": "Show repo-inspired Seed upgrade map."
            },
            {
                "id": "dna.borrow_candidates",
                "name": "Borrow candidates",
                "risk": "read_only",
                "tool": "open_source_borrow_candidates",
                "description": "Show candidate files worth studying."
            }
        ]
    },
    {
        "id": "agent",
        "name": "Agent Skill",
        "category": "planning",
        "inspired_by": ["LangGraph", "Hermes Agent", "OpenHands", "MCP Servers"],
        "purpose": "Plan and run safe read-only diagnostic steps.",
        "risk": "diagnostic",
        "approval_rule": "Only read-only and diagnostic capabilities may auto-run.",
        "capabilities": [
            {
                "id": "agent.snapshot",
                "name": "System snapshot",
                "risk": "read_only",
                "tool": "system_snapshot",
                "description": "Show full Seed system state."
            },
            {
                "id": "agent.self_review",
                "name": "Self-review",
                "risk": "diagnostic",
                "command": "/self-review",
                "description": "Generate a self-review improvement report."
            }
        ]
    },
    {
        "id": "coding",
        "name": "Coding Skill",
        "category": "coding_agent",
        "inspired_by": ["Aider", "Cline", "SWE-agent", "mini-SWE-agent", "OpenHands"],
        "purpose": "Support repo-aware coding, diagnostics, and safe self-improvement workflows.",
        "risk": "diagnostic",
        "approval_rule": "Code edits require self-edit proposal, diff, approval, backup, test, and rollback.",
        "capabilities": [
            {
                "id": "coding.project_report",
                "name": "Coding project report",
                "risk": "read_only",
                "tool": "project_report",
                "description": "Inspect repo architecture before coding."
            },
            {
                "id": "coding.syntax_test",
                "name": "Coding syntax test",
                "risk": "diagnostic",
                "tool": "self_test",
                "description": "Run syntax checks before/after edits."
            },
            {
                "id": "coding.propose_edit",
                "name": "Coding edit proposal",
                "risk": "dangerous",
                "command": "/self-edit",
                "description": "Create a safe edit proposal."
            }
        ]
    },
    {
        "id": "cockpit",
        "name": "Cockpit Skill",
        "category": "interface",
        "inspired_by": ["Open WebUI", "AnythingLLM", "OpenClaw", "Moltbot AI Assistant"],
        "purpose": "Represent Seed's visual control surface and future local cockpit direction.",
        "risk": "read_only",
        "approval_rule": "Cockpit display is read-only until explicit UI actions are approved.",
        "capabilities": [
            {
                "id": "cockpit.hud",
                "name": "Terminal HUD",
                "risk": "read_only",
                "command": "/hud",
                "description": "Show Seed mission-control dashboard."
            },
            {
                "id": "cockpit.boot",
                "name": "Boot brief",
                "risk": "read_only",
                "command": "/boot",
                "description": "Show Seed boot/system brief."
            }
        ]
    }
]


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def ensure_skills_dir():
    os.makedirs(SEED_SKILLS_DIR, exist_ok=True)


def skill_manifest_path(skill_id):
    return os.path.join(SEED_SKILLS_DIR, f"{skill_id}.skill.json")


def bootstrap_default_skills(overwrite=False):
    print("\n=== SKILL OS BOOTSTRAP ===")

    ensure_skills_dir()

    written = 0
    skipped = 0

    for manifest in DEFAULT_SKILL_MANIFESTS:
        path = skill_manifest_path(manifest["id"])

        if os.path.exists(path) and not overwrite:
            skipped += 1
            continue

        manifest["updated_at"] = now_timestamp()

        with open(path, "w") as file:
            json.dump(manifest, file, indent=4)

        written += 1

    print(f"Written: {written}")
    print(f"Skipped existing: {skipped}")
    print(f"Folder: {SEED_SKILLS_DIR}")


def load_skill_file(path):
    try:
        with open(path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        return {
            "id": os.path.basename(path),
            "error": "Invalid JSON"
        }


def load_all_skills():
    ensure_skills_dir()

    skill_files = [
        file_name for file_name in os.listdir(SEED_SKILLS_DIR)
        if file_name.endswith(".skill.json")
    ]

    skills = []

    for file_name in sorted(skill_files):
        path = os.path.join(SEED_SKILLS_DIR, file_name)
        skill = load_skill_file(path)

        if skill is not None:
            skills.append(skill)

    return skills


def get_skill(skill_query):
    skill_query = skill_query.strip().lower()
    skills = load_all_skills()

    for skill in skills:
        if skill_query == skill.get("id", "").lower():
            return skill

        if skill_query in skill.get("name", "").lower():
            return skill

    return None


def get_all_capabilities():
    capabilities = []

    for skill in load_all_skills():
        for capability in skill.get("capabilities", []):
            capabilities.append({
                "skill_id": skill.get("id"),
                "skill_name": skill.get("name"),
                "skill_category": skill.get("category"),
                "capability": capability
            })

    return capabilities


def get_capability(capability_query):
    capability_query = capability_query.strip().lower()

    for item in get_all_capabilities():
        capability = item["capability"]

        if capability_query == capability.get("id", "").lower():
            return item

        if capability_query in capability.get("name", "").lower():
            return item

    return None


def validate_skill(skill):
    problems = []

    required_fields = [
        "id",
        "name",
        "category",
        "purpose",
        "risk",
        "approval_rule",
        "capabilities"
    ]

    for field in required_fields:
        if field not in skill:
            problems.append(f"Missing field: {field}")

    if not isinstance(skill.get("capabilities", []), list):
        problems.append("Capabilities must be a list.")
        return problems

    capability_ids = set()

    for capability in skill.get("capabilities", []):
        capability_id = capability.get("id")

        if not capability_id:
            problems.append("Capability missing id.")
        elif capability_id in capability_ids:
            problems.append(f"Duplicate capability id: {capability_id}")
        else:
            capability_ids.add(capability_id)

        if "risk" not in capability:
            problems.append(f"Capability {capability_id} missing risk.")

        if "tool" not in capability and "command" not in capability:
            problems.append(
                f"Capability {capability_id} needs either tool or command."
            )

    return problems


def format_skills():
    skills = load_all_skills()

    text = "=== SEED SKILL OS ===\n"
    text += f"Skills loaded: {len(skills)}\n\n"

    if not skills:
        text += "No skills found. Run /skill-bootstrap first.\n"
        return text

    for skill in skills:
        text += f"{skill.get('id')} — {skill.get('name')}\n"
        text += f"  Category: {skill.get('category')}\n"
        text += f"  Risk: {skill.get('risk')}\n"
        text += f"  Capabilities: {len(skill.get('capabilities', []))}\n"
        text += f"  Purpose: {skill.get('purpose')}\n\n"

    return text


def show_skills():
    print("\n" + format_skills())


def format_skill_detail(skill_query):
    skill = get_skill(skill_query)

    if skill is None:
        return f"No skill found for: {skill_query}"

    text = f"=== SKILL: {skill.get('name')} ===\n"
    text += f"ID: {skill.get('id')}\n"
    text += f"Category: {skill.get('category')}\n"
    text += f"Risk: {skill.get('risk')}\n"
    text += f"Purpose: {skill.get('purpose')}\n"
    text += f"Approval rule: {skill.get('approval_rule')}\n"
    text += f"Inspired by: {', '.join(skill.get('inspired_by', []))}\n"

    text += "\nCapabilities:\n"

    for capability in skill.get("capabilities", []):
        text += f"- {capability.get('id')} — {capability.get('name')}\n"
        text += f"  Risk: {capability.get('risk')}\n"
        text += f"  Description: {capability.get('description')}\n"

        if "tool" in capability:
            text += f"  Tool: {capability.get('tool')}\n"

        if "command" in capability:
            text += f"  Command: {capability.get('command')}\n"

    return text


def show_skill_detail(skill_query):
    print("\n" + format_skill_detail(skill_query))


def format_skill_map():
    skills = load_all_skills()

    text = "=== SEED SKILL MAP ===\n"

    for skill in skills:
        text += f"\n## {skill.get('name')} [{skill.get('category')}]\n"
        text += f"Purpose: {skill.get('purpose')}\n"
        text += f"Approval: {skill.get('approval_rule')}\n"

        for capability in skill.get("capabilities", []):
            target = capability.get("tool") or capability.get("command")
            text += (
                f"- {capability.get('id')} "
                f"({capability.get('risk')}): {target}\n"
            )

    return text


def show_skill_map():
    print("\n" + format_skill_map())


def format_skill_audit():
    skills = load_all_skills()

    text = "=== SEED SKILL AUDIT ===\n"

    if not skills:
        text += "No skills loaded.\n"
        return text

    total_capabilities = 0
    risk_counts = {}

    for skill in skills:
        problems = validate_skill(skill)
        capabilities = skill.get("capabilities", [])
        total_capabilities += len(capabilities)

        for capability in capabilities:
            risk = capability.get("risk", "unknown")

            if risk not in risk_counts:
                risk_counts[risk] = 0

            risk_counts[risk] += 1

        text += f"\n{skill.get('id')} — {skill.get('name')}\n"

        if problems:
            text += "Problems:\n"
            for problem in problems:
                text += f"- {problem}\n"
        else:
            text += "Status: OK\n"

    text += "\nSummary:\n"
    text += f"- Skills: {len(skills)}\n"
    text += f"- Capabilities: {total_capabilities}\n"

    for risk, count in risk_counts.items():
        text += f"- {risk}: {count}\n"

    return text


def show_skill_audit():
    print("\n" + format_skill_audit())


def get_skill_context_for_prompt(user_prompt):
    if not SKILL_CONTEXT_ENABLED:
        return "Skill OS context is disabled."

    lowered = user_prompt.lower()

    skill_keywords = [
        "skill",
        "skills",
        "capability",
        "capabilities",
        "permission",
        "approval",
        "planner",
        "plan",
        "tool",
        "tools",
        "borrow",
        "architecture",
        "v1.12",
        "v2.0"
    ]

    if not any(keyword in lowered for keyword in skill_keywords):
        return "No Skill OS context needed."

    return format_skill_map()