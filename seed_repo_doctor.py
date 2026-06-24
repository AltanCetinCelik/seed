import json
from datetime import datetime


try:
    from seed_config import SEED_REPO_DOCTOR_REPORT_FILE
except Exception:
    SEED_REPO_DOCTOR_REPORT_FILE = "seed_repo_doctor_report.json"


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def run_repo_doctor():
    report = {
        "created_at": now_timestamp(),
        "version": "v2.7.0",
        "ok": False,
        "checks": {},
        "findings": [],
        "recommendations": []
    }

    try:
        from seed_skill_kernel import run_skill

        report["checks"]["git_status"] = run_skill("git", "status")
        report["checks"]["git_diff_stat"] = run_skill("git", "diff_stat")
        report["checks"]["repo_summary"] = run_skill("repo", "summary")
        report["checks"]["repo_todos"] = run_skill("repo", "todos")
        report["checks"]["safe_diagnostic"] = run_skill("safe_shell", "diagnostic")
    except Exception as error:
        report["error"] = str(error)

    git_status = report["checks"].get("git_status", {})
    repo_summary = report["checks"].get("repo_summary", {})
    todos = report["checks"].get("repo_todos", {})
    diagnostic = report["checks"].get("safe_diagnostic", {})

    if git_status.get("data", {}).get("dirty"):
        report["findings"].append("Working tree is dirty.")
        report["recommendations"].append("Commit or checkpoint before running external agents.")

    py_count = repo_summary.get("data", {}).get("python_file_count", 0)
    if py_count >= 250:
        report["findings"].append(f"Large Python project detected: {py_count} files.")
        report["recommendations"].append("Use scoped tasks and repo inspection before agent execution.")

    todo_count = todos.get("data", {}).get("count", 0)
    if todo_count:
        report["findings"].append(f"TODO/FIXME/HACK markers found: {todo_count}.")
        report["recommendations"].append("Use /repo-todos before choosing cleanup tasks.")

    if diagnostic.get("ok"):
        report["findings"].append("Safe diagnostics passed.")
    else:
        report["findings"].append("Safe diagnostics did not pass.")
        report["recommendations"].append("Fix diagnostics before external agent execution.")

    report["ok"] = diagnostic.get("ok") is True and repo_summary.get("ok") is True

    if not report["recommendations"]:
        report["recommendations"].append("Repo appears safe for planning. External execution still requires approval.")

    with open(SEED_REPO_DOCTOR_REPORT_FILE, "w") as file:
        json.dump(report, file, indent=4)

    return report


def repo_doctor_context(user_prompt=""):
    report = run_repo_doctor()
    lines = ["=== SEED REPO DOCTOR CONTEXT ==="]
    lines.append(f"OK: {report.get('ok')}")
    lines.append("Findings:")
    for finding in report.get("findings", [])[:8]:
        lines.append(f"- {finding}")
    lines.append("Recommendations:")
    for rec in report.get("recommendations", [])[:8]:
        lines.append(f"- {rec}")
    return "\n".join(lines)


def show_repo_doctor():
    report = run_repo_doctor()

    print("\n=== SEED REPO DOCTOR ===")
    print(f"OK: {report.get('ok')}")
    print("\nFindings:")
    for item in report.get("findings", []):
        print(f"- {item}")
    print("\nRecommendations:")
    for item in report.get("recommendations", []):
        print(f"- {item}")


if __name__ == "__main__":
    show_repo_doctor()
