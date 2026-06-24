import json
from datetime import datetime


try:
    from seed_config import SEED_SMOOTH_UX_STATE_FILE
except Exception:
    SEED_SMOOTH_UX_STATE_FILE = "seed_smooth_ux_state.json"


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def smooth_ux_state():
    try:
        from seed_experience_modes import load_mode
        mode = load_mode()
    except Exception:
        mode = {"mode": "unknown", "profile": {"name": "Unknown"}}

    state = {
        "updated_at": now_timestamp(),
        "version": "v2.4.0",
        "mode": mode.get("mode"),
        "mode_name": mode.get("profile", {}).get("name"),
        "home_commands": [
            "open cockpit",
            "show what you can do",
            "switch to coding mode",
            "search memory for active voice",
            "build a safe coding plan",
            "show almost-perfect build plan"
        ],
        "ux_rules": [
            "short direct answer first",
            "then one suggested next action",
            "no fake completed actions",
            "use mode-aware tone",
            "route risky actions through approval"
        ]
    }

    with open(SEED_SMOOTH_UX_STATE_FILE, "w") as file:
        json.dump(state, file, indent=4)

    return state


def seed_home_text():
    state = smooth_ux_state()

    text = "\n=== SEED HOME ===\n"
    text += f"Version: v2.4.0 Experience Fusion\n"
    text += f"Mode: {state['mode']} — {state['mode_name']}\n\n"
    text += "What Seed can do now:\n"
    text += "- Talk with active local voice\n"
    text += "- Open Cockpit with verified action\n"
    text += "- Search memory/repo/docs semantically\n"
    text += "- Build workflow plans\n"
    text += "- Route tools through safe gateways\n"
    text += "- Build coding/browser/MCP plans without blind execution\n"
    text += "- Adapt behavior using Companion/Coding/Research/Focus/Guardian/Muse/Archive modes\n\n"
    text += "Try saying/typing:\n"
    for command in state["home_commands"]:
        text += f"- {command}\n"

    return text


def classify_smooth_request(text):
    lowered = (text or "").lower()

    if any(x in lowered for x in ["what can you do", "seed home", "home screen", "jarvis home", "dashboard"]):
        return "seed_home"

    if any(x in lowered for x in ["almost perfect", "perfect seed", "make seed perfect", "next perfect build"]):
        return "almost_perfect_plan"

    if "mode" in lowered:
        return "mode"

    if "reference" in lowered or "repo dna" in lowered or "friend advice" in lowered:
        return "reference_fusion"

    return None


def maybe_handle_smooth_request(text):
    kind = classify_smooth_request(text)

    if kind == "seed_home":
        return seed_home_text()

    if kind == "almost_perfect_plan":
        from seed_reference_fusion import build_seed_almost_perfect_plan
        plan = build_seed_almost_perfect_plan()
        lines = ["=== SEED ALMOST-PERFECT PLAN ==="]
        for item in plan["milestones"]:
            lines.append(f"- {item['id']} {item['name']}: {item['result']}")
        return "\n".join(lines)

    if kind == "mode":
        from seed_experience_modes import maybe_switch_mode_from_text, experience_mode_context
        switched = maybe_switch_mode_from_text(text)
        return switched or experience_mode_context(text)

    if kind == "reference_fusion":
        from seed_reference_fusion import reference_fusion_context
        return reference_fusion_context(text)

    return None


def smooth_ux_context(user_prompt=""):
    state = smooth_ux_state()

    return f"""
=== SMOOTH UX CONTEXT ===
Seed should feel like a local companion command center, not just a CLI.
Current mode: {state['mode']} — {state['mode_name']}

UX rules:
- Answer short and useful first.
- Provide one clear next action.
- Use mode-aware tone.
- Do not fake actions.
- For risky tools: approval, sandbox, verify.
""".strip()


def show_seed_home():
    print(seed_home_text())


def show_smooth_ux():
    print("\n=== SMOOTH UX STATE ===")
    print(json.dumps(smooth_ux_state(), indent=4))


if __name__ == "__main__":
    show_seed_home()
