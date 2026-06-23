import json
from datetime import datetime

try:
    from seed_tool_router import route_task
except Exception:
    route_task = None

try:
    from seed_friend_advice_registry import get_friend_advice_context_for_prompt
except Exception:
    get_friend_advice_context_for_prompt = None


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def build_capability_plan(task):
    if route_task:
        route = route_task(task)
    else:
        route = {
            "task": task,
            "best_capability": "unknown",
            "risk": "unknown",
            "approval": "required_if_action_has_side_effects",
            "sandbox": "manual review",
            "recommended_tools": []
        }

    plan = {
        "created_at": now_timestamp(),
        "task": task,
        "capability": route.get("best_capability"),
        "recommended_tools": route.get("recommended_tools", []),
        "risk": route.get("risk"),
        "approval_required": route.get("approval") != "none",
        "approval_rule": route.get("approval"),
        "sandbox_plan": route.get("sandbox"),
        "safe_order": [
            "Understand task and classify capability",
            "Choose repo/tool candidate",
            "Explain side effects and risk",
            "Ask Altan for approval if write/browser/audio/external action is needed",
            "Use sandbox or branch",
            "Run tests/checks",
            "Trace decision",
            "Keep rollback path"
        ],
        "not_allowed": [
            "Do not install random repos blindly",
            "Do not run shell/write/browser/account actions without approval",
            "Do not enable always-listening",
            "Do not claim Seed is alive or conscious",
            "Do not rewrite working systems without backup"
        ],
        "route": route
    }

    return plan


def show_capability_match():
    task = input("Task: ").strip()
    plan = build_capability_plan(task)
    print("\n=== CAPABILITY MATCH ===")
    print(json.dumps(plan, indent=4))


def show_sandbox_plan():
    task = input("Task needing sandbox plan: ").strip()
    plan = build_capability_plan(task)
    print("\n=== SANDBOX PLAN ===")
    print(f"Task: {plan['task']}")
    print(f"Capability: {plan['capability']}")
    print(f"Risk: {plan['risk']}")
    print(f"Approval required: {plan['approval_required']}")
    print(f"Approval rule: {plan['approval_rule']}")
    print(f"Sandbox: {plan['sandbox_plan']}")
    print("\nSafe order:")
    for item in plan["safe_order"]:
        print(f"- {item}")
    print("\nNot allowed:")
    for item in plan["not_allowed"]:
        print(f"- {item}")


def get_capability_planner_context_for_prompt(user_prompt=""):
    plan = build_capability_plan(user_prompt or "general task")
    text = "=== CAPABILITY PLANNER CONTEXT ===\n"
    text += f"Capability: {plan['capability']}\n"
    text += f"Tools: {', '.join(plan['recommended_tools'])}\n"
    text += f"Risk: {plan['risk']}\n"
    text += f"Approval required: {plan['approval_required']}\n"
    text += f"Sandbox: {plan['sandbox_plan']}\n"
    if get_friend_advice_context_for_prompt:
        text += "\n" + get_friend_advice_context_for_prompt()
    return text


if __name__ == "__main__":
    show_capability_match()
