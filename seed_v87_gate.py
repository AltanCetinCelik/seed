import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

MODULES = [
    "seed_self_state_v87.py",
    "seed_wake_word_v861.py",
    "seed_senses_v87.py",
    "seed_curiosity_life_v87.py",
    "seed_alive_runtime_v87.py",
    "seed_v87_systems.py",
    "seed_v87_gate.py",
    "seed_v87_commands.py",
    "seed_natural_intent_router_v87.py",
]

def now():
    return datetime.now().isoformat(timespec="seconds")

def compile_module(module):
    proc = subprocess.run([sys.executable, "-m", "py_compile", module], capture_output=True, text=True, timeout=30)
    return {"module": module, "ok": proc.returncode == 0, "stderr": proc.stderr[-1600:]}

def run_v87_gate():
    checks = [compile_module(m) for m in MODULES]
    modules_ok = all(c["ok"] for c in checks)
    details = {}

    try:
        from seed_v87_systems import build_v87_state
        state = build_v87_state()
        systems_ok = state.get("ok") is True and len(state.get("cards", [])) >= 5
        details["v87_state"] = {"ok": state.get("ok"), "cards": len(state.get("cards", []))}
    except Exception as e:
        systems_ok = False
        details["v87_state_error"] = str(e)

    try:
        from seed_wake_word_v861 import is_wake_phrase
        wake_ok = (
            is_wake_phrase("hey seed")[0] is True and
            is_wake_phrase("wake up")[0] is True and
            is_wake_phrase("see it")[0] is False
        )
        details["wake_tests"] = {
            "hey_seed": is_wake_phrase("hey seed"),
            "wake_up": is_wake_phrase("wake up"),
            "false_positive_see_it": is_wake_phrase("see it"),
        }
    except Exception as e:
        wake_ok = False
        details["wake_error"] = str(e)

    try:
        from seed_curiosity_life_v87 import generate_curiosities
        curiosity_ok = len(generate_curiosities()) > 0
        details["curiosity_count"] = len(generate_curiosities())
    except Exception as e:
        curiosity_ok = False
        details["curiosity_error"] = str(e)

    report = {
        "created_at": now(),
        "version": "v87.0.0",
        "ready": modules_ok and systems_ok and wake_ok and curiosity_ok,
        "modules_ok": modules_ok,
        "systems_ok": systems_ok,
        "wake_ok": wake_ok,
        "curiosity_ok": curiosity_ok,
        "module_checks": checks,
        "details": details,
    }
    Path("seed_v87_gate_report.json").write_text(json.dumps(report, indent=4, ensure_ascii=False))
    return report

def show_v87_gate():
    r = run_v87_gate()
    print("\n=== SEED v87 ALIVE COMPANION GATE ===")
    print(f"Ready: {r['ready']}")
    print(f"Modules OK: {r['modules_ok']}")
    print(f"Systems OK: {r['systems_ok']}")
    print(f"Wake OK: {r['wake_ok']}")
    print(f"Curiosity OK: {r['curiosity_ok']}")
    print(f"Details: {r['details']}")

if __name__ == "__main__":
    show_v87_gate()
