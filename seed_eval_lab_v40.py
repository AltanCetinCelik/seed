import json
import subprocess
import time
from datetime import datetime
from pathlib import Path


EVAL_FILE = Path("seed_eval_lab_v40.json")


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def run_command(command, timeout=180):
    start = time.time()
    try:
        proc = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
        elapsed = int((time.time() - start) * 1000)
        return {
            "command": " ".join(command),
            "ok": proc.returncode == 0,
            "ms": elapsed,
            "stdout_tail": proc.stdout[-2000:],
            "stderr_tail": proc.stderr[-2000:]
        }
    except Exception as error:
        return {"command": " ".join(command), "ok": False, "error": str(error)}


def run_eval_lab():
    tests = [
        ["python", "seed_latency_probe.py"],
        ["python", "seed_v30_megapatch_gate.py"],
        ["python", "seed_v203_presence_gate.py"],
        ["python", "seed_v20_sovereign_gate.py"],
    ]

    results = [run_command(t) for t in tests]

    data = {
        "created_at": now_timestamp(),
        "version": "v45.0.0",
        "ok": all(r.get("ok") for r in results),
        "results": results,
        "benchmarks": {
            "latency": "seed_latency_probe.py",
            "agent_hq": "seed_v30_megapatch_gate.py",
            "presence": "seed_v203_presence_gate.py",
            "sovereign_os": "seed_v20_sovereign_gate.py"
        }
    }

    EVAL_FILE.write_text(json.dumps(data, indent=4))
    return data


def show_eval_lab():
    print("\n=== SEED EVALUATION LAB v40 ===")
    print(json.dumps(run_eval_lab(), indent=4))


if __name__ == "__main__":
    show_eval_lab()
