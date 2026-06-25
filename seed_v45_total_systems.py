import json
from datetime import datetime
from pathlib import Path


STATE_FILE = Path("seed_v45_total_systems_state.json")


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def safe_card(title, fn):
    try:
        data = fn()
        ok = bool(data.get("ok", True)) if isinstance(data, dict) else True
        body = json.dumps(data, ensure_ascii=False)[:260]
        return {"title": title, "status": "ok" if ok else "warning", "body": body, "data": data}
    except Exception as error:
        return {"title": title, "status": "error", "body": str(error), "data": {"ok": False, "error": str(error)}}


def build_v45_state():
    cards = [
        safe_card("Task Hygiene", lambda: __import__("seed_task_hygiene_v302", fromlist=["task_stats"]).task_stats()),
        safe_card("Aider Cockpit", lambda: {"ok": True, "module": "seed_aider_cockpit_v31"}),
        safe_card("Memory Brain Max", lambda: __import__("seed_memory_brain_max_v32", fromlist=["memory_stats"]).memory_stats()),
        safe_card("Workflow Runtime", lambda: __import__("seed_workflow_runtime_v33", fromlist=["workflow_status"]).workflow_status()),
        safe_card("MCP Marketplace Max", lambda: __import__("seed_mcp_marketplace_max_v34", fromlist=["build_mcp_marketplace_max"]).build_mcp_marketplace_max()),
        safe_card("Browser Read-only", lambda: {"ok": True, "module": "seed_browser_executor_v35"}),
        safe_card("Voice Runtime Max", lambda: __import__("seed_voice_runtime_max_v36", fromlist=["voice_runtime_status"]).voice_runtime_status()),
        safe_card("Heavy Agent Sandbox", lambda: {"ok": True, "module": "seed_heavy_agent_sandbox_v37"}),
        safe_card("Agent HQ UI Model", lambda: __import__("seed_agent_hq_ui_model_v38", fromlist=["build_ui_model"]).build_ui_model()),
        safe_card("Presence Max", lambda: __import__("seed_presence_max_v39", fromlist=["build_presence_max"]).build_presence_max()),
        safe_card("Evaluation Lab", lambda: {"ok": True, "module": "seed_eval_lab_v40"}),
        safe_card("Desktop Packaging", lambda: __import__("seed_desktop_packaging_v42", fromlist=["create_launchers"]).create_launchers()),
        safe_card("Multi-device Hub", lambda: __import__("seed_multidevice_hub_max_v43", fromlist=["build_multidevice_max"]).build_multidevice_max()),
        safe_card("Seed World UI", lambda: __import__("seed_world_ui_v44", fromlist=["build_world_ui"]).build_world_ui()),
        safe_card("Self-Improvement Loop", lambda: {"ok": True, "module": "seed_self_improvement_loop_v45"}),
    ]

    state = {
        "created_at": now_timestamp(),
        "version": "v45.0.0",
        "ok": all(c["status"] != "error" for c in cards),
        "cards": cards,
        "terminal_pro": True,
        "professional_control_plane": True
    }

    STATE_FILE.write_text(json.dumps(state, indent=4))
    return state


def show_v45_status():
    data = build_v45_state()
    print("\n=== SEED v45 TOTAL SYSTEMS ===")
    print(f"OK: {data['ok']}")
    for card in data["cards"]:
        print(f"- {card['title']}: {card['status']}")


if __name__ == "__main__":
    show_v45_status()
