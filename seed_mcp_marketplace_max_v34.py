import json
from datetime import datetime
from pathlib import Path


MCP_MAX_FILE = Path("seed_mcp_marketplace_max_v34.json")


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def build_tool_catalog():
    tools = []

    try:
        from seed_mcp_skill_server import list_tools
        tools.extend(list_tools())
    except Exception:
        pass

    seed_tools = [
        {"name": "seed.memory.search", "risk": "read_only", "module": "seed_memory_brain_max_v32"},
        {"name": "seed.task.stats", "risk": "read_only", "module": "seed_task_hygiene_v302"},
        {"name": "seed.workflow.tick", "risk": "manual_write", "module": "seed_workflow_runtime_v33"},
        {"name": "seed.aider.plan", "risk": "file_write_planned", "module": "seed_aider_cockpit_v31"},
        {"name": "seed.browser.readonly", "risk": "network_read", "module": "seed_browser_executor_v35"},
        {"name": "seed.voice.transcribe", "risk": "local_audio", "module": "seed_voice_runtime_max_v36"},
        {"name": "seed.agent_hq.status", "risk": "read_only", "module": "seed_agent_hq_v30"},
    ]

    return tools + seed_tools


def build_mcp_marketplace_max():
    catalog = build_tool_catalog()
    data = {
        "created_at": now_timestamp(),
        "version": "v45.0.0",
        "ok": True,
        "tool_count": len(catalog),
        "tools": catalog,
        "ui_groups": {
            "memory": [t for t in catalog if "memory" in str(t).lower()],
            "tasks": [t for t in catalog if "task" in str(t).lower()],
            "agents": [t for t in catalog if "agent" in str(t).lower() or "aider" in str(t).lower()],
            "browser_voice": [t for t in catalog if "browser" in str(t).lower() or "voice" in str(t).lower()],
        }
    }
    MCP_MAX_FILE.write_text(json.dumps(data, indent=4))
    return data


def show_mcp_marketplace_max():
    data = build_mcp_marketplace_max()
    print("\n=== SEED MCP MARKETPLACE MAX v34 ===")
    print(f"Tools: {data['tool_count']}")
    for tool in data["tools"][:40]:
        print(f"- {tool.get('name')} risk={tool.get('risk')}")


if __name__ == "__main__":
    show_mcp_marketplace_max()
