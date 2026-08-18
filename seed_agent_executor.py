import json
import os
import subprocess
from datetime import datetime
from pathlib import Path


try:
    from seed_config import SEED_AGENT_RUNS_DIR
except Exception:
    SEED_AGENT_RUNS_DIR = "seed_agent_runs"


try:
    from seed_agent_tool_profiles import find_profile, agent_tool_profiles_data
    PROFILES_AVAILABLE = True
except Exception:
    PROFILES_AVAILABLE = False


try:
    from seed_agency_hardening import request_action_approval, simulate_action
    AGENCY_AVAILABLE = True
except Exception:
    AGENCY_AVAILABLE = False


try:
    from seed_trace_engine import append_trace
    TRACE_AVAILABLE = True
except Exception:
    TRACE_AVAILABLE = False


SAFE_DIAGNOSTIC_COMMANDS = [
    ["git", "status", "--short"],
    ["git", "diff", "--stat"],
    ["python", "-m", "py_compile"],
    ["python", "seed_v2_release_gate.py"],
    ["python", "seed_integration_gate.py"],
    ["python", "seed_v2_stable_release.py"]
]


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def ensure_runs_dir():
    path = Path(SEED_AGENT_RUNS_DIR)
    path.mkdir(exist_ok=True)
    return path


def safe_filename(text):
    return "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in text)[:80]


def create_agent_run(task, capability, tool_id=None):
    runs = ensure_runs_dir()
    run_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{safe_filename(capability)}"
    path = runs / run_id
    path.mkdir(exist_ok=True)

    data = {
        "created_at": now_timestamp(),
        "run_id": run_id,
        "task": task,
        "capability": capability,
        "tool_id": tool_id,
        "status": "planned",
        "approval_status": "not_requested",
        "commands": [],
        "notes": [],
        "results": []
    }

    (path / "plan.json").write_text(json.dumps(data, indent=4))
    return data, path


def is_safe_diagnostic(command):
    if isinstance(command, str):
        parts = command.split()
    else:
        parts = list(command)

    if not parts:
        return False

    if parts[:3] == ["git", "status", "--short"]:
        return True
    if parts[:3] == ["git", "diff", "--stat"]:
        return True
    if parts[:3] == ["python", "-m", "py_compile"]:
        return True
    if parts == ["python", "seed_v2_release_gate.py"]:
        return True
    if parts == ["python", "seed_integration_gate.py"]:
        return True
    if parts == ["python", "seed_v2_stable_release.py"]:
        return True

    return False


def run_safe_diagnostic(command, cwd=None):
    if isinstance(command, str):
        parts = command.split()
    else:
        parts = list(command)

    if not is_safe_diagnostic(parts):
        return {
            "ok": False,
            "error": "Command is not in safe diagnostic allowlist.",
            "command": parts
        }

    result = subprocess.run(
        parts,
        cwd=cwd,
        capture_output=True,
        text=True
    )

    return {
        "ok": result.returncode == 0,
        "command": parts,
        "returncode": result.returncode,
        "stdout": result.stdout[-4000:],
        "stderr": result.stderr[-4000:]
    }


def propose_agent_execution(task, capability, tool_id=None):
    profile = find_profile(tool_id) if tool_id and PROFILES_AVAILABLE else None
    run, path = create_agent_run(task, capability, tool_id=tool_id)

    profile_risk = profile.get("risk") if profile else "unknown"
    profile_available = profile.get("available") if profile else False

    proposal = {
        "created_at": now_timestamp(),
        "task": task,
        "capability": capability,
        "tool_id": tool_id,
        "profile": profile,
        "profile_available": profile_available,
        "risk": profile_risk,
        "run_dir": str(path),
        "approval_required": True,
        "safe_plan": [
            "Create backup or git branch.",
            "Prepare exact command/tool plan.",
            "Ask User for approval.",
            "Run in repo sandbox only.",
            "Run tests.",
            "Show diff/results.",
            "Rollback if needed."
        ],
        "execution_status": "not_executed"
    }

    (path / "proposal.json").write_text(json.dumps(proposal, indent=4))

    if AGENCY_AVAILABLE:
        try:
            request = request_action_approval(
                action_text=f"Run agent tool {tool_id or 'unknown'} for task: {task}",
                tool_id=tool_id,
                reason="Agent Arsenal Activation requires explicit approval before file/shell/browser execution.",
                requested_by="agent_executor"
            )
            proposal["approval_request"] = request
            run["approval_status"] = "queued"
        except Exception as error:
            proposal["approval_error"] = str(error)

    if TRACE_AVAILABLE:
        try:
            append_trace(
                trace_type="proposal_trace",
                title="Agent execution proposed",
                summary=json.dumps(proposal, indent=2)[:3000],
                sources=["agent_executor", "agent_tool_profiles", "agency_hardening"],
                decision="approval_queued",
                risk=profile_risk
            )
        except Exception:
            pass

    (path / "proposal.json").write_text(json.dumps(proposal, indent=4))
    (path / "plan.json").write_text(json.dumps(run, indent=4))

    return proposal


def show_agent_diagnostic():
    print("\n=== AGENT DIAGNOSTIC ===")
    commands = [
        ["git", "status", "--short"],
        ["git", "diff", "--stat"],
        ["python", "seed_v2_release_gate.py"],
        ["python", "seed_integration_gate.py"],
        ["python", "seed_v2_stable_release.py"]
    ]

    for command in commands:
        print("\n$", " ".join(command))
        result = run_safe_diagnostic(command)
        print("OK:", result.get("ok"))
        if result.get("stdout"):
            print(result["stdout"][:1500])
        if result.get("stderr"):
            print(result["stderr"][:1500])


if __name__ == "__main__":
    show_agent_diagnostic()
