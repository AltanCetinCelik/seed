import json

from seed_config import SKILL_PLAN_MAX_STEPS
from seed_llm import ask_llm
from seed_skill_kernel import format_skill_map, get_capability
from seed_capability_runtime import run_capability
from seed_permission_engine import risk_allows_auto_run
from seed_open_source_dna import format_borrow_map
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


def build_skill_plan_prompt(goal):
    skill_map = format_skill_map()
    borrow_map = format_borrow_map()

    return f"""
You are Seed's Skill OS planner.

Altan's goal:
{goal}

Available Seed skills and capabilities:
{skill_map}

Open-source DNA borrow map:
{borrow_map}

Rules:
- Return JSON only.
- Return a JSON array.
- Maximum steps: {SKILL_PLAN_MAX_STEPS}.
- Use capability_id values from the skill map.
- Do not invent capabilities.
- Prefer read_only and diagnostic capabilities first.
- Any write, dangerous, or external action must be marked requires_approval.
- Do not claim Seed has done something unless the plan actually executes it.

JSON step shape:
{{
  "step": 1,
  "capability_id": "project.report",
  "risk": "read_only",
  "reason": "Inspect current project architecture."
}}
"""


def create_skill_plan(goal, chat_state=None):
    print("\n=== SKILL PLAN ===")

    response = ask_llm(
        build_skill_plan_prompt(goal),
        task_type="debug",
        runtime_context=chat_state
    )

    plan = extract_json_array(response)

    if plan is None:
        print("Seed could not create a valid skill plan.")
        print("\nRaw response:")
        print(response)
        return None

    plan = plan[:SKILL_PLAN_MAX_STEPS]

    valid_plan = []

    for step in plan:
        capability_id = step.get("capability_id")

        if get_capability(capability_id) is None:
            continue

        valid_plan.append(step)

    if chat_state is not None:
        chat_state["pending_skill_plan"] = valid_plan

        log_system_event(
            chat_state.get("log_path"),
            f"Skill plan created for goal: {goal}"
        )

    print(format_skill_plan(valid_plan))

    return valid_plan


def format_skill_plan(plan):
    if not plan:
        return "No skill plan available."

    text = "=== PENDING SKILL PLAN ===\n"

    for step in plan:
        text += f"\nStep {step.get('step')}\n"
        text += f"  Capability: {step.get('capability_id')}\n"
        text += f"  Risk: {step.get('risk')}\n"
        text += f"  Reason: {step.get('reason')}\n"

    return text


def show_pending_skill_plan(chat_state):
    plan = chat_state.get("pending_skill_plan")

    if not plan:
        print("No pending skill plan.")
        return

    print("\n" + format_skill_plan(plan))


def run_readonly_skill_plan(chat_state):
    print("\n=== RUN READ-ONLY SKILL PLAN ===")

    plan = chat_state.get("pending_skill_plan")

    if not plan:
        print("No pending skill plan.")
        return

    outputs = []

    for step in plan:
        capability_id = step.get("capability_id")
        item = get_capability(capability_id)

        if item is None:
            outputs.append(f"Skipped unknown capability: {capability_id}")
            continue

        capability = item["capability"]
        risk = capability.get("risk")

        if not risk_allows_auto_run(risk):
            outputs.append(
                f"Skipped approval-required capability: {capability_id}"
            )
            continue

        result = run_capability(capability_id, chat_state)
        outputs.append(f"\n=== {capability_id} ===\n{result}")

    if not outputs:
        print("No read-only or diagnostic capabilities executed.")
        return

    output_text = "\n".join(outputs)
    print(output_text)

    chat_state["last_skill_run"] = output_text

    log_system_event(
        chat_state.get("log_path"),
        "Read-only Skill OS plan executed."
    )