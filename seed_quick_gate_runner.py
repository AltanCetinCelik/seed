import json
import subprocess
from datetime import datetime


QUICK_GATE_COMMANDS = [
    ["python", "seed_v85_gate.py"],
    ["python", "seed_v81_gate.py"],
    ["python", "seed_v75_gate.py"],
    ["python", "seed_v70_gate.py"],
    ["python", "seed_v60_gate.py"],
    ["python", "seed_v50_gate.py"],
    ["python", "seed_v45_total_gate.py"],
    ["python", "seed_v30_megapatch_gate.py"],
    ["python", "seed_v20_sovereign_gate.py"],
    ["python", "seed_v50_operator_gate.py"],
    ["python", "seed_v40_os_gate.py"],
]


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def run_quick_gates():
    results = []
    for command in QUICK_GATE_COMMANDS:
        proc = subprocess.run(command, capture_output=True, text=True, timeout=120)
        combined = (proc.stdout or "") + "\n" + (proc.stderr or "")
        ok = proc.returncode == 0 and "Ready: False" not in combined and "Traceback" not in combined
        results.append({
            "command": " ".join(command),
            "ok": ok,
            "returncode": proc.returncode,
            "stdout_tail": (proc.stdout or "")[-2500:],
            "stderr_tail": (proc.stderr or "")[-1500:]
        })

    return {
        "created_at": now_timestamp(),
        "version": "v5.1.0",
        "ok": all(x["ok"] for x in results),
        "passed": sum(1 for x in results if x["ok"]),
        "count": len(results),
        "results": results
    }


def show_quick_gates():
    report = run_quick_gates()
    print("\n=== SEED QUICK GATES ===")
    print(f"OK: {report['ok']}")
    print(f"Passed: {report['passed']}/{report['count']}")
    for item in report["results"]:
        print(f"- {'OK' if item['ok'] else 'FAIL'}: {item['command']}")


if __name__ == "__main__":
    show_quick_gates()
