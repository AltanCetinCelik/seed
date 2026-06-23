import json
import subprocess
from datetime import datetime


try:
    from seed_config import SEED_V21_GATE_REPORT_FILE, V21_REQUIRED_MODULES
except Exception:
    SEED_V21_GATE_REPORT_FILE = "seed_v21_gate_report.json"
    V21_REQUIRED_MODULES = [
        "seed_active_voice_daemon.py",
        "seed_agent_tool_profiles.py",
        "seed_agent_executor.py",
        "seed_agent_orchestrator.py",
        "seed_v21_capability_gate.py"
    ]


try:
    from seed_active_voice_daemon import active_voice_check_data
    ACTIVE_VOICE_AVAILABLE = True
except Exception:
    ACTIVE_VOICE_AVAILABLE = False


try:
    from seed_agent_tool_profiles import agent_tool_profiles_data
    PROFILES_AVAILABLE = True
except Exception:
    PROFILES_AVAILABLE = False


try:
    from seed_agent_orchestrator import build_agent_task
    ORCHESTRATOR_AVAILABLE = True
except Exception:
    ORCHESTRATOR_AVAILABLE = False


try:
    from seed_v2_stable_release import run_v2_stable_gate
    V2_STABLE_AVAILABLE = True
except Exception:
    V2_STABLE_AVAILABLE = False


try:
    from seed_integration_gate import run_integration_gate
    INTEGRATION_AVAILABLE = True
except Exception:
    INTEGRATION_AVAILABLE = False


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def compile_module(module):
    result = subprocess.run(
        ["python", "-m", "py_compile", module],
        capture_output=True,
        text=True
    )
    return {
        "module": module,
        "ok": result.returncode == 0,
        "stderr": result.stderr[-3000:]
    }


def run_v21_gate():
    module_checks = [compile_module(module) for module in V21_REQUIRED_MODULES]
    modules_ok = all(item["ok"] for item in module_checks)

    active_voice = active_voice_check_data() if ACTIVE_VOICE_AVAILABLE else {"active_voice_ready": False}
    active_voice_ready = bool(active_voice.get("active_voice_ready"))

    profiles = agent_tool_profiles_data(refresh=True) if PROFILES_AVAILABLE else {"profiles": [], "local_repos": []}
    profile_count = len(profiles.get("profiles", []))
    local_repo_count = len(profiles.get("local_repos", []))
    agent_profile_ok = profile_count >= 5

    samples = []
    if ORCHESTRATOR_AVAILABLE:
        for task in [
            "Fix a bug in Seed and run tests",
            "Use browser automation to research a webpage",
            "Upgrade memory with vector search",
            "Add active voice listener"
        ]:
            samples.append(build_agent_task(task))

    orchestrator_ok = ORCHESTRATOR_AVAILABLE and len(samples) >= 4

    v2_stable = run_v2_stable_gate() if V2_STABLE_AVAILABLE else {"stable_ready": False}
    v2_stable_ok = bool(v2_stable.get("stable_ready"))

    integration = run_integration_gate() if INTEGRATION_AVAILABLE else {"ready": False}
    integration_ok = bool(integration.get("ready"))

    ready = (
        modules_ok
        and active_voice_ready
        and agent_profile_ok
        and orchestrator_ok
        and v2_stable_ok
        and integration_ok
    )

    report = {
        "created_at": now_timestamp(),
        "release": "Seed v2.1.0 — Active Voice + Agent Arsenal Activation",
        "ready": ready,
        "modules_ok": modules_ok,
        "active_voice_ready": active_voice_ready,
        "agent_profile_ok": agent_profile_ok,
        "orchestrator_ok": orchestrator_ok,
        "v2_stable_ok": v2_stable_ok,
        "integration_ok": integration_ok,
        "profile_count": profile_count,
        "local_repo_count": local_repo_count,
        "module_checks": module_checks,
        "active_voice": active_voice,
        "agent_profiles": profiles,
        "orchestrator_samples": samples,
        "v2_stable": v2_stable,
        "integration": integration
    }

    with open(SEED_V21_GATE_REPORT_FILE, "w") as file:
        json.dump(report, file, indent=4)

    return report


def show_v21_gate():
    report = run_v21_gate()

    print("\n=== SEED v2.1.0 CAPABILITY GATE ===")
    print(f"Ready: {report['ready']}")
    print(f"Modules OK: {report['modules_ok']}")
    print(f"Active voice ready: {report['active_voice_ready']}")
    print(f"Agent profiles OK: {report['agent_profile_ok']}")
    print(f"Orchestrator OK: {report['orchestrator_ok']}")
    print(f"V2 stable OK: {report['v2_stable_ok']}")
    print(f"Integration OK: {report['integration_ok']}")
    print(f"Profiles: {report['profile_count']}")
    print(f"Local repos found: {report['local_repo_count']}")

    print("\nModule checks:")
    for item in report["module_checks"]:
        status = "OK" if item["ok"] else "FAIL"
        print(f"- {status}: {item['module']}")
        if item["stderr"] and not item["ok"]:
            print(item["stderr"][:1200])

    if not report["active_voice_ready"]:
        print("\nActive voice blocker:")
        av = report.get("active_voice", {})
        if not av.get("ffmpeg_available"):
            print("- ffmpeg missing: brew install ffmpeg")
        if not av.get("faster_whisper_available"):
            print("- faster-whisper missing: python -m pip install faster-whisper")
        if not av.get("tts_available"):
            print("- TTS unavailable")

    print("\nOrchestrator samples:")
    for sample in report["orchestrator_samples"]:
        print(f"- {sample.get('task')} => {sample.get('capability')} via {sample.get('selected_tool')}")


if __name__ == "__main__":
    show_v21_gate()
