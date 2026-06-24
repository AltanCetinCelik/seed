import json
import subprocess
from datetime import datetime


try:
    from seed_config import SEED_GATE_MATRIX_REPORT_FILE
except Exception:
    SEED_GATE_MATRIX_REPORT_FILE = "seed_gate_matrix_report.json"


GATES = [
    {
        "id": "v29",
        "label": "Mission Control MegaPack",
        "command": ["python", "seed_v29_mission_gate.py"]
    },
    {
        "id": "v28",
        "label": "Aider First Executor Bridge",
        "command": ["python", "seed_v28_aider_gate.py"]
    },
    {
        "id": "v27",
        "label": "Executor Bridge / Repo Doctor / Voice Planner",
        "command": ["python", "seed_v27_executor_gate.py"]
    },
    {
        "id": "v26",
        "label": "Supervised Agent Execution",
        "command": ["python", "seed_v26_agent_gate.py"]
    },
    {
        "id": "v25",
        "label": "Real Skill System",
        "command": ["python", "seed_v25_skill_gate.py"]
    },
    {
        "id": "v24",
        "label": "Experience Fusion",
        "command": ["python", "seed_v24_experience_gate.py"]
    },
    {
        "id": "v23",
        "label": "Real Intelligence",
        "command": ["python", "seed_v23_intelligence_gate.py"]
    },
    {
        "id": "v22",
        "label": "Mega Capability",
        "command": ["python", "seed_v22_mega_gate.py"]
    },
    {
        "id": "v2",
        "label": "V2 Release Gate",
        "command": ["python", "seed_v2_release_gate.py"]
    },
    {
        "id": "release",
        "label": "Release Manager",
        "command": ["python", "seed_release_manager.py"]
    }
]


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def run_gate(gate, timeout=60):
    try:
        result = subprocess.run(
            gate["command"],
            capture_output=True,
            text=True,
            timeout=timeout
        )

        stdout = result.stdout or ""
        stderr = result.stderr or ""
        combined = stdout + "\n" + stderr

        ok = (
            result.returncode == 0
            and "Ready: False" not in combined
            and "Overall OK: False" not in combined
            and "Traceback" not in combined
            and "FAIL:" not in combined
        )

        return {
            "id": gate["id"],
            "label": gate["label"],
            "command": " ".join(gate["command"]),
            "ok": ok,
            "returncode": result.returncode,
            "stdout_tail": stdout[-4000:],
            "stderr_tail": stderr[-2500:]
        }
    except Exception as error:
        return {
            "id": gate["id"],
            "label": gate["label"],
            "command": " ".join(gate["command"]),
            "ok": False,
            "error": str(error)
        }


def run_gate_matrix():
    results = [run_gate(gate) for gate in GATES]
    ok = all(item.get("ok") for item in results)

    report = {
        "created_at": now_timestamp(),
        "version": "v3.0.0",
        "ok": ok,
        "count": len(results),
        "passed": sum(1 for item in results if item.get("ok")),
        "failed": sum(1 for item in results if not item.get("ok")),
        "results": results
    }

    with open(SEED_GATE_MATRIX_REPORT_FILE, "w") as file:
        json.dump(report, file, indent=4)

    return report


def gate_matrix_context(user_prompt=""):
    return (
        "=== SEED v3.0 GATE MATRIX ===\n"
        "Runs local safe gates v29 through release manager.\n"
        "No installs, no edits, no commits.\n"
        "Use /gate-matrix before major checkpoints.\n"
    )


def show_gate_matrix():
    report = run_gate_matrix()

    print("\n=== SEED GATE MATRIX ===")
    print(f"OK: {report['ok']}")
    print(f"Passed: {report['passed']}/{report['count']}")

    for item in report["results"]:
        status = "OK" if item.get("ok") else "FAIL"
        print(f"- {status}: {item['id']} — {item['label']}")


if __name__ == "__main__":
    show_gate_matrix()
