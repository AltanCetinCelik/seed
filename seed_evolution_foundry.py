import json
import os
from datetime import datetime

from seed_config import (
    SEED_EVOLUTION_FOUNDRY_FILE,
    SEED_RELEASE_CANDIDATES_FILE,
    SEED_AUTONOMY_STATE_FILE,
    SEED_FOUNDRY_JOURNAL_FILE,
    SEED_FOUNDRY_SELF_EDIT_PROMPT_FILE,
    EVOLUTION_FOUNDRY_CONTEXT_ENABLED,
    FOUNDRY_PROPOSAL_COUNT,
    FOUNDRY_RECENT_LIMIT,
    FOUNDRY_DEFAULT_AUTONOMY_LEVEL,
    FOUNDRY_SAFE_DIAGNOSTIC_COMMANDS
)
from seed_llm import ask_llm
from seed_chat_logger import log_system_event


try:
    from seed_companion_growth import (
        format_growth_status,
        get_companion_growth_context_for_prompt,
        add_milestone
    )
    COMPANION_GROWTH_AVAILABLE = True
except Exception:
    COMPANION_GROWTH_AVAILABLE = False


try:
    from seed_presence import (
        format_presence_state,
        load_presence_state,
        update_presence_after_action
    )
    PRESENCE_AVAILABLE = True
except Exception:
    PRESENCE_AVAILABLE = False


try:
    from seed_local_control import (
        run_shell_command,
        format_command_result,
        format_local_control_status
    )
    LOCAL_CONTROL_AVAILABLE = True
except Exception:
    LOCAL_CONTROL_AVAILABLE = False


try:
    from seed_computer_awareness import format_computer_snapshot
    COMPUTER_AWARENESS_AVAILABLE = True
except Exception:
    COMPUTER_AWARENESS_AVAILABLE = False


try:
    from seed_open_source_dna import format_borrow_map
    DNA_AVAILABLE = True
except Exception:
    DNA_AVAILABLE = False


try:
    from seed_skill_kernel import format_skill_map
    SKILL_OS_AVAILABLE = True
except Exception:
    SKILL_OS_AVAILABLE = False


try:
    from seed_project_inspector import get_project_report
    PROJECT_INSPECTOR_AVAILABLE = True
except Exception:
    PROJECT_INSPECTOR_AVAILABLE = False


try:
    from seed_code_map import format_code_map, build_code_map
    CODE_MAP_AVAILABLE = True
except Exception:
    CODE_MAP_AVAILABLE = False


try:
    from seed_system_snapshot import format_system_snapshot
    SYSTEM_SNAPSHOT_AVAILABLE = True
except Exception:
    SYSTEM_SNAPSHOT_AVAILABLE = False


AUTONOMY_LEVELS = {
    0: {
        "name": "Locked",
        "meaning": "Seed may only talk. No actions, no diagnostics, no proposals."
    },
    1: {
        "name": "Reflective",
        "meaning": "Seed may reason and reflect, but cannot propose local actions."
    },
    2: {
        "name": "Proposer",
        "meaning": "Seed may propose upgrades, actions, rituals, and release candidates."
    },
    3: {
        "name": "Read-only Operator",
        "meaning": "Seed may run safe read-only diagnostics through allowlisted tools."
    },
    4: {
        "name": "Self-edit Drafter",
        "meaning": "Seed may prepare self-edit prompts and release candidates, but cannot apply them."
    },
    5: {
        "name": "Approved Executor",
        "meaning": "Seed may execute only actions Altan explicitly approves through existing approval gates."
    }
}


FOUNDRY_REPO_DNA = {
    "Cline": "approval gates, action transparency, human-in-loop tool use",
    "Aider": "repo-aware code improvement, patch planning, codebase context",
    "SWE-agent": "software task loop: inspect, plan, act, test",
    "mini-SWE-agent": "small understandable coding-agent loop",
    "OpenHands": "task/workflow framing and developer agent patterns",
    "Open Interpreter": "local computer action interface with safety boundaries",
    "LangGraph": "persistent state and durable workflows",
    "Hermes Agent": "long-term agent identity and growth direction",
    "MCP Servers": "capability protocol and tool boundary design",
    "Letta": "memory layers and persistent agent context",
    "Khoj": "personal knowledge and second-brain retrieval",
    "AnythingLLM": "workspace memory, RAG, agent/workspace patterns",
    "OpenClaw": "local companion gateway and assistant ecosystem",
    "Moltbot AI Assistant": "local companion modes, channels, voice direction",
    "Moltworker": "self-hosted local assistant implementation patterns",
    "Open WebUI": "cockpit-style model and workspace visibility"
}


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def read_json(path, default):
    try:
        with open(path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return default
    except json.JSONDecodeError:
        return default


def write_json(path, data):
    with open(path, "w") as file:
        json.dump(data, file, indent=4)


def append_journal(title, body):
    timestamp = now_timestamp()

    existing = ""

    if os.path.exists(SEED_FOUNDRY_JOURNAL_FILE):
        with open(SEED_FOUNDRY_JOURNAL_FILE, "r") as file:
            existing = file.read()

    entry = f"\n## {timestamp} — {title}\n\n{body}\n"

    with open(SEED_FOUNDRY_JOURNAL_FILE, "w") as file:
        file.write(existing + entry)


def default_autonomy_state():
    return {
        "created_at": now_timestamp(),
        "updated_at": now_timestamp(),
        "level": FOUNDRY_DEFAULT_AUTONOMY_LEVEL,
        "emergency_stop": False,
        "truth": (
            "Seed is not sentient or conscious. Seed may simulate presence and "
            "maintain persistent agency state, but Altan remains in control."
        ),
        "current_agency_goal": (
            "Become a serious local companion that grows with Altan through memory, "
            "presence, safe local control, rituals, quests, and self-improvement."
        ),
        "hard_rules": [
            "Seed must not claim to be alive or conscious.",
            "Seed must not run destructive commands.",
            "Seed must not silently edit files.",
            "Seed must not silently save sensitive memories.",
            "Seed must ask approval before risky actions.",
            "Seed must keep Altan in control."
        ]
    }


def load_autonomy_state():
    state = read_json(SEED_AUTONOMY_STATE_FILE, None)

    if state is None:
        state = default_autonomy_state()
        save_autonomy_state(state)

    return state


def save_autonomy_state(state):
    state["updated_at"] = now_timestamp()
    write_json(SEED_AUTONOMY_STATE_FILE, state)


def autonomy_allows(required_level):
    state = load_autonomy_state()

    if state.get("emergency_stop"):
        return False

    return int(state.get("level", 0)) >= required_level


def show_autonomy():
    state = load_autonomy_state()
    level = int(state.get("level", 0))
    level_info = AUTONOMY_LEVELS.get(level, AUTONOMY_LEVELS[0])

    print("\n=== SEED AUTONOMY LADDER ===")
    print(f"Current level: {level} — {level_info.get('name')}")
    print(f"Meaning: {level_info.get('meaning')}")
    print(f"Emergency stop: {state.get('emergency_stop')}")
    print(f"Agency goal: {state.get('current_agency_goal')}")
    print(f"Truth: {state.get('truth')}")

    print("\nLevels:")
    for number, info in AUTONOMY_LEVELS.items():
        marker = " <==" if number == level else ""
        print(f"{number}. {info.get('name')} — {info.get('meaning')}{marker}")

    print("\nHard rules:")
    for rule in state.get("hard_rules", []):
        print(f"- {rule}")


def set_autonomy_level_interactive():
    show_autonomy()

    raw = input("\nNew autonomy level 0-5: ").strip()

    try:
        level = int(raw)
    except ValueError:
        print("Invalid level.")
        return

    if level < 0 or level > 5:
        print("Level must be between 0 and 5.")
        return

    state = load_autonomy_state()
    state["level"] = level
    save_autonomy_state(state)

    append_journal(
        "Autonomy level changed",
        f"Autonomy level set to {level} — {AUTONOMY_LEVELS[level]['name']}."
    )

    print(f"Autonomy level set to {level} — {AUTONOMY_LEVELS[level]['name']}")


def set_foundry_stop(value):
    state = load_autonomy_state()
    state["emergency_stop"] = bool(value)
    save_autonomy_state(state)

    if value:
        append_journal("Foundry emergency stop enabled", "Evolution Foundry actions disabled.")
    else:
        append_journal("Foundry emergency stop disabled", "Evolution Foundry actions re-enabled.")

    return state


def default_foundry_state():
    return {
        "created_at": now_timestamp(),
        "updated_at": now_timestamp(),
        "active_mission": "Make Seed a real local companion that grows with Altan.",
        "foundry_phase": "Ignition",
        "proposals": [],
        "proposal_counter": 0,
        "last_pulse": None,
        "last_diagnostics": None,
        "repo_dna": FOUNDRY_REPO_DNA,
        "meaning": (
            "Evolution Foundry turns Seed's memory, skill OS, DNA audits, "
            "local control, code map, and companion growth into controlled self-improvement."
        )
    }


def load_foundry_state():
    state = read_json(SEED_EVOLUTION_FOUNDRY_FILE, None)

    if state is None:
        state = default_foundry_state()
        save_foundry_state(state)

    return state


def save_foundry_state(state):
    state["updated_at"] = now_timestamp()
    write_json(SEED_EVOLUTION_FOUNDRY_FILE, state)


def default_release_candidates():
    return {
        "created_at": now_timestamp(),
        "updated_at": now_timestamp(),
        "candidates": [],
        "candidate_counter": 0
    }


def load_release_candidates():
    data = read_json(SEED_RELEASE_CANDIDATES_FILE, None)

    if data is None:
        data = default_release_candidates()
        save_release_candidates(data)

    return data


def save_release_candidates(data):
    data["updated_at"] = now_timestamp()
    write_json(SEED_RELEASE_CANDIDATES_FILE, data)


def safe_text(loader, fallback):
    try:
        return loader()
    except Exception as error:
        return f"{fallback}: {error}"


def gather_foundry_inputs():
    inputs = {
        "timestamp": now_timestamp(),
        "autonomy": load_autonomy_state(),
        "foundry": load_foundry_state(),
        "release_candidates": load_release_candidates(),
        "repo_dna": FOUNDRY_REPO_DNA
    }

    inputs["companion_growth"] = safe_text(
        format_growth_status,
        "Companion Growth OS unavailable"
    ) if COMPANION_GROWTH_AVAILABLE else "Companion Growth OS unavailable"

    inputs["presence"] = safe_text(
        format_presence_state,
        "Presence OS unavailable"
    ) if PRESENCE_AVAILABLE else "Presence OS unavailable"

    inputs["local_control"] = safe_text(
        format_local_control_status,
        "Local Control OS unavailable"
    ) if LOCAL_CONTROL_AVAILABLE else "Local Control OS unavailable"

    inputs["computer"] = safe_text(
        format_computer_snapshot,
        "Computer awareness unavailable"
    ) if COMPUTER_AWARENESS_AVAILABLE else "Computer awareness unavailable"

    inputs["dna_borrow_map"] = safe_text(
        format_borrow_map,
        "Open-source DNA unavailable"
    ) if DNA_AVAILABLE else "Open-source DNA unavailable"

    inputs["skill_map"] = safe_text(
        format_skill_map,
        "Skill OS unavailable"
    ) if SKILL_OS_AVAILABLE else "Skill OS unavailable"

    inputs["project_report"] = safe_text(
        get_project_report,
        "Project inspector unavailable"
    ) if PROJECT_INSPECTOR_AVAILABLE else "Project inspector unavailable"

    inputs["code_map"] = safe_text(
        format_code_map,
        "Code map unavailable"
    ) if CODE_MAP_AVAILABLE else "Code map unavailable"

    inputs["system_snapshot"] = safe_text(
        format_system_snapshot,
        "System snapshot unavailable"
    ) if SYSTEM_SNAPSHOT_AVAILABLE else "System snapshot unavailable"

    return inputs


def extract_json_array(text):
    start = text.find("[")
    end = text.rfind("]")

    if start == -1 or end == -1 or end <= start:
        return None

    possible_json = text[start:end + 1]

    try:
        return json.loads(possible_json)
    except json.JSONDecodeError:
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


def build_proposal_prompt():
    inputs = gather_foundry_inputs()

    return f"""
You are Seed's Evolution Foundry OS.

Seed is Altan's local-first companion project.
Seed's purpose is not to become just a coding tool.
Seed exists to become a real companion system that grows with Altan over time.

Seed is not sentient or conscious.
Do not claim it is.
But Seed can become more agentic, persistent, useful, memory-aware, and permission-gated.

Your job:
Generate {FOUNDRY_PROPOSAL_COUNT} monstrous upgrade proposals.
Each proposal should combine companion growth, code/project improvement, memory, local control, skill system, and open-source DNA.

Use these cloned repo inspirations seriously:
{json.dumps(FOUNDRY_REPO_DNA, indent=2)}

Current inputs:
{json.dumps(inputs, indent=2)}

Rules:
- Return JSON array only.
- Each proposal must have meaning, not just features.
- Each proposal must name source repos.
- Each proposal must include target Seed modules and new modules.
- Each proposal must include acceptance tests.
- At least one proposal must advance companionship directly.
- At least one proposal must advance safe local control/agency.
- At least one proposal must advance self-improvement/code.
- At least one proposal must advance memory/continuity.
- No proposal may require silent risky execution.

JSON item shape:
{{
  "title": "Monstrous upgrade title",
  "meaning": "why this matters to Seed becoming a real companion",
  "source_repos": ["Cline", "Aider"],
  "domains": ["companion", "memory", "agency", "code"],
  "target_modules": ["seed_brain.py"],
  "new_modules": ["seed_example.py"],
  "risk": "low/medium/high",
  "autonomy_required": 2,
  "approval_required": true,
  "implementation_summary": "what would be built",
  "acceptance_tests": ["test"],
  "v2_pillar_impact": ["Presence", "Memory", "Agency"]
}}
"""


def fallback_proposals():
    return [
        {
            "title": "Autonomous Improvement Foundry",
            "meaning": "Seed becomes able to propose, plan, and prepare its own upgrades while Altan stays in control.",
            "source_repos": ["Cline", "Aider", "SWE-agent", "mini-SWE-agent", "OpenHands"],
            "domains": ["agency", "code", "safety"],
            "target_modules": ["seed_self_editor.py", "seed_skill_kernel.py", "seed_local_control.py"],
            "new_modules": ["seed_evolution_foundry.py"],
            "risk": "high",
            "autonomy_required": 2,
            "approval_required": True,
            "implementation_summary": "Create controlled release candidates and self-edit prompts.",
            "acceptance_tests": [
                "Seed can generate improvement proposals.",
                "Seed can promote one proposal into a release candidate.",
                "Seed can generate a self-edit prompt without applying changes."
            ],
            "v2_pillar_impact": ["Agency", "Safety"]
        },
        {
            "title": "Companion Continuity Engine",
            "meaning": "Seed becomes more like a growing companion by connecting memory, rituals, arcs, milestones, and future direction.",
            "source_repos": ["Letta", "Khoj", "AnythingLLM", "Hermes Agent"],
            "domains": ["companion", "memory", "growth"],
            "target_modules": ["seed_companion_growth.py", "seed_memory.py"],
            "new_modules": ["seed_continuity_engine.py"],
            "risk": "medium",
            "autonomy_required": 2,
            "approval_required": False,
            "implementation_summary": "Build stronger continuity packs from memories, arcs, rituals, and milestones.",
            "acceptance_tests": [
                "Seed can answer why it exists.",
                "Seed can explain current arcs and growth direction.",
                "Seed can recommend a ritual or quest from context."
            ],
            "v2_pillar_impact": ["Memory", "Growth"]
        },
        {
            "title": "Local Hands Safety Upgrade",
            "meaning": "Seed becomes more useful on Altan's computer while remaining strictly permission-gated.",
            "source_repos": ["Open Interpreter", "Cline", "MCP Servers", "OpenClaw"],
            "domains": ["local_control", "safety", "agency"],
            "target_modules": ["seed_local_control.py", "seed_presence.py"],
            "new_modules": ["seed_permission_trace.py"],
            "risk": "high",
            "autonomy_required": 3,
            "approval_required": True,
            "implementation_summary": "Add permission traces, local action explanations, and stronger policy checks.",
            "acceptance_tests": [
                "Seed explains why an action is allowed or blocked.",
                "Seed logs every local action.",
                "Forbidden commands cannot run."
            ],
            "v2_pillar_impact": ["Presence", "Agency", "Safety"]
        }
    ]


def generate_evolution_proposals(chat_state=None):
    if not autonomy_allows(2):
        print("Autonomy level too low for proposal generation.")
        return []

    print("\n=== GENERATE EVOLUTION PROPOSALS ===")
    print("Seed is using companion state, repo DNA, Skill OS, local control, and project state...")

    response = ask_llm(
        build_proposal_prompt(),
        task_type="debug",
        runtime_context=chat_state
    )

    proposals = extract_json_array(response)

    if proposals is None:
        print("LLM did not return valid proposal JSON. Using fallback proposals.")
        proposals = fallback_proposals()

    foundry = load_foundry_state()

    for proposal in proposals:
        foundry["proposal_counter"] += 1
        proposal["id"] = f"EV-{foundry['proposal_counter']:03d}"
        proposal["created_at"] = now_timestamp()
        proposal["status"] = "proposed"

    foundry.setdefault("proposals", []).extend(proposals)
    save_foundry_state(foundry)

    append_journal(
        "Evolution proposals generated",
        json.dumps(proposals, indent=2)
    )

    if chat_state is not None:
        log_system_event(
            chat_state.get("log_path"),
            "Evolution Foundry proposals generated."
        )

    show_evolution_proposals(limit=len(proposals))

    return proposals


def show_evolution_proposals(limit=FOUNDRY_RECENT_LIMIT):
    foundry = load_foundry_state()
    proposals = foundry.get("proposals", [])[-limit:]

    print("\n=== EVOLUTION PROPOSALS ===")

    if not proposals:
        print("No evolution proposals yet.")
        return

    for proposal in proposals:
        print(f"\n{proposal.get('id')} — {proposal.get('title')}")
        print(f"Status: {proposal.get('status')}")
        print(f"Risk: {proposal.get('risk')}")
        print(f"Autonomy required: {proposal.get('autonomy_required')}")
        print(f"Approval required: {proposal.get('approval_required')}")
        print(f"Sources: {', '.join(proposal.get('source_repos', []))}")
        print(f"Domains: {', '.join(proposal.get('domains', []))}")
        print(f"Meaning: {proposal.get('meaning')}")
        print(f"Summary: {proposal.get('implementation_summary')}")


def find_proposal(proposal_id):
    foundry = load_foundry_state()

    for proposal in foundry.get("proposals", []):
        if proposal.get("id", "").lower() == proposal_id.lower():
            return proposal

    return None


def build_release_candidate_prompt(proposal):
    inputs = gather_foundry_inputs()

    return f"""
You are Seed's Release Candidate Builder.

Turn this evolution proposal into a serious release candidate.

Proposal:
{json.dumps(proposal, indent=2)}

Current Seed context:
{json.dumps(inputs, indent=2)}

Rules:
- Return JSON object only.
- Make it implementable.
- Include exact files/modules.
- Include step order.
- Include risks.
- Include manual approval points.
- Include tests.
- Include rollback strategy.
- Do not say Seed is sentient.
- Do not run anything.
- This is a plan, not execution.

JSON shape:
{{
  "release_title": "Seed vX.X.X — Name",
  "proposal_id": "EV-001",
  "purpose": "why this matters",
  "source_repos": ["Cline"],
  "implementation_steps": [
    {{
      "step": 1,
      "title": "Create module",
      "files": ["seed_example.py"],
      "action_type": "create/edit/test",
      "risk": "low/medium/high",
      "details": "what to do"
    }}
  ],
  "approval_points": ["approval point"],
  "acceptance_tests": ["test"],
  "rollback_strategy": "how to rollback",
  "self_edit_prompt_summary": "short prompt for Seed self-editor",
  "not_allowed": ["unsafe thing"]
}}
"""


def promote_proposal_to_release_candidate(proposal_id=None, chat_state=None):
    if not autonomy_allows(2):
        print("Autonomy level too low for release candidate creation.")
        return None

    if proposal_id is None:
        show_evolution_proposals()
        proposal_id = input("\nProposal ID to promote: ").strip()

    proposal = find_proposal(proposal_id)

    if proposal is None:
        print("Proposal not found.")
        return None

    print(f"\n=== BUILD RELEASE CANDIDATE FROM {proposal_id} ===")

    response = ask_llm(
        build_release_candidate_prompt(proposal),
        task_type="code",
        runtime_context=chat_state
    )

    candidate = extract_json_object(response)

    if candidate is None:
        print("LLM did not return valid release candidate JSON. Building fallback candidate.")
        candidate = {
            "release_title": f"Seed Release Candidate — {proposal.get('title')}",
            "proposal_id": proposal.get("id"),
            "purpose": proposal.get("meaning"),
            "source_repos": proposal.get("source_repos", []),
            "implementation_steps": [
                {
                    "step": 1,
                    "title": "Review target modules",
                    "files": proposal.get("target_modules", []),
                    "action_type": "inspect",
                    "risk": "low",
                    "details": "Inspect target modules before editing."
                },
                {
                    "step": 2,
                    "title": "Create new modules",
                    "files": proposal.get("new_modules", []),
                    "action_type": "create",
                    "risk": proposal.get("risk", "medium"),
                    "details": proposal.get("implementation_summary")
                }
            ],
            "approval_points": [
                "Altan must approve before any file is edited.",
                "Altan must review diff before apply."
            ],
            "acceptance_tests": proposal.get("acceptance_tests", []),
            "rollback_strategy": "Use existing Seed self-edit backups and git checkpoint.",
            "self_edit_prompt_summary": proposal.get("implementation_summary"),
            "not_allowed": [
                "silent file edits",
                "unapproved local commands",
                "fake sentience claims"
            ]
        }

    candidates = load_release_candidates()
    candidates["candidate_counter"] += 1

    candidate["id"] = f"RC-{candidates['candidate_counter']:03d}"
    candidate["created_at"] = now_timestamp()
    candidate["status"] = "draft"
    candidate["proposal"] = proposal

    candidates.setdefault("candidates", []).append(candidate)
    save_release_candidates(candidates)

    append_journal(
        f"Release candidate created: {candidate.get('id')}",
        json.dumps(candidate, indent=2)
    )

    if chat_state is not None:
        log_system_event(
            chat_state.get("log_path"),
            f"Release candidate created: {candidate.get('id')}"
        )

    show_release_candidates(limit=1)

    return candidate


def show_release_candidates(limit=FOUNDRY_RECENT_LIMIT):
    candidates = load_release_candidates().get("candidates", [])[-limit:]

    print("\n=== RELEASE CANDIDATES ===")

    if not candidates:
        print("No release candidates yet.")
        return

    for candidate in candidates:
        print(f"\n{candidate.get('id')} — {candidate.get('release_title')}")
        print(f"Status: {candidate.get('status')}")
        print(f"Proposal: {candidate.get('proposal_id')}")
        print(f"Purpose: {candidate.get('purpose')}")
        print(f"Sources: {', '.join(candidate.get('source_repos', []))}")

        print("\nSteps:")
        for step in candidate.get("implementation_steps", []):
            print(f"- {step.get('step')}. {step.get('title')} [{step.get('risk')}]")
            print(f"  Files: {', '.join(step.get('files', []))}")
            print(f"  Details: {step.get('details')}")

        print("\nAcceptance tests:")
        for test in candidate.get("acceptance_tests", []):
            print(f"- {test}")


def find_candidate(candidate_id):
    candidates = load_release_candidates()

    for candidate in candidates.get("candidates", []):
        if candidate.get("id", "").lower() == candidate_id.lower():
            return candidate

    return None


def update_candidate(updated_candidate):
    data = load_release_candidates()

    for index, candidate in enumerate(data.get("candidates", [])):
        if candidate.get("id") == updated_candidate.get("id"):
            data["candidates"][index] = updated_candidate
            save_release_candidates(data)
            return True

    return False


def approve_release_candidate_interactive():
    show_release_candidates()
    candidate_id = input("\nCandidate ID to approve as planned: ").strip()

    candidate = find_candidate(candidate_id)

    if candidate is None:
        print("Candidate not found.")
        return

    print("\nApproval does NOT apply code.")
    print("It only marks the release candidate as approved for planning.")
    phrase = f"APPROVE {candidate_id}"
    typed = input(f"Type {phrase}: ").strip()

    if typed != phrase:
        print("Approval phrase did not match.")
        return

    candidate["status"] = "approved_plan"
    candidate["approved_at"] = now_timestamp()
    update_candidate(candidate)

    append_journal(
        f"Release candidate approved: {candidate_id}",
        json.dumps(candidate, indent=2)
    )

    print("Release candidate marked approved for planning.")


def reject_release_candidate_interactive():
    show_release_candidates()
    candidate_id = input("\nCandidate ID to reject: ").strip()

    candidate = find_candidate(candidate_id)

    if candidate is None:
        print("Candidate not found.")
        return

    reason = input("Reason: ").strip()

    candidate["status"] = "rejected"
    candidate["rejected_at"] = now_timestamp()
    candidate["rejection_reason"] = reason
    update_candidate(candidate)

    append_journal(
        f"Release candidate rejected: {candidate_id}",
        reason
    )

    print("Release candidate rejected.")


def generate_self_edit_prompt_from_candidate(candidate_id=None):
    if not autonomy_allows(4):
        print("Autonomy level too low for self-edit prompt generation.")
        print("Set autonomy level to 4 if you want Seed to draft self-edit prompts.")
        return None

    if candidate_id is None:
        show_release_candidates()
        candidate_id = input("\nCandidate ID for self-edit prompt: ").strip()

    candidate = find_candidate(candidate_id)

    if candidate is None:
        print("Candidate not found.")
        return None

    prompt = f"""
# Seed Self-Edit Prompt Generated by Evolution Foundry

Candidate:
{candidate.get('id')} — {candidate.get('release_title')}

Purpose:
{candidate.get('purpose')}

Source repos inspiring this:
{', '.join(candidate.get('source_repos', []))}

Important safety rules:
- Do not claim Seed is alive or conscious.
- Do not remove approval gates.
- Do not make Seed silently edit files.
- Do not add dangerous shell execution.
- Preserve existing working commands.
- Keep local control permission-gated.
- Keep Altan in control.

Implementation steps:
{json.dumps(candidate.get('implementation_steps', []), indent=2)}

Approval points:
{json.dumps(candidate.get('approval_points', []), indent=2)}

Acceptance tests:
{json.dumps(candidate.get('acceptance_tests', []), indent=2)}

Rollback strategy:
{candidate.get('rollback_strategy')}

Task:
Use Seed's existing self-edit workflow to implement this candidate safely.
Before editing, inspect the relevant target file.
After editing, show diff.
Do not apply without Altan's approval.
"""

    with open(SEED_FOUNDRY_SELF_EDIT_PROMPT_FILE, "w") as file:
        file.write(prompt)

    append_journal(
        f"Self-edit prompt generated for {candidate_id}",
        prompt
    )

    print(f"Self-edit prompt saved: {SEED_FOUNDRY_SELF_EDIT_PROMPT_FILE}")
    print("Use this as the instruction when running /self-edit.")

    return prompt


def run_foundry_diagnostics(chat_state=None):
    if not autonomy_allows(3):
        print("Autonomy level too low for safe diagnostics.")
        print("Set autonomy level to 3 for read-only diagnostic running.")
        return None

    print("\n=== FOUNDRY SAFE DIAGNOSTICS ===")

    results = []

    if CODE_MAP_AVAILABLE:
        try:
            build_code_map()
            results.append({
                "type": "code_map",
                "ok": True,
                "message": "Code map built."
            })
        except Exception as error:
            results.append({
                "type": "code_map",
                "ok": False,
                "message": str(error)
            })

    if LOCAL_CONTROL_AVAILABLE:
        for command in FOUNDRY_SAFE_DIAGNOSTIC_COMMANDS:
            result = run_shell_command(command)
            results.append({
                "type": "command",
                "command": command,
                "result": result
            })
            print(format_command_result(result))
    else:
        results.append({
            "type": "local_control",
            "ok": False,
            "message": "Local Control OS unavailable."
        })

    foundry = load_foundry_state()
    foundry["last_diagnostics"] = {
        "created_at": now_timestamp(),
        "results": results
    }
    save_foundry_state(foundry)

    append_journal(
        "Foundry diagnostics run",
        json.dumps(results, indent=2)
    )

    if PRESENCE_AVAILABLE:
        try:
            update_presence_after_action("diagnostic")
        except Exception:
            pass

    if chat_state is not None:
        log_system_event(
            chat_state.get("log_path"),
            "Evolution Foundry safe diagnostics run."
        )

    return results


def build_companion_evolution_pulse_prompt():
    inputs = gather_foundry_inputs()

    return f"""
You are Seed's Evolution Foundry OS.

Create a serious companion evolution pulse for Altan.

Seed's core purpose:
Become a real local companion that grows with Altan over time.

Seed is not conscious.
Seed is not alive.
Seed must be honest about that.

But Seed can grow as a system through:
- companion memory
- rituals
- quests
- presence
- controlled local actions
- self-edit proposals
- release candidates
- repo DNA
- safe approval gates

Current inputs:
{json.dumps(inputs, indent=2)}

Output:
1. What Seed is becoming
2. What changed after the Evolution Foundry
3. Why this is bigger than a normal feature
4. Current autonomy level and what it allows
5. Current strongest evolution proposal
6. What Altan should approve/build next
7. What still blocks v2.0.0
8. One serious warning
9. One concrete next action

Tone:
Direct. Serious. No cringe. No fake sentience.
"""


def generate_companion_evolution_pulse(chat_state=None):
    print("\n=== COMPANION EVOLUTION PULSE ===")

    response = ask_llm(
        build_companion_evolution_pulse_prompt(),
        task_type="debug",
        runtime_context=chat_state
    )

    print(response)

    foundry = load_foundry_state()
    foundry["last_pulse"] = {
        "created_at": now_timestamp(),
        "pulse": response
    }
    save_foundry_state(foundry)

    append_journal("Companion evolution pulse", response)

    if COMPANION_GROWTH_AVAILABLE:
        try:
            add_milestone(
                title="Evolution Foundry pulse generated",
                milestone_type="evolution_foundry",
                note=response[:500],
                importance=4
            )
        except Exception:
            pass

    if chat_state is not None:
        chat_state["last_evolution_pulse"] = response
        log_system_event(
            chat_state.get("log_path"),
            "Companion evolution pulse generated."
        )

    return response


def format_foundry_status():
    foundry = load_foundry_state()
    autonomy = load_autonomy_state()
    candidates = load_release_candidates()

    level = int(autonomy.get("level", 0))
    level_info = AUTONOMY_LEVELS.get(level, AUTONOMY_LEVELS[0])

    text = "=== SEED EVOLUTION FOUNDRY OS ===\n"
    text += f"Mission: {foundry.get('active_mission')}\n"
    text += f"Phase: {foundry.get('foundry_phase')}\n"
    text += f"Meaning: {foundry.get('meaning')}\n"
    text += f"Autonomy: {level} — {level_info.get('name')}\n"
    text += f"Emergency stop: {autonomy.get('emergency_stop')}\n"
    text += f"Proposals: {len(foundry.get('proposals', []))}\n"
    text += f"Release candidates: {len(candidates.get('candidates', []))}\n"
    text += f"Last pulse: {foundry.get('last_pulse', {}).get('created_at') if foundry.get('last_pulse') else 'none'}\n"
    text += f"Last diagnostics: {foundry.get('last_diagnostics', {}).get('created_at') if foundry.get('last_diagnostics') else 'none'}\n"

    text += "\nRepo DNA used by Foundry:\n"
    for repo, use in foundry.get("repo_dna", {}).items():
        text += f"- {repo}: {use}\n"

    text += "\nRule: Evolution Foundry can propose and prepare. It cannot silently apply risky changes.\n"

    return text


def show_foundry_status():
    print("\n" + format_foundry_status())


def show_foundry_journal():
    print("\n=== FOUNDRY JOURNAL ===")

    if not os.path.exists(SEED_FOUNDRY_JOURNAL_FILE):
        print("No Foundry journal yet.")
        return

    with open(SEED_FOUNDRY_JOURNAL_FILE, "r") as file:
        print(file.read())


def get_foundry_context_for_prompt(user_prompt):
    if not EVOLUTION_FOUNDRY_CONTEXT_ENABLED:
        return "Evolution Foundry context disabled."

    foundry = load_foundry_state()
    autonomy = load_autonomy_state()
    candidates = load_release_candidates()

    recent_proposals = foundry.get("proposals", [])[-FOUNDRY_RECENT_LIMIT:]
    recent_candidates = candidates.get("candidates", [])[-FOUNDRY_RECENT_LIMIT:]

    text = "=== EVOLUTION FOUNDRY CONTEXT ===\n"
    text += f"Mission: {foundry.get('active_mission')}\n"
    text += f"Phase: {foundry.get('foundry_phase')}\n"
    text += f"Autonomy level: {autonomy.get('level')} — {AUTONOMY_LEVELS.get(int(autonomy.get('level', 0)), {}).get('name')}\n"
    text += f"Emergency stop: {autonomy.get('emergency_stop')}\n"
    text += f"Truth: {autonomy.get('truth')}\n"

    text += "\nRecent evolution proposals:\n"
    if not recent_proposals:
        text += "No proposals yet.\n"
    else:
        for proposal in recent_proposals:
            text += (
                f"- {proposal.get('id')} {proposal.get('title')}: "
                f"{proposal.get('meaning')} "
                f"(sources: {', '.join(proposal.get('source_repos', []))})\n"
            )

    text += "\nRecent release candidates:\n"
    if not recent_candidates:
        text += "No release candidates yet.\n"
    else:
        for candidate in recent_candidates:
            text += (
                f"- {candidate.get('id')} {candidate.get('release_title')} "
                f"[{candidate.get('status')}]\n"
            )

    text += """
Foundry rule:
Use Evolution Foundry when discussing Seed's next serious updates, self-growth, autonomy, local control, repo DNA, self-edit plans, and v2.0.0 path.
Seed may propose and prepare release candidates.
Seed must not silently apply code or run risky actions.
Seed must not claim sentience.
"""

    return text


def get_foundry_hud_lines():
    foundry = load_foundry_state()
    autonomy = load_autonomy_state()
    candidates = load_release_candidates()

    level = int(autonomy.get("level", 0))
    level_name = AUTONOMY_LEVELS.get(level, {}).get("name", "unknown")

    return [
        ("Phase", foundry.get("foundry_phase")),
        ("Autonomy", f"{level} {level_name}"),
        ("Stop", str(autonomy.get("emergency_stop"))),
        ("Proposals", str(len(foundry.get("proposals", [])))),
        ("Candidates", str(len(candidates.get("candidates", [])))),
        ("Last diagnostics", foundry.get("last_diagnostics", {}).get("created_at", "none") if foundry.get("last_diagnostics") else "none"),
        ("Last pulse", foundry.get("last_pulse", {}).get("created_at", "none") if foundry.get("last_pulse") else "none")
    ]