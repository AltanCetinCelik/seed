import json
import subprocess
from datetime import datetime

MODULES = [
    "seed_self_state_v81.py",
    "seed_voice_v76.py",
    "seed_panel_v77.py",
    "seed_proactive_v78.py",
    "seed_permission_executor_v79.py",
    "seed_aider_loop_v80.py",
    "seed_assimilation_v81.py",
    "seed_v81_systems.py",
    "seed_v81_gate.py",
    "seed_v81_commands.py",
    "seed_natural_intent_router_v81.py",
]

def now():
    return datetime.now().isoformat(timespec="seconds")

def compile_module(module):
    proc = subprocess.run(["python", "-m", "py_compile", module], capture_output=True, text=True, timeout=30)
    return {"module": module, "ok": proc.returncode == 0, "stderr": proc.stderr[-1600:]}

def run_v81_gate():
    checks = [compile_module(m) for m in MODULES]
    modules_ok = all(c["ok"] for c in checks)
    details = {}

    try:
        from seed_v81_systems import build_v81_state
        state = build_v81_state()
        systems_ok = state.get("ok") is True and len(state.get("cards", [])) >= 8
        details["v81_state"] = {"ok": state.get("ok"), "cards": len(state.get("cards", []))}
    except Exception as e:
        systems_ok = False
        details["v81_state_error"] = str(e)

    try:
        from seed_v75_gate import run_v75_gate
        v75 = run_v75_gate()
        v75_ok = v75.get("ready") is True
        details["v75"] = {"ready": v75.get("ready")}
    except Exception as e:
        v75_ok = False
        details["v75_error"] = str(e)

    try:
        from seed_self_state_v81 import build_self_state
        s = build_self_state()
        truth_ok = s.get("true_current_version") == "v81.0.0"
        details["truth"] = {"current": s.get("true_current_version"), "green_layers": s.get("installed_layers_green", [])}
    except Exception as e:
        truth_ok = False
        details["truth_error"] = str(e)

    report = {
        "created_at": now(),
        "version": "v81.0.0",
        "ready": modules_ok and systems_ok and v75_ok and truth_ok,
        "modules_ok": modules_ok,
        "systems_ok": systems_ok,
        "v75_ok": v75_ok,
        "truth_ok": truth_ok,
        "module_checks": checks,
        "details": details,
    }
    open("seed_v81_gate_report.json", "w").write(json.dumps(report, indent=4))
    return report

def show_v81_gate():
    r = run_v81_gate()
    print("\n=== SEED v81 V1-ALPHA MEGA STACK GATE ===")
    print(f"Ready: {r['ready']}")
    print(f"Modules OK: {r['modules_ok']}")
    print(f"Systems OK: {r['systems_ok']}")
    print(f"v75 OK: {r['v75_ok']}")
    print(f"Truth OK: {r['truth_ok']}")
    print(f"Details: {r['details']}")

if __name__ == "__main__":
    show_v81_gate()
