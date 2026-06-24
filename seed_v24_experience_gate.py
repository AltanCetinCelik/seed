import json
import subprocess
from datetime import datetime


try:
    from seed_config import SEED_V24_GATE_REPORT_FILE, V24_REQUIRED_MODULES
except Exception:
    SEED_V24_GATE_REPORT_FILE = "seed_v24_gate_report.json"
    V24_REQUIRED_MODULES = [
        "seed_reference_fusion.py",
        "seed_experience_modes.py",
        "seed_smooth_ux.py",
        "seed_v24_experience_gate.py"
    ]


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def compile_module(module):
    result = subprocess.run(["python", "-m", "py_compile", module], capture_output=True, text=True)
    return {
        "module": module,
        "ok": result.returncode == 0,
        "stderr": result.stderr[-3000:]
    }


def run_v24_gate():
    module_checks = [compile_module(module) for module in V24_REQUIRED_MODULES]
    modules_ok = all(item["ok"] for item in module_checks)

    reference_ok = False
    mode_ok = False
    smooth_ok = False
    voice_context_ok = False

    details = {}

    try:
        from seed_reference_fusion import build_reference_fusion_state, build_seed_almost_perfect_plan
        state = build_reference_fusion_state()
        plan = build_seed_almost_perfect_plan()
        reference_ok = (
            len(state.get("public_reference_stack", {})) >= 8
            and len(state.get("friend_advice_rules", [])) >= 5
            and len(plan.get("milestones", [])) >= 6
        )
        details["reference_stack_count"] = len(state.get("public_reference_stack", {}))
        details["friend_advice_count"] = len(state.get("friend_advice_rules", []))
        details["milestone_count"] = len(plan.get("milestones", []))
    except Exception as error:
        details["reference_error"] = str(error)

    try:
        from seed_experience_modes import EXPERIENCE_MODES, save_mode, load_mode
        save_mode("coding")
        current = load_mode()
        mode_ok = "companion" in EXPERIENCE_MODES and "coding" in EXPERIENCE_MODES and current.get("mode") == "coding"
        save_mode("companion")
        details["mode_count"] = len(EXPERIENCE_MODES)
    except Exception as error:
        details["mode_error"] = str(error)

    try:
        from seed_smooth_ux import maybe_handle_smooth_request, seed_home_text
        home = seed_home_text()
        smooth_answer = maybe_handle_smooth_request("what can you do")
        smooth_ok = "SEED HOME" in home and smooth_answer and "SEED HOME" in smooth_answer
        details["home_chars"] = len(home)
    except Exception as error:
        details["smooth_error"] = str(error)

    try:
        from seed_fast_voice_context import get_fast_voice_context_for_prompt
        ctx = get_fast_voice_context_for_prompt("switch to coding mode")
        voice_context_ok = (
            ("v2.4.0" in ctx or "v2.5.0" in ctx or "EXPERIENCE" in ctx.upper())
            and ("VOICE" in ctx.upper() or "EXPERIENCE" in ctx.upper())
        )
        details["voice_context_chars"] = len(ctx)
    except Exception as error:
        details["voice_context_error"] = str(error)

    ready = all([modules_ok, reference_ok, mode_ok, smooth_ok, voice_context_ok])

    report = {
        "created_at": now_timestamp(),
        "release": "Seed v2.4.0 — Experience Fusion Layer",
        "ready": ready,
        "modules_ok": modules_ok,
        "reference_fusion_ok": reference_ok,
        "experience_modes_ok": mode_ok,
        "smooth_ux_ok": smooth_ok,
        "voice_context_ok": voice_context_ok,
        "module_checks": module_checks,
        "details": details
    }

    with open(SEED_V24_GATE_REPORT_FILE, "w") as file:
        json.dump(report, file, indent=4)

    return report


def show_v24_gate():
    report = run_v24_gate()

    print("\n=== SEED v2.4.0 EXPERIENCE FUSION GATE ===")
    print(f"Ready: {report['ready']}")
    print(f"Modules OK: {report['modules_ok']}")
    print(f"Reference fusion OK: {report['reference_fusion_ok']}")
    print(f"Experience modes OK: {report['experience_modes_ok']}")
    print(f"Smooth UX OK: {report['smooth_ux_ok']}")
    print(f"Voice context OK: {report['voice_context_ok']}")

    print("\nModule checks:")
    for item in report["module_checks"]:
        status = "OK" if item["ok"] else "FAIL"
        print(f"- {status}: {item['module']}")
        if item["stderr"] and not item["ok"]:
            print(item["stderr"][:1200])

    print("\nDetails:")
    for key, value in report.get("details", {}).items():
        print(f"- {key}: {value}")


if __name__ == "__main__":
    show_v24_gate()
