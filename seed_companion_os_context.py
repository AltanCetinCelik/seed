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

    hardening_status = safe_call(
        "seed_v2_hardening_metrics",
        "hardening_status_data",
        default={}
    )

    agency_hardening_status = safe_call(
        "seed_agency_hardening",
        "agency_hardening_status_data",
        default={}
    )

    self_hardening_status_text = safe_call(
        "seed_self_improvement_hardening",
        "get_self_improvement_hardening_context_for_prompt",
        default=""
    )

    voice_hardening_status = safe_call(
        "seed_voice_hardening",
        "voice_hardening_status_data",
        default={}
    )

    cockpit_hardening_status = safe_call(
        "seed_cockpit_actions",
        "cockpit_hardening_status_data",
        default={}
    )

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
        "voice_hardening": {
            "active_session": voice_hardening_status.get("active_session"),
            "sessions": voice_hardening_status.get("session_count"),
            "privacy_checks": voice_hardening_status.get("privacy_check_count"),
            "latest_privacy_ok": voice_hardening_status.get("latest_privacy_ok"),
            "pulse_checks": voice_hardening_status.get("pulse_check_count"),
            "ritual_checks": voice_hardening_status.get("ritual_check_count"),
            "transcript_placeholders": voice_hardening_status.get("transcript_placeholder_count"),
            "stt_boundary": voice_hardening_status.get("stt_boundary")
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
        "agency_hardening": {
            "autonomy": agency_hardening_status.get("current_autonomy_name"),
            "autonomy_level": agency_hardening_status.get("current_autonomy_level"),
            "approval_queue": agency_hardening_status.get("approval_queue_count"),
            "pending": agency_hardening_status.get("pending_count"),
            "simulations": agency_hardening_status.get("simulation_count"),
            "tool_decisions": agency_hardening_status.get("tool_decision_count"),
            "emergency_bridge": agency_hardening_status.get("emergency_bridge")
        },
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
        "hardening": {
            "voice": hardening_status.get("voice_score"),
            "cockpit": hardening_status.get("cockpit_score"),
            "agency": hardening_status.get("agency_score"),
            "self_improvement": hardening_status.get("self_improvement_score"),
            "presence": hardening_status.get("presence_score"),
            "blockers": hardening_status.get("blockers")
        },
        "cockpit_hardening": {
            "interactive_ready": cockpit_hardening_status.get("interactive_ready"),
            "actions": cockpit_hardening_status.get("action_count"),
            "action_log": cockpit_hardening_status.get("action_log_count"),
            "last_action": cockpit_hardening_status.get("last_action_at"),
            "available": cockpit_hardening_status.get("available")
        },
        "self_improvement_hardening": self_hardening_status_text,
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



# v1.19 Arsenal Integration context wrapper
try:
    _original_v119_arsenal_context_function = get_full_companion_os_context_for_prompt

    def get_full_companion_os_context_for_prompt(user_prompt=""):
        base = _original_v119_arsenal_context_function(user_prompt)

        extras = []

        try:
            from seed_repo_arsenal import get_repo_arsenal_context_for_prompt
            extras.append(get_repo_arsenal_context_for_prompt())
        except Exception:
            pass

        try:
            from seed_tool_router import get_tool_router_context_for_prompt
            extras.append(get_tool_router_context_for_prompt(user_prompt))
        except Exception:
            pass

        try:
            from seed_capability_planner import get_capability_planner_context_for_prompt
            extras.append(get_capability_planner_context_for_prompt(user_prompt))
        except Exception:
            pass

        try:
            from seed_integration_gate import get_integration_gate_context_for_prompt
            extras.append(get_integration_gate_context_for_prompt())
        except Exception:
            pass

        if extras:
            return str(base) + "\n\n" + "\n\n".join(extras)

        return base
except Exception:
    pass




# v2.0.0 Voice Command Bridge context wrapper
try:
    _original_v200_voice_command_context_function = get_full_companion_os_context_for_prompt

    def get_full_companion_os_context_for_prompt(user_prompt=""):
        base = _original_v200_voice_command_context_function(user_prompt)

        extras = []

        try:
            from seed_voice_command_bridge import get_voice_command_context_for_prompt
            extras.append(get_voice_command_context_for_prompt())
        except Exception:
            pass

        try:
            from seed_v2_stable_release import run_v2_stable_gate
            report = run_v2_stable_gate()
            extras.append(
                "=== V2 STABLE CONTEXT ===\n"
                + f"Stable ready: {report.get('stable_ready')}\n"
                + f"Voice command OK: {report.get('voice_command_ok')}\n"
                + f"Integration OK: {report.get('integration_ok')}\n"
            )
        except Exception:
            pass

        if extras:
            return str(base) + "\n\n" + "\n\n".join(extras)

        return base
except Exception:
    pass




# v2.1 Active Voice + Agent Arsenal context wrapper
try:
    _original_v21_active_agents_context_function = get_full_companion_os_context_for_prompt

    def get_full_companion_os_context_for_prompt(user_prompt=""):
        base = _original_v21_active_agents_context_function(user_prompt)

        extras = []

        try:
            from seed_active_voice_daemon import get_active_voice_context_for_prompt
            extras.append(get_active_voice_context_for_prompt())
        except Exception:
            pass

        try:
            from seed_agent_tool_profiles import get_agent_tool_profiles_context_for_prompt
            extras.append(get_agent_tool_profiles_context_for_prompt())
        except Exception:
            pass

        try:
            from seed_agent_orchestrator import get_agent_orchestrator_context_for_prompt
            extras.append(get_agent_orchestrator_context_for_prompt(user_prompt))
        except Exception:
            pass

        if extras:
            return str(base) + "\n\n" + "\n\n".join(extras)

        return base
except Exception:
    pass




# v2.2 Action Kernel + Memory + Tool Gateway context wrapper
try:
    _original_v22_mega_context_function = get_full_companion_os_context_for_prompt

    def get_full_companion_os_context_for_prompt(user_prompt=""):
        base = _original_v22_mega_context_function(user_prompt)
        extras = []

        try:
            from seed_action_kernel import get_action_kernel_context
            extras.append(get_action_kernel_context())
        except Exception:
            pass

        try:
            from seed_capability_memory import memory_context
            extras.append(memory_context(user_prompt))
        except Exception:
            pass

        try:
            from seed_mcp_gateway import get_mcp_context
            extras.append(get_mcp_context())
        except Exception:
            pass

        try:
            from seed_coding_agent_gateway import get_coding_context
            extras.append(get_coding_context(user_prompt))
        except Exception:
            pass

        try:
            from seed_browser_agent_gateway import get_browser_context
            extras.append(get_browser_context(user_prompt))
        except Exception:
            pass

        if extras:
            return str(base) + "\n\n" + "\n\n".join(extras)

        return base
except Exception:
    pass




# v2.3 Real Intelligence Layer context wrapper
try:
    _original_v23_intelligence_context_function = get_full_companion_os_context_for_prompt

    def get_full_companion_os_context_for_prompt(user_prompt=""):
        base = _original_v23_intelligence_context_function(user_prompt)
        extras = []

        try:
            from seed_intelligence_context import get_intelligence_context_for_prompt
            extras.append(get_intelligence_context_for_prompt(user_prompt))
        except Exception:
            pass

        if extras:
            return str(base) + "\n\n" + "\n\n".join(extras)

        return base
except Exception:
    pass




# v2.4 Experience Fusion context wrapper
try:
    _original_v24_experience_context_function = get_full_companion_os_context_for_prompt

    def get_full_companion_os_context_for_prompt(user_prompt=""):
        base = _original_v24_experience_context_function(user_prompt)
        extras = []

        try:
            from seed_experience_modes import experience_mode_context
            extras.append(experience_mode_context(user_prompt))
        except Exception:
            pass

        try:
            from seed_reference_fusion import reference_fusion_context
            extras.append(reference_fusion_context(user_prompt))
        except Exception:
            pass

        try:
            from seed_smooth_ux import smooth_ux_context
            extras.append(smooth_ux_context(user_prompt))
        except Exception:
            pass

        if extras:
            return str(base) + "\n\n" + "\n\n".join(extras)

        return base
except Exception:
    pass




# v2.5 Real Skill System context wrapper
try:
    _original_v25_skill_context_function = get_full_companion_os_context_for_prompt

    def get_full_companion_os_context_for_prompt(user_prompt=""):
        base = _original_v25_skill_context_function(user_prompt)
        extras = []

        try:
            from seed_skill_kernel import skill_kernel_context
            extras.append(skill_kernel_context(user_prompt))
        except Exception:
            pass

        if extras:
            return str(base) + "\n\n" + "\n\n".join(extras)

        return base
except Exception:
    pass




# v2.6 Supervised Agent Execution context wrapper
try:
    _original_v26_agent_context_function = get_full_companion_os_context_for_prompt

    def get_full_companion_os_context_for_prompt(user_prompt=""):
        base = _original_v26_agent_context_function(user_prompt)
        extras = []

        try:
            from seed_agent_run_lifecycle import agent_execution_context
            extras.append(agent_execution_context(user_prompt))
        except Exception:
            pass

        try:
            from seed_agent_operator_console import agent_operator_context
            extras.append(agent_operator_context(user_prompt))
        except Exception:
            pass

        if extras:
            return str(base) + "\n\n" + "\n\n".join(extras)

        return base
except Exception:
    pass




# v2.7 Executor Bridge + Repo Doctor + Voice Planner context wrapper
try:
    _original_v27_executor_context_function = get_full_companion_os_context_for_prompt

    def get_full_companion_os_context_for_prompt(user_prompt=""):
        base = _original_v27_executor_context_function(user_prompt)
        extras = []

        try:
            from seed_external_executor_bridge import executor_bridge_context
            extras.append(executor_bridge_context(user_prompt))
        except Exception:
            pass

        try:
            from seed_repo_doctor import repo_doctor_context
            extras.append(repo_doctor_context(user_prompt))
        except Exception:
            pass

        try:
            from seed_voice_upgrade_planner import voice_upgrade_context
            extras.append(voice_upgrade_context(user_prompt))
        except Exception:
            pass

        if extras:
            return str(base) + "\n\n" + "\n\n".join(extras)

        return base
except Exception:
    pass




# v2.8 Aider First Executor Bridge context wrapper
try:
    _original_v28_aider_context_function = get_full_companion_os_context_for_prompt

    def get_full_companion_os_context_for_prompt(user_prompt=""):
        base = _original_v28_aider_context_function(user_prompt)
        extras = []

        try:
            from seed_aider_bridge import aider_bridge_context
            extras.append(aider_bridge_context(user_prompt))
        except Exception:
            pass

        if extras:
            return str(base) + "\n\n" + "\n\n".join(extras)

        return base
except Exception:
    pass




# v2.9 Mission Control MegaPack context wrapper
try:
    _original_v29_mission_context_function = get_full_companion_os_context_for_prompt

    def get_full_companion_os_context_for_prompt(user_prompt=""):
        base = _original_v29_mission_context_function(user_prompt)
        extras = []

        for module_name, fn_name in [
            ("seed_mission_control", "mission_control_context"),
            ("seed_release_orchestrator", "release_orchestrator_context"),
            ("seed_voice_ux_pack", "voice_ux_context"),
            ("seed_self_repair_planner", "self_repair_context"),
            ("seed_command_memory", "command_memory_context"),
            ("seed_local_app_manifest", "app_manifest_context"),
        ]:
            try:
                module = __import__(module_name, fromlist=[fn_name])
                extras.append(getattr(module, fn_name)(user_prompt))
            except Exception:
                pass

        if extras:
            return str(base) + "\n\n" + "\n\n".join(extras)

        return base
except Exception:
    pass




# v3.0 Jarvis Control Plane context wrapper
try:
    _original_v30_control_context_function = get_full_companion_os_context_for_prompt

    def get_full_companion_os_context_for_prompt(user_prompt=""):
        base = _original_v30_control_context_function(user_prompt)
        extras = []

        for module_name, fn_name in [
            ("seed_control_plane_launcher", "control_plane_context"),
            ("seed_gate_matrix", "gate_matrix_context"),
            ("seed_runtime_supervisor", "runtime_supervisor_context"),
            ("seed_session_timeline", "timeline_context"),
            ("seed_command_center", "command_center_context"),
        ]:
            try:
                module = __import__(module_name, fromlist=[fn_name])
                extras.append(getattr(module, fn_name)(user_prompt))
            except Exception:
                pass

        if extras:
            return str(base) + "\n\n" + "\n\n".join(extras)

        return base
except Exception:
    pass




# v3.5 Omega Integration Pack context wrapper
try:
    _original_v35_omega_context_function = get_full_companion_os_context_for_prompt

    def get_full_companion_os_context_for_prompt(user_prompt=""):
        base = _original_v35_omega_context_function(user_prompt)
        extras = []

        for module_name, fn_name in [
            ("seed_repo_dna_engine", "repo_dna_context"),
            ("seed_integration_fusion_engine", "integration_fusion_context"),
            ("seed_omega_planner", "omega_plan_context"),
            ("seed_voice_one_shot", "voice_one_shot_context"),
        ]:
            try:
                module = __import__(module_name, fromlist=[fn_name])
                extras.append(getattr(module, fn_name)(user_prompt))
            except Exception:
                pass

        if extras:
            return str(base) + "\n\n" + "\n\n".join(extras)

        return base
except Exception:
    pass

