import json
from datetime import datetime


try:
    from seed_config import SEED_VOICE_ONE_SHOT_HISTORY_FILE
except Exception:
    SEED_VOICE_ONE_SHOT_HISTORY_FILE = "seed_voice_one_shot_history.jsonl"


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def classify(text):
    lowered = (text or "").lower()
    if "control plane" in lowered or "dashboard" in lowered:
        return "control_plane"
    if "gate" in lowered or "release" in lowered:
        return "release"
    if "voice" in lowered:
        return "voice"
    if "agent" in lowered or "aider" in lowered:
        return "agent_executor"
    if "repo" in lowered or "git" in lowered:
        return "repo_skill"
    return "chat"


def one_shot_response(text):
    intent = classify(text)
    command = None

    if intent == "control_plane":
        command = "/control-plane-open"
    elif intent == "release":
        command = "/gate-matrix"
    elif intent == "voice":
        command = "/voice-ux"
    elif intent == "agent_executor":
        command = "/agent-operator"
    elif intent == "repo_skill":
        command = "/repo-doctor"

    item = {
        "created_at": now_timestamp(),
        "version": "v3.5.0",
        "transcript": text,
        "intent": intent,
        "suggested_command": command,
        "executed": False,
        "note": "One-shot planner does not auto-execute commands."
    }

    with open(SEED_VOICE_ONE_SHOT_HISTORY_FILE, "a") as file:
        file.write(json.dumps(item) + "\n")

    return item


def show_voice_one_shot():
    text = input("One-shot transcript/text: ").strip()
    result = one_shot_response(text)
    print(json.dumps(result, indent=4))


def voice_one_shot_context(user_prompt=""):
    result = one_shot_response(user_prompt or "")
    return (
        "=== SEED VOICE ONE-SHOT ===\n"
        f"Intent: {result['intent']}\n"
        f"Suggested command: {result['suggested_command']}\n"
        "No auto-execution.\n"
    )


if __name__ == "__main__":
    show_voice_one_shot()
