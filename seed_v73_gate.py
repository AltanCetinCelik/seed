import json
import subprocess
from datetime import datetime

MODULES = [
    "seed_expressive_state_v73.py",
    "seed_memory_review_actions_v73.py",
    "seed_voice_live_v73.py",
    "seed_avatar_panel_v73.py",
    "seed_task_converter_v73.py",
    "seed_curiosity_speaker_v73.py",
    "seed_v73_systems.py",
    "seed_v73_gate.py",
    "seed_v73_commands.py",
    "seed_natural_intent_router_v73.py",
]

def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")

def compile_module(module):
    proc = subprocess.run(["python", "-m", "py_compile", module], capture_output=True, text=True, timeout=30)
    return {"module": module, "ok": proc.returncode == 0, "stderr": proc.stderr[-1200:]}

def run_v73_gate():
    checks = [compile_module(m) for m in MODULES]
    modules_ok = all(c["ok"] for c in checks)
    details = {}
    try:
        from seed_v73_systems import build_v73_state
        state = build_v73_state()
        systems_ok = state.get("ok") is True and len(state.get("cards", [])) >= 6
        details["v73_state"] = {"ok": state.get("ok"), "cards": len(state.get("cards", []))}
    except Exception as error:
        systems_ok = False
        details["v73_state_error"] = str(error)
    try:
        from seed_v72_gate import run_v72_gate
        v72 = run_v72_gate()
        v72_ok = v72.get("ready") is True
        details["v72"] = {"ready": v72.get("ready")}
    except Exception as error:
        v72_ok = False
        details["v72_error"] = str(error)
    ready = modules_ok and systems_ok and v72_ok
    report = {"created_at": now_timestamp(), "version": "v73.0.0", "ready": ready, "modules_ok": modules_ok, "systems_ok": systems_ok, "v72_ok": v72_ok, "module_checks": checks, "details": details}
    with open("seed_v73_gate_report.json", "w") as f:
        json.dump(report, f, indent=4)
    return report

def show_v73_gate():
    report = run_v73_gate()
    print("\n=== SEED v73 ACTION PRESENCE GATE ===")
    print(f"Ready: {report['ready']}")
    print(f"Modules OK: {report['modules_ok']}")
    print(f"Systems OK: {report['systems_ok']}")
    print(f"v72 OK: {report['v72_ok']}")
    print("Details:", report["details"])

if __name__ == "__main__":
    show_v73_gate()
