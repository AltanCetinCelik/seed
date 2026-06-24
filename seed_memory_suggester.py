PROGRESS_KEYWORDS = [
    "added",
    "built",
    "fixed",
    "created",
    "implemented",
    "refactored",
    "connected",
    "updated",
    "completed",
    "done",
    "works",
    "finished"
]


def should_suggest_memory(user_message, seed_answer):
    user_message = user_message or ""
    seed_answer = seed_answer or ""
    combined_text = (user_message + " " + seed_answer).lower()

    for keyword in PROGRESS_KEYWORDS:
        if keyword in combined_text:
            return True

    return False


def guess_memory_type(user_message, seed_answer):
    combined_text = (user_message + " " + seed_answer).lower()

    if "bug" in combined_text or "fixed" in combined_text or "error" in combined_text:
        return "mistake"

    if "rule" in combined_text or "boundary" in combined_text:
        return "seed_boundary"

    if "identity" in combined_text or "seed is" in combined_text:
        return "seed_identity"

    if "lesson" in combined_text or "realized" in combined_text or "reflection" in combined_text:
        return "reflection"

    return "technical_progress"


def guess_importance(user_message, seed_answer):
    combined_text = (user_message + " " + seed_answer).lower()

    if "completed" in combined_text or "works" in combined_text or "fixed" in combined_text:
        return 5

    return 4


def build_memory_content(user_message, seed_answer):
    return f"User progress update: {user_message}"


def suggest_memory(user_message, seed_answer):
    user_message = user_message or ""
    seed_answer = seed_answer or ""
    if not should_suggest_memory(user_message, seed_answer):
        return None

    memory_type = guess_memory_type(user_message, seed_answer)
    importance = guess_importance(user_message, seed_answer)
    content = build_memory_content(user_message, seed_answer)

    return {
        "type": memory_type,
        "content": content,
        "importance": importance
    }