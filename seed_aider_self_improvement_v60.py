import json
import shutil
import subprocess
import uuid
from datetime import datetime
from pathlib import Path


LOOP_FILE = Path("seed_aider_self_improvement_v60.json")
RUN_DIR = Path("seed_agent_runs")


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def detect_aider():
    return shutil.which("aider") or shutil.which("aider-chat")


def valid_file(path):
    p = Path(path)
    return p.exists() and p.is_file()


def create_loop(goal, target_files):
    target_files = [f for f in target_files if f.strip()]
    invalid = [f for f in target_files if not valid_file(f)]

    if not goal.strip():
        return {"ok": False, "error": "Goal cannot be empty."}

    if goal.strip().startswith("/"):
        return {"ok": False, "error": "Goal looks like an internal command. Say the improvement goal in normal words."}

    if invalid:
        return {"ok": False, "error": "Invalid target files.", "invalid": invalid}

    loop_id = uuid.uuid4().hex[:10]
    run_dir = RUN_DIR / f"v60_self_improve_{loop_id}"
    run_dir.mkdir(parents=True, exist_ok=True)

    approval = f"APPROVE_V60_AIDER_{loop_id}"

    loop = {
        "id": loop_id,
        "created_at": now_timestamp(),
        "version": "v60.0.0",
        "ok": True,
        "goal": goal,
        "target_files": target_files,
        "run_dir": str(run_dir),
        "aider": detect_aider(),
        "approval_phrase": approval,
        "status": "planned",
        "stages": [
            "checkpoint",
            "memory recall",
            "repo fusion context",
            "aider patch plan",
            "tests",
            "approval",
            "real aider run",
            "gates",
            "memory writeback"
        ],
        "real_run_command_preview": f"aider {' '.join(target_files)} --message {json.dumps(goal)}",
    }

    Path(run_dir / "loop.json").write_text(json.dumps(loop, indent=4))
    LOOP_FILE.write_text(json.dumps(loop, indent=4))
    return loop


def load_loop():
    if LOOP_FILE.exists():
        return json.loads(LOOP_FILE.read_text(errors="ignore"))
    return None


def run_preflight_tests():
    commands = [
        ["python", "-m", "py_compile", "seed_cli.py"],
        ["python", "seed_latency_probe.py"],
        ["python", "seed_v50_gate.py"],
    ]

    results = []
    for command in commands:
        try:
            proc = subprocess.run(command, capture_output=True, text=True, timeout=240)
            results.append({
                "command": " ".join(command),
                "ok": proc.returncode == 0,
                "stdout_tail": proc.stdout[-2000:],
                "stderr_tail": proc.stderr[-2000:],
            })
        except Exception as error:
            results.append({"command": " ".join(command), "ok": False, "error": str(error)})

    return {"ok": all(r.get("ok") for r in results), "results": results}


def approved_real_aider_run(approval_phrase):
    loop = load_loop()
    if not loop:
        return {"ok": False, "error": "No v60 self-improvement loop found."}

    if approval_phrase.strip() != loop.get("approval_phrase"):
        return {
            "ok": False,
            "error": "Approval phrase mismatch.",
            "required": loop.get("approval_phrase"),
        }

    aider = loop.get("aider")
    if not aider:
        return {"ok": False, "error": "Aider not found."}

    preflight = run_preflight_tests()
    if not preflight.get("ok"):
        return {"ok": False, "error": "Preflight tests failed.", "preflight": preflight}

    command = [aider] + loop["target_files"] + ["--message", loop["goal"]]

    try:
        proc = subprocess.run(command, capture_output=True, text=True, timeout=900)
        result = {
            "ok": proc.returncode == 0,
            "command": " ".join(command),
            "stdout_tail": proc.stdout[-5000:],
            "stderr_tail": proc.stderr[-5000:],
            "returncode": proc.returncode,
        }
    except Exception as error:
        result = {"ok": False, "error": str(error), "command": " ".join(command)}

    loop["last_real_run"] = result
    loop["status"] = "real_run_complete" if result.get("ok") else "real_run_failed"
    LOOP_FILE.write_text(json.dumps(loop, indent=4))

    return result


def show_self_improvement_v60():
    loop = load_loop()
    print("\n=== SEED v60 REAL AIDER SELF-IMPROVEMENT LOOP ===")
    if not loop:
        print("No loop yet. Say: create a patch plan for <goal> targeting <file.py>")
        return
    print(json.dumps(loop, indent=4))


def show_self_improvement_new():
    goal = input("Improvement goal in normal words: ").strip()
    files = input("Target files comma-separated: ").strip()
    target_files = [x.strip() for x in files.split(",") if x.strip()]
    print(json.dumps(create_loop(goal, target_files), indent=4))


def show_self_improvement_approve():
    phrase = input("Approval phrase: ").strip()
    print(json.dumps(approved_real_aider_run(phrase), indent=4))


if __name__ == "__main__":
    show_self_improvement_v60()
