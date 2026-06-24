import json
import sys
from datetime import datetime


try:
    from seed_config import SEED_MCP_SKILL_SERVER_STATE_FILE
except Exception:
    SEED_MCP_SKILL_SERVER_STATE_FILE = "seed_mcp_skill_server_state.json"


SAFE_TOOLS = {
    "seed.git_status": {
        "skill": "git",
        "operation": "status",
        "description": "Read-only git status."
    },
    "seed.git_diff_stat": {
        "skill": "git",
        "operation": "diff_stat",
        "description": "Read-only git diff stat."
    },
    "seed.repo_summary": {
        "skill": "repo",
        "operation": "summary",
        "description": "Read-only repo summary."
    },
    "seed.repo_todos": {
        "skill": "repo",
        "operation": "todos",
        "description": "Read-only TODO/FIXME scan."
    },
    "seed.safe_diagnostic": {
        "skill": "safe_shell",
        "operation": "diagnostic",
        "description": "Whitelisted safe diagnostic."
    },
    "seed.filesystem_list": {
        "skill": "filesystem",
        "operation": "list",
        "description": "List files inside project root."
    },
    "seed.filesystem_search": {
        "skill": "filesystem",
        "operation": "search",
        "description": "Search files inside project root."
    },
    "seed.browser_validate": {
        "skill": "browser",
        "operation": "validate_url",
        "description": "Validate public http(s) URL."
    }
}


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def save_state(event, extra=None):
    state = {
        "created_at": now_timestamp(),
        "version": "v3.6.0",
        "event": event,
        "tool_count": len(SAFE_TOOLS),
        "local_only": True,
        "no_arbitrary_shell": True,
        "extra": extra or {}
    }

    try:
        with open(SEED_MCP_SKILL_SERVER_STATE_FILE, "w") as file:
            json.dump(state, file, indent=4)
    except Exception:
        pass

    return state


def tool_schema(tool_id, spec):
    return {
        "name": tool_id,
        "description": spec["description"],
        "inputSchema": {
            "type": "object",
            "properties": {
                "args": {
                    "type": "object",
                    "description": "Arguments for the Seed skill operation."
                }
            }
        }
    }


def list_tools():
    return [tool_schema(tool_id, spec) for tool_id, spec in SAFE_TOOLS.items()]


def call_tool(name, arguments=None):
    if name not in SAFE_TOOLS:
        return {
            "ok": False,
            "error": f"Tool not allowlisted: {name}"
        }

    spec = SAFE_TOOLS[name]
    arguments = arguments or {}
    args = arguments.get("args", {}) if isinstance(arguments, dict) else {}

    try:
        from seed_skill_kernel import run_skill
        result = run_skill(spec["skill"], spec["operation"], args)
        return {
            "ok": True,
            "tool": name,
            "skill_result": result
        }
    except Exception as error:
        return {
            "ok": False,
            "tool": name,
            "error": str(error)
        }


def handle_rpc(message):
    method = message.get("method")
    msg_id = message.get("id")

    if method in ["initialize", "mcp.initialize"]:
        save_state("initialize")
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "serverInfo": {
                    "name": "seed-mcp-skill-server",
                    "version": "v3.6.0"
                },
                "capabilities": {
                    "tools": {}
                }
            }
        }

    if method in ["tools/list", "mcp.tools.list"]:
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "tools": list_tools()
            }
        }

    if method in ["tools/call", "mcp.tools.call"]:
        params = message.get("params", {}) or {}
        name = params.get("name")
        arguments = params.get("arguments", {}) or {}
        result = call_tool(name, arguments)
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result, indent=2)
                    }
                ],
                "isError": not result.get("ok", False)
            }
        }

    return {
        "jsonrpc": "2.0",
        "id": msg_id,
        "error": {
            "code": -32601,
            "message": f"Unknown method: {method}"
        }
    }


def run_stdio_server():
    save_state("stdio_server_started")

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            message = json.loads(line)
            response = handle_rpc(message)
        except Exception as error:
            response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32000,
                    "message": str(error)
                }
            }

        print(json.dumps(response), flush=True)


def self_test():
    init = handle_rpc({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    tools = handle_rpc({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
    call = handle_rpc({
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "seed.git_status",
            "arguments": {"args": {}}
        }
    })

    return {
        "ok": bool(init.get("result")) and bool(tools.get("result")) and bool(call.get("result")),
        "init": init,
        "tools_count": len(tools.get("result", {}).get("tools", [])),
        "call_is_error": call.get("result", {}).get("isError")
    }


def show_mcp_skill_server():
    print("\n=== SEED MCP SKILL SERVER ===")
    print(json.dumps({
        "version": "v3.6.0",
        "tools": list_tools(),
        "self_test": self_test()
    }, indent=4))


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        show_mcp_skill_server()
    else:
        run_stdio_server()
