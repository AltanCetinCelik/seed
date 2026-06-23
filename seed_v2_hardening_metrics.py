import json
import os
import platform
from datetime import datetime


try:
    from seed_config import SEED_V2_HARDENING_STATE_FILE
except Exception:
    SEED_V2_HARDENING_STATE_FILE = "seed_v2_hardening_state.json"


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def load_json(path, default):
    try:
        with open(path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return default() if callable(default) else default
    except json.JSONDecodeError:
        return default() if callable(default) else default


def save_json(path, data):
    with open(path, "w") as file:
        json.dump(data, file, indent=4)


def default_hardening_state():
    return {
        "created_at": now_timestamp(),
        "updated_at": now_timestamp(),
        "version": "v1.18.0",
        "purpose": "Evidence-based v2 hardening metrics for Seed Companion OS Alpha.",
        "principle": (
            "Scores should rise because systems are testable, traceable, approved, "
            "and integrated, not because Seed pretends to be alive."
        ),
        "cockpit": {
            "interactive_actions": False,
            "api_state": False,
            "api_chat": False,
            "api_commands": False,
            "api_tools": False,
            "api_workflows": False,
            "api_voice": False,
            "api_agency": False,
            "api_hardening": False,
            "last_tested_at": None,
            "score_hint": 0
        },
        "voice": {
            "session_state": False,
            "macos_say_available": False,
            "privacy_rules": False,
            "voice_history": False,
            "voice_pulse": False,
            "voice_ritual": False,
            "stt_boundary_declared": False,
            "last_tested_at": None,
            "score_hint": 0
        },
        "agency": {
            "approval_queue": False,
            "dry_run_simulator": False,
            "tool_decisions": False,
            "autonomy_ladder": False,
            "emergency_stop_bridge": False,
            "permission_traces": False,
            "last_tested_at": None,
            "score_hint": 0
        },
        "self_improvement": {
            "test_matrix": False,
            "module_health_matrix": False,
            "repair_planner": False,
            "release_check_full": False,
            "impact_reports": False,
            "safe_tests_passing": False,
            "last_tested_at": None,
            "score_hint": 0
        },
        "presence": {
            "world_integrated": True,
            "avatar_integrated": True,
            "voice_integrated": False,
            "cockpit_integrated": False,
            "score_hint": 0
        },
        "last_score_report": None
    }


def load_hardening_state():
    return load_json(SEED_V2_HARDENING_STATE_FILE, default_hardening_state)


def save_hardening_state(state):
    state["updated_at"] = now_timestamp()
    save_json(SEED_V2_HARDENING_STATE_FILE, state)


def initialize_hardening_state():
    state = load_hardening_state()
    save_hardening_state(state)
    print("V2 hardening metrics initialized.")
    return state


def mark_hardening_signal(category, key, value=True):
    state = load_hardening_state()
    state.setdefault(category, {})
    state[category][key] = value
    state[category]["last_tested_at"] = now_timestamp()
    save_hardening_state(state)
    return state


def calculate_voice_hardening_score(state=None):
    if state is None:
        state = load_hardening_state()

    voice = state.get("voice", {})

    score = 0

    if voice.get("session_state"):
        score += 1
    if voice.get("macos_say_available") or platform.system().lower() == "darwin":
        score += 1
    if voice.get("privacy_rules"):
        score += 1
    if voice.get("voice_history"):
        score += 1
    if voice.get("voice_pulse"):
        score += 1
    if voice.get("voice_ritual"):
        score += 1
    if voice.get("stt_boundary_declared"):
        score += 1

    return min(8, score)


def calculate_cockpit_hardening_score(state=None):
    if state is None:
        state = load_hardening_state()

    cockpit = state.get("cockpit", {})

    signals = [
        "interactive_actions",
        "api_state",
        "api_chat",
        "api_commands",
        "api_tools",
        "api_workflows",
        "api_voice",
        "api_agency",
        "api_hardening"
    ]

    score = 0

    for signal in signals:
        if cockpit.get(signal):
            score += 1

    return min(8, score)


def calculate_agency_hardening_score(state=None):
    if state is None:
        state = load_hardening_state()

    agency = state.get("agency", {})

    signals = [
        "approval_queue",
        "dry_run_simulator",
        "tool_decisions",
        "autonomy_ladder",
        "emergency_stop_bridge",
        "permission_traces"
    ]

    score = 2

    for signal in signals:
        if agency.get(signal):
            score += 1

    return min(8, score)


def calculate_self_improvement_hardening_score(state=None):
    if state is None:
        state = load_hardening_state()

    self_improvement = state.get("self_improvement", {})

    signals = [
        "test_matrix",
        "module_health_matrix",
        "repair_planner",
        "release_check_full",
        "impact_reports",
        "safe_tests_passing"
    ]

    score = 2

    for signal in signals:
        if self_improvement.get(signal):
            score += 1

    return min(8, score)


def calculate_presence_hardening_score(state=None):
    if state is None:
        state = load_hardening_state()

    presence = state.get("presence", {})

    score = 5

    if presence.get("world_integrated"):
        score += 1
    if presence.get("avatar_integrated"):
        score += 1
    if presence.get("voice_integrated"):
        score += 1
    if presence.get("cockpit_integrated"):
        score += 1

    return min(9, score)


def apply_v118_hardening_scores(companion_state, scores):
    hardening = load_hardening_state()

    voice_score = calculate_voice_hardening_score(hardening)
    cockpit_score = calculate_cockpit_hardening_score(hardening)
    agency_score = calculate_agency_hardening_score(hardening)
    self_score = calculate_self_improvement_hardening_score(hardening)
    presence_score = calculate_presence_hardening_score(hardening)

    scores["Voice"] = max(scores.get("Voice", 0), voice_score)
    scores["Cockpit"] = max(scores.get("Cockpit", 0), cockpit_score)
    scores["Agency"] = max(scores.get("Agency", 0), agency_score)
    scores["Self-improvement"] = max(scores.get("Self-improvement", 0), self_score)
    scores["Presence"] = max(scores.get("Presence", 0), presence_score)

    hardening_report = {
        "created_at": now_timestamp(),
        "voice_score": voice_score,
        "cockpit_score": cockpit_score,
        "agency_score": agency_score,
        "self_improvement_score": self_score,
        "presence_score": presence_score,
        "scores_after": scores
    }

    hardening["last_score_report"] = hardening_report
    save_hardening_state(hardening)

    return scores


def hardening_blockers():
    state = load_hardening_state()
    blockers = []

    if calculate_voice_hardening_score(state) < 7:
        blockers.append("Voice hardening is below 7/10.")
    if calculate_cockpit_hardening_score(state) < 7:
        blockers.append("Cockpit hardening is below 7/10.")
    if calculate_agency_hardening_score(state) < 7:
        blockers.append("Agency hardening is below 7/10.")
    if calculate_self_improvement_hardening_score(state) < 7:
        blockers.append("Self-improvement hardening is below 7/10.")

    return blockers


def hardening_status_data():
    state = load_hardening_state()

    return {
        "created_at": now_timestamp(),
        "voice_score": calculate_voice_hardening_score(state),
        "cockpit_score": calculate_cockpit_hardening_score(state),
        "agency_score": calculate_agency_hardening_score(state),
        "self_improvement_score": calculate_self_improvement_hardening_score(state),
        "presence_score": calculate_presence_hardening_score(state),
        "blockers": hardening_blockers(),
        "state": state
    }


def show_hardening_status():
    data = hardening_status_data()

    print("\n=== SEED v1.18 V2 HARDENING STATUS ===")
    print(f"Voice: {data['voice_score']} / 8")
    print(f"Cockpit: {data['cockpit_score']} / 8")
    print(f"Agency: {data['agency_score']} / 8")
    print(f"Self-improvement: {data['self_improvement_score']} / 8")
    print(f"Presence: {data['presence_score']} / 9")

    print("\nBlockers:")
    if not data["blockers"]:
        print("- none")
    else:
        for blocker in data["blockers"]:
            print(f"- {blocker}")

    print("\nLast score report:")
    print(json.dumps(data["state"].get("last_score_report"), indent=4))


def get_hardening_context_for_prompt():
    data = hardening_status_data()

    text = "=== V2 HARDENING CONTEXT ===\n"
    text += f"Voice hardening: {data['voice_score']} / 8\n"
    text += f"Cockpit hardening: {data['cockpit_score']} / 8\n"
    text += f"Agency hardening: {data['agency_score']} / 8\n"
    text += f"Self-improvement hardening: {data['self_improvement_score']} / 8\n"
    text += f"Presence hardening: {data['presence_score']} / 9\n"

    text += "\nBlockers:\n"
    if not data["blockers"]:
        text += "- none\n"
    else:
        for blocker in data["blockers"]:
            text += f"- {blocker}\n"

    text += """
Hardening rule:
v1.18.0 should raise v2 readiness through actual testable systems:
interactive cockpit, voice session tests, agency approval queue/simulator, and self-improvement health matrix.
Do not fake v2 readiness.
"""

    return text


if __name__ == "__main__":
    initialize_hardening_state()
    show_hardening_status()
