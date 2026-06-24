def fast_reply_for_message(text):
    if not text:
        return None

    raw = text.strip()
    lowered = raw.lower()

    # Terminal commands should not hit Ollama.
    try:
        from seed_terminal_guard import looks_like_terminal_block, terminal_block_message
        if looks_like_terminal_block(raw):
            return terminal_block_message(raw)
    except Exception:
        pass

    # Let slash commands be handled by command router, not here.
    if raw.startswith("/"):
        return None

    # Fast operational replies.
    if lowered in {"hi", "hello", "hey", "yo", "selam", "sa"}:
        return "Yo. Seed is online. Use `/operator-status`, `/quick-gates`, or tell me the next goal."

    if "slow" in lowered or "minute" in lowered or "takes too long" in lowered:
        return (
            "Yeah, Seed is carrying too much runtime weight. Use `/performance` and `/quick-gates` for fast checks. "
            "Full `/final-gates` is intentionally slower because it runs multiple gate scripts. "
            "For normal chat, v5.2 fast runtime should avoid heavy context and cap the LLM wait."
        )


    if (
        "what changed" in lowered
        or "what has changed" in lowered
        or "tell me what changed" in lowered
        or "tell me what has changed" in lowered
    ):
        return (
            "Big change: Seed jumped from v5.2 fast runtime into v20 Sovereign Companion OS MegaCore. "
            "Added Memory Engine 2.0, Voice Runtime, Workflow Graph Brain, Browser Sandbox, MCP Marketplace, "
            "OpenHands Sandbox, Project/Life OS, Seed World + Avatar Presence, Multi-Agent Council, "
            "Self-Improvement Lab, Multi-Device Hub, and a v20 Control Plane panel. "
            "Gates show v20, v50, v40, and v36 are passing. The current bug was only a None-response/memory-suggester crash, now hotfixed."
        )

    if "what should we build next" in lowered or "next upgrade" in lowered or "bigger upgrade" in lowered:
        return (
            "Next major target: Seed v5.3 — Live Operator Dashboard. "
            "It should add live task ticks, one-click checkpoint, Aider dry-run review panel, service controls, "
            "and a clean latency monitor. After that: v6 Voice Runtime."
        )

    if "status" in lowered and "seed" in lowered:
        try:
            from seed_operator_runtime import operator_status
            s = operator_status()
            return (
                "Seed status: "
                f"ready_tasks={s.get('ready_task_count')}, "
                f"total_tasks={s.get('total_task_count')}, "
                f"manual_tick_only={s.get('manual_tick_only')}. "
                "Use `/operator-status` for full details."
            )
        except Exception:
            return "Seed status is available with `/operator-status`."

    return None
