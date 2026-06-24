import json
import subprocess
from datetime import datetime


try:
    from seed_config import SEED_V22_GATE_REPORT_FILE, V22_REQUIRED_MODULES
except Exception:
    SEED_V22_GATE_REPORT_FILE = "seed_v22_gate_report.json"
    V22_REQUIRED_MODULES = [
        "seed_action_kernel.py",
        "seed_capability_memory.py",
        "seed_mcp_gateway.py",
        "seed_coding_agent_gateway.py",
        "seed_browser_agent_gateway.py",
        "seed_voice_quality_router.py",
        "seed_v22_mega_gate.py"
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


def run_v22_gate():
    module_checks = [compile_module(module) for module in V22_REQUIRED_MODULES]
    modules_ok = all(item["ok"] for item in module_checks)

    action_ok = False
    memory_ok = False
    mcp_ok = False
    coding_ok = False
    browser_ok = False
    voice_quality_ok = False

    details = {}

    try:
        from seed_action_kernel import run_action, ACTIONS
        result = run_action("safe_diagnostic")
        action_ok = bool(result.get("ok")) and "open_cockpit" in ACTIONS
        details["action_kernel"] = {
            "actions": list(ACTIONS.keys()),
            "safe_diagnostic": result
        }
    except Exception as error:
        details["action_kernel_error"] = str(error)

    try:
        from seed_capability_memory import build_memory_index, search_memory
        index = build_memory_index(".")
        results = search_memory("Seed", rebuild=False)
        memory_ok = index.get("item_count", 0) > 0
        details["memory"] = {
            "item_count": index.get("item_count"),
            "sample_results": len(results)
        }
    except Exception as error:
        details["memory_error"] = str(error)

    try:
        from seed_mcp_gateway import mcp_gateway_data
        mcp = mcp_gateway_data()
        mcp_ok = bool(mcp.get("ready_for_planning"))
        details["mcp_gateway"] = mcp
    except Exception as error:
        details["mcp_error"] = str(error)

    try:
        from seed_coding_agent_gateway import coding_gateway_data
        coding = coding_gateway_data()
        coding_ok = bool(coding.get("ready_for_planning"))
        details["coding_gateway"] = {
            "ready_for_planning": coding.get("ready_for_planning"),
            "profile_count": len(coding.get("profiles", [])),
            "git_dirty": coding.get("git_status", {}).get("dirty")
        }
    except Exception as error:
        details["coding_error"] = str(error)

    try:
        from seed_browser_agent_gateway import browser_gateway_data
        browser = browser_gateway_data()
        browser_ok = bool(browser.get("ready_for_planning"))
        details["browser_gateway"] = browser
    except Exception as error:
        details["browser_error"] = str(error)

    try:
        from seed_voice_quality_router import classify_voice_text
        voice = classify_voice_text("what are you now")
        voice_quality_ok = voice.get("should_answer") is True
        details["voice_quality"] = voice
    except Exception as error:
        details["voice_quality_error"] = str(error)

    ready = all([
        modules_ok,
        action_ok,
        memory_ok,
        mcp_ok,
        coding_ok,
        browser_ok,
        voice_quality_ok
    ])

    report = {
        "created_at": now_timestamp(),
        "release": "Seed v2.2.0 — Action Kernel + Memory Index + Tool Gateway Mega Update",
        "ready": ready,
        "modules_ok": modules_ok,
        "action_kernel_ok": action_ok,
        "memory_ok": memory_ok,
        "mcp_gateway_ok": mcp_ok,
        "coding_gateway_ok": coding_ok,
        "browser_gateway_ok": browser_ok,
        "voice_quality_ok": voice_quality_ok,
        "module_checks": module_checks,
        "details": details
    }

    with open(SEED_V22_GATE_REPORT_FILE, "w") as file:
        json.dump(report, file, indent=4)

    return report


def show_v22_gate():
    report = run_v22_gate()

    print("\n=== SEED v2.2.0 MEGA CAPABILITY GATE ===")
    print(f"Ready: {report['ready']}")
    print(f"Modules OK: {report['modules_ok']}")
    print(f"Action kernel OK: {report['action_kernel_ok']}")
    print(f"Memory OK: {report['memory_ok']}")
    print(f"MCP gateway OK: {report['mcp_gateway_ok']}")
    print(f"Coding gateway OK: {report['coding_gateway_ok']}")
    print(f"Browser gateway OK: {report['browser_gateway_ok']}")
    print(f"Voice quality OK: {report['voice_quality_ok']}")

    print("\nModule checks:")
    for item in report["module_checks"]:
        status = "OK" if item["ok"] else "FAIL"
        print(f"- {status}: {item['module']}")
        if item["stderr"] and not item["ok"]:
            print(item["stderr"][:1200])

    memory = report.get("details", {}).get("memory", {})
    if memory:
        print(f"\nMemory index items: {memory.get('item_count')}")


if __name__ == "__main__":
    show_v22_gate()
