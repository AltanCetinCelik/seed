import json
import shutil
import subprocess
import uuid
from datetime import datetime
from pathlib import Path


STATE_FILE = Path("seed_aider_cockpit_v31.json")


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def _read_state():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(errors="ignore"))
        except Exception:
            pass
    return {"version": "v45.0.0", "sessions": []}


def _write_state(data):
    STATE_FILE.write_text(json.dumps(data, indent=4))
    return data


def detect_aider():
    return shutil.which("aider") or shutil.which("aider-chat")


def git_diff_stat():
    try:
        proc = subprocess.run(["git", "diff", "--stat"], capture_output=True, text=True, timeout=20)
        return proc.stdout.strip()
    except Exception as error:
        return f"diff-stat-error: {error}"


def git_status_short():
    try:
        proc = subprocess.run(["git", "status", "--short"], capture_output=True, text=True, timeout=20)
        return proc.stdout.strip()
    except Exception as error:
        return f"git-status-error: {error}"




def validate_aider_goal_and_files(goal, target_files):
    errors = []
    warnings = []

    goal = (goal or "").strip()
    target_files = target_files or []

    if not goal:
        errors.append("Patch goal cannot be empty.")

    if goal.startswith("/"):
        errors.append(
            "Patch goal looks like a Seed slash command. "
            "Use /service-start directly in Seed, not inside Aider Cockpit."
        )

    if not target_files:
        errors.append("Target files are required for Aider Cockpit.")

    for file in target_files:
        p = Path(file)
        if not p.exists():
            errors.append(f"Target file does not exist: {file}")
        elif p.is_dir():
            errors.append(f"Target must be a file, not a directory: {file}")

    if len(target_files) > 6:
        warnings.append("Many target files selected. Prefer 1-3 files for safer patches.")

    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings
    }


def create_aider_session(goal, target_files=None, mode="dry_run"):
    target_files = target_files or []

    validation = validate_aider_goal_and_files(goal, target_files)
    if not validation["ok"]:
        return {
            "created_at": now_timestamp(),
            "version": "v45.1.0",
            "ok": False,
            "engine": "Seed Aider Cockpit v31",
            "status": "rejected",
            "goal": goal,
            "target_files": target_files,
            "validation": validation,
            "hint": "Use Aider Cockpit only for file patch goals. Use Seed slash commands directly in chat."
        }
    session_id = uuid.uuid4().hex[:10]
    run_dir = Path("seed_agent_runs") / f"aider_cockpit_{session_id}"
    run_dir.mkdir(parents=True, exist_ok=True)

    approval_phrase = f"APPROVE_AIDER_REAL_{session_id}"

    session = {
        "id": session_id,
        "created_at": now_timestamp(),
        "version": "v45.0.0",
        "engine": "Seed Aider Cockpit v31",
        "goal": goal,
        "target_files": target_files,
        "mode": mode,
        "status": "planned",
        "aider_command": detect_aider(),
        "run_dir": str(run_dir),
        "approval_phrase": approval_phrase,
        "git_status_before": git_status_short(),
        "diff_stat_before": git_diff_stat(),
        "pipeline": [
            "checkpoint",
            "dry-run plan",
            "diff review",
            "tests",
            "manual approval",
            "real patch",
            "gates",
            "rollback if needed"
        ],
        "commands": {
            "dry_run_preview": f"aider {' '.join(target_files)} --message {json.dumps(goal)}",
            "real_run_requires_phrase": approval_phrase
        }
    }

    state = _read_state()
    state.setdefault("sessions", []).append(session)
    _write_state(state)

    Path(run_dir / "session.json").write_text(json.dumps(session, indent=4))

    return session


def run_tests_for_session(session_id=None):
    tests = [
        ["python", "-m", "py_compile", "seed_cli.py"],
        ["python", "seed_latency_probe.py"],
        ["python", "seed_v30_megapatch_gate.py"],
    ]

    results = []
    for command in tests:
        try:
            proc = subprocess.run(command, capture_output=True, text=True, timeout=180)
            results.append({
                "command": " ".join(command),
                "ok": proc.returncode == 0,
                "stdout_tail": proc.stdout[-3000:],
                "stderr_tail": proc.stderr[-3000:]
            })
        except Exception as error:
            results.append({"command": " ".join(command), "ok": False, "error": str(error)})

    return {
        "created_at": now_timestamp(),
        "version": "v45.0.0",
        "ok": all(r.get("ok") for r in results),
        "session_id": session_id,
        "results": results
    }


def latest_session():
    state = _read_state()
    sessions = state.get("sessions", [])
    return sessions[-1] if sessions else None


def show_aider_cockpit():
    print("\n=== SEED AIDER COCKPIT v31 ===")
    session = latest_session()
    if not session:
        print("No Aider cockpit sessions yet. Use /aider-cockpit-new.")
        return
    print(json.dumps(session, indent=4))


def show_aider_cockpit_new():
    goal = input("Patch goal: ").strip()
    files = input("Target files comma-separated: ").strip()
    target_files = [x.strip() for x in files.split(",") if x.strip()]
    print(json.dumps(create_aider_session(goal, target_files), indent=4))


def show_aider_cockpit_tests():
    session = latest_session()
    print(json.dumps(run_tests_for_session(session.get("id") if session else None), indent=4))


if __name__ == "__main__":
    show_aider_cockpit()
