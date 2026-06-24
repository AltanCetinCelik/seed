import json
from datetime import datetime
from pathlib import Path


try:
    from seed_config import SEED_COMMAND_MEMORY_FILE
except Exception:
    SEED_COMMAND_MEMORY_FILE = "seed_command_memory.json"


DEFAULT_COMMANDS = {
    "release_check_stack": [
        "/v29-check",
        "/v28-check",
        "/v27-check",
        "/v26-check",
        "/v25-check",
        "/v24-check",
        "/v23-check",
        "/v22-check",
        "/v2-check",
        "/release-check",
        "/fake-sentience-scan"
    ],
    "mission_control": [
        "/mission-control",
        "/repo-doctor",
        "/voice-ux",
        "/executor-registry",
        "/aider-status"
    ],
    "agent_work": [
        "/agent-operator",
        "/agent-run-create",
        "/agent-run-list",
        "/executor-plan",
        "/aider-plan"
    ],
    "voice_debug": [
        "/voice-ux",
        "/voice-transcript-add",
        "/voice-transcripts",
        "/voice-upgrade-plan"
    ]
}


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def load_command_memory():
    path = Path(SEED_COMMAND_MEMORY_FILE)
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception:
            pass

    data = {
        "created_at": now_timestamp(),
        "version": "v2.9.0",
        "commands": DEFAULT_COMMANDS,
        "recent": []
    }
    save_command_memory(data)
    return data


def save_command_memory(data):
    with open(SEED_COMMAND_MEMORY_FILE, "w") as file:
        json.dump(data, file, indent=4)


def remember_command(command, note=None):
    data = load_command_memory()
    data.setdefault("recent", []).append({
        "created_at": now_timestamp(),
        "command": command,
        "note": note
    })
    data["recent"] = data["recent"][-100:]
    save_command_memory(data)
    return data


def suggest_commands(topic=""):
    data = load_command_memory()
    lowered = (topic or "").lower()

    if "release" in lowered or "gate" in lowered:
        key = "release_check_stack"
    elif "agent" in lowered or "aider" in lowered or "executor" in lowered:
        key = "agent_work"
    elif "voice" in lowered or "transcript" in lowered:
        key = "voice_debug"
    else:
        key = "mission_control"

    return {
        "ok": True,
        "topic": topic,
        "selected_group": key,
        "commands": data["commands"].get(key, []),
        "all_groups": data["commands"]
    }


def command_memory_context(user_prompt=""):
    suggestions = suggest_commands(user_prompt)
    return (
        "=== SEED COMMAND MEMORY ===\n"
        f"Suggested command group: {suggestions['selected_group']}\n"
        + "\n".join(f"- {cmd}" for cmd in suggestions["commands"][:8])
    )


def show_command_memory():
    print(json.dumps(load_command_memory(), indent=4))


def show_command_suggestions():
    topic = input("Topic: ").strip()
    print(json.dumps(suggest_commands(topic), indent=4))


if __name__ == "__main__":
    show_command_memory()
