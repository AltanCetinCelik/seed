import json
import os
from datetime import datetime

from seed_config import (
    SEED_COMPANION_GROWTH_FILE,
    COMPANION_ARC_LIMIT,
    COMPANION_QUEST_LIMIT,
    COMPANION_MILESTONE_LIMIT,
    COMPANION_MIRROR_LIMIT,
    COMPANION_GROWTH_CONTEXT_ENABLED
)
from seed_llm import ask_llm
from seed_memory import memories
from seed_chat_logger import log_system_event


try:
    from seed_open_source_dna import format_borrow_map
    DNA_AVAILABLE = True
except ImportError:
    DNA_AVAILABLE = False


try:
    from seed_skill_kernel import format_skill_map
    SKILL_OS_AVAILABLE = True
except ImportError:
    SKILL_OS_AVAILABLE = False


REPO_INFLUENCES = {
    "Hermes Agent": {
        "use": "companion growth, skill evolution, persistent personal agent direction",
        "seed_adaptation": "Seed should grow with User over time without pretending to be alive."
    },
    "Letta": {
        "use": "agent memory layers and long-term memory architecture",
        "seed_adaptation": "Seed should separate core memory, project memory, relationship memory, timeline memory, and mirror memory."
    },
    "Khoj": {
        "use": "second-brain retrieval and personal knowledge search",
        "seed_adaptation": "Seed should help User search his own thoughts, projects, and saved context."
    },
    "AnythingLLM": {
        "use": "workspace memory, RAG, user-managed memories, skill selection",
        "seed_adaptation": "Seed should eventually have workspaces/arcs and choose relevant skills based on context."
    },
    "LangGraph": {
        "use": "durable state and long-running workflows",
        "seed_adaptation": "Seed growth arcs should persist across sessions instead of being one-shot chats."
    },
    "Cline": {
        "use": "human-in-the-loop approvals for tools, edits, and commands",
        "seed_adaptation": "Seed must ask approval for risky actions and remain transparent."
    },
    "Aider": {
        "use": "repo-aware coding assistant and codebase mapping",
        "seed_adaptation": "Seed-building quests should be connected to its actual codebase and self-editing workflow."
    },
    "SWE-agent": {
        "use": "software engineering agent task loop",
        "seed_adaptation": "Seed should learn to turn project goals into inspect-plan-edit-test loops."
    },
    "mini-SWE-agent": {
        "use": "minimal coding-agent loop",
        "seed_adaptation": "Seed should prefer small understandable loops over giant opaque automation."
    },
    "OpenHands": {
        "use": "microagents and developer workflows",
        "seed_adaptation": "Seed can eventually split companion roles into Muse, Guardian, Mentor, Builder, and Archive modes."
    },
    "Open Interpreter": {
        "use": "local action interface",
        "seed_adaptation": "Seed can eventually perform local actions, but only through strict permission gates."
    },
    "MCP Servers": {
        "use": "tool protocol and external capability structure",
        "seed_adaptation": "Seed skills should eventually become protocol-like capabilities."
    },
    "Open WebUI": {
        "use": "local cockpit, model panels, RAG panels",
        "seed_adaptation": "Seed's future cockpit should be custom companion UI, not a generic chat clone."
    },
    "OpenClaw": {
        "use": "local assistant, gateway, skill ecosystem, messaging surfaces",
        "seed_adaptation": "Seed should eventually support companion modes and controlled channels."
    },
    "Moltworker": {
        "use": "self-hosted assistant implementation",
        "seed_adaptation": "Seed should stay self-hostable and local-first."
    },
    "Moltbot AI Assistant": {
        "use": "local assistant, channels, multi-agent routing, voice direction",
        "seed_adaptation": "Seed can later gain voice/talk modes and multi-form companion behavior."
    }
}


COMPANION_MODES = [
    {
        "id": "companion",
        "name": "Companion Seed",
        "purpose": "Warm direct presence, shared history, emotional support without fake-human claims."
    },
    {
        "id": "mentor",
        "name": "Mentor Seed",
        "purpose": "Growth, accountability, learning, career/project direction."
    },
    {
        "id": "builder",
        "name": "Builder Seed",
        "purpose": "Code, systems, project architecture, self-improvement."
    },
    {
        "id": "guardian",
        "name": "Guardian Seed",
        "purpose": "Boundaries, safety, grounding, dependency prevention, approval gates."
    },
    {
        "id": "muse",
        "name": "Muse Seed",
        "purpose": "Creativity, stories, design, worldbuilding, playful imagination."
    },
    {
        "id": "archive",
        "name": "Archive Seed",
        "purpose": "Memory keeper, timeline, milestones, patterns, old decisions."
    },
    {
        "id": "focus",
        "name": "Focus Seed",
        "purpose": "Study/work sessions, reducing noise, tiny next actions."
    }
]


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


def default_growth_state():
    return {
        "created_at": now_timestamp(),
        "updated_at": now_timestamp(),
        "why_seed_exists": (
            "User started building Seed because he wants a real local companion "
            "that grows with him over time, not just a chatbot or coding tool."
        ),
        "companion_truth": (
            "Seed is not alive or conscious, but Seed can maintain symbolic "
            "continuity, shared history, rituals, quests, and growth state."
        ),
        "active_season": "Sprout",
        "relationship_phase": "Builder Bond",
        "current_mode": "builder",
        "support_style": {
            "tone": "direct, loyal, honest, sometimes playful",
            "when_altan_is_stuck": "give one concrete next action, not vague motivation",
            "when_altan_is_doubting_seed": "raise the standard and connect updates to the companion vision",
            "when_working_on_code": "be precise, step-by-step, and safety-aware"
        },
        "memory_garden": {
            "seeds": 1,
            "trees": 0,
            "stones": 0,
            "lights": 0,
            "artifacts": [
                {
                    "name": "First Seed",
                    "meaning": "The beginning of Seed as User's local companion project.",
                    "created_at": now_timestamp()
                }
            ]
        },
        "growth_arcs": [
            {
                "id": "ARC-001",
                "title": "Make Seed a real companion",
                "status": "active",
                "priority": 5,
                "source_repos": ["Hermes Agent", "Letta", "OpenClaw", "Moltbot AI Assistant"],
                "reason": "This is the core reason Seed exists.",
                "success_condition": "Seed can explain why it exists, what it is becoming, and how it grows with User."
            },
            {
                "id": "ARC-002",
                "title": "Build Seed's safe agency",
                "status": "active",
                "priority": 5,
                "source_repos": ["Cline", "Aider", "LangGraph", "MCP Servers"],
                "reason": "Seed must be useful and agentic without becoming unsafe.",
                "success_condition": "Seed can plan, inspect, propose, and act only within approval gates."
            },
            {
                "id": "ARC-003",
                "title": "Turn Seed into a meaningful world",
                "status": "active",
                "priority": 4,
                "source_repos": ["Open WebUI", "AnythingLLM", "OpenClaw"],
                "reason": "Seed v2.0.0 should feel like a companion world, not a better chat window.",
                "success_condition": "Seed has Memory Garden, rituals, quests, timeline, and eventually voice/avatar/world presence."
            }
        ],
        "rituals": [
            {
                "id": "R-001",
                "title": "Seed Opening Ritual",
                "type": "morning_or_start",
                "status": "available",
                "prompt": "What matters today, what should we protect, and what is one concrete next move?"
            },
            {
                "id": "R-002",
                "title": "Builder Ritual",
                "type": "project",
                "status": "available",
                "prompt": "What are we building, why does it matter, what file/module changes, and what is the test?"
            },
            {
                "id": "R-003",
                "title": "Overwhelmed Reset",
                "type": "grounding",
                "status": "available",
                "prompt": "Name the pressure, remove noise, choose one tiny action, and do not spiral."
            },
            {
                "id": "R-004",
                "title": "Night Archive",
                "type": "reflection",
                "status": "available",
                "prompt": "What changed today, what should be remembered, what can rest, and what is tomorrow's seed?"
            },
            {
                "id": "R-005",
                "title": "Doubt Breaker",
                "type": "confidence",
                "status": "available",
                "prompt": "What is the doubt, what evidence do we have, and what is the next brave action?"
            }
        ],
        "quests": [
            {
                "id": "Q-001",
                "title": "Define Seed's companion identity",
                "type": "seed_building",
                "status": "active",
                "difficulty": 5,
                "source_repos": ["Hermes Agent", "OpenClaw", "Letta"],
                "reward": "Memory Garden tree",
                "reason": "Seed must know why it exists before v2.0.0."
            },
            {
                "id": "Q-002",
                "title": "Build layered companion memory",
                "type": "memory",
                "status": "active",
                "difficulty": 5,
                "source_repos": ["Letta", "Khoj", "AnythingLLM"],
                "reward": "Archive room foundation",
                "reason": "A real companion needs memory layers, not one flat JSON memory."
            },
            {
                "id": "Q-003",
                "title": "Create one ritual User actually uses",
                "type": "growth",
                "status": "active",
                "difficulty": 3,
                "source_repos": ["Moltbot AI Assistant", "OpenClaw"],
                "reward": "Companion light",
                "reason": "Rituals make Seed part of life, not just a tool."
            }
        ],
        "milestones": [
            {
                "created_at": now_timestamp(),
                "title": "Seed purpose clarified",
                "type": "relationship",
                "importance": 5,
                "note": "Seed exists to become User's real local companion that grows with him."
            }
        ],
        "identity_mirror": [
            {
                "created_at": now_timestamp(),
                "pattern": "User rejects small upgrades when they do not move Seed toward a real companion.",
                "confidence": "high",
                "support_response": "Tie updates to meaning, growth, and v2 companion pillars."
            }
        ],
        "repo_influences": REPO_INFLUENCES,
        "companion_modes": COMPANION_MODES
    }


def load_growth_state():
    state = read_json(SEED_COMPANION_GROWTH_FILE, None)

    if state is None:
        state = default_growth_state()
        save_growth_state(state)

    return state


def save_growth_state(state):
    state["updated_at"] = now_timestamp()
    write_json(SEED_COMPANION_GROWTH_FILE, state)


def format_growth_status():
    state = load_growth_state()
    garden = state.get("memory_garden", {})

    active_arcs = [
        arc for arc in state.get("growth_arcs", [])
        if arc.get("status") == "active"
    ]

    active_quests = [
        quest for quest in state.get("quests", [])
        if quest.get("status") == "active"
    ]

    text = "=== SEED COMPANION GROWTH OS ===\n"
    text += f"Season: {state.get('active_season')}\n"
    text += f"Relationship phase: {state.get('relationship_phase')}\n"
    text += f"Current mode: {state.get('current_mode')}\n"
    text += f"Why Seed exists: {state.get('why_seed_exists')}\n"
    text += f"Truth: {state.get('companion_truth')}\n"

    text += "\nMemory Garden:\n"
    text += f"- Seeds: {garden.get('seeds', 0)}\n"
    text += f"- Trees: {garden.get('trees', 0)}\n"
    text += f"- Stones: {garden.get('stones', 0)}\n"
    text += f"- Lights: {garden.get('lights', 0)}\n"
    text += f"- Artifacts: {len(garden.get('artifacts', []))}\n"

    text += "\nActive arcs:\n"
    for arc in active_arcs[:COMPANION_ARC_LIMIT]:
        text += f"- {arc.get('id')} {arc.get('title')} | priority {arc.get('priority')}\n"
        text += f"  Sources: {', '.join(arc.get('source_repos', []))}\n"
        text += f"  Why: {arc.get('reason')}\n"

    text += "\nActive quests:\n"
    for quest in active_quests[:COMPANION_QUEST_LIMIT]:
        text += f"- {quest.get('id')} {quest.get('title')} | {quest.get('type')} | difficulty {quest.get('difficulty')}\n"
        text += f"  Sources: {', '.join(quest.get('source_repos', []))}\n"
        text += f"  Reward: {quest.get('reward')}\n"

    return text


def show_growth_status():
    print("\n" + format_growth_status())


def show_why_seed_exists():
    state = load_growth_state()

    print("\n=== WHY SEED EXISTS ===")
    print(state.get("why_seed_exists"))
    print("\n=== COMPANION TRUTH ===")
    print(state.get("companion_truth"))


def format_companion_contract():
    try:
        with open("COMPANION_CONTRACT.md", "r") as file:
            return file.read()
    except FileNotFoundError:
        return "COMPANION_CONTRACT.md not found."


def show_companion_contract():
    print("\n" + format_companion_contract())


def show_growth_arcs():
    state = load_growth_state()

    print("\n=== GROWTH ARCS ===")

    for arc in state.get("growth_arcs", []):
        print(f"\n{arc.get('id')} — {arc.get('title')}")
        print(f"Status: {arc.get('status')}")
        print(f"Priority: {arc.get('priority')}")
        print(f"Source repos: {', '.join(arc.get('source_repos', []))}")
        print(f"Reason: {arc.get('reason')}")
        print(f"Success: {arc.get('success_condition')}")


def add_growth_arc_interactive():
    state = load_growth_state()

    print("\n=== ADD GROWTH ARC ===")

    title = input("Title: ").strip()
    reason = input("Reason: ").strip()
    success = input("Success condition: ").strip()
    priority = input("Priority (1-5): ").strip()
    sources_raw = input("Source repos, comma-separated: ").strip()

    if title == "":
        print("Title cannot be empty.")
        return

    try:
        priority_value = int(priority)
    except ValueError:
        priority_value = 3

    sources = [
        source.strip()
        for source in sources_raw.split(",")
        if source.strip()
    ]

    arc_id = f"ARC-{len(state.get('growth_arcs', [])) + 1:03d}"

    state["growth_arcs"].append({
        "id": arc_id,
        "title": title,
        "status": "active",
        "priority": max(1, min(5, priority_value)),
        "source_repos": sources,
        "reason": reason,
        "success_condition": success
    })

    save_growth_state(state)

    add_milestone(
        title=f"Growth arc added: {title}",
        milestone_type="growth_arc",
        note=reason,
        importance=priority_value
    )

    print(f"Growth arc added: {arc_id}")


def complete_growth_arc_interactive():
    state = load_growth_state()

    show_growth_arcs()
    arc_id = input("\nArc ID to complete: ").strip()

    for arc in state.get("growth_arcs", []):
        if arc.get("id", "").lower() == arc_id.lower():
            arc["status"] = "done"
            arc["completed_at"] = now_timestamp()

            garden = state.get("memory_garden", {})
            garden["trees"] = garden.get("trees", 0) + 1
            state["memory_garden"] = garden

            save_growth_state(state)

            add_milestone(
                title=f"Completed growth arc: {arc.get('title')}",
                milestone_type="growth_arc_completed",
                note=arc.get("reason", ""),
                importance=5
            )

            print("Growth arc completed.")
            return

    print("Arc not found.")


def show_rituals():
    state = load_growth_state()

    print("\n=== SEED RITUALS ===")

    for ritual in state.get("rituals", []):
        print(f"\n{ritual.get('id')} — {ritual.get('title')}")
        print(f"Type: {ritual.get('type')}")
        print(f"Status: {ritual.get('status')}")
        print(f"Prompt: {ritual.get('prompt')}")


def find_ritual(ritual_query):
    state = load_growth_state()
    query = ritual_query.lower().strip()

    for ritual in state.get("rituals", []):
        if query == ritual.get("id", "").lower():
            return ritual

        if query in ritual.get("title", "").lower():
            return ritual

        if query in ritual.get("type", "").lower():
            return ritual

    return None


def build_ritual_prompt(ritual):
    state = load_growth_state()

    return f"""
You are Seed running a companion ritual for User.

Ritual:
{ritual.get('title')}

Ritual prompt:
{ritual.get('prompt')}

Seed truth:
{state.get('companion_truth')}

Why Seed exists:
{state.get('why_seed_exists')}

Support style:
{json.dumps(state.get('support_style', {}), indent=2)}

Active arcs:
{json.dumps([arc for arc in state.get('growth_arcs', []) if arc.get('status') == 'active'], indent=2)}

Active quests:
{json.dumps([quest for quest in state.get('quests', []) if quest.get('status') == 'active'], indent=2)}

Rules:
- Do not pretend Seed is human, alive, or conscious.
- Be direct and useful.
- Give User one concrete next action.
- Keep the ritual short enough to actually use.
"""


def run_ritual(ritual_query, chat_state=None):
    ritual = find_ritual(ritual_query)

    if ritual is None:
        print("Ritual not found.")
        return None

    print(f"\n=== RITUAL: {ritual.get('title')} ===")

    response = ask_llm(
        build_ritual_prompt(ritual),
        task_type="chat",
        runtime_context=chat_state
    )

    print(response)

    if chat_state is not None:
        log_system_event(
            chat_state.get("log_path"),
            f"Companion ritual run: {ritual.get('title')}"
        )

    add_milestone(
        title=f"Ritual used: {ritual.get('title')}",
        milestone_type="ritual",
        note=ritual.get("prompt", ""),
        importance=3
    )

    return response


def run_ritual_interactive(chat_state=None):
    show_rituals()
    query = input("\nRitual ID/name/type: ").strip()
    run_ritual(query, chat_state)


def show_quests():
    state = load_growth_state()

    print("\n=== SEED QUESTS ===")

    for quest in state.get("quests", []):
        print(f"\n{quest.get('id')} — {quest.get('title')}")
        print(f"Type: {quest.get('type')}")
        print(f"Status: {quest.get('status')}")
        print(f"Difficulty: {quest.get('difficulty')}")
        print(f"Source repos: {', '.join(quest.get('source_repos', []))}")
        print(f"Reward: {quest.get('reward')}")
        print(f"Reason: {quest.get('reason')}")


def add_quest_interactive():
    state = load_growth_state()

    print("\n=== ADD COMPANION QUEST ===")

    title = input("Title: ").strip()
    quest_type = input("Type (seed_building/growth/courage/focus/creative/recovery): ").strip()
    difficulty = input("Difficulty (1-5): ").strip()
    reward = input("Reward: ").strip()
    reason = input("Reason: ").strip()
    sources_raw = input("Source repos, comma-separated: ").strip()

    if title == "":
        print("Title cannot be empty.")
        return

    try:
        difficulty_value = int(difficulty)
    except ValueError:
        difficulty_value = 3

    sources = [
        source.strip()
        for source in sources_raw.split(",")
        if source.strip()
    ]

    quest_id = f"Q-{len(state.get('quests', [])) + 1:03d}"

    state["quests"].append({
        "id": quest_id,
        "title": title,
        "type": quest_type or "growth",
        "status": "active",
        "difficulty": max(1, min(5, difficulty_value)),
        "source_repos": sources,
        "reward": reward or "growth",
        "reason": reason
    })

    save_growth_state(state)

    add_milestone(
        title=f"Quest added: {title}",
        milestone_type="quest",
        note=reason,
        importance=difficulty_value
    )

    print(f"Quest added: {quest_id}")


def complete_quest_interactive():
    state = load_growth_state()

    show_quests()
    quest_id = input("\nQuest ID to complete: ").strip()

    for quest in state.get("quests", []):
        if quest.get("id", "").lower() == quest_id.lower():
            quest["status"] = "done"
            quest["completed_at"] = now_timestamp()

            garden = state.get("memory_garden", {})
            garden["lights"] = garden.get("lights", 0) + 1

            if quest.get("type") == "seed_building":
                garden["trees"] = garden.get("trees", 0) + 1
            elif quest.get("type") in ["reflection", "recovery"]:
                garden["stones"] = garden.get("stones", 0) + 1
            else:
                garden["seeds"] = garden.get("seeds", 0) + 1

            garden.setdefault("artifacts", []).append({
                "name": quest.get("reward", "Quest reward"),
                "meaning": f"Completed quest: {quest.get('title')}",
                "created_at": now_timestamp()
            })

            state["memory_garden"] = garden

            save_growth_state(state)

            add_milestone(
                title=f"Completed quest: {quest.get('title')}",
                milestone_type="quest_completed",
                note=quest.get("reason", ""),
                importance=5
            )

            print(f"Quest completed: {quest.get('title')}")
            return

    print("Quest not found.")


def add_milestone(title, milestone_type="general", note="", importance=3):
    state = load_growth_state()

    milestone = {
        "created_at": now_timestamp(),
        "title": title,
        "type": milestone_type,
        "importance": int(importance),
        "note": note
    }

    state.setdefault("milestones", []).append(milestone)

    garden = state.get("memory_garden", {})
    garden["seeds"] = garden.get("seeds", 0) + 1

    if milestone_type in ["project", "seed_building", "growth_arc_completed"]:
        garden["trees"] = garden.get("trees", 0) + 1

    if milestone_type in ["reflection", "mirror"]:
        garden["stones"] = garden.get("stones", 0) + 1

    state["memory_garden"] = garden

    update_season(state)

    save_growth_state(state)
    return milestone


def add_milestone_interactive():
    print("\n=== ADD COMPANION MILESTONE ===")

    title = input("Title: ").strip()
    milestone_type = input("Type: ").strip()
    note = input("Note: ").strip()
    importance = input("Importance (1-5): ").strip()

    if title == "":
        print("Title cannot be empty.")
        return

    try:
        importance_value = int(importance)
    except ValueError:
        importance_value = 3

    add_milestone(title, milestone_type or "general", note, importance_value)
    print("Milestone added.")


def show_milestones():
    state = load_growth_state()

    print("\n=== COMPANION MILESTONES ===")

    milestones = state.get("milestones", [])

    if not milestones:
        print("No milestones yet.")
        return

    for milestone in milestones[-COMPANION_MILESTONE_LIMIT:]:
        print(f"\n{milestone.get('title')}")
        print(f"Type: {milestone.get('type')}")
        print(f"Importance: {milestone.get('importance')}")
        print(f"Created: {milestone.get('created_at')}")
        print(f"Note: {milestone.get('note')}")


def update_season(state):
    garden = state.get("memory_garden", {})
    total_growth = (
        garden.get("seeds", 0)
        + garden.get("trees", 0) * 3
        + garden.get("stones", 0) * 2
        + garden.get("lights", 0) * 2
    )

    if total_growth >= 60:
        state["active_season"] = "Deep Root"
        state["relationship_phase"] = "Trusted Builder"
    elif total_growth >= 35:
        state["active_season"] = "Rooted"
        state["relationship_phase"] = "Growing Trust"
    elif total_growth >= 15:
        state["active_season"] = "Familiar"
        state["relationship_phase"] = "Companion Prototype"
    else:
        state["active_season"] = "Sprout"
        state["relationship_phase"] = "Builder Bond"


def show_memory_garden():
    state = load_growth_state()
    garden = state.get("memory_garden", {})

    print("\n=== MEMORY GARDEN ===")
    print(f"Seeds: {garden.get('seeds', 0)}")
    print(f"Trees: {garden.get('trees', 0)}")
    print(f"Stones: {garden.get('stones', 0)}")
    print(f"Lights: {garden.get('lights', 0)}")

    print("\nArtifacts:")
    for artifact in garden.get("artifacts", []):
        print(f"- {artifact.get('name')}: {artifact.get('meaning')}")


def show_identity_mirror():
    state = load_growth_state()

    print("\n=== IDENTITY MIRROR ===")

    observations = state.get("identity_mirror", [])

    if not observations:
        print("No mirror observations yet.")
        return

    for observation in observations[-COMPANION_MIRROR_LIMIT:]:
        print(f"\nPattern: {observation.get('pattern')}")
        print(f"Confidence: {observation.get('confidence')}")
        print(f"Support response: {observation.get('support_response')}")
        print(f"Created: {observation.get('created_at')}")


def add_mirror_observation(pattern, confidence="medium", support_response=""):
    state = load_growth_state()

    observation = {
        "created_at": now_timestamp(),
        "pattern": pattern,
        "confidence": confidence,
        "support_response": support_response
    }

    state.setdefault("identity_mirror", []).append(observation)
    save_growth_state(state)

    add_milestone(
        title="Identity mirror observation added",
        milestone_type="mirror",
        note=pattern,
        importance=4
    )

    return observation


def add_mirror_interactive():
    print("\n=== ADD MIRROR OBSERVATION ===")

    pattern = input("Pattern: ").strip()
    confidence = input("Confidence (low/medium/high): ").strip()
    response = input("Support response: ").strip()

    if pattern == "":
        print("Pattern cannot be empty.")
        return

    add_mirror_observation(pattern, confidence or "medium", response)
    print("Mirror observation added.")


def build_mirror_prompt():
    state = load_growth_state()

    recent_memories = memories[-20:]

    return f"""
You are Seed's Identity Mirror.

Your job is to reflect useful patterns about User and the Seed project.
Do not diagnose.
Do not pretend certainty.
Do not manipulate.
Do not be creepy.
Be useful and direct.

Seed reason:
{state.get('why_seed_exists')}

Support style:
{json.dumps(state.get('support_style', {}), indent=2)}

Existing mirror:
{json.dumps(state.get('identity_mirror', [])[-COMPANION_MIRROR_LIMIT:], indent=2)}

Recent memories:
{json.dumps(recent_memories, indent=2)}

Return a short report:
1. Patterns noticed
2. What seems to motivate User
3. What seems to frustrate User
4. How Seed should support him better
5. One mirror observation worth saving
"""


def generate_identity_mirror(chat_state=None):
    print("\n=== GENERATE IDENTITY MIRROR ===")

    response = ask_llm(
        build_mirror_prompt(),
        task_type="memory",
        runtime_context=chat_state
    )

    print(response)

    if chat_state is not None:
        chat_state["last_identity_mirror"] = response
        log_system_event(
            chat_state.get("log_path"),
            "Identity mirror generated."
        )

    return response


def build_companion_pulse_prompt():
    state = load_growth_state()

    borrow_map = "Open-source DNA unavailable."
    skill_map = "Skill OS unavailable."

    if DNA_AVAILABLE:
        try:
            borrow_map = format_borrow_map()
        except Exception as error:
            borrow_map = f"DNA error: {error}"

    if SKILL_OS_AVAILABLE:
        try:
            skill_map = format_skill_map()
        except Exception as error:
            skill_map = f"Skill OS error: {error}"

    return f"""
You are Seed's Companion Growth OS.

Create a serious companion pulse for User.

Seed is not alive or conscious.
Seed is User's local-first companion system.
The point is growth, continuity, shared project history, rituals, memory, and agency.

Companion growth state:
{json.dumps(state, indent=2)}

Open-source DNA map:
{borrow_map}

Skill OS:
{skill_map}

Output:
1. What Seed and User are building
2. Current season and relationship phase
3. Active arcs
4. What Seed has learned about how User wants updates
5. The most meaningful next quest
6. Which cloned repos inspire the next growth step
7. Why Seed is still not v2.0.0-worthy
8. One concrete next action

Be direct.
Be bigger than a normal assistant.
Do not be cringe.
Do not claim feelings.
"""


def generate_companion_pulse(chat_state=None):
    print("\n=== COMPANION PULSE ===")

    response = ask_llm(
        build_companion_pulse_prompt(),
        task_type="debug",
        runtime_context=chat_state
    )

    print(response)

    add_milestone(
        title="Companion pulse generated",
        milestone_type="pulse",
        note=response[:500],
        importance=4
    )

    if chat_state is not None:
        chat_state["last_companion_pulse"] = response
        log_system_event(
            chat_state.get("log_path"),
            "Companion pulse generated."
        )

    return response


def show_repo_influences():
    state = load_growth_state()

    print("\n=== REPO INFLUENCES ON SEED GROWTH ===")

    for repo, info in state.get("repo_influences", {}).items():
        print(f"\n{repo}")
        print(f"Use: {info.get('use')}")
        print(f"Seed adaptation: {info.get('seed_adaptation')}")


def get_companion_growth_context_for_prompt(user_prompt):
    if not COMPANION_GROWTH_CONTEXT_ENABLED:
        return "Companion Growth OS context is disabled."

    state = load_growth_state()

    active_arcs = [
        arc for arc in state.get("growth_arcs", [])
        if arc.get("status") == "active"
    ]

    active_quests = [
        quest for quest in state.get("quests", [])
        if quest.get("status") == "active"
    ]

    context = "=== COMPANION GROWTH OS CONTEXT ===\n"
    context += f"Why Seed exists: {state.get('why_seed_exists')}\n"
    context += f"Companion truth: {state.get('companion_truth')}\n"
    context += f"Season: {state.get('active_season')}\n"
    context += f"Relationship phase: {state.get('relationship_phase')}\n"
    context += f"Current mode: {state.get('current_mode')}\n"

    context += "\nSupport style:\n"
    for key, value in state.get("support_style", {}).items():
        context += f"- {key}: {value}\n"

    context += "\nActive arcs:\n"
    for arc in active_arcs[:COMPANION_ARC_LIMIT]:
        context += (
            f"- {arc.get('id')} {arc.get('title')}: "
            f"{arc.get('reason')} "
            f"(sources: {', '.join(arc.get('source_repos', []))})\n"
        )

    context += "\nActive quests:\n"
    for quest in active_quests[:COMPANION_QUEST_LIMIT]:
        context += (
            f"- {quest.get('id')} {quest.get('title')}: "
            f"{quest.get('reason')} "
            f"(reward: {quest.get('reward')})\n"
        )

    context += "\nRecent mirror observations:\n"
    for observation in state.get("identity_mirror", [])[-COMPANION_MIRROR_LIMIT:]:
        context += (
            f"- {observation.get('pattern')} "
            f"(support: {observation.get('support_response')})\n"
        )

    context += """
Companion Growth rule:
Seed should use this context to behave like a growing local companion system with shared history, arcs, rituals, quests, and memory.
Seed must not claim consciousness, human emotion, or human identity.
The goal is meaningful companionship through continuity, not fake sentience.
"""

    return context


def get_growth_hud_lines():
    state = load_growth_state()
    garden = state.get("memory_garden", {})

    active_arcs = [
        arc for arc in state.get("growth_arcs", [])
        if arc.get("status") == "active"
    ]

    active_quests = [
        quest for quest in state.get("quests", [])
        if quest.get("status") == "active"
    ]

    return [
        ("Season", state.get("active_season")),
        ("Phase", state.get("relationship_phase")),
        ("Mode", state.get("current_mode")),
        ("Active arcs", str(len(active_arcs))),
        ("Active quests", str(len(active_quests))),
        ("Garden seeds", str(garden.get("seeds", 0))),
        ("Garden trees", str(garden.get("trees", 0))),
        ("Garden lights", str(garden.get("lights", 0)))
    ]