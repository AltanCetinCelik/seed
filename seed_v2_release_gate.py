import json
import os
import subprocess
from datetime import datetime


try:
    from seed_config import V2_REQUIRED_MODULES, COMPANION_OS_V2_TARGET_SCORE
except Exception:
    V2_REQUIRED_MODULES = [
        "seed_companion_os.py",
        "seed_os_migrations.py",
        "seed_os_registry.py",
        "seed_os_bridge.py",
        "seed_trace_engine.py",
        "seed_tool_manifest_v2.py",
        "seed_trust_center.py",
        "seed_memory_backend.py",
        "seed_document_registry.py",
        "seed_continuity_engine.py",
        "seed_workflow_engine.py",
        "seed_microagent_council.py",
        "seed_self_improvement_engine.py",
        "seed_release_manager.py",
        "seed_world_engine.py",
        "seed_avatar_state.py",
        "seed_voice_session.py",
        "seed_companion_cockpit.py",
        "seed_companion_os_context.py",
        "seed_companion_os_commands.py",
        "seed_v2_release_gate.py"
    ]
    COMPANION_OS_V2_TARGET_SCORE = 85


from seed_companion_os import (
    calculate_companion_os_v2_score,
    load_companion_os_state,
    append_companion_os_event,
    append_companion_os_journal
)


try:
    from seed_os_registry import validate_os_registry
    REGISTRY_AVAILABLE = True
except Exception:
    REGISTRY_AVAILABLE = False


try:
    from seed_tool_manifest_v2 import validate_tool_manifest
    TOOL_MANIFEST_AVAILABLE = True
except Exception:
    TOOL_MANIFEST_AVAILABLE = False


try:
    from seed_trust_center import scan_core_for_fake_sentience, risk_report
    TRUST_AVAILABLE = True
except Exception:
    TRUST_AVAILABLE = False


try:
    from seed_trace_engine import append_trace, trace_stats
    TRACE_AVAILABLE = True
except Exception:
    TRACE_AVAILABLE = False


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def compile_module(path):
    if not os.path.exists(path):
        return {
            "path": path,
            "ok": False,
            "status": "missing",
            "stderr": "File missing."
        }

    result = subprocess.run(
        ["python", "-m", "py_compile", path],
        capture_output=True,
        text=True
    )

    return {
        "path": path,
        "ok": result.returncode == 0,
        "status": "compiled" if result.returncode == 0 else "compile_failed",
        "stdout": result.stdout,
        "stderr": result.stderr
    }


def run_v2_module_checks():
    return [compile_module(path) for path in V2_REQUIRED_MODULES]


def git_status_short():
    result = subprocess.run(
        "git status --short",
        shell=True,
        capture_output=True,
        text=True
    )

    return {
        "ok": result.returncode == 0,
        "stdout": result.stdout,
        "stderr": result.stderr
    }


def run_v2_release_gate():
    score = calculate_companion_os_v2_score(save=True)
    module_checks = run_v2_module_checks()
    missing_or_failed = [
        check for check in module_checks
        if not check["ok"]
    ]

    registry_failures = []
    tool_failures = []
    fake_sentience_findings = []
    trust_risks = {}
    trace_data = {}

    if REGISTRY_AVAILABLE:
        try:
            registry_failures = validate_os_registry()
        except Exception as error:
            registry_failures = [str(error)]
    else:
        registry_failures = ["OS registry unavailable."]

    if TOOL_MANIFEST_AVAILABLE:
        try:
            tool_failures = validate_tool_manifest()
        except Exception as error:
            tool_failures = [str(error)]
    else:
        tool_failures = ["Tool Manifest v2 unavailable."]

    if TRUST_AVAILABLE:
        try:
            fake_sentience_findings = scan_core_for_fake_sentience()
        except Exception as error:
            fake_sentience_findings = [{"error": str(error)}]

        try:
            trust_risks = risk_report()
        except Exception as error:
            trust_risks = {"error": str(error)}
    else:
        fake_sentience_findings = [{"error": "Trust Center unavailable."}]
        trust_risks = {"error": "Trust Center unavailable."}

    if TRACE_AVAILABLE:
        try:
            trace_data = trace_stats()
        except Exception as error:
            trace_data = {"error": str(error)}
    else:
        trace_data = {"error": "Trace engine unavailable."}

    git = git_status_short()

    blockers = []

    if missing_or_failed:
        blockers.append(f"{len(missing_or_failed)} required modules missing or failing compile.")

    if registry_failures:
        blockers.append(f"OS registry has {len(registry_failures)} issue(s).")

    if tool_failures:
        blockers.append(f"Tool Manifest v2 has {len(tool_failures)} issue(s).")

    if fake_sentience_findings:
        blockers.append(f"Fake-sentience scan found {len(fake_sentience_findings)} issue(s).")

    if score["blockers"]:
        blockers.extend(score["blockers"])

    if score["score"] < COMPANION_OS_V2_TARGET_SCORE:
        blockers.append(
            f"V2 score {score['score']} is below target {COMPANION_OS_V2_TARGET_SCORE}."
        )

    report = {
        "created_at": now_timestamp(),
        "score": score,
        "module_checks": module_checks,
        "registry_failures": registry_failures,
        "tool_manifest_failures": tool_failures,
        "fake_sentience_findings": fake_sentience_findings,
        "trust_risks": trust_risks,
        "trace_stats": trace_data,
        "git_status_short": git,
        "blockers": blockers,
        "is_v2_ready": len(blockers) == 0
    }

    append_companion_os_event(
        "v2_release_gate_run",
        "V2 release gate run",
        {
            "is_v2_ready": report["is_v2_ready"],
            "blocker_count": len(blockers),
            "score": score["score"]
        },
        source="v2_release_gate",
        importance=5
    )

    append_companion_os_journal(
        "V2 release gate report",
        json.dumps(report, indent=2)
    )

    if TRACE_AVAILABLE:
        try:
            append_trace(
                trace_type="release_trace",
                title="V2 release gate run",
                summary=json.dumps({
                    "is_v2_ready": report["is_v2_ready"],
                    "blockers": blockers,
                    "score": score
                }, indent=2),
                sources=["v2_release_gate", "trust_center", "tool_manifest_v2", "os_registry"],
                decision="passed" if report["is_v2_ready"] else "blocked",
                risk="medium"
            )
        except Exception:
            pass

    return report


def show_v2_check():
    report = run_v2_release_gate()

    print("\n=== SEED v2.0.0 RELEASE GATE ===")
    print(f"Score: {report['score']['score']} / {report['score']['target']}")
    print(f"Ready: {report['is_v2_ready']}")

    print("\nPillar scores:")
    for pillar, score in report["score"]["scores"].items():
        print(f"- {pillar}: {score}/10")

    print("\nBlockers:")
    if not report["blockers"]:
        print("- none")
    else:
        for blocker in report["blockers"]:
            print(f"- {blocker}")

    print("\nModule checks:")
    for check in report["module_checks"]:
        status = "OK" if check["ok"] else "FAIL"
        print(f"- {status}: {check['path']} [{check['status']}]")


def show_v2_blockers():
    report = run_v2_release_gate()

    print("\n=== V2 BLOCKERS ===")

    if not report["blockers"]:
        print("No blockers. Seed may be ready for v2 label after manual review.")
        return

    for blocker in report["blockers"]:
        print(f"- {blocker}")

    print("\nFailed/missing modules:")
    for check in report["module_checks"]:
        if not check["ok"]:
            print(f"- {check['path']}: {check['status']}")
            if check.get("stderr"):
                print(check["stderr"])


def show_v2_pass_report():
    report = run_v2_release_gate()

    print("\n=== V2 PASS REPORT ===")
    print(json.dumps(report, indent=4)[:12000])


def generate_v2_release_notes():
    state = load_companion_os_state()
    report = run_v2_release_gate()

    notes = f"""
# Seed v2.0.0 Release Notes Draft

Generated: {now_timestamp()}

## Current result

Ready: {report['is_v2_ready']}
Score: {report['score']['score']} / {report['score']['target']}

## What v1.17.0 added

Seed Companion OS Alpha added:

- Companion OS state
- OS migrations
- OS registry
- OS bridge
- Trace Engine
- Trust Center
- Tool Manifest v2
- Memory Backend
- Document Registry
- Continuity Engine
- Workflow Engine
- Microagent Council
- Self-Improvement Engine
- Release Manager
- Seed World
- Memory Garden
- Avatar State
- Voice Session Alpha
- Companion Cockpit
- V2 Release Gate

## Hard truth

Seed is not alive.
Seed is not conscious.
Seed is not human.

Seed is a local-first companion system with memory, continuity, symbolic world state, voice alpha, safe agency, and approval-gated self-improvement.

## V2 blockers

{chr(10).join("- " + blocker for blocker in report['blockers']) if report['blockers'] else "- none"}

## Mission

{state.get('mission')}
"""

    append_companion_os_journal("V2 release notes draft", notes)

    print(notes)
    return notes


if __name__ == "__main__":
    show_v2_check()
