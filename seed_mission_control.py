import json
from datetime import datetime
from pathlib import Path


try:
    from seed_config import SEED_MISSION_CONTROL_STATE_FILE
except Exception:
    SEED_MISSION_CONTROL_STATE_FILE = "seed_mission_control_state.json"


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def safe_call(label, fn):
    try:
        return {"ok": True, "label": label, "data": fn()}
    except Exception as error:
        return {"ok": False, "label": label, "error": str(error)}


def mission_control_snapshot():
    snapshot = {
        "created_at": now_timestamp(),
        "version": "v2.9.0",
        "title": "Seed Mission Control",
        "ok": True,
        "sections": {},
        "health": {},
        "next_actions": []
    }

    snapshot["sections"]["git"] = safe_call(
        "git",
        lambda: __import__("seed_skill_kernel", fromlist=["run_skill"]).run_skill("git", "status")
    )

    snapshot["sections"]["repo"] = safe_call(
        "repo",
        lambda: __import__("seed_repo_doctor", fromlist=["run_repo_doctor"]).run_repo_doctor()
    )

    snapshot["sections"]["skills"] = safe_call(
        "skills",
        lambda: __import__("seed_skill_kernel", fromlist=["skill_status_data"]).skill_status_data()
    )

    snapshot["sections"]["agents"] = safe_call(
        "agents",
        lambda: __import__("seed_agent_run_lifecycle", fromlist=["list_agent_runs"]).list_agent_runs(limit=8)
    )

    snapshot["sections"]["executors"] = safe_call(
        "executors",
        lambda: __import__("seed_external_executor_bridge", fromlist=["detect_executors"]).detect_executors()
    )

    snapshot["sections"]["aider"] = safe_call(
        "aider",
        lambda: __import__("seed_aider_bridge", fromlist=["detect_aider"]).detect_aider()
    )

    snapshot["sections"]["voice_plan"] = safe_call(
        "voice_plan",
        lambda: __import__("seed_voice_upgrade_planner", fromlist=["build_voice_upgrade_plan"]).build_voice_upgrade_plan()
    )

    snapshot["health"] = {
        "git_known": snapshot["sections"]["git"]["ok"],
        "repo_doctor_known": snapshot["sections"]["repo"]["ok"],
        "skills_known": snapshot["sections"]["skills"]["ok"],
        "agents_known": snapshot["sections"]["agents"]["ok"],
        "executors_known": snapshot["sections"]["executors"]["ok"],
        "aider_known": snapshot["sections"]["aider"]["ok"],
        "voice_plan_known": snapshot["sections"]["voice_plan"]["ok"]
    }

    git_data = snapshot["sections"]["git"].get("data", {}).get("data", {})
    if git_data.get("dirty"):
        snapshot["next_actions"].append("Working tree is dirty. Commit/checkpoint before bigger executor work.")

    aider_data = snapshot["sections"]["aider"].get("data", {})
    if not aider_data.get("aider_available"):
        snapshot["next_actions"].append("Aider is not installed. Use /aider-install-plan before real Aider unlock.")

    snapshot["next_actions"].append("Use /release-orchestrate before every big commit.")
    snapshot["next_actions"].append("Use /self-repair-plan if an import or command breaks.")
    snapshot["next_actions"].append("Use /voice-ux to inspect voice reliability next steps.")

    with open(SEED_MISSION_CONTROL_STATE_FILE, "w") as file:
        json.dump(snapshot, file, indent=4)

    return snapshot


def mission_control_context(user_prompt=""):
    snap = mission_control_snapshot()
    lines = ["=== SEED v2.9 MISSION CONTROL ==="]
    lines.append(f"OK: {snap.get('ok')}")
    lines.append("Health:")
    for key, value in snap.get("health", {}).items():
        lines.append(f"- {key}: {value}")
    lines.append("Next actions:")
    for item in snap.get("next_actions", [])[:6]:
        lines.append(f"- {item}")
    return "\n".join(lines)


def show_mission_control():
    snap = mission_control_snapshot()

    print("\n=== SEED MISSION CONTROL ===")
    print(f"Version: {snap['version']}")
    print("\nHealth:")
    for key, value in snap["health"].items():
        print(f"- {key}: {value}")

    print("\nNext actions:")
    for item in snap["next_actions"]:
        print(f"- {item}")


if __name__ == "__main__":
    show_mission_control()
