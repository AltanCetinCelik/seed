import json
import subprocess
from datetime import datetime


FINAL_GATE_COMMANDS = [
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
    ["python", "seed_v36_integration_gate.py"],
    ["python", "seed_v35_omega_gate.py"],
    ["python", "seed_v30_control_gate.py"],
    ["python", "seed_release_orchestrator.py"],
]


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def run_final_gates():
    results = []

    for command in FINAL_GATE_COMMANDS:
        try:
            proc = subprocess.run(command, capture_output=True, text=True, timeout=180)
            combined = (proc.stdout or "") + "\n" + (proc.stderr or "")
            ok = (
                proc.returncode == 0
                and "Ready: False" not in combined
                and "Overall OK: False" not in combined
                and "Traceback" not in combined
            )

            results.append({
                "command": " ".join(command),
                "ok": ok,
                "returncode": proc.returncode,
                "stdout_tail": (proc.stdout or "")[-4000:],
                "stderr_tail": (proc.stderr or "")[-2500:]
            })
        except Exception as error:
            results.append({
                "command": " ".join(command),
                "ok": False,
                "error": str(error)
            })

    return {
        "created_at": now_timestamp(),
        "version": "v5.0.1",
        "ok": all(item.get("ok") for item in results),
        "passed": sum(1 for item in results if item.get("ok")),
        "count": len(results),
        "results": results
    }


def show_final_gates():
    report = run_final_gates()

    print("\n=== SEED FINAL GATES ===")
    print(f"OK: {report['ok']}")
    print(f"Passed: {report['passed']}/{report['count']}")

    for item in report["results"]:
        status = "OK" if item.get("ok") else "FAIL"
        print(f"- {status}: {item['command']}")
        if not item.get("ok"):
            print(item.get("stderr_tail") or item.get("stdout_tail") or item.get("error"))


if __name__ == "__main__":
    show_final_gates()
