import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

def now():
    return datetime.now().isoformat(timespec="seconds")

def run_v9011_gate():
    checks = []
    for module in ["seed_memory_garden_v90.py", "seed_v9011_gate.py"]:
        proc = subprocess.run([sys.executable, "-m", "py_compile", module], capture_output=True, text=True, timeout=30)
        checks.append({"module": module, "ok": proc.returncode == 0, "stderr": proc.stderr[-1000:]})

    modules_ok = all(c["ok"] for c in checks)

    try:
        import seed_memory_garden_v90 as garden
        summary = garden.daily_summary()["summary"]
        no_archive_leak = "organism mode started" not in summary.lower()
        no_old_noise = "stores notes only" not in summary.lower()
        status = garden.status()
        ready = modules_ok and no_archive_leak and no_old_noise and status.get("ok") is True
        details = {"summary": summary, "status": status, "no_archive_leak": no_archive_leak, "no_old_noise": no_old_noise}
    except Exception as e:
        ready = False
        no_archive_leak = False
        no_old_noise = False
        details = {"error": str(e)}

    report = {
        "created_at": now(),
        "version": "v90.1.1",
        "ready": ready,
        "modules_ok": modules_ok,
        "no_archive_leak": no_archive_leak,
        "no_old_noise": no_old_noise,
        "module_checks": checks,
        "details": details,
    }
    Path("seed_v9011_gate_report.json").write_text(json.dumps(report, indent=4, ensure_ascii=False))
    return report

def show_v9011_gate():
    r = run_v9011_gate()
    print("\n=== SEED v90.1.1 MEMORY SUMMARY GATE ===")
    print(f"Ready: {r['ready']}")
    print(f"Modules OK: {r['modules_ok']}")
    print(f"No Archive Leak: {r['no_archive_leak']}")
    print(f"No Old Noise: {r['no_old_noise']}")
    print(f"Details: {r['details']}")

if __name__ == "__main__":
    show_v9011_gate()
