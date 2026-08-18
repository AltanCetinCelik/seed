import json
import subprocess
from datetime import datetime


try:
    from seed_config import SEED_CODING_GATEWAY_STATE_FILE
except Exception:
    SEED_CODING_GATEWAY_STATE_FILE = "seed_coding_gateway_state.json"


try:
    from seed_agent_tool_profiles import agent_tool_profiles_data
except Exception:
    agent_tool_profiles_data = None


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def safe_git_status():
    result = subprocess.run(["git", "status", "--short"], capture_output=True, text=True)
    return {
        "ok": result.returncode == 0,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "dirty": bool(result.stdout.strip())
    }


def safe_git_diff_stat():
    result = subprocess.run(["git", "diff", "--stat"], capture_output=True, text=True)
    return {
        "ok": result.returncode == 0,
        "stdout": result.stdout,
        "stderr": result.stderr
    }


def coding_gateway_data():
    profiles = agent_tool_profiles_data(refresh=True) if agent_tool_profiles_data else {"profiles": []}
    coding = [
        p for p in profiles.get("profiles", [])
        if p.get("kind") in ["coding_agent", "coding_assistant", "test_runner", "repo_control"]
    ]

    data = {
        "created_at": now_timestamp(),
        "version": "v2.2.0",
        "plan_only_by_default": True,
        "profiles": coding,
        "git_status": safe_git_status(),
        "git_diff_stat": safe_git_diff_stat(),
        "ready_for_planning": True,
        "ready_for_execution": False,
        "execution_reason": "Coding agents can write files/shell. Execution requires explicit approval and sandbox branch."
    }

    with open(SEED_CODING_GATEWAY_STATE_FILE, "w") as file:
        json.dump(data, file, indent=4)

    return data


def build_coding_agent_plan(task):
    data = coding_gateway_data()
    available = [p for p in data["profiles"] if p.get("available")]

    selected = None
    for pref in ["aider", "openhands", "swe_agent", "pytest", "git"]:
        for profile in available:
            if profile.get("id") == pref:
                selected = profile
                break
        if selected:
            break

    if selected is None and data["profiles"]:
        selected = data["profiles"][0]

    return {
        "created_at": now_timestamp(),
        "task": task,
        "selected_tool": selected,
        "available_tools": [p.get("id") for p in available],
        "approval_required": True,
        "execution_status": "plan_only",
        "safe_order": [
            "Check git status",
            "Create backup/branch",
            "Write exact tool command",
            "Ask User for approval",
            "Run coding agent in sandbox",
            "Run tests",
            "Show diff",
            "Ask before commit",
            "Rollback if broken"
        ],
        "git_dirty": data["git_status"]["dirty"]
    }


def show_coding_gateway():
    data = coding_gateway_data()
    print("\n=== CODING AGENT GATEWAY ===")
    print(f"Ready for planning: {data['ready_for_planning']}")
    print(f"Ready for execution: {data['ready_for_execution']}")
    print(f"Git dirty: {data['git_status']['dirty']}")
    print("\nProfiles:")
    for p in data["profiles"]:
        print(f"- {p.get('id')}: available={p.get('available')} risk={p.get('risk')}")


def show_coding_plan():
    task = input("Coding task: ").strip()
    print(json.dumps(build_coding_agent_plan(task), indent=4))


def get_coding_context(task=""):
    plan = build_coding_agent_plan(task or "general coding task")
    return (
        "=== CODING AGENT GATEWAY CONTEXT ===\n"
        f"Selected tool: {plan.get('selected_tool', {}).get('id') if plan.get('selected_tool') else None}\n"
        f"Available tools: {', '.join(plan.get('available_tools', [])) or 'none'}\n"
        f"Git dirty: {plan.get('git_dirty')}\n"
        "Rule: coding agents require approval, sandbox, tests, diff, rollback.\n"
    )


if __name__ == "__main__":
    show_coding_gateway()
