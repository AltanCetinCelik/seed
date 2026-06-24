import subprocess


try:
    from seed_config import SEED_SKILL_SAFE_TIMEOUT_SECONDS
except Exception:
    SEED_SKILL_SAFE_TIMEOUT_SECONDS = 12


def run_git(args):
    command = ["git"] + args
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=int(SEED_SKILL_SAFE_TIMEOUT_SECONDS)
    )
    return {
        "command": command,
        "ok": result.returncode == 0,
        "returncode": result.returncode,
        "stdout": result.stdout[-12000:],
        "stderr": result.stderr[-4000:]
    }


def git_status():
    short = run_git(["status", "--short"])
    branch = run_git(["branch", "--show-current"])
    return {
        "ok": short["ok"] and branch["ok"],
        "branch": branch["stdout"].strip(),
        "dirty": bool(short["stdout"].strip()),
        "status_short": short["stdout"],
        "errors": [x["stderr"] for x in [short, branch] if x["stderr"]]
    }


def git_diff_stat():
    return run_git(["diff", "--stat"])


def git_diff_name_only():
    return run_git(["diff", "--name-only"])


def git_log_recent(limit=5):
    limit = str(int(limit))
    return run_git(["log", f"-{limit}", "--oneline"])


def git_summary():
    return {
        "ok": True,
        "status": git_status(),
        "diff_stat": git_diff_stat(),
        "changed_files": git_diff_name_only(),
        "recent_log": git_log_recent(5)
    }


def run_git_skill(operation, args=None):
    args = args or {}

    if operation == "status":
        return git_status()

    if operation == "diff_stat":
        return git_diff_stat()

    if operation == "changed_files":
        return git_diff_name_only()

    if operation == "log":
        return git_log_recent(args.get("limit", 5))

    if operation == "summary":
        return git_summary()

    return {"ok": False, "error": f"Unknown git operation: {operation}"}


if __name__ == "__main__":
    print(git_summary())
