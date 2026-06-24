from datetime import datetime


def get_fast_voice_context_for_prompt(user_prompt=""):
    now = datetime.now().isoformat(timespec="seconds")
    parts = []

    for loader in [
        ("seed_intelligence_context", "get_intelligence_context_for_prompt"),
        ("seed_experience_modes", "experience_mode_context"),
        ("seed_smooth_ux", "smooth_ux_context"),
        ("seed_reference_fusion", "reference_fusion_context"),
        ("seed_skill_kernel", "skill_kernel_context"),
        ("seed_agent_run_lifecycle", "agent_execution_context"),
        ("seed_agent_operator_console", "agent_operator_context"),
        ("seed_external_executor_bridge", "executor_bridge_context"),
        ("seed_voice_upgrade_planner", "voice_upgrade_context"),
        ("seed_aider_bridge", "aider_bridge_context"),
        ("seed_mission_control", "mission_control_context"),
        ("seed_voice_ux_pack", "voice_ux_context"),
        ("seed_command_memory", "command_memory_context"),
        ("seed_control_plane_launcher", "control_plane_context"),
        ("seed_gate_matrix", "gate_matrix_context"),
        ("seed_runtime_supervisor", "runtime_supervisor_context"),
        ("seed_command_center", "command_center_context"),
    ]:
        try:
            module = __import__(loader[0], fromlist=[loader[1]])
            parts.append(getattr(module, loader[1])(user_prompt))
        except Exception:
            pass

    extra = "\n\n".join(parts)

    return f"""
=== SEED VOICE + JARVIS CONTROL PLANE CONTEXT ===
Time: {now}
Mode: Seed v3.0.0 Jarvis Control Plane.

Identity:
Seed is Altan's local-first Companion OS.
Seed is not alive, conscious, sentient, or human.
Altan remains in control.

Voice behavior:
- Sound like a useful local command center.
- Keep spoken answers short.
- Route dashboards to Control Plane.
- Route checks to Gate Matrix.
- Route diagnostics to Runtime Supervisor / Self-Repair.
- Route local work through Skill Kernel.
- Route agent work through supervised lifecycle.
- Route Aider work through Aider Bridge plans.
- Do not say an action happened unless verified.
- No arbitrary shell.
- No deletes.
- No auto-commit.
- No blind installs.
- External executors remain locked unless explicitly approved.
- No secret always-listening.

Latest transcript:
{user_prompt}

{extra}
""".strip()
