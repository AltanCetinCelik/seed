import json
import subprocess
from datetime import datetime


try:
    from seed_config import SEED_RELEASE_ORCHESTRATOR_REPORT_FILE
except Exception:
    SEED_RELEASE_ORCHESTRATOR_REPORT_FILE = "seed_release_orchestrator_report.json"


SAFE_GATE_COMMANDS = [
    ["python", "seed_v28_aider_gate.py"],
    ["python", "seed_v27_executor_gate.py"],
    ["python", "seed_v26_agent_gate.py"],
    ["python", "seed_v25_skill_gate.py"],
    ["python", "seed_v24_experience_gate.py"],
    ["python", "seed_v23_intelligence_gate.py"],
    ["python", "seed_v22_mega_gate.py"],
    ["python", "seed_v2_release_gate.py"],
    ["python", "seed_release_manager.py"]
]


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def run_safe_gate(command, timeout=45):
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
        stdout = result.stdout[-5000:]
        stderr = result.stderr[-3000:]
        ok = result.returncode == 0 and (
            "Ready: False" not in stdout
            and "Overall OK: False" not in stdout
            and "Traceback" not in stdout
            and "Traceback" not in stderr
        )
        return {
            "command": " ".join(command),
            "returncode": result.returncode,
            "ok": ok,
            "stdout_tail": stdout,
            "stderr_tail": stderr
        }
    except Exception as error:
        return {
            "command": " ".join(command),
            "returncode": None,
            "ok": False,
            "error": str(error)
        }


def run_release_orchestrator():
    checks = [run_safe_gate(command) for command in SAFE_GATE_COMMANDS]
    ok = all(item.get("ok") for item in checks)

    report = {
        "created_at": now_timestamp(),
        "version": "v2.9.0",
        "ok": ok,
        "safe_only": True,
        "checks": checks,
        "summary": {
            "total": len(checks),
            "passed": sum(1 for item in checks if item.get("ok")),
            "failed": sum(1 for item in checks if not item.get("ok"))
        }
    }

    with open(SEED_RELEASE_ORCHESTRATOR_REPORT_FILE, "w") as file:
        json.dump(report, file, indent=4)

    return report


def release_orchestrator_context(user_prompt=""):
    return (
        "=== SEED RELEASE ORCHESTRATOR ===\n"
        "Runs safe local release gates only. No installs, no edits, no commits.\n"
        "Use /release-orchestrate before big checkpoints.\n"
    )


def show_release_orchestrator():
    report = run_release_orchestrator()

    print("\n=== SEED RELEASE ORCHESTRATOR ===")
    print(f"OK: {report['ok']}")
    print(f"Passed: {report['summary']['passed']}/{report['summary']['total']}")

    for item in report["checks"]:
        status = "OK" if item.get("ok") else "FAIL"
        print(f"- {status}: {item.get('command')}")


if __name__ == "__main__":
    show_release_orchestrator()
