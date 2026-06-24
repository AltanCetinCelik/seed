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

# v2.5 Real Skill System integration.
try:
    _v25_previous_route_action_from_text = route_action_from_text
except Exception:
    _v25_previous_route_action_from_text = None

try:
    _v25_previous_maybe_handle_action_text = maybe_handle_action_text
except Exception:
    _v25_previous_maybe_handle_action_text = None


def route_action_from_text(text):
    if _v25_previous_route_action_from_text:
        action_id, args = _v25_previous_route_action_from_text(text)
        if action_id:
            return action_id, args

    try:
        from seed_skill_kernel import route_skill_from_text
        skill_id, operation, skill_args = route_skill_from_text(text)
        if skill_id:
            return "run_skill", {
                "skill_id": skill_id,
                "operation": operation,
                "args": skill_args or {}
            }
    except Exception:
        pass

    return None, None


def action_run_skill(args=None):
    args = args or {}
    try:
        from seed_skill_kernel import run_skill
        result = run_skill(
            args.get("skill_id"),
            args.get("operation"),
            args.get("args") or {}
        )

        return action_result(
            "run_skill",
            ok=result.get("ok"),
            verified=result.get("verified"),
            risk=result.get("risk", "skill"),
            spoken_message=result.get("spoken_message", "I ran the skill."),
            data=result
        )
    except Exception as error:
        return action_result(
            "run_skill",
            ok=False,
            verified=False,
            risk="skill",
            spoken_message=f"Skill execution failed: {error}",
            data={"error": str(error), "args": args}
        )


try:
    ACTIONS["run_skill"] = {
        "handler": action_run_skill,
        "risk": "skill",
        "approval_required": False,
        "description": "Run a verified Seed real skill through the skill kernel."
    }
except Exception:
    pass


def maybe_handle_action_text(text):
    action_id, args = route_action_from_text(text)
    if action_id:
        result = run_action(action_id, args)
        return result.get("spoken_message")

    if _v25_previous_maybe_handle_action_text:
        return _v25_previous_maybe_handle_action_text(text)

    return None

# v2.6 supervised agent execution action integration.
try:
    _v26_previous_route_action_from_text = route_action_from_text
except Exception:
    _v26_previous_route_action_from_text = None

try:
    _v26_previous_maybe_handle_action_text = maybe_handle_action_text
except Exception:
    _v26_previous_maybe_handle_action_text = None


def action_agent_run_create(args=None):
    args = args or {}
    try:
        from seed_agent_run_lifecycle import create_agent_run
        result = create_agent_run(args.get("task", "unspecified agent task"))
        return action_result(
            "agent_run_create",
            ok=result.get("ok"),
            verified=result.get("ok"),
            risk="agent_preparation",
            spoken_message=f"I created a supervised agent run: {result.get('run_id')}. Approval token is {result.get('approval_token')}.",
            data=result
        )
    except Exception as error:
        return action_result(
            "agent_run_create",
            ok=False,
            verified=False,
            risk="agent_preparation",
            spoken_message=f"Could not create supervised agent run: {error}",
            data={"error": str(error)}
        )


def action_agent_run_list(args=None):
    try:
        from seed_agent_run_lifecycle import list_agent_runs
        result = list_agent_runs()
        return action_result(
            "agent_run_list",
            ok=result.get("ok"),
            verified=result.get("ok"),
            risk="read_only",
            spoken_message=f"I found {result.get('count', 0)} supervised agent runs.",
            data=result
        )
    except Exception as error:
        return action_result(
            "agent_run_list",
            ok=False,
            verified=False,
            risk="read_only",
            spoken_message=f"Could not list supervised agent runs: {error}",
            data={"error": str(error)}
        )


try:
    ACTIONS["agent_run_create"] = {
        "handler": action_agent_run_create,
        "risk": "agent_preparation",
        "approval_required": False,
        "description": "Create a supervised approval-gated agent run."
    }
    ACTIONS["agent_run_list"] = {
        "handler": action_agent_run_list,
        "risk": "read_only",
        "approval_required": False,
        "description": "List supervised agent runs."
    }
except Exception:
    pass


def route_action_from_text(text):
    lowered = (text or "").lower()

    if _v26_previous_route_action_from_text:
        action_id, args = _v26_previous_route_action_from_text(text)
        if action_id:
            return action_id, args

    if "create agent run" in lowered or "prepare agent run" in lowered or "supervised agent run" in lowered:
        return "agent_run_create", {"task": text}

    if "list agent runs" in lowered or "show agent runs" in lowered:
        return "agent_run_list", {}

    return None, None


def maybe_handle_action_text(text):
    action_id, args = route_action_from_text(text)
    if action_id:
        result = run_action(action_id, args)
        return result.get("spoken_message")

    if _v26_previous_maybe_handle_action_text:
        return _v26_previous_maybe_handle_action_text(text)

    return None

# v2.7 executor bridge / repo doctor / voice upgrade natural action integration.
try:
    _v27_previous_route_action_from_text = route_action_from_text
except Exception:
    _v27_previous_route_action_from_text = None

try:
    _v27_previous_maybe_handle_action_text = maybe_handle_action_text
except Exception:
    _v27_previous_maybe_handle_action_text = None


def action_executor_plan(args=None):
    args = args or {}
    try:
        from seed_external_executor_bridge import create_executor_plan
        result = create_executor_plan(args.get("task", "unspecified executor task"))
        return action_result(
            "executor_plan",
            ok=result.get("ok"),
            verified=result.get("ok"),
            risk="external_agent_plan",
            spoken_message=f"I created a manual executor plan: {result.get('plan_id')}. External execution is still locked.",
            data=result
        )
    except Exception as error:
        return action_result(
            "executor_plan",
            ok=False,
            verified=False,
            risk="external_agent_plan",
            spoken_message=f"Could not create executor plan: {error}",
            data={"error": str(error)}
        )


def action_repo_doctor(args=None):
    try:
        from seed_repo_doctor import run_repo_doctor
        result = run_repo_doctor()
        return action_result(
            "repo_doctor",
            ok=result.get("ok"),
            verified=True,
            risk="read_only",
            spoken_message=f"Repo Doctor finished. Findings: {len(result.get('findings', []))}. Recommendations: {len(result.get('recommendations', []))}.",
            data=result
        )
    except Exception as error:
        return action_result(
            "repo_doctor",
            ok=False,
            verified=False,
            risk="read_only",
            spoken_message=f"Repo Doctor failed: {error}",
            data={"error": str(error)}
        )


def action_voice_upgrade_plan(args=None):
    try:
        from seed_voice_upgrade_planner import build_voice_upgrade_plan
        result = build_voice_upgrade_plan()
        return action_result(
            "voice_upgrade_plan",
            ok=result.get("ok"),
            verified=True,
            risk="read_only",
            spoken_message=f"Voice upgrade plan created. Recommended next patch: {result.get('recommended_next_patch')}",
            data=result
        )
    except Exception as error:
        return action_result(
            "voice_upgrade_plan",
            ok=False,
            verified=False,
            risk="read_only",
            spoken_message=f"Voice upgrade planning failed: {error}",
            data={"error": str(error)}
        )


try:
    ACTIONS["executor_plan"] = {
        "handler": action_executor_plan,
        "risk": "external_agent_plan",
        "approval_required": False,
        "description": "Create a manual-only external executor plan."
    }
    ACTIONS["repo_doctor"] = {
        "handler": action_repo_doctor,
        "risk": "read_only",
        "approval_required": False,
        "description": "Run read-only repo doctor."
    }
    ACTIONS["voice_upgrade_plan"] = {
        "handler": action_voice_upgrade_plan,
        "risk": "read_only",
        "approval_required": False,
        "description": "Create read-only voice upgrade plan."
    }
except Exception:
    pass


def route_action_from_text(text):
    lowered = (text or "").lower()

    if _v27_previous_route_action_from_text:
        action_id, args = _v27_previous_route_action_from_text(text)
        if action_id:
            return action_id, args

    if "repo doctor" in lowered or "diagnose repo" in lowered:
        return "repo_doctor", {}

    if "voice upgrade" in lowered or "improve voice plan" in lowered or "voice improvement plan" in lowered:
        return "voice_upgrade_plan", {}

    if "executor plan" in lowered or "external executor" in lowered or "aider plan" in lowered or "openhands plan" in lowered:
        return "executor_plan", {"task": text}

    return None, None


def maybe_handle_action_text(text):
    action_id, args = route_action_from_text(text)
    if action_id:
        result = run_action(action_id, args)
        return result.get("spoken_message")

    if _v27_previous_maybe_handle_action_text:
        return _v27_previous_maybe_handle_action_text(text)

    return None

# v2.8 Aider first executor bridge natural action integration.
try:
    _v28_previous_route_action_from_text = route_action_from_text
except Exception:
    _v28_previous_route_action_from_text = None

try:
    _v28_previous_maybe_handle_action_text = maybe_handle_action_text
except Exception:
    _v28_previous_maybe_handle_action_text = None


def action_aider_plan(args=None):
    args = args or {}
    try:
        from seed_aider_bridge import create_aider_plan
        result = create_aider_plan(args.get("task", "unspecified Aider task"))
        return action_result(
            "aider_plan",
            ok=result.get("ok"),
            verified=result.get("ok"),
            risk="file_write_agent_plan",
            spoken_message=f"I created a manual-only Aider plan: {result.get('plan_id')}. Aider execution is still locked.",
            data=result
        )
    except Exception as error:
        return action_result(
            "aider_plan",
            ok=False,
            verified=False,
            risk="file_write_agent_plan",
            spoken_message=f"Could not create Aider plan: {error}",
            data={"error": str(error)}
        )


def action_aider_status(args=None):
    try:
        from seed_aider_bridge import detect_aider
        result = detect_aider()
        return action_result(
            "aider_status",
            ok=True,
            verified=True,
            risk="read_only",
            spoken_message=f"Aider available: {result.get('aider_available')}.",
            data=result
        )
    except Exception as error:
        return action_result(
            "aider_status",
            ok=False,
            verified=False,
            risk="read_only",
            spoken_message=f"Could not check Aider status: {error}",
            data={"error": str(error)}
        )


try:
    ACTIONS["aider_plan"] = {
        "handler": action_aider_plan,
        "risk": "file_write_agent_plan",
        "approval_required": False,
        "description": "Create a manual-only Aider plan."
    }
    ACTIONS["aider_status"] = {
        "handler": action_aider_status,
        "risk": "read_only",
        "approval_required": False,
        "description": "Check Aider availability."
    }
except Exception:
    pass


def route_action_from_text(text):
    lowered = (text or "").lower()

    if _v28_previous_route_action_from_text:
        action_id, args = _v28_previous_route_action_from_text(text)
        if action_id:
            return action_id, args

    if "aider status" in lowered or "is aider installed" in lowered:
        return "aider_status", {}

    if "aider plan" in lowered or "use aider" in lowered or "prepare aider" in lowered:
        return "aider_plan", {"task": text}

    return None, None


def maybe_handle_action_text(text):
    action_id, args = route_action_from_text(text)
    if action_id:
        result = run_action(action_id, args)
        return result.get("spoken_message")

    if _v28_previous_maybe_handle_action_text:
        return _v28_previous_maybe_handle_action_text(text)

    return None

# v2.9 Mission Control MegaPack natural action integration.
try:
    _v29_previous_route_action_from_text = route_action_from_text
except Exception:
    _v29_previous_route_action_from_text = None

try:
    _v29_previous_maybe_handle_action_text = maybe_handle_action_text
except Exception:
    _v29_previous_maybe_handle_action_text = None


def action_mission_control(args=None):
    try:
        from seed_mission_control import mission_control_snapshot
        result = mission_control_snapshot()
        return action_result(
            "mission_control",
            ok=result.get("ok"),
            verified=True,
            risk="read_only",
            spoken_message=f"Mission Control is ready. Next actions: {len(result.get('next_actions', []))}.",
            data=result
        )
    except Exception as error:
        return action_result("mission_control", False, False, "read_only", f"Mission Control failed: {error}", {"error": str(error)})


def action_self_repair_plan(args=None):
    try:
        from seed_self_repair_planner import build_self_repair_plan
        result = build_self_repair_plan()
        return action_result(
            "self_repair_plan",
            ok=True,
            verified=True,
            risk="read_only",
            spoken_message=f"Self-repair plan built. Failures: {len(result.get('failures', []))}.",
            data=result
        )
    except Exception as error:
        return action_result("self_repair_plan", False, False, "read_only", f"Self-repair planner failed: {error}", {"error": str(error)})


def action_voice_ux(args=None):
    try:
        from seed_voice_ux_pack import voice_ux_snapshot
        result = voice_ux_snapshot()
        return action_result(
            "voice_ux",
            ok=result.get("ok"),
            verified=True,
            risk="read_only",
            spoken_message=f"Voice UX pack is ready. Next voice patch has {len(result.get('next_voice_patch', []))} items.",
            data=result
        )
    except Exception as error:
        return action_result("voice_ux", False, False, "read_only", f"Voice UX failed: {error}", {"error": str(error)})


try:
    ACTIONS["mission_control"] = {
        "handler": action_mission_control,
        "risk": "read_only",
        "approval_required": False,
        "description": "Show Seed Mission Control."
    }
    ACTIONS["self_repair_plan"] = {
        "handler": action_self_repair_plan,
        "risk": "read_only",
        "approval_required": False,
        "description": "Build self-repair plan."
    }
    ACTIONS["voice_ux"] = {
        "handler": action_voice_ux,
        "risk": "read_only",
        "approval_required": False,
        "description": "Show voice UX status."
    }
except Exception:
    pass


def route_action_from_text(text):
    lowered = (text or "").lower()

    if _v29_previous_route_action_from_text:
        action_id, args = _v29_previous_route_action_from_text(text)
        if action_id:
            return action_id, args

    if "mission control" in lowered or "command center" in lowered or "seed dashboard" in lowered:
        return "mission_control", {}

    if "self repair" in lowered or "repair plan" in lowered or "fix import" in lowered:
        return "self_repair_plan", {}

    if "voice ux" in lowered or "voice debug" in lowered:
        return "voice_ux", {}

    return None, None


def maybe_handle_action_text(text):
    action_id, args = route_action_from_text(text)
    if action_id:
        result = run_action(action_id, args)
        return result.get("spoken_message")

    if _v29_previous_maybe_handle_action_text:
        return _v29_previous_maybe_handle_action_text(text)

    return None

# v3.0 Jarvis Control Plane natural action integration.
try:
    _v30_previous_route_action_from_text = route_action_from_text
except Exception:
    _v30_previous_route_action_from_text = None

try:
    _v30_previous_maybe_handle_action_text = maybe_handle_action_text
except Exception:
    _v30_previous_maybe_handle_action_text = None


def action_control_plane_status(args=None):
    try:
        from seed_control_plane_launcher import control_plane_status
        result = control_plane_status()
        return action_result(
            "control_plane_status",
            ok=True,
            verified=True,
            risk="read_only",
            spoken_message=f"Control Plane is configured at {result.get('url')}.",
            data=result
        )
    except Exception as error:
        return action_result("control_plane_status", False, False, "read_only", f"Control Plane status failed: {error}", {"error": str(error)})


def action_gate_matrix(args=None):
    try:
        from seed_gate_matrix import run_gate_matrix
        result = run_gate_matrix()
        return action_result(
            "gate_matrix",
            ok=result.get("ok"),
            verified=True,
            risk="diagnostic",
            spoken_message=f"Gate Matrix finished. Passed {result.get('passed')}/{result.get('count')}.",
            data=result
        )
    except Exception as error:
        return action_result("gate_matrix", False, False, "diagnostic", f"Gate Matrix failed: {error}", {"error": str(error)})


def action_runtime_supervisor(args=None):
    try:
        from seed_runtime_supervisor import runtime_supervisor_snapshot
        result = runtime_supervisor_snapshot()
        return action_result(
            "runtime_supervisor",
            ok=result.get("ok"),
            verified=True,
            risk="read_only",
            spoken_message=f"Runtime Supervisor finished. OK: {result.get('ok')}.",
            data=result
        )
    except Exception as error:
        return action_result("runtime_supervisor", False, False, "read_only", f"Runtime Supervisor failed: {error}", {"error": str(error)})


try:
    ACTIONS["control_plane_status"] = {
        "handler": action_control_plane_status,
        "risk": "read_only",
        "approval_required": False,
        "description": "Show Control Plane status."
    }
    ACTIONS["gate_matrix"] = {
        "handler": action_gate_matrix,
        "risk": "diagnostic",
        "approval_required": False,
        "description": "Run full gate matrix."
    }
    ACTIONS["runtime_supervisor"] = {
        "handler": action_runtime_supervisor,
        "risk": "read_only",
        "approval_required": False,
        "description": "Show runtime supervisor."
    }
except Exception:
    pass


def route_action_from_text(text):
    lowered = (text or "").lower()

    if _v30_previous_route_action_from_text:
        action_id, args = _v30_previous_route_action_from_text(text)
        if action_id:
            return action_id, args

    if "control plane" in lowered or "jarvis dashboard" in lowered or "local dashboard" in lowered:
        return "control_plane_status", {}

    if "gate matrix" in lowered or "run all gates" in lowered or "full check" in lowered:
        return "gate_matrix", {}

    if "runtime supervisor" in lowered or "runtime status" in lowered:
        return "runtime_supervisor", {}

    return None, None


def maybe_handle_action_text(text):
    action_id, args = route_action_from_text(text)
    if action_id:
        result = run_action(action_id, args)
        return result.get("spoken_message")

    if _v30_previous_maybe_handle_action_text:
        return _v30_previous_maybe_handle_action_text(text)

    return None
