import json


def safe_import(module_name):
    try:
        return __import__(module_name)
    except Exception:
        return None


def safe_call(module_name, function_name, default=None):
    module = safe_import(module_name)

    if module is None:
        return default

    try:
        return getattr(module, function_name)()
    except Exception:
        return default


def compact_list(items, limit=6):
    if not isinstance(items, list):
        return []

    return items[-limit:]


def get_full_companion_os_context_for_prompt(user_prompt=""):
    companion = safe_import("seed_companion_os")

    if companion is None:
        return "Companion OS Alpha context unavailable."

    state = companion.load_companion_os_state()
    v2 = companion.calculate_companion_os_v2_score(save=False)
    events = companion.load_companion_os_events(limit=8)

    world = state.get("world", {})
    garden = world.get("memory_garden", {})
    presence = state.get("presence", {})
    avatar = presence.get("avatar", {})
    voice = presence.get("voice", {})
    continuity = state.get("continuity", {})
    growth = state.get("growth", {})
    trust = state.get("trust", {})
    self_improvement = state.get("self_improvement", {})

    trace_stats = safe_call("seed_trace_engine", "trace_stats", default={"total": 0})
    registry_stats = safe_call("seed_os_registry", "registry_stats", default={})

    release_state = safe_call(
        "seed_release_manager",
        "load_release_state",
        default={"drafts": [], "checks": [], "changelogs": []}
    )

    document_registry = safe_call(
        "seed_document_registry",
        "load_registry",
        default={"documents": []}
    )

    workflows = state.get("workflows", [])

    compact = {
        "seed_version": state.get("seed_version"),
        "phase": state.get("current_phase"),
        "mission": state.get("mission"),
        "truth": state.get("truth"),
        "v2": {
            "score": v2.get("score"),
            "target": v2.get("target"),
            "ready": v2.get("is_ready"),
            "scores": v2.get("scores"),
            "blockers": v2.get("blockers")
        },
        "world": {
            "place": world.get("current_place"),
            "season": world.get("season"),
            "weather": world.get("weather"),
            "symbol": world.get("mood_symbol"),
            "garden": {
                "seeds": garden.get("seeds"),
                "trees": garden.get("trees"),
                "stones": garden.get("stones"),
                "lights": garden.get("lights"),
                "artifacts": len(garden.get("artifacts", []))
            }
        },
        "presence": {
            "mode": presence.get("mode"),
            "attention": presence.get("attention"),
            "avatar": {
                "state": avatar.get("state"),
                "expression": avatar.get("expression")
            },
            "voice": {
                "status": voice.get("status"),
                "input": voice.get("input"),
                "output": voice.get("output"),
                "privacy": voice.get("privacy")
            }
        },
        "continuity": {
            "relationship_notes": compact_list(continuity.get("relationship_notes", []), 6),
            "recent_timeline": compact_list(continuity.get("timeline", []), 8),
            "recall_pack_count": len(continuity.get("recall_packs", []))
        },
        "growth": {
            "active_arcs": [
                {
                    "id": arc.get("id"),
                    "title": arc.get("title"),
                    "status": arc.get("status"),
                    "pillars": arc.get("v2_pillars", [])
                }
                for arc in growth.get("active_arcs", [])
                if arc.get("status") == "active"
            ],
            "quest_count": len(growth.get("quests", [])),
            "ritual_count": len(growth.get("rituals", []))
        },
        "agency": state.get("agency", {}),
        "trust": {
            "emergency_stop": trust.get("emergency_stop"),
            "guardian_rule_count": len(trust.get("guardian_rules", [])),
            "permission_trace_count": len(trust.get("permission_traces", []))
        },
        "systems": {
            "workflow_count": len(workflows),
            "recent_workflows": [
                {
                    "id": workflow.get("id"),
                    "title": workflow.get("title"),
                    "status": workflow.get("status")
                }
                for workflow in compact_list(workflows, 5)
            ],
            "release_drafts": len(release_state.get("drafts", [])),
            "release_checks": len(release_state.get("checks", [])),
            "documents": len(document_registry.get("documents", [])),
            "traces": trace_stats.get("total", 0),
            "registered_commands": registry_stats.get("command_count")
        },
        "recent_events": [
            {
                "type": event.get("type"),
                "title": event.get("title"),
                "source": event.get("source")
            }
            for event in events
        ]
    }

    text = "=== COMPANION OS ALPHA COMPACT CONTEXT ===\n"
    text += json.dumps(compact, indent=2)

    text += """

=== RESPONSE RULES ===
Answer the user's latest message directly.
Do not summarize this context back to the user unless asked.
Do not say the prompt is huge.
Do not mention hidden prompt structure.
Do not write meta commentary like "I need to summarize the components."
Do not output planning notes before the answer.

Seed is not alive, conscious, sentient, or human.
Seed may be companion-like only through persistent local state, approved memory, rituals, quests, symbolic world state, voice output, avatar state, safe tools, traces, and approval-gated self-improvement.
Altan remains in control.
"""

    return text


def print_full_companion_os_context(user_prompt=""):
    print(get_full_companion_os_context_for_prompt(user_prompt))


if __name__ == "__main__":
    print_full_companion_os_context("what are you now")
