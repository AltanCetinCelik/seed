import json
import sys
from datetime import datetime
from pathlib import Path


try:
    from seed_config import SEED_MCP_SKILL_SERVER_MANIFEST_FILE
except Exception:
    SEED_MCP_SKILL_SERVER_MANIFEST_FILE = "seed_mcp_skill_manifest.json"


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def build_mcp_manifest():
    server_path = str(Path("seed_mcp_skill_server.py").resolve())

    manifest = {
        "created_at": now_timestamp(),
        "version": "v3.6.0",
        "ok": True,
        "server_name": "seed-skills",
        "server_type": "stdio",
        "command": sys.executable,
        "args": [server_path],
        "policy": {
            "local_only": True,
            "allowlist_only": True,
            "no_arbitrary_shell": True,
            "no_delete": True,
            "approval_for_risky_actions": True
        },
        "example_mcp_config": {
            "mcpServers": {
                "seed-skills": {
                    "command": sys.executable,
                    "args": [server_path]
                }
            }
        }
    }

    with open(SEED_MCP_SKILL_SERVER_MANIFEST_FILE, "w") as file:
        json.dump(manifest, file, indent=4)

    return manifest


def show_mcp_manifest():
    print("\n=== SEED MCP SKILL MANIFEST ===")
    print(json.dumps(build_mcp_manifest(), indent=4))


if __name__ == "__main__":
    show_mcp_manifest()
