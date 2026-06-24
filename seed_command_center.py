import json
from datetime import datetime


try:
    from seed_config import SEED_COMMAND_CENTER_FILE
except Exception:
    SEED_COMMAND_CENTER_FILE = "seed_command_center.json"


COMMAND_CATALOG = {
    "control_plane": [
        "/control-plane",
        "/control-plane-open",
        "/control-plane-status",
        "/command-center"
    ],
    "mission": [
        "/v20-status",
        "/memory-v2",
        "/voice-runtime",
        "/workflow-graph",
        "/browser-sandbox",
        "/mcp-marketplace",
        "/openhands-sandbox",
        "/project-life",
        "/seed-world",
        "/agent-council",
        "/self-improvement-lab",
        "/multidevice-hub",
        "/aider-review",
        "/operator-goal",
        "/operator-status",
        "/operator-tick",
        "/task-list",
        "/task-create",
        "/task-done",
        "/capability-graph",
        "/capability-route",
        "/policy",
        "/policy-check",
        "/inbox",
        "/inbox-add",
        "/event-bus",
        "/service-status",
        "/service-start",
        "/service-stop",
        "/mcp-client",
        "/workflow-list",
        "/workflow-run",
        "/checkpoint-create",
        "/checkpoint-status",
        "/memory-distill",
        "/aider-patch-flow",
        "/mission-control",
        "/gate-matrix",
        "/runtime-supervisor",
        "/timeline",
        "/app-manifest"
    ],
    "release": [
        "/v20-check",
        "/v50-check",
        "/v40-check",
        "/v36-check",
        "/v35-check",
        "/v30-check",
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
    "voice": [
        "/voice-ux",
        "/voice-transcript-add",
        "/voice-transcripts",
        "/voice-upgrade-plan",
        "/active-voice-check",
        "/voice-command-check"
    ],
    "agents": [
        "/mcp-skill-server",
        "/mcp-manifest",
        "/agent-operator",
        "/agent-tools-real",
        "/agent-run-create",
        "/agent-run-list",
        "/agent-run-show",
        "/agent-run-approve",
        "/agent-run-execute",
        "/executor-registry",
        "/executor-plan"
    ],
    "aider": [
        "/aider-unlock-status",
        "/aider-unlock-plan",
        "/aider-unlock-approve",
        "/aider-unlock-execute",
        "/aider-status",
        "/aider-install-plan",
        "/aider-preflight",
        "/aider-plan"
    ],
    "skills": [
        "/skills",
        "/skill-run",
        "/skill-history",
        "/git-status",
        "/git-diff",
        "/repo-summary",
        "/repo-todos",
        "/repo-doctor",
        "/fs-list",
        "/fs-search"
    ],
    "repair": [
        "/self-repair-plan",
        "/release-orchestrate",
        "/command-suggest"
    ]
}


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def build_command_center():
    data = {
        "created_at": now_timestamp(),
        "version": "v3.0.0",
        "ok": True,
        "groups": COMMAND_CATALOG,
        "total_commands": sum(len(items) for items in COMMAND_CATALOG.values())
    }

    with open(SEED_COMMAND_CENTER_FILE, "w") as file:
        json.dump(data, file, indent=4)

    return data


def suggest_command_group(topic):
    lowered = (topic or "").lower()

    if "control" in lowered or "dashboard" in lowered or "jarvis" in lowered:
        return "control_plane"
    if "release" in lowered or "gate" in lowered or "check" in lowered:
        return "release"
    if "voice" in lowered or "transcript" in lowered:
        return "voice"
    if "agent" in lowered or "executor" in lowered:
        return "agents"
    if "aider" in lowered:
        return "aider"
    if "skill" in lowered or "repo" in lowered or "git" in lowered:
        return "skills"
    if "repair" in lowered or "broken" in lowered:
        return "repair"
    return "mission"


def command_center_context(user_prompt=""):
    group = suggest_command_group(user_prompt)
    data = build_command_center()
    return (
        "=== SEED COMMAND CENTER ===\n"
        f"Suggested group: {group}\n"
        + "\n".join(f"- {cmd}" for cmd in data["groups"][group][:10])
    )


def show_command_center():
    data = build_command_center()

    print("\n=== SEED COMMAND CENTER ===")
    print(f"Total commands: {data['total_commands']}")

    for group, commands in data["groups"].items():
        print(f"\n[{group}]")
        for cmd in commands:
            print(f"- {cmd}")


if __name__ == "__main__":
    show_command_center()
