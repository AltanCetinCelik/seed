import json
import subprocess
from datetime import datetime


try:
    from seed_config import (
        SEED_ACTION_KERNEL_HISTORY_FILE,
        SEED_ACTION_KERNEL_STATE_FILE,
        SEED_ACTION_KERNEL_VERIFY_RESULTS
    )
except Exception:
    SEED_ACTION_KERNEL_HISTORY_FILE = "seed_action_kernel_history.jsonl"
    SEED_ACTION_KERNEL_STATE_FILE = "seed_action_kernel_state.json"
    SEED_ACTION_KERNEL_VERIFY_RESULTS = True


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def append_history(item):
    try:
        with open(SEED_ACTION_KERNEL_HISTORY_FILE, "a") as file:
            file.write(json.dumps(item) + "\n")
    except Exception:
        pass


def save_state(data):
    try:
        with open(SEED_ACTION_KERNEL_STATE_FILE, "w") as file:
            json.dump(data, file, indent=4)
    except Exception:
        pass


def action_result(action_id, ok, spoken_message, data=None, verified=False, risk="unknown"):
    item = {
        "created_at": now_timestamp(),
        "action_id": action_id,
        "ok": bool(ok),
        "verified": bool(verified),
        "risk": risk,
        "spoken_message": spoken_message,
        "data": data or {}
    }
    append_history(item)
    save_state(item)
    return item


def action_open_cockpit(args=None):
    try:
        from seed_cockpit_browser_action import open_cockpit_browser
        result = open_cockpit_browser(start_server=True)
        return action_result(
            "open_cockpit",
            ok=result.get("ok"),
            verified=result.get("ok"),
            risk="local_control",
            spoken_message=result.get("spoken_message") or "I tried to open Cockpit.",
            data=result
        )
    except Exception as error:
        return action_result(
            "open_cockpit",
            ok=False,
            verified=False,
            risk="local_control",
            spoken_message=f"I could not open Cockpit: {error}",
            data={"error": str(error)}
        )


def action_memory_search(args=None):
    args = args or {}
    query = args.get("query", "")
    try:
        from seed_capability_memory import search_memory
        results = search_memory(query, rebuild=False)
        if not results:
            message = f"I searched local memory and repo files for '{query}', but found no strong matches."
        else:
            top = results[0]
            message = f"I found {len(results)} local matches. Top result is {top.get('path')}."

        return action_result(
            "memory_search",
            ok=True,
            verified=True,
            risk="read_only",
            spoken_message=message,
            data={"query": query, "results": results}
        )
    except Exception as error:
        return action_result(
            "memory_search",
            ok=False,
            verified=False,
            risk="read_only",
            spoken_message=f"Memory search failed: {error}",
            data={"error": str(error), "query": query}
        )


def action_memory_add(args=None):
    args = args or {}
    text = args.get("text", "")
    if not text:
        return action_result(
            "memory_add",
            ok=False,
            verified=False,
            risk="memory_write",
            spoken_message="I did not add a memory because the memory text was empty."
        )

    try:
        from seed_capability_memory import add_memory_note
        note = add_memory_note(text, source="action_kernel")
        return action_result(
            "memory_add",
            ok=True,
            verified=True,
            risk="memory_write",
            spoken_message="I saved that to Seed's local capability memory.",
            data={"note": note}
        )
    except Exception as error:
        return action_result(
            "memory_add",
            ok=False,
            verified=False,
            risk="memory_write",
            spoken_message=f"I could not save that memory: {error}",
            data={"error": str(error)}
        )


def action_build_memory_index(args=None):
    try:
        from seed_capability_memory import build_memory_index
        index = build_memory_index(".")
        return action_result(
            "build_memory_index",
            ok=True,
            verified=True,
            risk="read_only",
            spoken_message=f"I indexed {index.get('item_count')} local memory and repo items.",
            data={"item_count": index.get("item_count"), "root": index.get("root")}
        )
    except Exception as error:
        return action_result(
            "build_memory_index",
            ok=False,
            verified=False,
            risk="read_only",
            spoken_message=f"Memory indexing failed: {error}",
            data={"error": str(error)}
        )


def action_agent_plan(args=None):
    args = args or {}
    task = args.get("task", "")
    try:
        from seed_agent_orchestrator import build_agent_task
        plan = build_agent_task(task)
        tool = plan.get("selected_tool")
        message = f"I built an agent plan for that task. Suggested route: {plan.get('capability')} via {tool}. Approval is required before execution."
        return action_result(
            "agent_plan",
            ok=True,
            verified=True,
            risk="proposal",
            spoken_message=message,
            data=plan
        )
    except Exception as error:
        return action_result(
            "agent_plan",
            ok=False,
            verified=False,
            risk="proposal",
            spoken_message=f"Agent planning failed: {error}",
            data={"error": str(error), "task": task}
        )


def action_browser_plan(args=None):
    args = args or {}
    task = args.get("task", "")
    try:
        from seed_browser_agent_gateway import build_browser_plan
        plan = build_browser_plan(task)
        return action_result(
            "browser_plan",
            ok=True,
            verified=True,
            risk="external_web_action",
            spoken_message="I built a browser-agent plan. Browser automation needs your approval before it runs.",
            data=plan
        )
    except Exception as error:
        return action_result(
            "browser_plan",
            ok=False,
            verified=False,
            risk="external_web_action",
            spoken_message=f"Browser planning failed: {error}",
            data={"error": str(error), "task": task}
        )


def action_mcp_plan(args=None):
    args = args or {}
    task = args.get("task", "")
    try:
        from seed_mcp_gateway import build_mcp_plan
        plan = build_mcp_plan(task)
        return action_result(
            "mcp_plan",
            ok=True,
            verified=True,
            risk="external_tool_access",
            spoken_message="I built an MCP tool plan. MCP execution needs explicit configuration and approval first.",
            data=plan
        )
    except Exception as error:
        return action_result(
            "mcp_plan",
            ok=False,
            verified=False,
            risk="external_tool_access",
            spoken_message=f"MCP planning failed: {error}",
            data={"error": str(error), "task": task}
        )


def action_safe_diagnostic(args=None):
    """
    Safe diagnostic must NOT call seed_v22_mega_gate.py.
    The v22 gate already calls this function, so calling the gate from here creates recursion.
    """
    commands = [
        ["python", "-m", "py_compile", "seed_action_kernel.py"],
        ["python", "-m", "py_compile", "seed_capability_memory.py"],
        ["python", "-m", "py_compile", "seed_mcp_gateway.py"],
        ["python", "-m", "py_compile", "seed_coding_agent_gateway.py"],
        ["python", "-m", "py_compile", "seed_browser_agent_gateway.py"],
        ["python", "-m", "py_compile", "seed_voice_quality_router.py"]
    ]

    results = []
    for command in commands:
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=12
            )
            results.append({
                "command": command,
                "ok": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout[-1000:],
                "stderr": result.stderr[-2000:]
            })
        except subprocess.TimeoutExpired:
            results.append({
                "command": command,
                "ok": False,
                "returncode": None,
                "stdout": "",
                "stderr": "Diagnostic timed out."
            })

    ok = all(r["ok"] for r in results)
    return action_result(
        "safe_diagnostic",
        ok=ok,
        verified=True,
        risk="diagnostic",
        spoken_message="Safe diagnostics passed." if ok else "Safe diagnostics found a problem.",
        data={"results": results}
    )



ACTIONS = {
    "open_cockpit": {
        "handler": action_open_cockpit,
        "risk": "local_control",
        "approval_required": False,
        "description": "Open Seed Cockpit in browser and verify action."
    },
    "memory_search": {
        "handler": action_memory_search,
        "risk": "read_only",
        "approval_required": False,
        "description": "Search local Seed memory and indexed repo/docs."
    },
    "memory_add": {
        "handler": action_memory_add,
        "risk": "memory_write",
        "approval_required": False,
        "description": "Add explicit user-provided note to local capability memory."
    },
    "build_memory_index": {
        "handler": action_build_memory_index,
        "risk": "read_only",
        "approval_required": False,
        "description": "Build local search index over Seed memory/repo/docs."
    },
    "agent_plan": {
        "handler": action_agent_plan,
        "risk": "proposal",
        "approval_required": False,
        "description": "Build an approval-gated agent plan."
    },
    "browser_plan": {
        "handler": action_browser_plan,
        "risk": "external_web_action",
        "approval_required": False,
        "description": "Build browser-agent plan. Execution disabled by default."
    },
    "mcp_plan": {
        "handler": action_mcp_plan,
        "risk": "external_tool_access",
        "approval_required": False,
        "description": "Build MCP plan. Execution disabled by default."
    },
    "safe_diagnostic": {
        "handler": action_safe_diagnostic,
        "risk": "diagnostic",
        "approval_required": False,
        "description": "Run safe diagnostics."
    }
}


def run_action(action_id, args=None):
    spec = ACTIONS.get(action_id)
    if not spec:
        return action_result(
            action_id,
            ok=False,
            verified=False,
            risk="unknown",
            spoken_message=f"Unknown action: {action_id}",
            data={"args": args or {}}
        )

    return spec["handler"](args or {})


def route_action_from_text(text):
    lowered = (text or "").lower()

    if "cockpit" in lowered and any(x in lowered for x in ["open", "launch", "show", "browser"]):
        return "open_cockpit", {}

    if lowered.startswith("remember that "):
        return "memory_add", {"text": text[len("remember that "):].strip()}

    if "index memory" in lowered or "build memory index" in lowered or "index repo" in lowered:
        return "build_memory_index", {}

    if "search memory" in lowered or "search repo" in lowered or "find in seed" in lowered:
        query = lowered
        for prefix in ["search memory for", "search repo for", "find in seed"]:
            query = query.replace(prefix, "")
        return "memory_search", {"query": query.strip() or text}

    if "browser" in lowered and any(x in lowered for x in ["use", "plan", "agent", "automate"]):
        return "browser_plan", {"task": text}

    if "mcp" in lowered:
        return "mcp_plan", {"task": text}

    if any(x in lowered for x in ["agent plan", "coding agent", "use aider", "use openhands", "fix a bug", "edit code safely"]):
        return "agent_plan", {"task": text}

    if "safe diagnostic" in lowered or "run diagnostics" in lowered:
        return "safe_diagnostic", {}

    return None, None


def maybe_handle_action_text(text):
    action_id, args = route_action_from_text(text)
    if not action_id:
        return None

    result = run_action(action_id, args)
    return result.get("spoken_message")


def show_action_kernel():
    print("\n=== SEED ACTION KERNEL ===")
    for action_id, spec in ACTIONS.items():
        print(f"- {action_id}: risk={spec['risk']} approval={spec['approval_required']}")
        print(f"  {spec['description']}")


def show_action_test():
    result = run_action("safe_diagnostic")
    print(json.dumps(result, indent=4))


def show_action_history():
    print("\n=== ACTION HISTORY ===")
    try:
        with open(SEED_ACTION_KERNEL_HISTORY_FILE, "r") as file:
            lines = file.readlines()[-30:]
        for line in lines:
            item = json.loads(line)
            print(f"\n{item.get('created_at')} — {item.get('action_id')} ok={item.get('ok')} verified={item.get('verified')}")
            print(item.get("spoken_message"))
    except Exception:
        print("No action history yet.")


def get_action_kernel_context():
    return (
        "=== ACTION KERNEL CONTEXT ===\n"
        f"Registered actions: {', '.join(ACTIONS.keys())}\n"
        "Rule: Seed must only say an action happened if the action kernel verified it.\n"
    )


if __name__ == "__main__":
    show_action_kernel()
