import hashlib
import json
import shutil
import uuid
from datetime import datetime
from pathlib import Path


try:
    from seed_config import (
        SEED_AGENT_RUN_LIFECYCLE_DIR,
        SEED_AGENT_RUN_STATE_FILE,
        SEED_AGENT_RUN_HISTORY_FILE
    )
except Exception:
    SEED_AGENT_RUN_LIFECYCLE_DIR = "seed_agent_runs"
    SEED_AGENT_RUN_STATE_FILE = "seed_agent_run_state.json"
    SEED_AGENT_RUN_HISTORY_FILE = "seed_agent_run_history.jsonl"


RUN_DIR = Path(SEED_AGENT_RUN_LIFECYCLE_DIR)


AGENT_TOOL_CANDIDATES = {
    "aider": ["aider"],
    "openhands": ["openhands"],
    "swe-agent": ["sweagent", "swe-agent"],
    "browser-use": ["browser-use"],
    "mcp": ["npx", "uvx"],
    "python": ["python"],
    "git": ["git"]
}


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


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
    return slug[:max_len] or "agent-run"


def append_history(item):
    try:
        with open(SEED_AGENT_RUN_HISTORY_FILE, "a") as file:
            file.write(json.dumps(item) + "\n")
    except Exception:
        pass


def save_state(item):
    try:
        with open(SEED_AGENT_RUN_STATE_FILE, "w") as file:
            json.dump(item, file, indent=4)
    except Exception:
        pass


def detect_agent_tools():
    detected = {}

    for tool_name, commands in AGENT_TOOL_CANDIDATES.items():
        found = []
        for command in commands:
            path = shutil.which(command)
            if path:
                found.append({
                    "command": command,
                    "path": path
                })

        detected[tool_name] = {
            "available": bool(found),
            "matches": found
        }

    return detected


def load_run(run_id):
    path = RUN_DIR / run_id / "agent_run.json"
    if not path.exists():
        raise FileNotFoundError(f"Agent run not found: {run_id}")
    return json.loads(path.read_text())


def save_run(run):
    run_id = run["run_id"]
    run_dir = RUN_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    path = run_dir / "agent_run.json"
    path.write_text(json.dumps(run, indent=4))
    save_state(run)
    append_history({
        "created_at": now_timestamp(),
        "event": "save_run",
        "run_id": run_id,
        "status": run.get("status")
    })
    return path


def get_git_snapshot():
    snapshot = {
        "git_status": None,
        "git_diff_stat": None,
        "repo_summary": None
    }

    try:
        from seed_skill_kernel import run_skill
        snapshot["git_status"] = run_skill("git", "status")
        snapshot["git_diff_stat"] = run_skill("git", "diff_stat")
        snapshot["repo_summary"] = run_skill("repo", "summary")
    except Exception as error:
        snapshot["error"] = str(error)

    return snapshot


def choose_agent_type(task):
    lowered = (task or "").lower()

    if any(x in lowered for x in ["browser", "website", "web", "search online"]):
        return "browser"
    if any(x in lowered for x in ["mcp", "tool server", "connector"]):
        return "mcp"
    if any(x in lowered for x in ["code", "bug", "fix", "repo", "implement", "python"]):
        return "coding"
    return "general"


def create_agent_run(task, requested_agent=None, mode=None):
    RUN_DIR.mkdir(exist_ok=True)

    mode = mode or choose_agent_type(task)
    slug = safe_slug(task)
    short_id = datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + slug
    run_id = short_id

    token_source = f"{run_id}:{uuid.uuid4().hex}"
    approval_token = hashlib.sha256(token_source.encode("utf-8")).hexdigest()[:12]

    run_dir = RUN_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    tools = detect_agent_tools()
    git_snapshot = get_git_snapshot()

    run = {
        "created_at": now_timestamp(),
        "updated_at": now_timestamp(),
        "version": "v2.6.0",
        "run_id": run_id,
        "task": task,
        "mode": mode,
        "requested_agent": requested_agent,
        "status": "prepared",
        "approval": {
            "required": True,
            "approved": False,
            "approval_token": approval_token,
            "approved_at": None
        },
        "execution_policy": {
            "supervised_only": True,
            "no_auto_edit": True,
            "no_auto_commit": True,
            "no_external_agent_by_default": True,
            "safe_internal_only": True
        },
        "detected_tools": tools,
        "git_snapshot": git_snapshot,
        "safe_runbook": [
            "Review the task and run metadata.",
            "Confirm the target repo.",
            "Approve with the displayed approval token.",
            "Run supervised execution.",
            "Execution may run safe internal diagnostics and prepare agent files.",
            "External agents remain locked unless Altan explicitly asks for that later.",
            "Show results and verification.",
            "No auto-commit."
        ],
        "outputs": {}
    }

    save_run(run)

    task_file = run_dir / "TASK.md"
    task_file.write_text(
        f"# Seed Agent Run\n\n"
        f"Run ID: {run_id}\n"
        f"Mode: {mode}\n"
        f"Task:\n\n{task}\n\n"
        f"Approval token: {approval_token}\n\n"
        f"Policy:\n"
        f"- supervised only\n"
        f"- no auto-edit\n"
        f"- no auto-commit\n"
        f"- no external agent by default\n"
    )

    return {
        "ok": True,
        "run_id": run_id,
        "run_dir": str(run_dir),
        "task_file": str(task_file),
        "approval_token": approval_token,
        "status": run["status"],
        "mode": mode,
        "detected_tools": tools
    }


def list_agent_runs(limit=30):
    RUN_DIR.mkdir(exist_ok=True)
    runs = []

    for path in sorted(RUN_DIR.iterdir(), reverse=True):
        if not path.is_dir():
            continue

        run_file = path / "agent_run.json"
        if not run_file.exists():
            continue

        try:
            run = json.loads(run_file.read_text())
        except Exception:
            continue

        runs.append({
            "run_id": run.get("run_id"),
            "status": run.get("status"),
            "mode": run.get("mode"),
            "task": run.get("task"),
            "approved": run.get("approval", {}).get("approved"),
            "created_at": run.get("created_at")
        })

        if len(runs) >= limit:
            break

    return {
        "ok": True,
        "runs": runs,
        "count": len(runs)
    }


def approve_agent_run(run_id, token):
    run = load_run(run_id)
    expected = run.get("approval", {}).get("approval_token")

    if token != expected:
        return {
            "ok": False,
            "error": "Approval token does not match.",
            "run_id": run_id
        }

    run["approval"]["approved"] = True
    run["approval"]["approved_at"] = now_timestamp()
    run["status"] = "approved"
    run["updated_at"] = now_timestamp()
    save_run(run)

    return {
        "ok": True,
        "run_id": run_id,
        "status": "approved"
    }


def execute_supervised_agent_run(run_id):
    run = load_run(run_id)

    if not run.get("approval", {}).get("approved"):
        return {
            "ok": False,
            "run_id": run_id,
            "status": run.get("status"),
            "error": "Run is not approved. Use approval token first."
        }

    results = {}

    try:
        from seed_skill_kernel import run_skill
        results["git_status_before"] = run_skill("git", "status")
        results["repo_summary"] = run_skill("repo", "summary")
        results["safe_diagnostic"] = run_skill("safe_shell", "diagnostic")
        results["git_diff_after"] = run_skill("git", "diff_stat")
    except Exception as error:
        results["error"] = str(error)

    ok = (
        results.get("git_status_before", {}).get("ok") is True
        and results.get("repo_summary", {}).get("ok") is True
        and results.get("safe_diagnostic", {}).get("ok") is True
    )

    run["status"] = "executed_safe_internal" if ok else "execution_failed"
    run["updated_at"] = now_timestamp()
    run["outputs"]["supervised_execution"] = results
    run["outputs"]["external_agent_locked"] = True
    run["outputs"]["reason"] = "v2.6 executes safe internal verification only. External Aider/OpenHands/browser-use execution remains approval-gated for a later layer."

    run_dir = RUN_DIR / run_id
    result_file = run_dir / "supervised_execution_result.json"
    result_file.write_text(json.dumps(results, indent=4))

    save_run(run)

    return {
        "ok": ok,
        "run_id": run_id,
        "status": run["status"],
        "result_file": str(result_file),
        "external_agent_locked": True,
        "results": results
    }


def show_agent_tools():
    tools = detect_agent_tools()

    print("\n=== SEED AGENT TOOL DETECTION ===")
    for tool, data in tools.items():
        print(f"- {tool}: available={data['available']}")
        for match in data["matches"]:
            print(f"  {match['command']} → {match['path']}")

    return tools


def show_agent_run_create():
    task = input("Agent task: ").strip()
    if not task:
        print("No task provided.")
        return

    result = create_agent_run(task)
    print(json.dumps(result, indent=4))


def show_agent_run_list():
    print(json.dumps(list_agent_runs(), indent=4))


def show_agent_run_show():
    run_id = input("Run ID: ").strip()
    try:
        print(json.dumps(load_run(run_id), indent=4))
    except Exception as error:
        print(f"Could not load run: {error}")


def show_agent_run_approve():
    run_id = input("Run ID: ").strip()
    token = input("Approval token: ").strip()
    print(json.dumps(approve_agent_run(run_id, token), indent=4))


def show_agent_run_execute():
    run_id = input("Run ID: ").strip()
    print(json.dumps(execute_supervised_agent_run(run_id), indent=4))


def agent_execution_context(user_prompt=""):
    return (
        "=== SEED v2.6 SUPERVISED AGENT EXECUTION ===\n"
        "Seed can create agent runs, snapshot repo state, require approval tokens, and execute safe internal verification.\n"
        "External agents like Aider/OpenHands/browser-use are detected but locked by default.\n"
        "Rules: supervised only, no auto-edit, no auto-commit, no blind installs, approval required.\n"
    )


if __name__ == "__main__":
    show_agent_tools()
