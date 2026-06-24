import json
from datetime import datetime


try:
    from seed_config import SEED_EXPERIENCE_MODE_FILE, SEED_DEFAULT_EXPERIENCE_MODE
except Exception:
    SEED_EXPERIENCE_MODE_FILE = "seed_experience_mode.json"
    SEED_DEFAULT_EXPERIENCE_MODE = "companion"


EXPERIENCE_MODES = {
    "companion": {
        "name": "Companion Seed",
        "style": "warm, direct, present",
        "best_for": ["talking", "support", "general help"],
        "voice": "short and human-feeling, but never claims consciousness"
    },
    "coding": {
        "name": "Coding Seed",
        "style": "precise, cautious, repo-aware",
        "best_for": ["debugging", "patches", "agents", "tests"],
        "voice": "short, command-focused, asks before risky changes"
    },
    "research": {
        "name": "Research Seed",
        "style": "source-grounded, comparative, skeptical",
        "best_for": ["web research", "repo docs", "tool comparison"],
        "voice": "clear summary with uncertainty"
    },
    "focus": {
        "name": "Focus Seed",
        "style": "minimal, calm, task-driven",
        "best_for": ["study", "deep work", "timers", "tiny quests"],
        "voice": "low chatter, next action only"
    },
    "guardian": {
        "name": "Guardian Seed",
        "style": "safe, grounding, protective",
        "best_for": ["safety", "approval gates", "risk checks"],
        "voice": "calm and firm"
    },
    "muse": {
        "name": "Muse Seed",
        "style": "creative, playful, idea-rich",
        "best_for": ["writing", "stories", "design", "creative quests"],
        "voice": "energetic but concise"
    },
    "archive": {
        "name": "Archive Seed",
        "style": "memory keeper, historian, organized",
        "best_for": ["timeline", "memory garden", "past decisions"],
        "voice": "careful, retrieval-first"
    }
}


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def save_mode(mode):
    if mode not in EXPERIENCE_MODES:
        raise ValueError(f"Unknown mode: {mode}")

    data = {
        "updated_at": now_timestamp(),
        "mode": mode,
        "profile": EXPERIENCE_MODES[mode]
    }

    with open(SEED_EXPERIENCE_MODE_FILE, "w") as file:
        json.dump(data, file, indent=4)

    return data


def load_mode():
    try:
        with open(SEED_EXPERIENCE_MODE_FILE, "r") as file:
            data = json.load(file)
        if data.get("mode") in EXPERIENCE_MODES:
            return data
    except Exception:
        pass

    return save_mode(SEED_DEFAULT_EXPERIENCE_MODE)


def detect_mode_from_text(text):
    lowered = (text or "").lower()

    aliases = {
        "coding": ["coding mode", "developer mode", "code mode", "debug mode"],
        "research": ["research mode", "web mode", "internet mode"],
        "focus": ["focus mode", "study mode", "deep work"],
        "guardian": ["guardian mode", "safety mode", "safe mode"],
        "muse": ["muse mode", "creative mode", "story mode"],
        "archive": ["archive mode", "memory mode", "timeline mode"],
        "companion": ["companion mode", "normal mode", "seed mode"]
    }

    for mode, phrases in aliases.items():
        if any(phrase in lowered for phrase in phrases):
            return mode

    return None


def experience_mode_context(user_prompt=""):
    current = load_mode()
    mode = current["mode"]
    profile = current["profile"]

    return f"""
=== SEED EXPERIENCE MODE ===
Current mode: {mode}
Name: {profile['name']}
Style: {profile['style']}
Best for: {', '.join(profile['best_for'])}
Voice: {profile['voice']}

Mode rule:
Seed should adapt tone and routing to this mode, while keeping all safety and approval gates.
""".strip()


def maybe_switch_mode_from_text(text):
    mode = detect_mode_from_text(text)
    if not mode:
        return None

    data = save_mode(mode)
    profile = data["profile"]
    return f"Switched to {profile['name']}."


def show_experience_modes():
    current = load_mode()

    print("\n=== SEED EXPERIENCE MODES ===")
    print(f"Current mode: {current['mode']} — {current['profile']['name']}")

    for mode, profile in EXPERIENCE_MODES.items():
        marker = "*" if mode == current["mode"] else "-"
        print(f"{marker} {mode}: {profile['name']}")
        print(f"  {profile['style']}")


def show_set_mode():
    show_experience_modes()
    mode = input("\nMode to set: ").strip().lower()
    try:
        data = save_mode(mode)
        print(f"\nSwitched to {data['profile']['name']}.")
    except Exception as error:
        print(f"Could not switch mode: {error}")


if __name__ == "__main__":
    show_experience_modes()
