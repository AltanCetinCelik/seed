import json
import os
import subprocess
from datetime import datetime


try:
    from seed_config import (
        SEED_SELF_IMPROVEMENT_HARDENING_FILE,
        V2_REQUIRED_MODULES,
        SELF_IMPROVEMENT_TEST_COMMANDS
    )
except Exception:
    SEED_SELF_IMPROVEMENT_HARDENING_FILE = "seed_self_improvement_hardening.json"
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
        "seed_v2_release_gate.py",
        "seed_v2_hardening_metrics.py",
        "seed_agency_hardening.py",
        "seed_self_improvement_hardening.py"
    ]
    SELF_IMPROVEMENT_TEST_COMMANDS = [
        f"python -m py_compile {path}"
        for path in V2_REQUIRED_MODULES
    ]


try:
    from seed_companion_os import (
        load_companion_os_state,
        save_companion_os_state,
        append_companion_os_event,
        append_companion_os_journal
    )
    COMPANION_OS_AVAILABLE = True
except Exception:
    COMPANION_OS_AVAILABLE = False


try:
    from seed_trace_engine import append_trace
    TRACE_AVAILABLE = True
except Exception:
    TRACE_AVAILABLE = False


try:
    from seed_v2_hardening_metrics import mark_hardening_signal
    HARDENING_METRICS_AVAILABLE = True
except Exception:
    HARDENING_METRICS_AVAILABLE = False


try:
    from seed_self_improvement_engine import impact_check, build_dependency_graph
    BASE_SELF_IMPROVEMENT_AVAILABLE = True
except Exception:
    BASE_SELF_IMPROVEMENT_AVAILABLE = False


try:
    from seed_os_registry import validate_os_registry, registry_stats
    REGISTRY_AVAILABLE = True
except Exception:
    REGISTRY_AVAILABLE = False


try:
    from seed_tool_manifest_v2 import validate_tool_manifest, get_tool_manifest
    TOOL_MANIFEST_AVAILABLE = True
except Exception:
    TOOL_MANIFEST_AVAILABLE = False


try:
    from seed_trust_center import scan_core_for_fake_sentience, risk_report
    TRUST_AVAILABLE = True
except Exception:
    TRUST_AVAILABLE = False


try:
    from seed_llm import ask_llm
    LLM_AVAILABLE = True
except Exception:
    LLM_AVAILABLE = False


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def load_json(path, default):
    try:
        with open(path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return default() if callable(default) else default
    except json.JSONDecodeError:
        return default() if callable(default) else default


def save_json(path, data):
    with open(path, "w") as file:
        json.dump(data, file, indent=4)


def default_hardening_state():
    return {
        "created_at": now_timestamp(),
        "updated_at": now_timestamp(),
        "version": "v1.18.0",
        "purpose": "Self-improvement hardening evidence for Seed.",
        "rule": (
            "Seed may inspect, plan, test, and propose repairs. "
            "Seed must not silently edit files or apply risky changes."
        ),
        "test_matrix": [],
        "module_health_matrix": [],
        "repair_plans": [],
        "release_readiness_reports": [],
        "last_full_test": None,
        "last_health_matrix": None,
        "last_repair_plan": None,
        "last_release_readiness": None
    }


def load_hardening_state():
    return load_json(SEED_SELF_IMPROVEMENT_HARDENING_FILE, default_hardening_state)


def save_hardening_state(state):
    state["updated_at"] = now_timestamp()
    save_json(SEED_SELF_IMPROVEMENT_HARDENING_FILE, state)


def mark_self_signal(key, value=True):
    if HARDENING_METRICS_AVAILABLE:
        try:
            mark_hardening_signal("self_improvement", key, value)
        except Exception:
            pass


def module_exists(path):
    return os.path.exists(path) and os.path.isfile(path)


def compile_module(path):
    if not module_exists(path):
        return {
            "module": path,
            "exists": False,
            "compiled": False,
            "returncode": None,
            "stdout": "",
            "stderr": "missing file",
            "health": "missing"
        }

    result = subprocess.run(
        ["python", "-m", "py_compile", path],
        capture_output=True,
        text=True
    )

    return {
        "module": path,
        "exists": True,
        "compiled": result.returncode == 0,
        "returncode": result.returncode,
        "stdout": result.stdout[-2000:],
        "stderr": result.stderr[-4000:],
        "health": "ok" if result.returncode == 0 else "compile_failed"
    }


def run_command(command):
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True
    )

    return {
        "command": command,
        "returncode": result.returncode,
        "ok": result.returncode == 0,
        "stdout": result.stdout[-3000:],
        "stderr": result.stderr[-5000:]
    }


def build_module_health_matrix():
    modules = list(dict.fromkeys(V2_REQUIRED_MODULES))
    matrix = []

    for module in modules:
        matrix.append(compile_module(module))

    ok_count = len([item for item in matrix if item["compiled"]])
    missing_count = len([item for item in matrix if item["health"] == "missing"])
    failed_count = len([item for item in matrix if item["health"] == "compile_failed"])

    report = {
        "created_at": now_timestamp(),
        "total": len(matrix),
        "ok": ok_count,
        "missing": missing_count,
        "failed": failed_count,
        "matrix": matrix
    }

    state = load_hardening_state()
    state["module_health_matrix"].append(report)
    state["last_health_matrix"] = report
    save_hardening_state(state)

    if missing_count == 0 and failed_count == 0:
        mark_self_signal("module_health_matrix", True)
    else:
        mark_self_signal("module_health_matrix", False)

    if COMPANION_OS_AVAILABLE:
        try:
            append_companion_os_event(
                "module_health_matrix_built",
                "Self-improvement module health matrix built",
                {
                    "total": report["total"],
                    "ok": ok_count,
                    "missing": missing_count,
                    "failed": failed_count
                },
                source="self_improvement_hardening",
                importance=4
            )
        except Exception:
            pass

    return report


def show_module_health_matrix():
    report = build_module_health_matrix()

    print("\n=== MODULE HEALTH MATRIX ===")
    print(f"Total: {report['total']}")
    print(f"OK: {report['ok']}")
    print(f"Missing: {report['missing']}")
    print(f"Failed: {report['failed']}")

    print("\nModules:")
    for item in report["matrix"]:
        status = "OK" if item["compiled"] else "FAIL"
        print(f"- {status}: {item['module']} [{item['health']}]")
        if item.get("stderr") and not item["compiled"]:
            print(item["stderr"][:1000])


def build_test_matrix():
    commands = list(dict.fromkeys(SELF_IMPROVEMENT_TEST_COMMANDS))

    # Ensure the current v1.18 hardening module is always checked.
    current_compile = "python -m py_compile seed_self_improvement_hardening.py"
    if current_compile not in commands:
        commands.append(current_compile)

    results = []

    for command in commands:
        results.append(run_command(command))

    ok_count = len([item for item in results if item["ok"]])
    fail_count = len(results) - ok_count

    report = {
        "created_at": now_timestamp(),
        "total": len(results),
        "ok": ok_count,
        "failed": fail_count,
        "results": results
    }

    state = load_hardening_state()
    state["test_matrix"].append(report)
    state["last_full_test"] = report
    save_hardening_state(state)

    mark_self_signal("test_matrix", True)
    mark_self_signal("safe_tests_passing", fail_count == 0)

    if COMPANION_OS_AVAILABLE:
        try:
            append_companion_os_event(
                "self_improvement_test_matrix_run",
                "Self-improvement test matrix run",
                {
                    "total": report["total"],
                    "ok": ok_count,
                    "failed": fail_count
                },
                source="self_improvement_hardening",
                importance=4
            )
        except Exception:
            pass

    if TRACE_AVAILABLE:
        try:
            append_trace(
                trace_type="self_edit_trace",
                title="Self-improvement test matrix run",
                summary=json.dumps({
                    "total": report["total"],
                    "ok": ok_count,
                    "failed": fail_count
                }, indent=2),
                sources=["self_improvement_hardening", "SWE-agent", "mini-SWE-agent"],
                decision="tested",
                risk="low"
            )
        except Exception:
            pass

    return report


def show_test_matrix():
    report = build_test_matrix()

    print("\n=== SELF-IMPROVEMENT TEST MATRIX ===")
    print(f"Total: {report['total']}")
    print(f"OK: {report['ok']}")
    print(f"Failed: {report['failed']}")

    for item in report["results"]:
        status = "OK" if item["ok"] else "FAIL"
        print(f"\n{status}: {item['command']}")
        if item["stderr"] and not item["ok"]:
            print("STDERR:")
            print(item["stderr"][:2000])


def build_repair_plan(chat_state=None):
    health = build_module_health_matrix()
    tests = build_test_matrix()

    registry_failures = []
    tool_failures = []
    fake_sentience_findings = []
    trust_report = None

    if REGISTRY_AVAILABLE:
        try:
            registry_failures = validate_os_registry()
        except Exception as error:
            registry_failures = [str(error)]

    if TOOL_MANIFEST_AVAILABLE:
        try:
            tool_failures = validate_tool_manifest()
        except Exception as error:
            tool_failures = [str(error)]

    if TRUST_AVAILABLE:
        try:
            fake_sentience_findings = scan_core_for_fake_sentience()
        except Exception as error:
            fake_sentience_findings = [{"error": str(error)}]

        try:
            trust_report = risk_report()
        except Exception as error:
            trust_report = {"error": str(error)}

    failed_modules = [
        item for item in health["matrix"]
        if not item["compiled"]
    ]

    failed_tests = [
        item for item in tests["results"]
        if not item["ok"]
    ]

    raw_report = {
        "created_at": now_timestamp(),
        "failed_modules": failed_modules,
        "failed_tests": failed_tests,
        "registry_failures": registry_failures,
        "tool_manifest_failures": tool_failures,
        "fake_sentience_findings": fake_sentience_findings,
        "trust_report": trust_report
    }

    if LLM_AVAILABLE:
        prompt = f"""
You are Seed's Self-Improvement Hardening repair planner.

Seed is not alive or conscious.
Seed may inspect, test, and plan repairs.
Seed must not silently edit or apply changes.

Given this report, produce a repair plan:
{json.dumps(raw_report, indent=2)}

Output:
1. critical blockers
2. likely cause
3. exact files to inspect
4. safe fix order
5. tests to run
6. rollback plan
7. whether this blocks v2
"""
        plan_text = ask_llm(prompt, task_type="debug", runtime_context=chat_state)

        if isinstance(plan_text, str) and "timed out" in plan_text.lower():
            plan_text = fallback_repair_plan(raw_report)
    else:
        plan_text = fallback_repair_plan(raw_report)

    plan = {
        "created_at": now_timestamp(),
        "raw_report": raw_report,
        "plan": plan_text
    }

    state = load_hardening_state()
    state["repair_plans"].append(plan)
    state["last_repair_plan"] = plan
    save_hardening_state(state)

    mark_self_signal("repair_planner", True)

    if COMPANION_OS_AVAILABLE:
        try:
            append_companion_os_journal(
                "Self-improvement repair plan",
                plan_text
            )
            append_companion_os_event(
                "self_improvement_repair_plan_created",
                "Self-improvement repair plan created",
                {
                    "failed_modules": len(failed_modules),
                    "failed_tests": len(failed_tests)
                },
                source="self_improvement_hardening",
                importance=4
            )
        except Exception:
            pass

    if TRACE_AVAILABLE:
        try:
            append_trace(
                trace_type="self_edit_trace",
                title="Repair plan generated",
                summary=plan_text,
                sources=["self_improvement_hardening", "Aider", "Cline", "SWE-agent"],
                decision="planned",
                risk="medium",
                related_files=[item.get("module") for item in failed_modules]
            )
        except Exception:
            pass

    return plan


def fallback_repair_plan(raw_report):
    lines = []
    lines.append("=== SELF-IMPROVEMENT REPAIR PLAN ===")
    lines.append("")
    lines.append("Seed is allowed to inspect, test, and plan. It must not silently edit files.")
    lines.append("")

    failed_modules = raw_report.get("failed_modules", [])
    failed_tests = raw_report.get("failed_tests", [])

    if not failed_modules and not failed_tests:
        lines.append("No compile/test failures found.")
    else:
        lines.append("Critical blockers:")

        for item in failed_modules:
            lines.append(f"- Module problem: {item.get('module')} [{item.get('health')}]")

        for item in failed_tests:
            lines.append(f"- Test problem: {item.get('command')}")

    if raw_report.get("registry_failures"):
        lines.append("")
        lines.append("Registry issues:")
        for failure in raw_report.get("registry_failures", []):
            lines.append(f"- {failure}")

    if raw_report.get("tool_manifest_failures"):
        lines.append("")
        lines.append("Tool manifest issues:")
        for failure in raw_report.get("tool_manifest_failures", []):
            lines.append(f"- {failure}")

    if raw_report.get("fake_sentience_findings"):
        lines.append("")
        lines.append("Fake-sentience scan issues:")
        for finding in raw_report.get("fake_sentience_findings", []):
            lines.append(f"- {finding}")

    lines.append("")
    lines.append("Safe fix order:")
    lines.append("1. Fix missing files first.")
    lines.append("2. Fix syntax/compile errors second.")
    lines.append("3. Rerun module health matrix.")
    lines.append("4. Rerun test matrix.")
    lines.append("5. Rerun release-check and v2-check.")
    lines.append("6. Only then consider applying patches through the existing approval-gated self-edit system.")

    return "\n".join(lines)


def show_repair_plan(chat_state=None):
    plan = build_repair_plan(chat_state=chat_state)

    print("\n=== SELF-IMPROVEMENT REPAIR PLAN ===")
    print(plan["plan"])


def build_release_readiness_report():
    health = build_module_health_matrix()
    tests = build_test_matrix()

    registry_ok = True
    tool_ok = True
    fake_ok = True
    trust_ok = True

    registry_failures = []
    tool_failures = []
    fake_findings = []
    trust_data = None

    if REGISTRY_AVAILABLE:
        registry_failures = validate_os_registry()
        registry_ok = len(registry_failures) == 0

    if TOOL_MANIFEST_AVAILABLE:
        tool_failures = validate_tool_manifest()
        tool_ok = len(tool_failures) == 0

    if TRUST_AVAILABLE:
        fake_findings = scan_core_for_fake_sentience()
        fake_ok = len(fake_findings) == 0

        trust_data = risk_report()
        release_blocking = []

        for risk in trust_data.get("risks", []):
            lowered = str(risk).lower()

            if "voice is still alpha" in lowered:
                continue
            if "cockpit is not fully interactive" in lowered:
                continue
            if "v2 score" in lowered:
                continue

            release_blocking.append(risk)

        trust_ok = len(release_blocking) == 0

    ok = (
        health["missing"] == 0
        and health["failed"] == 0
        and tests["failed"] == 0
        and registry_ok
        and tool_ok
        and fake_ok
        and trust_ok
    )

    report = {
        "created_at": now_timestamp(),
        "release_ready": ok,
        "module_health": {
            "total": health["total"],
            "ok": health["ok"],
            "missing": health["missing"],
            "failed": health["failed"]
        },
        "test_matrix": {
            "total": tests["total"],
            "ok": tests["ok"],
            "failed": tests["failed"]
        },
        "registry_ok": registry_ok,
        "registry_failures": registry_failures,
        "tool_manifest_ok": tool_ok,
        "tool_manifest_failures": tool_failures,
        "fake_sentience_ok": fake_ok,
        "fake_sentience_findings": fake_findings,
        "trust_ok": trust_ok,
        "trust_report": trust_data
    }

    state = load_hardening_state()
    state["release_readiness_reports"].append(report)
    state["last_release_readiness"] = report
    save_hardening_state(state)

    mark_self_signal("release_check_full", True)
    mark_self_signal("impact_reports", BASE_SELF_IMPROVEMENT_AVAILABLE)

    if COMPANION_OS_AVAILABLE:
        try:
            append_companion_os_event(
                "self_improvement_release_readiness_report",
                "Self-improvement release readiness report created",
                {
                    "release_ready": ok,
                    "module_failed": health["failed"],
                    "test_failed": tests["failed"]
                },
                source="self_improvement_hardening",
                importance=4
            )
        except Exception:
            pass

    return report


def show_release_readiness_report():
    report = build_release_readiness_report()

    print("\n=== SELF-IMPROVEMENT RELEASE READINESS ===")
    print(f"Release ready: {report['release_ready']}")

    print("\nModule health:")
    print(json.dumps(report["module_health"], indent=4))

    print("\nTest matrix:")
    print(json.dumps(report["test_matrix"], indent=4))

    print("\nChecks:")
    print(f"Registry OK: {report['registry_ok']}")
    print(f"Tool Manifest OK: {report['tool_manifest_ok']}")
    print(f"Fake-sentience OK: {report['fake_sentience_ok']}")
    print(f"Trust OK: {report['trust_ok']}")


def run_self_improvement_hardening_suite(chat_state=None):
    print("\n=== RUNNING SELF-IMPROVEMENT HARDENING SUITE ===")

    health = build_module_health_matrix()
    tests = build_test_matrix()
    readiness = build_release_readiness_report()

    # Only build repair plan if something is wrong.
    plan = None

    if not readiness["release_ready"]:
        plan = build_repair_plan(chat_state=chat_state)

    summary = {
        "created_at": now_timestamp(),
        "module_health": {
            "total": health["total"],
            "ok": health["ok"],
            "missing": health["missing"],
            "failed": health["failed"]
        },
        "test_matrix": {
            "total": tests["total"],
            "ok": tests["ok"],
            "failed": tests["failed"]
        },
        "release_ready": readiness["release_ready"],
        "repair_plan_created": plan is not None
    }

    if COMPANION_OS_AVAILABLE:
        try:
            append_companion_os_journal(
                "Self-improvement hardening suite",
                json.dumps(summary, indent=2)
            )
        except Exception:
            pass

    print(json.dumps(summary, indent=4))
    return summary


def show_self_improvement_hardening_status():
    state = load_hardening_state()

    print("\n=== SELF-IMPROVEMENT HARDENING STATUS ===")
    print(f"Test matrices: {len(state.get('test_matrix', []))}")
    print(f"Health matrices: {len(state.get('module_health_matrix', []))}")
    print(f"Repair plans: {len(state.get('repair_plans', []))}")
    print(f"Release readiness reports: {len(state.get('release_readiness_reports', []))}")

    last_health = state.get("last_health_matrix")
    last_test = state.get("last_full_test")
    last_ready = state.get("last_release_readiness")

    if last_health:
        print("\nLast health matrix:")
        print(f"OK: {last_health.get('ok')} / {last_health.get('total')}")
        print(f"Missing: {last_health.get('missing')}")
        print(f"Failed: {last_health.get('failed')}")

    if last_test:
        print("\nLast test matrix:")
        print(f"OK: {last_test.get('ok')} / {last_test.get('total')}")
        print(f"Failed: {last_test.get('failed')}")

    if last_ready:
        print("\nLast release readiness:")
        print(f"Release ready: {last_ready.get('release_ready')}")


def get_self_improvement_hardening_context_for_prompt():
    state = load_hardening_state()

    text = "=== SELF-IMPROVEMENT HARDENING CONTEXT ===\n"
    text += f"Health matrices: {len(state.get('module_health_matrix', []))}\n"
    text += f"Test matrices: {len(state.get('test_matrix', []))}\n"
    text += f"Repair plans: {len(state.get('repair_plans', []))}\n"
    text += f"Release readiness reports: {len(state.get('release_readiness_reports', []))}\n"

    if state.get("last_health_matrix"):
        health = state["last_health_matrix"]
        text += f"Last module health: {health.get('ok')}/{health.get('total')} ok, missing={health.get('missing')}, failed={health.get('failed')}\n"

    if state.get("last_full_test"):
        tests = state["last_full_test"]
        text += f"Last test matrix: {tests.get('ok')}/{tests.get('total')} ok, failed={tests.get('failed')}\n"

    if state.get("last_release_readiness"):
        ready = state["last_release_readiness"]
        text += f"Last release readiness: {ready.get('release_ready')}\n"

    text += """
Self-improvement hardening rule:
Seed may inspect, test, generate health matrices, and propose repairs.
Seed must not silently edit or apply risky changes.
Use repair plans before patching.
"""

    return text


if __name__ == "__main__":
    run_self_improvement_hardening_suite()
    show_self_improvement_hardening_status()
