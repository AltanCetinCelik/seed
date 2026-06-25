import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

MODULES = [
    "seed_wake_word_v86.py",
    "seed_v86_systems.py",
    "seed_v86_gate.py",
    "seed_v86_commands.py",
    "seed_natural_intent_router_v86.py",
]

def now():
    return datetime.now().isoformat(timespec="seconds")

def compile_module(module):
    proc = subprocess.run([sys.executable, "-m", "py_compile", module], capture_output=True, text=True, timeout=30)
    return {"module": module, "ok": proc.returncode == 0, "stderr": proc.stderr[-1600:]}

def run_v86_gate():
    checks = [compile_module(m) for m in MODULES]
    modules_ok = all(c["ok"] for c in checks)
    details = {}

    try:
        from seed_v86_systems import build_v86_state
        state = build_v86_state()
        systems_ok = state.get("ok") is True and len(state.get("cards", [])) >= 4
        details["v86_state"] = {"ok": state.get("ok"), "cards": len(state.get("cards", []))}
    except Exception as e:
        systems_ok = False
        details["v86_state_error"] = str(e)

    try:
        from seed_wake_word_v86 import is_wake_phrase
        wake_ok = is_wake_phrase("hey seed")[0] is True and is_wake_phrase("wake up")[0] is True
        details["phrase_tests"] = {"hey_seed": is_wake_phrase("hey seed"), "wake_up": is_wake_phrase("wake up")}
    except Exception as e:
        wake_ok = False
        details["phrase_error"] = str(e)

    report = {
        "created_at": now(),
        "version": "v86.0.0",
        "ready": modules_ok and systems_ok and wake_ok,
        "modules_ok": modules_ok,
        "systems_ok": systems_ok,
        "wake_phrase_ok": wake_ok,
        "module_checks": checks,
        "details": details,
    }
    Path("seed_v86_gate_report.json").write_text(json.dumps(report, indent=4, ensure_ascii=False))
    return report

def show_v86_gate():
    r = run_v86_gate()
    print("\n=== SEED v86 WAKE WORD GATE ===")
    print(f"Ready: {r['ready']}")
    print(f"Modules OK: {r['modules_ok']}")
    print(f"Systems OK: {r['systems_ok']}")
    print(f"Wake Phrase OK: {r['wake_phrase_ok']}")
    print(f"Details: {r['details']}")

if __name__ == "__main__":
    show_v86_gate()
