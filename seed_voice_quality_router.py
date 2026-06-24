import json
from datetime import datetime


try:
    from seed_config import SEED_VOICE_QUALITY_STATE_FILE
except Exception:
    SEED_VOICE_QUALITY_STATE_FILE = "seed_voice_quality_state.json"


GARBAGE_FRAGMENTS = [
    "thanks for watching",
    "subscribe",
    "music",
    "[music]",
    "foreign",
    "you you"
]

INCOMPLETE_PATTERNS = [
    "tell me",
    "so tell me",
    "can you",
    "could you",
    "what about",
    "and then",
    "but"
]


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def classify_voice_text(text):
    cleaned = (text or "").strip()
    lowered = cleaned.lower()

    if not cleaned:
        status = "empty"
    elif any(x in lowered for x in GARBAGE_FRAGMENTS):
        status = "garbage"
    elif len(cleaned.split()) < 2:
        status = "too_short"
    elif lowered in INCOMPLETE_PATTERNS or any(lowered.endswith(x) for x in INCOMPLETE_PATTERNS):
        status = "incomplete"
    else:
        status = "usable"

    result = {
        "created_at": now_timestamp(),
        "text": text,
        "status": status,
        "should_answer": status == "usable",
        "should_clarify": status != "usable"
    }

    with open(SEED_VOICE_QUALITY_STATE_FILE, "w") as file:
        json.dump(result, file, indent=4)

    return result


def show_voice_quality():
    text = input("Voice transcript to classify: ").strip()
    print(json.dumps(classify_voice_text(text), indent=4))


def get_voice_quality_context(text=""):
    result = classify_voice_text(text or "empty")
    return (
        "=== VOICE QUALITY ROUTER CONTEXT ===\n"
        f"Status: {result['status']}\n"
        f"Should answer: {result['should_answer']}\n"
        "Rule: clarify incomplete/noisy transcripts; do not invent facts.\n"
    )


if __name__ == "__main__":
    show_voice_quality()
