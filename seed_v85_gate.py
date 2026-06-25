import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

REPORT_FILE = Path("seed_v85_gate_report.json")

CORE_MODULES = [
    "seed_self_state_v85.py",
    "seed_recovery_v82.py",
    "seed_runtime_v83.py",
    "seed_privacy_backup_v84.py",
    "seed_release_candidate_v85.py",
    "seed_v85_systems.py",
    "seed_v85_gate.py",
    "seed_v85_commands.py",
    "seed_natural_intent_router_v85.py",
    "seed_v81_gate.py",
    "seed_v75_gate.py",
]

def now():
    return datetime.now().isoformat(timespec="seconds")

def compile_module(module):
    if not Path(module).exists():
        return {"module": module, "ok": False, "stderr": "missing"}
    proc = subprocess.run([sys.executable, "-m", "py_compile", module], capture_output=True, text=True, timeout=20)
    return {"module": module, "ok": proc.returncode == 0, "stderr": proc.stderr[-1200:]}

def read_report(path):
    p = Path(path)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(errors="ignore"))
    except Exception:
        return {}

def report_ready(path, max_age_seconds=86400):
    p = Path(path)
    if not p.exists():
        return False, {"source": "missing_report", "path": str(p)}
    data = read_report(path)
    age = time.time() - p.stat().st_mtime
    return data.get("ready") is True and age <= max_age_seconds, {
        "source": "cached_report",
        "path": str(p),
        "age_seconds": round(age, 1),
        "ready": data.get("ready"),
        "version": data.get("version"),
    }

def run_v85_gate(deep=False):
    checks = [compile_module(m) for m in CORE_MODULES]
    modules_ok = all(c["ok"] for c in checks)

    v81_ok, v81_meta = report_ready("seed_v81_gate_report.json")
    v75_ok, v75_meta = report_ready("seed_v75_gate_report.json")

    if deep:
        for script, key in [("seed_v81_gate.py", "v81"), ("seed_v75_gate.py", "v75")]:
            try:
                proc = subprocess.run([sys.executable, script], capture_output=True, text=True, timeout=240)
                meta = {"source": "deep_subprocess", "returncode": proc.returncode, "stdout_tail": proc.stdout[-2000:], "stderr_tail": proc.stderr[-2000:]}
                if key == "v81":
                    v81_ok, v81_meta = proc.returncode == 0, meta
                else:
                    v75_ok, v75_meta = proc.returncode == 0, meta
            except Exception as e:
                if key == "v81":
                    v81_ok, v81_meta = False, {"source": "deep_subprocess", "error": str(e)}
                else:
                    v75_ok, v75_meta = False, {"source": "deep_subprocess", "error": str(e)}

    try:
        from seed_self_state_v85 import build_self_state
        s = build_self_state()
        truth_ok = s.get("true_current_version") in {"v85.0.0", "v85.1.0", "v85.2.0", "v85.3.0"}
        truth_meta = {"current": s.get("true_current_version"), "green_layers": s.get("installed_layers_green", [])}
    except Exception as e:
        truth_ok, truth_meta = False, {"error": str(e)}

    try:
        from seed_runtime_v83 import install_seed_script
        script = install_seed_script()
        script_ok = script.get("ok") is True and Path("seed").exists()
    except Exception as e:
        script, script_ok = {"ok": False, "error": str(e)}, False

    try:
        from seed_recovery_v82 import recovery_summary
        rec = recovery_summary()
        recovery_ok = rec.get("ok") is True
    except Exception as e:
        rec, recovery_ok = {"ok": False, "error": str(e)}, False

    report = {
        "created_at": now(),
        "version": "v85.3.0",
        "ready": modules_ok and v81_ok and v75_ok and truth_ok and script_ok and recovery_ok,
        "modules_ok": modules_ok,
        "v81_ok": v81_ok,
        "v75_ok": v75_ok,
        "truth_ok": truth_ok,
        "script_ok": script_ok,
        "recovery_ok": recovery_ok,
        "module_checks": checks,
        "details": {
            "v81": v81_meta,
            "v75": v75_meta,
            "truth": truth_meta,
            "runtime_script": script,
            "recovery": {"ok": rec.get("ok"), "blockers": rec.get("blockers"), "warnings": rec.get("warnings"), "recursion_guard": rec.get("recursion_guard")},
            "mode": "deep" if deep else "fast_cached",
        },
        "note": "v85.3 fast gate with AST recursion guard.",
    }
    REPORT_FILE.write_text(json.dumps(report, indent=4, ensure_ascii=False))
    return report

def show_v85_gate(deep=False):
    r = run_v85_gate(deep=deep)
    print("\n=== SEED v85.3 FAST REAL V1 PREP GATE ===")
    print(f"Ready: {r['ready']}")
    print(f"Modules OK: {r['modules_ok']}")
    print(f"v81 OK: {r['v81_ok']}")
    print(f"v75 OK: {r['v75_ok']}")
    print(f"Truth OK: {r['truth_ok']}")
    print(f"Script OK: {r['script_ok']}")
    print(f"Recovery OK: {r['recovery_ok']}")
    print(f"Details: {r['details']}")

if __name__ == "__main__":
    show_v85_gate(deep="--deep" in sys.argv)
