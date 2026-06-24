import json
import subprocess
from datetime import datetime


try:
    from seed_config import SEED_V40_GATE_REPORT_FILE, V40_REQUIRED_MODULES
except Exception:
    SEED_V40_GATE_REPORT_FILE = "seed_v40_gate_report.json"
    V40_REQUIRED_MODULES = [
        "seed_event_bus.py",
        "seed_service_manager.py",
        "seed_mcp_client.py",
        "seed_workflow_automation.py",
        "seed_patch_rollback.py",
        "seed_aider_patch_flow.py",
        "seed_memory_distiller.py",
        "seed_v40_os_gate.py"
    ]


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def compile_module(module):
    result = subprocess.run(["python", "-m", "py_compile", module], capture_output=True, text=True)
    return {"module": module, "ok": result.returncode == 0, "stderr": result.stderr[-2500:]}


def run_v40_gate():
    module_checks = [compile_module(module) for module in V40_REQUIRED_MODULES]
    modules_ok = all(x["ok"] for x in module_checks)
    details = {}

    try:
        from seed_event_bus import emit_event, event_bus_status
        emit_event("v40_gate_probe", {"gate": "v40"}, source="v40_gate")
        event_bus_ok = event_bus_status().get("ok") is True
        details["event_bus"] = event_bus_status()
    except Exception as error:
        event_bus_ok = False
        details["event_bus_error"] = str(error)

    try:
        from seed_service_manager import service_status
        service_ok = service_status().get("ok") is True
        details["services"] = service_status()
    except Exception as error:
        service_ok = False
        details["service_error"] = str(error)

    try:
        from seed_mcp_client import mcp_client_self_test
        mcp_client = mcp_client_self_test()
        mcp_client_ok = mcp_client.get("ok") is True and mcp_client.get("tool_count", 0) >= 5
        details["mcp_client"] = {"ok": mcp_client.get("ok"), "tool_count": mcp_client.get("tool_count")}
    except Exception as error:
        mcp_client_ok = False
        details["mcp_client_error"] = str(error)

    try:
        from seed_patch_rollback import create_checkpoint, checkpoint_status
        ckpt = create_checkpoint("v40-gate", ["seed_fast_voice_context.py"])
        rollback_ok = ckpt.get("ok") is True and checkpoint_status().get("count", 0) >= 1
        details["checkpoint"] = {"id": ckpt.get("checkpoint_id"), "files": ckpt.get("files")}
    except Exception as error:
        rollback_ok = False
        details["rollback_error"] = str(error)

    try:
        from seed_workflow_automation import workflow_status
        workflows = workflow_status()
        workflow_ok = workflows.get("ok") is True and "runtime-health" in workflows.get("available", [])
        details["workflows"] = workflows
    except Exception as error:
        workflow_ok = False
        details["workflow_error"] = str(error)

    try:
        from seed_memory_distiller import build_memory_distill
        distill = build_memory_distill()
        memory_ok = distill.get("ok") is True and "summary" in distill
        details["memory_distill"] = distill.get("summary", {})
    except Exception as error:
        memory_ok = False
        details["memory_error"] = str(error)

    try:
        from seed_aider_patch_flow import create_patch_flow
        flow = create_patch_flow(
            "v40 gate dry-run patch flow test",
            ["seed_fast_voice_context.py"],
            mode="dry_run"
        )
        aider_flow_ok = flow.get("ok") is True and flow.get("aider_plan", {}).get("mode") == "dry_run"
        details["aider_patch_flow"] = {
            "mode": flow.get("mode"),
            "checkpoint": flow.get("checkpoint", {}).get("checkpoint_id"),
            "aider_plan": flow.get("aider_plan", {}).get("plan_id")
        }
    except Exception as error:
        aider_flow_ok = False
        details["aider_flow_error"] = str(error)

    ready = all([
        modules_ok,
        event_bus_ok,
        service_ok,
        mcp_client_ok,
        rollback_ok,
        workflow_ok,
        memory_ok,
        aider_flow_ok
    ])

    report = {
        "created_at": now_timestamp(),
        "release": "Seed v4.0.0 — Runtime OS Upgrade",
        "ready": ready,
        "modules_ok": modules_ok,
        "event_bus_ok": event_bus_ok,
        "service_manager_ok": service_ok,
        "mcp_client_ok": mcp_client_ok,
        "rollback_ok": rollback_ok,
        "workflow_ok": workflow_ok,
        "memory_distiller_ok": memory_ok,
        "aider_patch_flow_ok": aider_flow_ok,
        "module_checks": module_checks,
        "details": details
    }

    with open(SEED_V40_GATE_REPORT_FILE, "w") as file:
        json.dump(report, file, indent=4)

    return report


def show_v40_gate():
    report = run_v40_gate()

    print("\n=== SEED v4.0.0 RUNTIME OS GATE ===")
    print(f"Ready: {report['ready']}")
    print(f"Modules OK: {report['modules_ok']}")
    print(f"Event Bus OK: {report['event_bus_ok']}")
    print(f"Service Manager OK: {report['service_manager_ok']}")
    print(f"MCP Client OK: {report['mcp_client_ok']}")
    print(f"Rollback OK: {report['rollback_ok']}")
    print(f"Workflow OK: {report['workflow_ok']}")
    print(f"Memory Distiller OK: {report['memory_distiller_ok']}")
    print(f"Aider Patch Flow OK: {report['aider_patch_flow_ok']}")

    print("\nModule checks:")
    for item in report["module_checks"]:
        status = "OK" if item["ok"] else "FAIL"
        print(f"- {status}: {item['module']}")
        if item["stderr"] and not item["ok"]:
            print(item["stderr"][:1000])


if __name__ == "__main__":
    show_v40_gate()
