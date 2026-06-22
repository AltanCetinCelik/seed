import json

from seed_config import (
    MEMORY_CAPTURE_LLM_ENABLED,
    SMART_MEMORY_AUTO_REINDEX,
    SMART_MEMORY_DEFAULT_IMPORTANCE
)
from seed_memory import ALLOWED_TYPES, save_memory_direct
from seed_llm import ask_llm
from seed_chat_logger import log_system_event


try:
    from seed_semantic_memory import build_memory_embedding_index
    SEMANTIC_MEMORY_AVAILABLE = True
except ImportError:
    SEMANTIC_MEMORY_AVAILABLE = False


TYPE_ALIASES = {
    "technical_progress": [
        "technical_progress",
        "technical progress",
        "progress",
        "built",
        "fixed",
        "added",
        "implemented",
        "completed",
        "works",
        "update",
        "feature"
    ],
    "mistake": [
        "mistake",
        "bug",
        "error",
        "issue",
        "problem",
        "wrong",
        "failed",
        "crash",
        "fix"
    ],
    "reflection": [
        "reflection",
        "realization",
        "thought",
        "lesson",
        "learned",
        "understood",
        "idea",
        "insight"
    ],
    "seed_boundary": [
        "seed_boundary",
        "boundary",
        "rule",
        "limit",
        "must not",
        "should not",
        "allowed",
        "not allowed"
    ],
    "job_goal": [
        "job_goal",
        "job",
        "career",
        "internship",
        "portfolio",
        "cv",
        "resume",
        "hire",
        "marketable"
    ],
    "seed_identity": [
        "seed_identity",
        "identity",
        "seed is",
        "personality",
        "voice",
        "companion",
        "local-first"
    ],
    "personal_rule": [
        "personal_rule",
        "personal rule",
        "preference",
        "from now on",
        "remember that i prefer",
        "style"
    ]
}


def normalize_memory_type(memory_type):
    if memory_type is None:
        return None

    cleaned = str(memory_type).strip().lower()
    cleaned = cleaned.replace("-", "_")

    if cleaned in ALLOWED_TYPES:
        return cleaned

    for official_type, aliases in TYPE_ALIASES.items():
        for alias in aliases:
            alias_clean = alias.lower().replace("-", "_").replace(" ", "_")

            if cleaned == alias_clean:
                return official_type

            if cleaned == alias.lower():
                return official_type

    return None


def clamp_importance(value):
    try:
        importance = int(value)
    except (TypeError, ValueError):
        return SMART_MEMORY_DEFAULT_IMPORTANCE

    if importance < 1:
        return 1

    if importance > 5:
        return 5

    return importance


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


def parse_explicit_fields(text):
    fields = {}

    lines = text.splitlines()

    for line in lines:
        if ":" not in line:
            continue

        key, value = line.split(":", 1)

        key = key.strip().lower()
        value = value.strip()

        if key in ["type", "memory_type", "memory type"]:
            fields["type"] = value

        elif key in ["content", "memory", "text"]:
            fields["content"] = value

        elif key in ["importance", "priority"]:
            fields["importance"] = value

    return fields


def clean_memory_content(text):
    cleaned = text.strip()

    prefixes = [
        "/remember",
        "/save",
        "remember that",
        "save this",
        "save memory",
        "memory:"
    ]

    lowered = cleaned.lower()

    for prefix in prefixes:
        if lowered.startswith(prefix):
            cleaned = cleaned[len(prefix):].strip()
            break

    return cleaned


def infer_type_rule_based(text):
    lowered = text.lower()

    scores = {}

    for memory_type, aliases in TYPE_ALIASES.items():
        scores[memory_type] = 0

        for alias in aliases:
            if alias in lowered:
                scores[memory_type] += 1

    best_type = max(scores, key=scores.get)

    if scores[best_type] > 0:
        return best_type

    return "reflection"


def infer_importance_rule_based(text, memory_type):
    lowered = text.lower()

    high_importance_words = [
        "v1.",
        "v2.",
        "major",
        "mega",
        "important",
        "completed",
        "works",
        "fixed",
        "self-edit",
        "semantic",
        "cognition",
        "memory engine",
        "rollback",
        "critical"
    ]

    for word in high_importance_words:
        if word in lowered:
            return 5

    if memory_type in ["seed_boundary", "seed_identity", "technical_progress"]:
        return 5

    return SMART_MEMORY_DEFAULT_IMPORTANCE


def build_memory_extraction_prompt(free_text):
    allowed_types = ", ".join(ALLOWED_TYPES)

    return f"""
You are Seed's smart memory capture engine.

Convert the user's free-form memory text into one JSON object.

Allowed memory types:
{allowed_types}

Rules:
- Use only one of the allowed memory types.
- If the user explicitly provides type/content/importance, preserve those fields unless invalid.
- Content should be clean, useful, and written as a durable memory.
- Do not include filler like "the user said".
- Importance must be an integer from 1 to 5.
- Use importance 5 for major Seed milestones, architecture decisions, important bugs, boundaries, or identity facts.
- Use importance 4 for normal useful progress or reflections.
- Use importance 3 or lower only for minor notes.
- Return JSON only. No markdown. No explanation.

JSON shape:
{{
  "type": "technical_progress",
  "content": "Clean memory content here.",
  "importance": 5,
  "reason": "Short reason for classification."
}}

Free-form memory text:
{free_text}
"""


def classify_memory_with_llm(free_text, runtime_context=None):
    prompt = build_memory_extraction_prompt(free_text)

    response = ask_llm(
        prompt,
        task_type="memory",
        runtime_context=runtime_context
    )

    parsed = extract_json_object(response)

    if parsed is None:
        return None

    return parsed


def create_memory_draft_from_text(free_text, runtime_context=None):
    explicit_fields = parse_explicit_fields(free_text)

    llm_result = None

    if MEMORY_CAPTURE_LLM_ENABLED:
        llm_result = classify_memory_with_llm(free_text, runtime_context)

    if llm_result is None:
        llm_result = {}

    raw_type = (
        explicit_fields.get("type")
        or llm_result.get("type")
        or infer_type_rule_based(free_text)
    )

    memory_type = normalize_memory_type(raw_type)

    if memory_type is None:
        memory_type = infer_type_rule_based(free_text)

    raw_content = (
        explicit_fields.get("content")
        or llm_result.get("content")
        or clean_memory_content(free_text)
    )

    content = clean_memory_content(raw_content)

    raw_importance = (
        explicit_fields.get("importance")
        or llm_result.get("importance")
    )

    if raw_importance is None:
        importance = infer_importance_rule_based(free_text, memory_type)
    else:
        importance = clamp_importance(raw_importance)

    reason = llm_result.get("reason", "Generated by smart memory capture.")

    return {
        "type": memory_type,
        "content": content,
        "importance": importance,
        "reason": reason,
        "source_text": free_text
    }


def print_memory_draft(draft):
    print("\n=== SMART MEMORY DRAFT ===")
    print(f"Type: {draft.get('type')}")
    print(f"Content: {draft.get('content')}")
    print(f"Importance: {draft.get('importance')}")
    print(f"Reason: {draft.get('reason')}")


def edit_memory_draft(draft):
    print("\n=== EDIT MEMORY DRAFT ===")
    print("Press Enter to keep the current value.")

    new_type = input(f"Type [{draft['type']}]: ").strip()
    new_content = input(f"Content [{draft['content']}]: ").strip()
    new_importance = input(f"Importance [{draft['importance']}]: ").strip()

    if new_type != "":
        normalized_type = normalize_memory_type(new_type)

        if normalized_type is None:
            print("Invalid memory type. Keeping previous type.")
        else:
            draft["type"] = normalized_type

    if new_content != "":
        draft["content"] = new_content

    if new_importance != "":
        draft["importance"] = clamp_importance(new_importance)

    return draft


def approve_pending_memory(chat_state, session_history=None):
    draft = chat_state.get("pending_memory_draft")

    if draft is None:
        print("No pending memory draft.")
        return False

    saved = save_memory_direct(
        draft["type"],
        draft["content"],
        draft["importance"]
    )

    if not saved:
        print("Memory save failed.")
        return False

    print("Smart memory saved.")

    if session_history is not None:
        session_history.append({
            "role": "System",
            "content": (
                f"User approved and saved smart memory: "
                f"[{draft['type']}] {draft['content']} "
                f"Importance: {draft['importance']}"
            )
        })

    log_system_event(
        chat_state.get("log_path"),
        (
            f"Smart memory saved: "
            f"[{draft['type']}] {draft['content']} "
            f"Importance: {draft['importance']}"
        )
    )

    chat_state["pending_memory_draft"] = None

    if SMART_MEMORY_AUTO_REINDEX and SEMANTIC_MEMORY_AVAILABLE:
        print("Refreshing semantic memory index...")
        build_memory_embedding_index(force=False)

    return True


def reject_pending_memory(chat_state):
    if chat_state.get("pending_memory_draft") is None:
        print("No pending memory draft.")
        return

    chat_state["pending_memory_draft"] = None
    print("Pending memory draft rejected.")

    log_system_event(
        chat_state.get("log_path"),
        "Pending smart memory draft rejected."
    )


def show_pending_memory_draft(chat_state):
    draft = chat_state.get("pending_memory_draft")

    if draft is None:
        print("No pending memory draft.")
        return

    print_memory_draft(draft)


def smart_memory_capture_from_chat(
    chat_state,
    session_history=None,
    initial_text=None
):
    print("\n=== SMART MEMORY CAPTURE ===")

    if initial_text is None:
        initial_text = input("Memory text: ")

    if initial_text.strip() == "":
        print("Memory text cannot be empty.")
        return

    draft = create_memory_draft_from_text(
        initial_text,
        runtime_context=chat_state
    )

    chat_state["pending_memory_draft"] = draft

    print_memory_draft(draft)

    while True:
        choice = input("Approve save? (y/n/edit/later): ").strip().lower()

        if choice == "y":
            approve_pending_memory(chat_state, session_history)
            return

        if choice == "n":
            reject_pending_memory(chat_state)
            return

        if choice == "edit":
            draft = edit_memory_draft(draft)
            chat_state["pending_memory_draft"] = draft
            print_memory_draft(draft)
            continue

        if choice == "later":
            print("Memory draft kept pending.")
            print("Use /memory-draft, /memory-approve, or /memory-reject.")
            return

        print("Invalid choice. Use y, n, edit, or later.")