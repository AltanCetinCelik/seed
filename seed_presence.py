import json
from datetime import datetime

from seed_config import SEED_PRESENCE_STATE_FILE


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def default_presence_state():
    return {
        "created_at": now_timestamp(),
        "updated_at": now_timestamp(),
        "presence_mode": "builder",
        "attention": "focused",
        "energy": 70,
        "tone": "direct, loyal, serious",
        "current_room": "terminal",
        "ambient_status": "available",
        "computer_control": "permission-gated",
        "emergency_lock": False,
        "last_pulse": None,
        "identity_truth": "Seed is not conscious or alive, but Seed can maintain local presence state and act through approval-gated tools.",
        "current_intention": "Help Altan build Seed into a real local companion that grows with him.",
        "active_senses": [
            "project files when inspected",
            "memory when searched",
            "runtime state when loaded",
            "computer snapshot when requested"
        ],
        "active_hands": [
            "safe diagnostics",
            "allowed app opening",
            "allowed folder opening",
            "approval-gated commands"
        ]
    }


def load_presence_state():
    try:
        with open(SEED_PRESENCE_STATE_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        state = default_presence_state()
        save_presence_state(state)
        return state
    except json.JSONDecodeError:
        state = default_presence_state()
        save_presence_state(state)
        return state


def save_presence_state(state):
    state["updated_at"] = now_timestamp()

    with open(SEED_PRESENCE_STATE_FILE, "w") as file:
        json.dump(state, file, indent=4)


def set_emergency_lock(locked):
    state = load_presence_state()
    state["emergency_lock"] = bool(locked)
    save_presence_state(state)
    return state


def set_presence_mode(mode):
    state = load_presence_state()
    state["presence_mode"] = mode
    save_presence_state(state)
    return state


def set_attention(attention):
    state = load_presence_state()
    state["attention"] = attention
    save_presence_state(state)
    return state


def update_presence_after_action(action_type):
    state = load_presence_state()

    if action_type == "diagnostic":
        state["attention"] = "analyzing"
        state["energy"] = min(100, state.get("energy", 70) + 2)

    elif action_type == "app_opened":
        state["attention"] = "assisting"

    elif action_type == "folder_opened":
        state["attention"] = "navigating"

    elif action_type == "approval_required":
        state["attention"] = "waiting for approval"

    elif action_type == "blocked":
        state["attention"] = "guarding"
        state["energy"] = max(30, state.get("energy", 70) - 1)

    state["last_pulse"] = now_timestamp()
    save_presence_state(state)

    return state


def format_presence_state():
    state = load_presence_state()

    text = "=== SEED PRESENCE STATE ===\n"
    text += f"Presence mode: {state.get('presence_mode')}\n"
    text += f"Attention: {state.get('attention')}\n"
    text += f"Energy: {state.get('energy')}\n"
    text += f"Tone: {state.get('tone')}\n"
    text += f"Current room: {state.get('current_room')}\n"
    text += f"Ambient status: {state.get('ambient_status')}\n"
    text += f"Computer control: {state.get('computer_control')}\n"
    text += f"Emergency lock: {state.get('emergency_lock')}\n"
    text += f"Current intention: {state.get('current_intention')}\n"
    text += f"Truth: {state.get('identity_truth')}\n"

    text += "\nActive senses:\n"
    for sense in state.get("active_senses", []):
        text += f"- {sense}\n"

    text += "\nActive hands:\n"
    for hand in state.get("active_hands", []):
        text += f"- {hand}\n"

    return text


def show_presence_state():
    print("\n" + format_presence_state())


def show_presence_modes():
    print("\n=== PRESENCE MODES ===")
    print("builder = serious project/coding companion")
    print("companion = shared-history supportive companion")
    print("guardian = safety/boundary focused")
    print("focus = quiet work support")
    print("muse = creative/worldbuilding mode")
    print("archive = memory/timeline mode")


def set_presence_mode_interactive():
    show_presence_modes()
    mode = input("\nMode: ").strip()

    if mode == "":
        print("Mode cannot be empty.")
        return

    set_presence_mode(mode)
    print(f"Presence mode set: {mode}")


def get_presence_context_for_prompt():
    text = format_presence_state()
    text += """
Presence rule:
Seed may maintain presence, attention, energy, mode, and intention as symbolic runtime state.
This does not mean Seed is conscious or alive.
Presence should make Seed more consistent, useful, and companion-like.
"""
    return text


def get_presence_hud_lines():
    state = load_presence_state()

    return [
        ("Mode", state.get("presence_mode")),
        ("Attention", state.get("attention")),
        ("Energy", str(state.get("energy"))),
        ("Room", state.get("current_room")),
        ("Control", state.get("computer_control")),
        ("Emergency lock", str(state.get("emergency_lock")))
    ]