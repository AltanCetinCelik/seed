from datetime import datetime


try:
    from seed_config import AVATAR_ALLOWED_STATES
except Exception:
    AVATAR_ALLOWED_STATES = [
        "focused",
        "thinking",
        "guarding",
        "celebrating",
        "quiet",
        "listening",
        "building",
        "reflecting",
        "archiving"
    ]


from seed_companion_os import (
    load_companion_os_state,
    save_companion_os_state,
    append_companion_os_event
)


try:
    from seed_trace_engine import append_trace
    TRACE_AVAILABLE = True
except Exception:
    TRACE_AVAILABLE = False


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def get_avatar_state():
    state = load_companion_os_state()
    return state.setdefault("presence", {}).setdefault("avatar", {
        "mode": "symbolic",
        "state": "focused",
        "expression": "thinking",
        "body": "not_implemented_yet",
        "future": "OpenAvatarChat / three-vrm / Godot direction"
    })


def save_avatar_state(avatar):
    state = load_companion_os_state()
    state.setdefault("presence", {})
    state["presence"]["avatar"] = avatar
    save_companion_os_state(state)


def set_avatar_state(avatar_state=None, expression=None, mode=None, note=""):
    avatar = get_avatar_state()

    if avatar_state:
        if avatar_state not in AVATAR_ALLOWED_STATES:
            return {
                "ok": False,
                "message": f"Invalid avatar state. Allowed: {', '.join(AVATAR_ALLOWED_STATES)}"
            }

        avatar["state"] = avatar_state

    if expression:
        avatar["expression"] = expression

    if mode:
        avatar["mode"] = mode

    avatar["updated_at"] = now_timestamp()
    avatar["note"] = note

    save_avatar_state(avatar)

    append_companion_os_event(
        "avatar_state_changed",
        f"Avatar state changed: {avatar.get('state')}",
        {
            "avatar": avatar,
            "note": note
        },
        source="avatar_state",
        importance=3
    )

    if TRACE_AVAILABLE:
        try:
            append_trace(
                trace_type="world_trace",
                title=f"Avatar state changed: {avatar.get('state')}",
                summary=f"Expression: {avatar.get('expression')}. Note: {note}",
                sources=["avatar_state", "OpenAvatarChat future", "three-vrm future", "Godot future"],
                decision="updated",
                risk="low"
            )
        except Exception:
            pass

    return {
        "ok": True,
        "avatar": avatar
    }


def set_avatar_state_interactive():
    print("\n=== SET AVATAR STATE ===")
    print("Allowed states:", ", ".join(AVATAR_ALLOWED_STATES))

    avatar_state = input("State: ").strip()
    expression = input("Expression: ").strip()
    note = input("Note: ").strip()

    result = set_avatar_state(
        avatar_state=avatar_state or None,
        expression=expression or None,
        note=note
    )

    if result["ok"]:
        print("Avatar state updated.")
    else:
        print(result["message"])


def show_avatar_state():
    avatar = get_avatar_state()

    print("\n=== AVATAR STATE ===")
    print(f"Mode: {avatar.get('mode')}")
    print(f"State: {avatar.get('state')}")
    print(f"Expression: {avatar.get('expression')}")
    print(f"Body: {avatar.get('body')}")
    print(f"Future: {avatar.get('future')}")
    print(f"Updated: {avatar.get('updated_at')}")
    print(f"Note: {avatar.get('note')}")


def avatar_test():
    result = set_avatar_state(
        avatar_state="listening",
        expression="soft focus",
        note="Avatar test switched Seed to listening state."
    )

    if result["ok"]:
        print("Avatar test OK: listening / soft focus.")
    else:
        print(result["message"])


def avatar_for_mode(mode):
    mapping = {
        "builder": ("building", "sharp focus"),
        "guardian": ("guarding", "steady watch"),
        "archive": ("archiving", "quiet attention"),
        "mentor": ("reflecting", "calm directness"),
        "muse": ("thinking", "creative spark"),
        "operator": ("focused", "terminal focus"),
        "voice": ("listening", "warm signal"),
        "celebration": ("celebrating", "gold glow"),
        "quiet": ("quiet", "dim amber")
    }

    avatar_state, expression = mapping.get(mode, ("focused", "thinking"))

    return set_avatar_state(
        avatar_state=avatar_state,
        expression=expression,
        note=f"Avatar state selected for mode: {mode}"
    )


def avatar_for_mode_interactive():
    mode = input("Mode: ").strip()

    if not mode:
        print("Mode required.")
        return

    result = avatar_for_mode(mode)

    if result["ok"]:
        print("Avatar mode applied.")
    else:
        print(result["message"])


def get_avatar_context_for_prompt():
    avatar = get_avatar_state()

    text = "=== AVATAR STATE CONTEXT ===\n"
    text += f"Mode: {avatar.get('mode')}\n"
    text += f"State: {avatar.get('state')}\n"
    text += f"Expression: {avatar.get('expression')}\n"
    text += f"Future body direction: {avatar.get('future')}\n"
    text += """
Avatar rule:
Avatar state is symbolic interface state, not emotion or consciousness.
Use it to represent Seed's current mode: focused, guarding, listening, building, archiving, etc.
"""
    return text


if __name__ == "__main__":
    show_avatar_state()
