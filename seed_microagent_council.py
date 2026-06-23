import json
from datetime import datetime


from seed_companion_os import (
    load_companion_os_state,
    save_companion_os_state,
    append_companion_os_event,
    append_companion_os_journal,
    MICROAGENTS
)


try:
    from seed_llm import ask_llm
    LLM_AVAILABLE = True
except Exception:
    LLM_AVAILABLE = False


try:
    from seed_trace_engine import append_trace
    TRACE_AVAILABLE = True
except Exception:
    TRACE_AVAILABLE = False


try:
    from seed_trust_center import guardian_review_text
    TRUST_AVAILABLE = True
except Exception:
    TRUST_AVAILABLE = False


try:
    from seed_workflow_engine import create_workflow, add_workflow_step
    WORKFLOW_AVAILABLE = True
except Exception:
    WORKFLOW_AVAILABLE = False


try:
    from seed_continuity_engine import build_continuity_context
    CONTINUITY_AVAILABLE = True
except Exception:
    CONTINUITY_AVAILABLE = False


try:
    from seed_os_registry import get_registry_context_for_prompt
    REGISTRY_AVAILABLE = True
except Exception:
    REGISTRY_AVAILABLE = False


try:
    from seed_tool_manifest_v2 import get_tool_manifest_context_for_prompt
    TOOL_MANIFEST_AVAILABLE = True
except Exception:
    TOOL_MANIFEST_AVAILABLE = False


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def council_context(goal):
    state = load_companion_os_state()

    world = state.get("world", {})
    garden = world.get("memory_garden", {})
    continuity = state.get("continuity", {})
    growth = state.get("growth", {})

    context = {
        "goal": goal,
        "mission": state.get("mission"),
        "truth": state.get("truth"),
        "microagents": MICROAGENTS,
        "v2": state.get("v2", {}),
        "world": {
            "place": world.get("current_place"),
            "season": world.get("season"),
            "weather": world.get("weather"),
            "garden": {
                "seeds": garden.get("seeds"),
                "trees": garden.get("trees"),
                "stones": garden.get("stones"),
                "lights": garden.get("lights"),
                "artifacts": len(garden.get("artifacts", []))
            }
        },
        "recent_timeline": continuity.get("timeline", [])[-8:],
        "relationship_notes": continuity.get("relationship_notes", [])[-6:],
        "active_arcs": [
            {
                "id": arc.get("id"),
                "title": arc.get("title"),
                "pillars": arc.get("v2_pillars", []),
                "success_condition": arc.get("success_condition")
            }
            for arc in growth.get("active_arcs", [])
            if arc.get("status") == "active"
        ],
        "quest_count": len(growth.get("quests", [])),
        "ritual_count": len(growth.get("rituals", [])),
        "workflow_count": len(state.get("workflows", [])),
        "trace_count": len(state.get("trust", {}).get("answer_traces", [])) + len(state.get("trust", {}).get("permission_traces", [])),
        "release_draft_count": len(state.get("self_improvement", {}).get("release_drafts", []))
    }

    return context


def fallback_council(goal):
    return f"""
=== MICROAGENT COUNCIL FALLBACK ===

Goal:
{goal}

Builder:
Build it as a safe module-first implementation. Avoid editing existing core files until all new modules compile.

Guardian:
Do not claim sentience. Do not allow silent file edits or risky local commands. Require approval gates.

Archive:
Tie the work to Seed's existing timeline, memories, and why Altan started Seed.

Mentor:
Prioritize features that make Seed more useful and companion-like, not just more complex.

Muse:
Represent progress inside Seed World and Memory Garden so the system feels continuous.

Operator:
Use only registered tools and safe diagnostics. Keep action history and traces.

Combined plan:
Create a workflow, define approval points, test new modules, then integrate commands in the final integration section.
"""


def run_council(goal, chat_state=None, create_workflow_from_result=False):
    context = council_context(goal)

    if LLM_AVAILABLE:
        prompt = f"""
You are Seed's Microagent Council.

Seed is Altan's local-first companion project.
Seed is not alive or conscious.
Seed must not pretend otherwise.

Goal:
{goal}

Microagents:
{json.dumps(MICROAGENTS, indent=2)}

Context:
{json.dumps(context, indent=2)}

Each microagent must speak:
1. Builder
2. Guardian
3. Archive
4. Mentor
5. Muse
6. Operator

Then produce:
- Combined plan
- Approval points
- Safety risks
- Files/modules likely involved
- V2 pillar impact
- Concrete next step

Tone: direct, serious, useful.
"""

        response = ask_llm(prompt, task_type="debug", runtime_context=chat_state)

        if isinstance(response, str) and "timed out" in response.lower():
            response = fallback_council(goal)
    else:
        response = fallback_council(goal)

    state = load_companion_os_state()

    council_record = {
        "created_at": now_timestamp(),
        "goal": goal,
        "response": response
    }

    state["council"]["last_council"] = council_record
    state["council"].setdefault("history", []).append(council_record)
    save_companion_os_state(state)

    append_companion_os_event(
        "microagent_council_ran",
        f"Microagent Council ran: {goal}",
        {
            "goal": goal
        },
        source="microagent_council",
        importance=4
    )

    append_companion_os_journal(
        f"Microagent Council: {goal}",
        response
    )

    if TRACE_AVAILABLE:
        try:
            append_trace(
                trace_type="proposal_trace",
                title=f"Council plan: {goal}",
                summary=response,
                sources=["Builder", "Guardian", "Archive", "Mentor", "Muse", "Operator"],
                decision="planned",
                risk="medium"
            )
        except Exception:
            pass

    if create_workflow_from_result and WORKFLOW_AVAILABLE:
        workflow = create_workflow(
            title=f"Council workflow: {goal[:60]}",
            goal=goal,
            source_repos=["LangGraph", "OpenHands", "Aider", "Cline"],
            v2_pillars=["Self-improvement", "Safety", "Growth"],
            risk="medium"
        )

        add_workflow_step(
            workflow_id=workflow["id"],
            title="Review council output",
            details=response[:2000],
            risk="low",
            approval_required=False,
            owner="Archive"
        )

        add_workflow_step(
            workflow_id=workflow["id"],
            title="Guardian approval review",
            details="Review the plan before any risky action.",
            risk="medium",
            approval_required=True,
            owner="Guardian"
        )

    return response


def council_interactive(chat_state=None):
    goal = input("Council goal: ").strip()

    if goal == "":
        print("Goal cannot be empty.")
        return

    make_workflow = input("Create workflow from council result? y/n: ").strip().lower() == "y"

    response = run_council(
        goal=goal,
        chat_state=chat_state,
        create_workflow_from_result=make_workflow
    )

    print("\n=== MICROAGENT COUNCIL ===")
    print(response)


def show_last_council():
    state = load_companion_os_state()
    last = state.get("council", {}).get("last_council")

    print("\n=== LAST MICROAGENT COUNCIL ===")

    if not last:
        print("No council has run yet.")
        return

    print(f"Created: {last.get('created_at')}")
    print(f"Goal: {last.get('goal')}")
    print("\n" + last.get("response", ""))


def show_council_history(limit=8):
    state = load_companion_os_state()
    history = state.get("council", {}).get("history", [])[-limit:]

    print("\n=== MICROAGENT COUNCIL HISTORY ===")

    if not history:
        print("No council history yet.")
        return

    for item in history:
        print(f"\n{item.get('created_at')} — {item.get('goal')}")
        print(item.get("response", "")[:900])


def guardian_council_review_interactive(chat_state=None):
    target = input("What should Guardian review? ").strip()

    if target == "":
        print("Target cannot be empty.")
        return

    if TRUST_AVAILABLE:
        result = guardian_review_text(target)
        print("\n=== GUARDIAN REVIEW ===")
        print(json.dumps(result, indent=4))
        return

    response = run_council(
        goal=f"Guardian-only review: {target}",
        chat_state=chat_state,
        create_workflow_from_result=False
    )

    print(response)


def get_council_context_for_prompt():
    state = load_companion_os_state()
    last = state.get("council", {}).get("last_council")
    history = state.get("council", {}).get("history", [])[-5:]

    text = "=== MICROAGENT COUNCIL CONTEXT ===\n"
    text += "Agents:\n"

    for name, data in MICROAGENTS.items():
        text += f"- {name}: {data.get('role')}\n"

    if last:
        text += f"\nLast council goal: {last.get('goal')}\n"
        text += f"Last council excerpt: {last.get('response', '')[:1200]}\n"
    else:
        text += "\nNo council has run yet.\n"

    text += f"\nCouncil history count shown: {len(history)}\n"

    text += """
Council rule:
The council is an internal planning structure, not separate conscious beings.
Use it to reason from Builder, Guardian, Archive, Mentor, Muse, and Operator perspectives.
"""

    return text


if __name__ == "__main__":
    show_last_council()
