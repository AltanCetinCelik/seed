def get_intelligence_context_for_prompt(user_prompt=""):
    parts = []

    try:
        from seed_workflow_brain import workflow_answer_hint
        parts.append(workflow_answer_hint(user_prompt))
    except Exception as error:
        parts.append(f"Workflow brain unavailable: {error}")

    try:
        from seed_semantic_memory import semantic_memory_context
        parts.append(semantic_memory_context(user_prompt))
    except Exception as error:
        parts.append(f"Semantic memory unavailable: {error}")

    parts.append(
        "=== REAL INTELLIGENCE RULES ===\n"
        "- Use retrieved memory when available.\n"
        "- Use the action kernel for local actions.\n"
        "- Do not say an action happened unless verified.\n"
        "- Risky tools require approval.\n"
        "- If retrieval is weak, say what is uncertain.\n"
    )

    return "\n\n".join(parts)
