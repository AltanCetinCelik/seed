import json
from datetime import datetime


try:
    from seed_config import SEED_V20_STATE_FILE
except Exception:
    SEED_V20_STATE_FILE = "seed_v20_sovereign_state.json"


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def safe(name, fn):
    try:
        data = fn()
        return {"ok": bool(data.get("ok", True)) if isinstance(data, dict) else True, "data": data}
    except Exception as error:
        return {"ok": False, "error": str(error), "name": name}


def build_v20_state():
    modules = {
        "memory_v2": safe("memory_v2", lambda: __import__("seed_memory_engine_v2", fromlist=["build_memory_v2"]).build_memory_v2()),
        "voice_runtime": safe("voice_runtime", lambda: __import__("seed_voice_runtime_v6", fromlist=["build_voice_runtime"]).build_voice_runtime()),
        "workflow_graph": safe("workflow_graph", lambda: __import__("seed_workflow_graph_v9", fromlist=["build_workflow_graph"]).build_workflow_graph()),
        "browser_sandbox": safe("browser_sandbox", lambda: __import__("seed_browser_sandbox_v10", fromlist=["build_browser_sandbox"]).build_browser_sandbox()),
        "mcp_marketplace": safe("mcp_marketplace", lambda: __import__("seed_mcp_marketplace_v11", fromlist=["build_mcp_marketplace"]).build_mcp_marketplace()),
        "openhands_sandbox": safe("openhands_sandbox", lambda: __import__("seed_openhands_sandbox_v12", fromlist=["build_openhands_sandbox"]).build_openhands_sandbox()),
        "project_life_os": safe("project_life_os", lambda: __import__("seed_project_life_os_v14", fromlist=["build_project_life_os"]).build_project_life_os()),
        "world_avatar": safe("world_avatar", lambda: __import__("seed_world_avatar_v16", fromlist=["build_world_avatar"]).build_world_avatar()),
        "agent_council": safe("agent_council", lambda: __import__("seed_agent_council_v17", fromlist=["council_review"]).council_review("Seed v20 release")),
        "self_improvement_lab": safe("self_improvement_lab", lambda: __import__("seed_self_improvement_lab_v18", fromlist=["create_self_improvement_proposal"]).create_self_improvement_proposal("Seed v20 self-improvement pipeline")),
        "multidevice_hub": safe("multidevice_hub", lambda: __import__("seed_multidevice_hub_v19", fromlist=["build_multidevice_hub"]).build_multidevice_hub()),
    }

    state = {
        "created_at": now_timestamp(),
        "version": "v20.0.0",
        "ok": all(item.get("ok") for item in modules.values()),
        "release": "Seed v20.0.0 — Sovereign Companion OS MegaCore",
        "identity_boundary": "Seed is not alive, conscious, sentient, human, or experiencing anything. It is User's local-first Companion OS.",
        "loop": ["understand", "remember", "plan", "ask_approval", "act", "verify", "rollback", "learn"],
        "modules": modules,
        "major_capabilities": [
            "fast chat runtime",
            "manual operator core",
            "task OS",
            "event bus",
            "service manager",
            "workflow graph",
            "MCP client/server/marketplace",
            "Aider dry-run review",
            "OpenHands sandbox",
            "browser sandbox",
            "memory engine 2.0",
            "voice runtime",
            "project + life OS",
            "Seed World / Memory Garden",
            "avatar presence",
            "multi-agent council",
            "self-improvement lab",
            "multi-device hub"
        ],
        "policy": {
            "local_first": True,
            "manual_tick_only": True,
            "adapter_first": True,
            "sandbox_high_risk_tools": True,
            "no_arbitrary_shell": True,
            "no_delete": True,
            "no_auto_commit": True,
            "approval_for_risky_actions": True
        },
        "next_after_v20": "v20.1 stabilization: live dashboard buttons, Aider review UI, push-to-talk executable."
    }

    with open(SEED_V20_STATE_FILE, "w") as file:
        json.dump(state, file, indent=4)

    return state


def show_v20_status():
    state = build_v20_state()
    print("\n=== SEED v20 SOVEREIGN COMPANION OS ===")
    print(f"OK: {state['ok']}")
    print("Capabilities:")
    for item in state["major_capabilities"]:
        print(f"- {item}")
    print("\nModule status:")
    for name, result in state["modules"].items():
        print(f"- {name}: {result.get('ok')}")


if __name__ == "__main__":
    show_v20_status()
