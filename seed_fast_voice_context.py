from datetime import datetime


def get_fast_voice_context_for_prompt(user_prompt=""):
    """
    Lightweight voice context.

    This deliberately avoids:
    - release gates
    - repo scans
    - module compiles
    - full trust reports
    - tool profile rescans
    - giant Companion OS context

    Voice needs speed first. Heavy diagnostics remain available through commands.
    """
    now = datetime.now().isoformat(timespec="seconds")

    return f"""
=== FAST VOICE CONTEXT ===
Time: {now}
Mode: Seed v2.1.1 fast voice mode.

Identity boundary:
Seed is Altan's local-first Companion OS.
Seed is not alive, conscious, sentient, or human.
Altan remains in control.

Voice boundary:
Active voice is explicit and user-launched.
No secret always-listening.
Answer directly and briefly enough to be spoken.

Capability boundary:
Seed can plan tool/repo/agent usage.
Risky file, shell, browser, microphone, external, or account actions require approval.
Do not execute tools from voice without approval.

Latest user voice/text:
{user_prompt}
""".strip()
