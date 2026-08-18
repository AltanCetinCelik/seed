import json
from datetime import datetime


try:
    from seed_config import SEED_AGENT_ORCHESTRATOR_TRACE_FILE
except Exception:
    SEED_AGENT_ORCHESTRATOR_TRACE_FILE = "seed_agent_orchestrator_trace.jsonl"


try:
    from seed_tool_router import route_task
    ROUTER_AVAILABLE = True
except Exception:
    ROUTER_AVAILABLE = False


try:
    from seed_capability_planner import build_capability_plan
    PLANNER_AVAILABLE = True
except Exception:
    PLANNER_AVAILABLE = False


try:
    from seed_agent_tool_profiles import agent_tool_profiles_data, show_agent_tool_profiles, show_agent_install_plan
    PROFILES_AVAILABLE = True
except Exception:
    PROFILES_AVAILABLE = False


try:
    from seed_agent_executor import propose_agent_execution, show_agent_diagnostic
    EXECUTOR_AVAILABLE = True
except Exception:
    EXECUTOR_AVAILABLE = False


try:
    from seed_companion_os import append_companion_os_event, append_companion_os_journal
    COMPANION_OS_AVAILABLE = True
except Exception:
    COMPANION_OS_AVAILABLE = False


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def append_orchestrator_trace(data):
    try:
        with open(SEED_AGENT_ORCHESTRATOR_TRACE_FILE, "a") as file:
            file.write(json.dumps(data) + "\n")
    except Exception:
        pass


def choose_tool_for_capability(capability, route):
    tools = route.get("recommended_tools", [])

    if not tools:
        return None

    if PROFILES_AVAILABLE:
        data = agent_tool_profiles_data(refresh=True)
        profiles = data.get("profiles", [])
        available = {p.get("id"): p for p in profiles if p.get("available")}

        for tool in tools:
            if tool in available:
                return tool

    return tools[0]


def build_agent_task(task):
    if ROUTER_AVAILABLE:
        route = route_task(task)
    else:
        route = {
            "best_capability": "unknown",
            "recommended_tools": [],
            "risk": "unknown",
            "approval": "required_if_action_has_side_effects",
            "sandbox": "manual review"
        }

    if PLANNER_AVAILABLE:
        plan = build_capability_plan(task)
    else:
        plan = {
            "task": task,
            "capability": route.get("best_capability"),
            "recommended_tools": route.get("recommended_tools", []),
            "risk": route.get("risk"),
            "approval_required": True,
            "sandbox_plan": route.get("sandbox")
        }

    selected_tool = choose_tool_for_capability(route.get("best_capability"), route)

    packet = {
        "created_at": now_timestamp(),
        "task": task,
        "capability": route.get("best_capability"),
        "selected_tool": selected_tool,
        "route": route,
        "plan": plan,
        "approval_required": True,
        "status": "planned_not_executed",
        "rule": "Seed may plan and queue approval. It must not run file/shell/browser agents without User approval."
    }

    append_orchestrator_trace(packet)

    if COMPANION_OS_AVAILABLE:
        try:
            append_companion_os_event(
                "agent_task_planned",
                "Agent task planned",
                {
                    "capability": packet["capability"],
                    "selected_tool": selected_tool
                },
                source="agent_orchestrator",
                importance=4
            )
        except Exception:
            pass

    return packet


def run_agent_task_interactive():
    print("\n=== AGENT TASK ORCHESTRATOR ===")
    task = input("Task: ").strip()

    if not task:
        print("Task required.")
        return

    packet = build_agent_task(task)
    print(json.dumps(packet, indent=4))

    if EXECUTOR_AVAILABLE:
        answer = input("\nQueue approval for this agent route? y/n: ").strip().lower()
        if answer == "y":
            proposal = propose_agent_execution(
                task=task,
                capability=packet.get("capability"),
                tool_id=packet.get("selected_tool")
            )
            print("\n=== APPROVAL QUEUED / PROPOSAL CREATED ===")
            print(json.dumps(proposal, indent=4))


def show_agent_task_plan():
    task = input("Task: ").strip()
    if not task:
        print("Task required.")
        return
    packet = build_agent_task(task)
    print("\n=== AGENT TASK PLAN ===")
    print(json.dumps(packet, indent=4))


def get_agent_orchestrator_context_for_prompt(user_prompt=""):
    packet = build_agent_task(user_prompt or "general task")
    text = "=== AGENT ORCHESTRATOR CONTEXT ===\n"
    text += f"Capability: {packet.get('capability')}\n"
    text += f"Selected tool: {packet.get('selected_tool')}\n"
    text += f"Approval required: {packet.get('approval_required')}\n"
    text += f"Status: {packet.get('status')}\n"
    text += "Rule: plan/queue first; run file/shell/browser agents only after approval.\n"
    return text


if __name__ == "__main__":
    run_agent_task_interactive()

# v5.0.1 compatibility: skip heavy agent context for pasted terminal commands.
try:
    _seed_v501_original_agent_context = get_agent_orchestrator_context_for_prompt

    def get_agent_orchestrator_context_for_prompt(user_prompt=""):
        try:
            from seed_terminal_guard import looks_like_terminal_block
            if looks_like_terminal_block(user_prompt):
                return (
                    "=== SEED AGENT ORCHESTRATOR ===\n"
                    "Skipped heavy repo scan because the user pasted terminal commands.\n"
                    "Terminal commands should be run in macOS Terminal, not Seed chat.\n"
                )
        except Exception:
            pass

        return _seed_v501_original_agent_context(user_prompt)
except Exception:
    pass
