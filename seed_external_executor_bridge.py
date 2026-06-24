import json
import shutil
from datetime import datetime
from pathlib import Path


try:
    from seed_config import (
        SEED_EXECUTOR_BRIDGE_STATE_FILE,
        SEED_EXECUTOR_BRIDGE_HISTORY_FILE,
        SEED_AGENT_RUN_LIFECYCLE_DIR
    )
except Exception:
    SEED_EXECUTOR_BRIDGE_STATE_FILE = "seed_executor_bridge_state.json"
    SEED_EXECUTOR_BRIDGE_HISTORY_FILE = "seed_executor_bridge_history.jsonl"
    SEED_AGENT_RUN_LIFECYCLE_DIR = "seed_agent_runs"


EXECUTORS = {
    "aider": {
        "commands": ["aider"],
        "kind": "coding_agent",
        "risk": "file_write_and_shell",
        "best_for": ["small repo patches", "code edits", "tests", "diffs"],
        "locked_reason": "Aider can edit files. Must be supervised and approved."
    },
    "openhands": {
        "commands": ["openhands"],
        "kind": "coding_agent",
        "risk": "file_write_shell_browser",
        "best_for": ["larger software tasks", "multi-step repo work"],
        "locked_reason": "OpenHands can operate broadly. Must be sandboxed later."
    },
    "swe-agent": {
        "commands": ["sweagent", "swe-agent"],
        "kind": "coding_agent",
        "risk": "file_write_and_shell",
        "best_for": ["issue-style bugfix tasks"],
        "locked_reason": "SWE-agent execution needs benchmark-style sandbox first."
    },
    "browser-use": {
        "commands": ["browser-use"],
        "kind": "browser_agent",
        "risk": "external_web_action",
        "best_for": ["browser automation", "web tasks"],
        "locked_reason": "Browser automation may touch accounts/forms. Approval required."
    },
    "mcp": {
        "commands": ["npx", "uvx"],
        "kind": "tool_protocol",
        "risk": "external_tool_access",
        "best_for": ["filesystem/git/browser/tool servers"],
        "locked_reason": "MCP servers require explicit allowlist and config."
    },
    "python": {
        "commands": ["python"],
        "kind": "internal_runtime",
        "risk": "diagnostic",
        "best_for": ["safe internal diagnostics"],
        "locked_reason": None
    },
    "git": {
        "commands": ["git"],
        "kind": "repo_runtime",
        "risk": "read_only_repo",
        "best_for": ["status", "diff", "logs"],
        "locked_reason": None
    }
}


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def save_json(path, data):
    with open(path, "w") as file:
        json.dump(data, file, indent=4)


def append_history(item):
    try:
        with open(SEED_EXECUTOR_BRIDGE_HISTORY_FILE, "a") as file:
            file.write(json.dumps(item) + "\n")
    except Exception:
        pass


def detect_executors():
    registry = {}

    for executor_id, spec in EXECUTORS.items():
        matches = []
        for command in spec["commands"]:
            path = shutil.which(command)
            if path:
                matches.append({
                    "command": command,
                    "path": path
                })

        registry[executor_id] = {
            "id": executor_id,
            "available": bool(matches),
            "matches": matches,
            "kind": spec["kind"],
            "risk": spec["risk"],
            "best_for": spec["best_for"],
            "locked": spec["locked_reason"] is not None,
            "locked_reason": spec["locked_reason"]
        }

    state = {
        "created_at": now_timestamp(),
        "version": "v2.7.0",
        "registry": registry,
        "policy": {
            "no_auto_install": True,
            "no_external_run_by_default": True,
            "manual_commands_only": True,
            "approval_required": True
        }
    }

    save_json(SEED_EXECUTOR_BRIDGE_STATE_FILE, state)
    append_history({
        "created_at": now_timestamp(),
        "event": "detect_executors",
        "available": [k for k, v in registry.items() if v["available"]]
    })

    return state


def choose_executor(task):
    lowered = (task or "").lower()
    registry = detect_executors()["registry"]

    if any(x in lowered for x in ["browser", "website", "web page", "form"]):
        preferred = ["browser-use", "mcp", "python"]
    elif any(x in lowered for x in ["mcp", "tool server", "connector"]):
        preferred = ["mcp", "python"]
    elif any(x in lowered for x in ["code", "bug", "repo", "implement", "patch", "fix"]):
        preferred = ["aider", "openhands", "swe-agent", "python"]
    else:
        preferred = ["python", "git", "mcp"]

    for executor_id in preferred:
        if registry.get(executor_id, {}).get("available"):
            return executor_id

    return preferred[0]


def safe_slug(text, max_len=70):
    out = []
    for ch in (text or "").lower():
        if ch.isalnum():
            out.append(ch)
        elif ch in " _-":
            out.append("-")
    slug = "".join(out).strip("-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug[:max_len] or "executor-plan"


def build_manual_command(executor_id, task):
    if executor_id == "aider":
        return [
            "# Manual only. Review first.",
            "# Suggested after installing/configuring Aider yourself:",
            f'aider --message "{task.replace(chr(34), chr(39))}"'
        ]

    if executor_id == "openhands":
        return [
            "# Manual only. OpenHands execution remains locked.",
            "# Use OpenHands UI/CLI only after creating a sandbox branch and backup."
        ]

    if executor_id == "browser-use":
        return [
            "# Manual only. Browser-use execution remains locked.",
            "# Browser tasks must avoid login/account/send/purchase actions unless explicitly approved."
        ]

    if executor_id == "mcp":
        return [
            "# Manual only. MCP server selection required.",
            "# Example discovery command only:",
            "npx --version"
        ]

    if executor_id == "python":
        return [
            "# Safe internal Python diagnostics only:",
            "python seed_v27_executor_gate.py"
        ]

    if executor_id == "git":
        return [
            "git status --short",
            "git diff --stat"
        ]

    return ["# No command generated."]


def create_executor_plan(task, executor_id=None):
    registry_state = detect_executors()
    registry = registry_state["registry"]
    executor_id = executor_id or choose_executor(task)

    run_root = Path(SEED_AGENT_RUN_LIFECYCLE_DIR)
    run_root.mkdir(exist_ok=True)

    plan_id = datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + safe_slug(task)
    plan_dir = run_root / plan_id
    plan_dir.mkdir(parents=True, exist_ok=True)

    executor = registry.get(executor_id, {
        "id": executor_id,
        "available": False,
        "locked": True,
        "locked_reason": "Unknown executor."
    })

    plan = {
        "created_at": now_timestamp(),
        "version": "v2.7.0",
        "plan_id": plan_id,
        "task": task,
        "executor_id": executor_id,
        "executor": executor,
        "status": "planned_manual_only",
        "can_execute_now": False,
        "why_not_execute": "v2.7 prepares executor bridge plans only. External execution unlocks one executor at a time after hardening.",
        "manual_command_preview": build_manual_command(executor_id, task),
        "safe_order": [
            "Review plan",
            "Check git status",
            "Create backup/branch",
            "Install/configure executor manually if missing",
            "Approve exact command",
            "Run supervised",
            "Run tests",
            "Review diff",
            "Commit only after approval"
        ]
    }

    plan_file = plan_dir / "executor_plan.json"
    plan_file.write_text(json.dumps(plan, indent=4))

    readme = plan_dir / "EXECUTOR_PLAN.md"
    readme.write_text(
        f"# Seed v2.7 Executor Plan\n\n"
        f"Task: {task}\n\n"
        f"Executor: {executor_id}\n\n"
        f"Status: manual plan only\n\n"
        f"Commands:\n\n"
        + "\n".join(f"    {line}" for line in plan["manual_command_preview"])
        + "\n"
    )

    append_history({
        "created_at": now_timestamp(),
        "event": "create_executor_plan",
        "plan_id": plan_id,
        "executor_id": executor_id,
        "task": task
    })

    return {
        "ok": True,
        "plan_id": plan_id,
        "plan_dir": str(plan_dir),
        "plan_file": str(plan_file),
        "executor_id": executor_id,
        "available": executor.get("available"),
        "locked": executor.get("locked"),
        "manual_only": True
    }


def executor_bridge_context(user_prompt=""):
    state = detect_executors()
    available = [k for k, v in state["registry"].items() if v["available"]]

    return (
        "=== SEED v2.7 EXECUTOR BRIDGE ===\n"
        f"Available executors/tools: {', '.join(available) or 'none'}\n"
        "External executor execution is locked by default.\n"
        "Seed can create executor plans and manual command previews.\n"
        "No blind installs, no auto-edit, no auto-commit.\n"
    )


def show_executor_registry():
    state = detect_executors()

    print("\n=== SEED EXTERNAL EXECUTOR REGISTRY ===")
    for key, value in state["registry"].items():
        print(f"- {key}: available={value['available']} locked={value['locked']} risk={value['risk']}")
        for match in value["matches"]:
            print(f"  {match['command']} → {match['path']}")


def show_executor_plan():
    task = input("Executor task: ").strip()
    executor_id = input("Executor id or blank for auto: ").strip() or None
    result = create_executor_plan(task, executor_id=executor_id)
    print(json.dumps(result, indent=4))


if __name__ == "__main__":
    show_executor_registry()
