import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

MODULES = [
    "seed_wake_conversation_v871.py",
    "seed_wake_word_v871.py",
    "seed_curiosity_life_v871.py",
    "seed_alive_runtime_v871.py",
    "seed_v871_systems.py",
    "seed_v871_gate.py",
    "seed_natural_intent_router_v871.py",
]

def now():
    return datetime.now().isoformat(timespec="seconds")

def compile_module(module):
    proc = subprocess.run([sys.executable, "-m", "py_compile", module], capture_output=True, text=True, timeout=30)
    return {"module": module, "ok": proc.returncode == 0, "stderr": proc.stderr[-1600:]}

def run_v871_gate():
    checks = [compile_module(m) for m in MODULES]
    modules_ok = all(c["ok"] for c in checks)
    details = {}

    try:
        from seed_v871_systems import build_v871_state
        state = build_v871_state()
        systems_ok = state.get("ok") is True and len(state.get("cards", [])) >= 4
        details["v871_state"] = {"ok": state.get("ok"), "cards": len(state.get("cards", []))}
    except Exception as e:
        systems_ok = False
        details["v871_state_error"] = str(e)

    try:
        from seed_wake_word_v871 import is_wake_phrase
        wake_ok = is_wake_phrase("hey seed")[0] and is_wake_phrase("wake up")[0] and not is_wake_phrase("see it")[0]
        details["wake_tests"] = {"hey_seed": is_wake_phrase("hey seed"), "wake_up": is_wake_phrase("wake up"), "see_it": is_wake_phrase("see it")}
    except Exception as e:
        wake_ok = False
        details["wake_error"] = str(e)

    try:
        from seed_wake_conversation_v871 import load_settings, ask_seed_fast
        conv = load_settings()
        # Do not call a real model in the gate; just verify the direct route settings.
        conv_ok = (
            conv.get("ack_before_listen") is False and
            int(conv.get("after_wake_listen_seconds", 0)) >= 8 and
            conv.get("fast_model") is not None
        )
        details["conversation_settings"] = conv
        details["conversation_route"] = "direct_ollama_no_context_gate"
    except Exception as e:
        conv_ok = False
        details["conversation_error"] = str(e)

    report = {
        "created_at": now(),
        "version": "v87.1.1",
        "ready": modules_ok and systems_ok and wake_ok and conv_ok,
        "modules_ok": modules_ok,
        "systems_ok": systems_ok,
        "wake_ok": wake_ok,
        "conversation_ok": conv_ok,
        "module_checks": checks,
        "details": details,
    }
    Path("seed_v871_gate_report.json").write_text(json.dumps(report, indent=4, ensure_ascii=False))
    return report

def show_v871_gate():
    r = run_v871_gate()
    print("\n=== SEED v87.1.1 WAKE CONVERSATION GATE ===")
    print(f"Ready: {r['ready']}")
    print(f"Modules OK: {r['modules_ok']}")
    print(f"Systems OK: {r['systems_ok']}")
    print(f"Wake OK: {r['wake_ok']}")
    print(f"Conversation OK: {r['conversation_ok']}")
    print(f"Details: {r['details']}")

if __name__ == "__main__":
    show_v871_gate()
