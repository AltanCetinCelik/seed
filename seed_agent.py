import json

from seed_config import AGENT_MAX_PLAN_STEPS, AGENT_ALLOWED_AUTO_TOOLS
from seed_llm import ask_llm
from seed_system_snapshot import format_system_snapshot
from seed_tool_kernel import (
    get_tools_for_prompt,
    execute_tool,
    TOOL_REGISTRY
)
from seed_chat_logger import log_system_event


def extract_json_array(text):
    start = text.find("[")
    end = text.rfind("]")

    if start == -1 or end == -1 or end <= start:
        return None

    possible_json = text[start:end + 1]

    try:
        return json.loads(possible_json)
    except json.JSONDecodeError:
        return None


def build_agent_plan_prompt(user_goal):
    snapshot = format_system_snapshot()
    tools = get_tools_for_prompt()

    return f"""
You are Seed's local agent planning kernel.

Create a safe multi-step plan for User goal.

Goal:
{user_goal}

Seed system snapshot:
{snapshot}

Available tools:
{tools}

Rules:
- Return JSON only.
- Return a JSON array of steps.
- Maximum steps: {AGENT_MAX_PLAN_STEPS}
- Use only tools from the available tools list.
- Prefer read_only or diagnostic tools first.
- Do not include file edits unless the user explicitly asks for an implementation plan.
- Risk must be one of: read_only, diagnostic, requires_approval.
- Every step must have: step, tool, reason, risk.
- If no tool is needed, use tool "none".

Example:
[
  {{
    "step": 1,
    "tool": "system_snapshot",
    "reason": "Inspect current system state.",
    "risk": "read_only"
  }}
]
"""


def create_agent_plan(user_goal, chat_state=None):
    print("\n=== AGENT PLAN ===")

    prompt = build_agent_plan_prompt(user_goal)

    response = ask_llm(
        prompt,
        task_type="debug",
        runtime_context=chat_state
    )

    plan = extract_json_array(response)

    if plan is None:
        print("Seed could not create a valid JSON plan.")
        print("\nRaw response:")
        print(response)
        return None

    if len(plan) > AGENT_MAX_PLAN_STEPS:
        plan = plan[:AGENT_MAX_PLAN_STEPS]

    if chat_state is not None:
        chat_state["pending_agent_plan"] = plan

        log_system_event(
            chat_state.get("log_path"),
            f"Agent plan created for goal: {user_goal}"
        )

    print(format_agent_plan(plan))

    return plan


def format_agent_plan(plan):
    text = "=== PENDING AGENT PLAN ===\n"

    for item in plan:
        text += f"\nStep {item.get('step')}\n"
        text += f"  Tool: {item.get('tool')}\n"
        text += f"  Risk: {item.get('risk')}\n"
        text += f"  Reason: {item.get('reason')}\n"

    return text


def show_pending_agent_plan(chat_state):
    plan = chat_state.get("pending_agent_plan")

    if not plan:
        print("No pending agent plan.")
        return

    print("\n" + format_agent_plan(plan))


def run_readonly_agent_plan(chat_state):
    print("\n=== RUN READ-ONLY AGENT PLAN ===")

    plan = chat_state.get("pending_agent_plan")

    if not plan:
        print("No pending agent plan.")
        return

    results = []

    for item in plan:
        tool_name = item.get("tool")
        risk = item.get("risk")

        if tool_name == "none":
            continue

        if tool_name not in TOOL_REGISTRY:
            results.append(f"Unknown tool skipped: {tool_name}")
            continue

        if tool_name not in AGENT_ALLOWED_AUTO_TOOLS:
            results.append(f"Tool not allowed for auto-run: {tool_name}")
            continue

        if risk not in ["read_only", "diagnostic"]:
            results.append(f"Skipped approval-required step: {tool_name}")
            continue

        result = execute_tool(tool_name, chat_state)
        results.append(f"\n=== {tool_name} ===\n{result}")

    if not results:
        print("No read-only steps were executed.")
        return

    output = "\n".join(results)
    print(output)

    chat_state["last_agent_run"] = output

    log_system_event(
        chat_state.get("log_path"),
        "Read-only agent plan executed."
    )


def generate_self_review(chat_state=None):
    print("\n=== SEED SELF-REVIEW ===")

    snapshot = format_system_snapshot()
    tools = get_tools_for_prompt()

    prompt = f"""
You are Seed's self-review engine.

Review Seed's current system state and propose the most important next upgrades.

Use only the system snapshot and available tools below.
Do not invent capabilities.
Be strict.
Do not call Seed v2.0.0 worthy unless it has:
- cognition engine
- semantic memory
- smart memory capture
- safe self-editing
- tool kernel
- planner loop
- self-review
- boot sequence
- visual presence
- approval gates

Output:
1. Current strengths
2. Current weaknesses
3. Top 5 next upgrades
4. Risks
5. Whether Seed is v2.0.0-worthy yet
6. The single best next action

System snapshot:
{snapshot}

Available tools:
{tools}
"""

    review = ask_llm(
        prompt,
        task_type="debug",
        runtime_context=chat_state
    )

    print(review)

    if chat_state is not None:
        chat_state["last_self_review"] = review

        log_system_event(
            chat_state.get("log_path"),
            "Self-review generated."
        )

    return review


def show_boot_brief(chat_state=None):
    print("\n=== SEED BOOT BRIEF ===")

    snapshot = format_system_snapshot()

    print(snapshot)

    print("\n=== BOOT RECOMMENDATION ===")
    print("Recommended next move:")
    print("- Run /self-review to generate an improvement report.")
    print("- Run /agent-plan <goal> to create a safe plan.")
    print("- Run /agent-run-readonly to execute safe diagnostic steps.")
    print("- Use self-edit commands only after reviewing diffs and approval gates.")

    if chat_state is not None:
        log_system_event(
            chat_state.get("log_path"),
            "Boot brief shown."
        )


def show_agent_status(chat_state=None):
    print("\n=== AGENT STATUS ===")

    if chat_state is None:
        chat_state = {}

    pending_plan = chat_state.get("pending_agent_plan")
    last_run = chat_state.get("last_agent_run")
    last_review = chat_state.get("last_self_review")

    print(f"Pending plan: {pending_plan is not None}")
    print(f"Last read-only run: {last_run is not None}")
    print(f"Last self-review: {last_review is not None}")
    print(f"Available tools: {len(TOOL_REGISTRY)}")
    print(f"Allowed auto-run tools: {len(AGENT_ALLOWED_AUTO_TOOLS)}")