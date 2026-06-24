import json
import subprocess
from datetime import datetime


try:
    from seed_config import SEED_V29_GATE_REPORT_FILE, V29_REQUIRED_MODULES
except Exception:
    SEED_V29_GATE_REPORT_FILE = "seed_v29_gate_report.json"
    V29_REQUIRED_MODULES = [
        "seed_mission_control.py",
        "seed_release_orchestrator.py",
        "seed_voice_ux_pack.py",
        "seed_self_repair_planner.py",
        "seed_command_memory.py",
        "seed_local_app_manifest.py",
        "seed_v29_mission_gate.py"
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


def run_v29_gate():
    module_checks = [compile_module(module) for module in V29_REQUIRED_MODULES]
    modules_ok = all(item["ok"] for item in module_checks)

    mission_ok = False
    release_orchestrator_ok = False
    voice_ux_ok = False
    self_repair_ok = False
    command_memory_ok = False
    app_manifest_ok = False
    details = {}

    try:
        from seed_mission_control import mission_control_snapshot
        mission = mission_control_snapshot()
        mission_ok = mission.get("ok") is True and "health" in mission
        details["mission_health"] = mission.get("health")
    except Exception as error:
        details["mission_error"] = str(error)

    try:
        from seed_release_orchestrator import release_orchestrator_context
        ctx = release_orchestrator_context()
        release_orchestrator_ok = "safe" in ctx.lower()
        details["release_orchestrator_context_chars"] = len(ctx)
    except Exception as error:
        details["release_orchestrator_error"] = str(error)

    try:
        from seed_voice_ux_pack import voice_ux_snapshot, classify_voice_intent, add_transcript_journal
        voice = voice_ux_snapshot()
        intent_ok = classify_voice_intent("open cockpit") == "cockpit"
        journal = add_transcript_journal("v2.9 gate transcript test", "test", "safe")
        voice_ux_ok = voice.get("ok") is True and intent_ok and journal.get("intent") in ["chat", "voice_debug"]
        details["voice_next_patch"] = voice.get("next_voice_patch")
    except Exception as error:
        details["voice_ux_error"] = str(error)

    try:
        from seed_self_repair_planner import build_self_repair_plan
        repair = build_self_repair_plan()
        self_repair_ok = "probes" in repair and "repair_steps" in repair
        details["self_repair_ok"] = repair.get("ok")
        details["self_repair_failures"] = len(repair.get("failures", []))
    except Exception as error:
        details["self_repair_error"] = str(error)

    try:
        from seed_command_memory import suggest_commands
        suggestions = suggest_commands("release gates")
        command_memory_ok = suggestions.get("ok") is True and "/release-check" in suggestions.get("commands", [])
        details["command_suggestions"] = suggestions.get("commands", [])[:5]
    except Exception as error:
        details["command_memory_error"] = str(error)

    try:
        from seed_local_app_manifest import build_app_manifest
        manifest = build_app_manifest()
        app_manifest_ok = manifest.get("ok") is True and "python" in manifest.get("tools", {})
        details["app_manifest_python"] = manifest.get("tools", {}).get("python")
    except Exception as error:
        details["app_manifest_error"] = str(error)

    ready = all([
        modules_ok,
        mission_ok,
        release_orchestrator_ok,
        voice_ux_ok,
        self_repair_ok,
        command_memory_ok,
        app_manifest_ok
    ])

    report = {
        "created_at": now_timestamp(),
        "release": "Seed v2.9.0 — Mission Control MegaPack",
        "ready": ready,
        "modules_ok": modules_ok,
        "mission_control_ok": mission_ok,
        "release_orchestrator_ok": release_orchestrator_ok,
        "voice_ux_ok": voice_ux_ok,
        "self_repair_ok": self_repair_ok,
        "command_memory_ok": command_memory_ok,
        "app_manifest_ok": app_manifest_ok,
        "module_checks": module_checks,
        "details": details
    }

    with open(SEED_V29_GATE_REPORT_FILE, "w") as file:
        json.dump(report, file, indent=4)

    return report


def show_v29_gate():
    report = run_v29_gate()

    print("\n=== SEED v2.9.0 MISSION CONTROL MEGAPACK GATE ===")
    print(f"Ready: {report['ready']}")
    print(f"Modules OK: {report['modules_ok']}")
    print(f"Mission Control OK: {report['mission_control_ok']}")
    print(f"Release Orchestrator OK: {report['release_orchestrator_ok']}")
    print(f"Voice UX OK: {report['voice_ux_ok']}")
    print(f"Self-Repair OK: {report['self_repair_ok']}")
    print(f"Command Memory OK: {report['command_memory_ok']}")
    print(f"App Manifest OK: {report['app_manifest_ok']}")

    print("\nModule checks:")
    for item in report["module_checks"]:
        status = "OK" if item["ok"] else "FAIL"
        print(f"- {status}: {item['module']}")
        if item["stderr"] and not item["ok"]:
            print(item["stderr"][:1200])


if __name__ == "__main__":
    show_v29_gate()
