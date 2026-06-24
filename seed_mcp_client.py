import json
import subprocess
import sys


def rpc_call(proc, message):
    proc.stdin.write(json.dumps(message) + "\n")
    proc.stdin.flush()
    line = proc.stdout.readline()
    return json.loads(line)


def with_seed_mcp(fn):
    proc = subprocess.Popen(
        [sys.executable, "seed_mcp_skill_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    try:
        init = rpc_call(proc, {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
        return fn(proc, init)
    finally:
        try:
            proc.kill()
        except Exception:
            pass


def list_seed_mcp_tools():
    def _run(proc, init):
        tools = rpc_call(proc, {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
        return {
            "ok": True,
            "init": init,
            "tools": tools.get("result", {}).get("tools", [])
        }

    return with_seed_mcp(_run)


def call_seed_mcp_tool(name, args=None):
    def _run(proc, init):
        result = rpc_call(proc, {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": name,
                "arguments": {
                    "args": args or {}
                }
            }
        })

        return {
            "ok": True,
            "tool": name,
            "result": result
        }

    return with_seed_mcp(_run)


def mcp_client_self_test():
    tools = list_seed_mcp_tools()
    call = call_seed_mcp_tool("seed.git_status", {})
    return {
        "ok": bool(tools.get("tools")) and call.get("ok") is True,
        "tool_count": len(tools.get("tools", [])),
        "call": call
    }


def show_mcp_client():
    print("\n=== SEED MCP CLIENT ===")
    print(json.dumps(mcp_client_self_test(), indent=4))


if __name__ == "__main__":
    show_mcp_client()
