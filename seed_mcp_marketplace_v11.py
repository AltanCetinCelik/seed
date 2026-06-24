import importlib.util
import json
from datetime import datetime


try:
    from seed_config import SEED_MCP_MARKETPLACE_FILE
except Exception:
    SEED_MCP_MARKETPLACE_FILE = "seed_mcp_marketplace_v11.json"


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def build_mcp_marketplace():
    tools = []
    try:
        from seed_mcp_skill_server import list_tools
        tools = list_tools()
    except Exception:
        pass

    marketplace = {
        "created_at": now_timestamp(),
        "version": "v20.0.0",
        "ok": True,
        "engine": "Seed MCP Marketplace v11",
        "seed_native_tools": tools,
        "adapters": {
            "memory": {
                "status": "available",
                "module": "seed_memory_engine_v2",
                "tool_shape": "seed.memory.query / seed.memory.write later"
            },
            "browser": {
                "status": "sandbox",
                "module": "seed_browser_sandbox_v10",
                "tool_shape": "seed.browser.validate / seed.browser.summarize later"
            },
            "voice": {
                "status": "available",
                "module": "seed_voice_runtime_v6",
                "tool_shape": "seed.voice.transcript / seed.voice.intent later"
            },
            "aider": {
                "status": "guarded",
                "module": "seed_aider_review_v7",
                "tool_shape": "seed.aider.dry_run only by default"
            },
            "openhands": {
                "status": "sandbox_only",
                "module": "seed_openhands_sandbox_v12",
                "tool_shape": "seed.openhands.plan only"
            }
        },
        "policy": {
            "allowlist_only": True,
            "approval_required_for_write": True,
            "no_arbitrary_shell": True,
            "no_delete": True
        }
    }

    with open(SEED_MCP_MARKETPLACE_FILE, "w") as file:
        json.dump(marketplace, file, indent=4)

    return marketplace


def show_mcp_marketplace():
    data = build_mcp_marketplace()
    print("\n=== SEED MCP MARKETPLACE v11 ===")
    print(f"Native tools: {len(data['seed_native_tools'])}")
    print("Adapters:")
    for key, item in data["adapters"].items():
        print(f"- {key}: {item['status']} -> {item['module']}")


if __name__ == "__main__":
    show_mcp_marketplace()
