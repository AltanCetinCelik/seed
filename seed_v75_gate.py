import json
import subprocess
from datetime import datetime

MODULES = [
    "seed_self_state_v741.py",
    "seed_memory_review_v75.py",
    "seed_v75_systems.py",
    "seed_v75_gate.py",
    "seed_v75_commands.py",
    "seed_natural_intent_router_v75.py",
]

def now():
    return datetime.now().isoformat(timespec="seconds")

def compile_module(module):
    proc = subprocess.run(["python", "-m", "py_compile", module], capture_output=True, text=True, timeout=30)
    return {"module": module, "ok": proc.returncode == 0, "stderr": proc.stderr[-1600:]}

def run_v75_gate():
    checks = [compile_module(m) for m in MODULES]
    modules_ok = all(c["ok"] for c in checks)
    details = {}

    try:
        from seed_v75_systems import build_v75_state
        state = build_v75_state()
        systems_ok = state.get("ok") is True and len(state.get("cards", [])) >= 4
        details["v75_state"] = {"ok": state.get("ok"), "cards": len(state.get("cards", [])), "version": state.get("version")}
    except Exception as e:
        systems_ok = False
        details["v75_state_error"] = str(e)

    try:
        from seed_v74_gate import run_v74_gate
        v74 = run_v74_gate()
        v74_ok = v74.get("ready") is True
        details["v74"] = {"ready": v74.get("ready")}
    except Exception as e:
        v74_ok = False
        details["v74_error"] = str(e)

    try:
        from seed_self_state_v741 import build_self_state
        s = build_self_state()
        truth_ok = s.get("true_current_version") == "v75.1.0" and s.get("capabilities", {}).get("recursion_hotfix") is True
        details["truth"] = {"current": s.get("true_current_version"), "green_layers": s.get("installed_layers_green", [])}
    except Exception as e:
        truth_ok = False
        details["truth_error"] = str(e)

    report = {
        "created_at": now(),
        "version": "v75.1.0",
        "ready": modules_ok and systems_ok and v74_ok and truth_ok,
        "modules_ok": modules_ok,
        "systems_ok": systems_ok,
        "v74_ok": v74_ok,
        "truth_ok": truth_ok,
        "module_checks": checks,
        "details": details,
        "hotfix": "Removed v75_gate call from self_state to stop recursion.",
    }

    with open("seed_v75_gate_report.json", "w") as f:
        json.dump(report, f, indent=4)

    return report

def show_v75_gate():
    report = run_v75_gate()
    print("\n=== SEED v75.1 SELF-TRUTH + REAL MEMORY GATE ===")
    print(f"Ready: {report['ready']}")
    print(f"Modules OK: {report['modules_ok']}")
    print(f"Systems OK: {report['systems_ok']}")
    print(f"v74 OK: {report['v74_ok']}")
    print(f"Truth OK: {report['truth_ok']}")
    print(f"Details: {report['details']}")

if __name__ == "__main__":
    show_v75_gate()
