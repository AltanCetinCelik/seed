import json
import subprocess
from datetime import datetime


try:
    from seed_config import SEED_V25_GATE_REPORT_FILE, V25_REQUIRED_MODULES
except Exception:
    SEED_V25_GATE_REPORT_FILE = "seed_v25_gate_report.json"
    V25_REQUIRED_MODULES = [
        "seed_skill_kernel.py",
        "seed_filesystem_skill.py",
        "seed_git_skill.py",
        "seed_repo_inspection_skill.py",
        "seed_safe_shell_skill.py",
        "seed_browser_skill.py",
        "seed_coding_prep_skill.py",
        "seed_v25_skill_gate.py"
    ]


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def compile_module(module):
    result = subprocess.run(["python", "-m", "py_compile", module], capture_output=True, text=True)
    return {
        "module": module,
        "ok": result.returncode == 0,
        "stderr": result.stderr[-3000:]
    }


def run_v25_gate():
    module_checks = [compile_module(module) for module in V25_REQUIRED_MODULES]
    modules_ok = all(item["ok"] for item in module_checks)

    checks = {}
    skills_ok = False
    fs_ok = False
    git_ok = False
    repo_ok = False
    shell_ok = False
    browser_ok = False
    coding_ok = False
    action_route_ok = False

    try:
        from seed_skill_kernel import SKILLS, run_skill, route_skill_from_text
        skills_ok = len(SKILLS) >= 6
        checks["skills"] = list(SKILLS.keys())

        fs = run_skill("filesystem", "list", {"path": "."})
        fs_ok = fs.get("ok") is True
        checks["filesystem"] = fs.get("spoken_message")

        git = run_skill("git", "status")
        git_ok = git.get("ok") is True
        checks["git"] = git.get("spoken_message")

        repo = run_skill("repo", "summary")
        repo_ok = repo.get("ok") is True
        checks["repo"] = repo.get("spoken_message")

        shell = run_skill("safe_shell", "diagnostic")
        shell_ok = shell.get("ok") is True
        checks["safe_shell"] = shell.get("spoken_message")

        browser = run_skill("browser", "validate", {"url": "https://example.com"})
        browser_ok = browser.get("ok") is True
        checks["browser"] = browser.get("spoken_message")

        coding = run_skill("coding_prep", "prepare", {"task": "v2.5 gate test coding task"})
        coding_ok = coding.get("ok") is True
        checks["coding_prep"] = coding.get("spoken_message")

        routed = route_skill_from_text("git status")
        checks["route_skill_from_text"] = routed
    except Exception as error:
        checks["skill_error"] = str(error)

    try:
        from seed_action_kernel import route_action_from_text
        action_id, args = route_action_from_text("git status")
        action_route_ok = action_id == "run_skill" and args.get("skill_id") == "git"
        checks["action_route"] = {"action_id": action_id, "args": args}
    except Exception as error:
        checks["action_route_error"] = str(error)

    ready = all([
        modules_ok,
        skills_ok,
        fs_ok,
        git_ok,
        repo_ok,
        shell_ok,
        browser_ok,
        coding_ok,
        action_route_ok
    ])

    report = {
        "created_at": now_timestamp(),
        "release": "Seed v2.5.0 — Real Skill System",
        "ready": ready,
        "modules_ok": modules_ok,
        "skills_ok": skills_ok,
        "filesystem_ok": fs_ok,
        "git_ok": git_ok,
        "repo_ok": repo_ok,
        "safe_shell_ok": shell_ok,
        "browser_ok": browser_ok,
        "coding_prep_ok": coding_ok,
        "action_route_ok": action_route_ok,
        "module_checks": module_checks,
        "checks": checks
    }

    with open(SEED_V25_GATE_REPORT_FILE, "w") as file:
        json.dump(report, file, indent=4)

    return report


def show_v25_gate():
    report = run_v25_gate()

    print("\n=== SEED v2.5.0 REAL SKILL SYSTEM GATE ===")
    print(f"Ready: {report['ready']}")
    print(f"Modules OK: {report['modules_ok']}")
    print(f"Skills OK: {report['skills_ok']}")
    print(f"Filesystem OK: {report['filesystem_ok']}")
    print(f"Git OK: {report['git_ok']}")
    print(f"Repo OK: {report['repo_ok']}")
    print(f"Safe shell OK: {report['safe_shell_ok']}")
    print(f"Browser OK: {report['browser_ok']}")
    print(f"Coding prep OK: {report['coding_prep_ok']}")
    print(f"Action route OK: {report['action_route_ok']}")

    print("\nModule checks:")
    for item in report["module_checks"]:
        status = "OK" if item["ok"] else "FAIL"
        print(f"- {status}: {item['module']}")
        if item["stderr"] and not item["ok"]:
            print(item["stderr"][:1200])

    print("\nChecks:")
    for key, value in report.get("checks", {}).items():
        print(f"- {key}: {value}")


if __name__ == "__main__":
    show_v25_gate()
