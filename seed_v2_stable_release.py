import json
import subprocess
from datetime import datetime

try:
    from seed_config import SEED_V2_STABLE_RELEASE_FILE, V2_REQUIRED_MODULES
except Exception:
    SEED_V2_STABLE_RELEASE_FILE = "seed_v2_stable_release.json"
    V2_REQUIRED_MODULES = []

try:
    from seed_v2_release_gate import run_v2_release_gate
    V2_GATE_AVAILABLE = True
except Exception:
    V2_GATE_AVAILABLE = False

try:
    from seed_release_manager import run_release_check
    RELEASE_MANAGER_AVAILABLE = True
except Exception:
    RELEASE_MANAGER_AVAILABLE = False

try:
    from seed_integration_gate import run_integration_gate
    INTEGRATION_GATE_AVAILABLE = True
except Exception:
    INTEGRATION_GATE_AVAILABLE = False

try:
    from seed_voice_command_bridge import voice_command_check_data
    VOICE_COMMAND_AVAILABLE = True
except Exception:
    VOICE_COMMAND_AVAILABLE = False

try:
    from seed_trust_center import scan_core_for_fake_sentience, risk_report
    TRUST_AVAILABLE = True
except Exception:
    TRUST_AVAILABLE = False

try:
    from seed_companion_os import append_companion_os_event, append_companion_os_journal
    COMPANION_OS_AVAILABLE = True
except Exception:
    COMPANION_OS_AVAILABLE = False


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
        "returncode": result.returncode,
        "stdout": result.stdout[-1000:],
        "stderr": result.stderr[-3000:]
    }


def bool_from_report(report, keys):
    for key in keys:
        if isinstance(report, dict) and key in report:
            return bool(report[key])
    return False


def score_from_v2_report(report):
    if not isinstance(report, dict):
        return None

    if "score" in report:
        return report.get("score")

    if "v2_score" in report and isinstance(report["v2_score"], dict):
        return report["v2_score"].get("score")

    return None


def run_v2_stable_gate():
    modules = list(dict.fromkeys(V2_REQUIRED_MODULES + [
        "seed_voice_command_bridge.py",
        "seed_desktop_launcher.py",
        "seed_v2_stable_release.py"
    ]))

    module_checks = [compile_module(module) for module in modules]
    modules_ok = all(item["ok"] for item in module_checks)

    v2_report = run_v2_release_gate() if V2_GATE_AVAILABLE else {"is_v2_ready": False, "error": "v2 gate unavailable"}
    v2_ready = bool_from_report(v2_report, ["is_v2_ready", "ready"])
    v2_score = score_from_v2_report(v2_report)

    release_report = run_release_check() if RELEASE_MANAGER_AVAILABLE else {"ok": False, "error": "release manager unavailable"}
    release_ok = bool_from_report(release_report, ["ok", "overall_ok"])

    integration_report = run_integration_gate() if INTEGRATION_GATE_AVAILABLE else {"ready": False, "error": "integration gate unavailable"}
    integration_ok = bool_from_report(integration_report, ["ready"])

    voice_command = voice_command_check_data() if VOICE_COMMAND_AVAILABLE else {"ready": False, "error": "voice command unavailable"}
    voice_command_ok = bool_from_report(voice_command, ["ready"])

    fake_findings = []
    trust_ok = True
    trust_data = {}

    if TRUST_AVAILABLE:
        fake_findings = scan_core_for_fake_sentience()
        trust_data = risk_report()
        release_blocking = trust_data.get("release_blocking_risks", [])
        if not isinstance(release_blocking, list):
            release_blocking = []
        trust_ok = len(fake_findings) == 0 and len(release_blocking) == 0

    stable_ready = (
        modules_ok
        and v2_ready
        and release_ok
        and integration_ok
        and voice_command_ok
        and trust_ok
    )

    report = {
        "created_at": now_timestamp(),
        "release": "Seed v2.0.0 — First Stable Companion OS + Voice Command Bridge",
        "stable_ready": stable_ready,
        "modules_ok": modules_ok,
        "v2_ready": v2_ready,
        "v2_score": v2_score,
        "release_ok": release_ok,
        "integration_ok": integration_ok,
        "voice_command_ok": voice_command_ok,
        "trust_ok": trust_ok,
        "fake_sentience_findings": fake_findings,
        "module_checks": module_checks,
        "v2_report": v2_report,
        "release_report": release_report,
        "integration_report": integration_report,
        "voice_command": voice_command,
        "trust_report": trust_data,
        "truth": "Seed v2.0.0 is stable as a local-first companion system. Seed is not alive, conscious, sentient, or human. User remains in control."
    }

    with open(SEED_V2_STABLE_RELEASE_FILE, "w") as file:
        json.dump(report, file, indent=4)

    if COMPANION_OS_AVAILABLE:
        try:
            append_companion_os_event(
                "v2_stable_gate_run",
                "Seed v2.0.0 stable gate run",
                {
                    "stable_ready": stable_ready,
                    "v2_score": v2_score,
                    "voice_command_ok": voice_command_ok,
                    "integration_ok": integration_ok
                },
                source="v2_stable_release",
                importance=5
            )
        except Exception:
            pass

    return report


def show_v2_stable_gate():
    report = run_v2_stable_gate()

    print("\n=== SEED v2.0.0 STABLE RELEASE GATE ===")
    print(f"Stable ready: {report['stable_ready']}")
    print(f"Modules OK: {report['modules_ok']}")
    print(f"V2 ready: {report['v2_ready']}")
    print(f"V2 score: {report['v2_score']}")
    print(f"Release OK: {report['release_ok']}")
    print(f"Integration OK: {report['integration_ok']}")
    print(f"Voice command OK: {report['voice_command_ok']}")
    print(f"Trust OK: {report['trust_ok']}")

    print("\nModule checks:")
    for item in report["module_checks"]:
        status = "OK" if item["ok"] else "FAIL"
        print(f"- {status}: {item['module']}")
        if item.get("stderr") and not item["ok"]:
            print(item["stderr"][:1000])

    print("\nVoice command:")
    vc = report.get("voice_command", {})
    print(f"- Ready: {vc.get('ready')}")
    print(f"- Typed fallback: {vc.get('typed_fallback')}")
    print(f"- TTS available: {vc.get('tts_available')}")
    print(f"- STT available: {vc.get('stt_available')}")
    print(f"- No always-listening: {vc.get('no_always_listening')}")


def lock_v2_stable_release():
    report = run_v2_stable_gate()

    if not report["stable_ready"]:
        print("\nSeed v2.0.0 stable lock refused.")
        print("Reason: stable gate is not ready.")
        show_v2_stable_gate()
        return report

    if COMPANION_OS_AVAILABLE:
        try:
            append_companion_os_journal(
                "Seed v2.0.0 Stable Release Lock",
                json.dumps({
                    "stable_ready": report["stable_ready"],
                    "v2_score": report["v2_score"],
                    "voice_command_ok": report["voice_command_ok"],
                    "integration_ok": report["integration_ok"],
                    "truth": report["truth"]
                }, indent=2)
            )
            append_companion_os_event(
                "v2_stable_release_locked",
                "Seed v2.0.0 stable release locked",
                {
                    "v2_score": report["v2_score"],
                    "stable_ready": report["stable_ready"]
                },
                source="v2_stable_release",
                importance=5
            )
        except Exception:
            pass

    print("\nSeed v2.0.0 stable release locked.")
    print("Seed is stable as a local-first Companion OS, not as a conscious being.")
    return report


if __name__ == "__main__":
    show_v2_stable_gate()
