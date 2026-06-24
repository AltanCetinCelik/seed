import json
import subprocess
from datetime import datetime


try:
    from seed_config import SEED_V36_GATE_REPORT_FILE, V36_REQUIRED_MODULES
except Exception:
    SEED_V36_GATE_REPORT_FILE = "seed_v36_gate_report.json"
    V36_REQUIRED_MODULES = [
        "seed_mcp_skill_server.py",
        "seed_mcp_skill_manifest.py",
        "seed_aider_execution_unlock.py",
        "seed_integration_sandbox.py",
        "seed_v36_integration_gate.py"
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


def run_v36_gate():
    module_checks = [compile_module(module) for module in V36_REQUIRED_MODULES]
    modules_ok = all(item["ok"] for item in module_checks)

    mcp_server_ok = False
    mcp_manifest_ok = False
    aider_unlock_ok = False
    sandbox_ok = False
    details = {}

    try:
        from seed_mcp_skill_server import self_test
        result = self_test()
        mcp_server_ok = result.get("ok") is True and result.get("tools_count", 0) >= 5
        details["mcp_self_test"] = result
    except Exception as error:
        details["mcp_server_error"] = str(error)

    try:
        from seed_mcp_skill_manifest import build_mcp_manifest
        manifest = build_mcp_manifest()
        mcp_manifest_ok = manifest.get("ok") is True and "mcpServers" in manifest.get("example_mcp_config", {})
        details["mcp_manifest"] = {
            "command": manifest.get("command"),
            "args": manifest.get("args")
        }
    except Exception as error:
        details["mcp_manifest_error"] = str(error)

    try:
        from seed_aider_execution_unlock import detect_aider_runtime, create_aider_unlock_plan
        runtime = detect_aider_runtime()
        plan = create_aider_unlock_plan(
            "v3.6 gate dry-run: inspect Seed voice integration safely",
            ["seed_fast_voice_context.py", "seed_voice_ux_pack.py"],
            mode="dry_run"
        )
        aider_unlock_ok = plan.get("ok") is True and plan.get("mode") == "dry_run" and plan.get("target_validation", {}).get("ok") is True
        details["aider_runtime"] = runtime
        details["aider_plan"] = {
            "plan_id": plan.get("plan_id"),
            "can_execute": plan.get("can_execute"),
            "mode": plan.get("mode"),
            "approval_token": plan.get("approval", {}).get("approval_token")
        }
    except Exception as error:
        details["aider_unlock_error"] = str(error)

    try:
        from seed_integration_sandbox import create_sandbox
        sandbox = create_sandbox("v36-mcp-aider-test", "Gate test sandbox for MCP/Aider integration")
        sandbox_ok = sandbox.get("ok") is True
        details["sandbox"] = sandbox
    except Exception as error:
        details["sandbox_error"] = str(error)

    ready = all([modules_ok, mcp_server_ok, mcp_manifest_ok, aider_unlock_ok, sandbox_ok])

    report = {
        "created_at": now_timestamp(),
        "release": "Seed v3.6.0 — Real Integration Runtime",
        "ready": ready,
        "modules_ok": modules_ok,
        "mcp_server_ok": mcp_server_ok,
        "mcp_manifest_ok": mcp_manifest_ok,
        "aider_unlock_ok": aider_unlock_ok,
        "sandbox_ok": sandbox_ok,
        "module_checks": module_checks,
        "details": details
    }

    with open(SEED_V36_GATE_REPORT_FILE, "w") as file:
        json.dump(report, file, indent=4)

    return report


def show_v36_gate():
    report = run_v36_gate()

    print("\n=== SEED v3.6.0 REAL INTEGRATION RUNTIME GATE ===")
    print(f"Ready: {report['ready']}")
    print(f"Modules OK: {report['modules_ok']}")
    print(f"MCP Server OK: {report['mcp_server_ok']}")
    print(f"MCP Manifest OK: {report['mcp_manifest_ok']}")
    print(f"Aider Unlock OK: {report['aider_unlock_ok']}")
    print(f"Sandbox OK: {report['sandbox_ok']}")

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
    show_v36_gate()
