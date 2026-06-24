import json
from datetime import datetime


try:
    from seed_config import SEED_WORKFLOW_BRAIN_STATE_FILE
except Exception:
    SEED_WORKFLOW_BRAIN_STATE_FILE = "seed_workflow_brain_state.json"


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def classify_intent(text):
    lowered = (text or "").lower()

    if any(w in lowered for w in ["open", "launch", "show cockpit", "browser"]):
        return "action"
    if any(w in lowered for w in ["remember", "save this", "note that"]):
        return "memory_write"
    if any(w in lowered for w in ["search", "find", "recall", "what did we"]):
        return "memory_recall"
    if any(w in lowered for w in ["fix", "bug", "code", "repo", "implement", "agent"]):
        return "coding_or_agent"
    if any(w in lowered for w in ["website", "web", "browser-use", "online"]):
        return "browser_or_web"
    if any(w in lowered for w in ["mcp", "tool server", "connector"]):
        return "mcp_tooling"
    if any(w in lowered for w in ["voice", "hear", "microphone", "stt", "tts"]):
        return "voice"
    return "general"


def build_workflow_plan(user_text):
    intent = classify_intent(user_text)

    memory_results = []
    semantic_context = ""
    route = {}
    action_id = None
    action_args = None

    try:
        from seed_semantic_memory import semantic_search, semantic_memory_context
        memory_results = semantic_search(user_text, rebuild=False, max_results=5)
        semantic_context = semantic_memory_context(user_text)
    except Exception as error:
        semantic_context = f"Semantic memory unavailable: {error}"

    try:
        from seed_tool_router import route_task
        route = route_task(user_text)
    except Exception as error:
        route = {"error": str(error)}

    try:
        from seed_action_kernel import route_action_from_text
        action_id, action_args = route_action_from_text(user_text)
    except Exception:
        action_id, action_args = None, None

    plan = {
        "created_at": now_timestamp(),
        "version": "v2.3.0",
        "user_text": user_text,
        "intent": intent,
        "semantic_memory_matches": memory_results,
        "route": route,
        "action_candidate": action_id,
        "action_args": action_args,
        "execution_mode": "plan_first",
        "approval_required_for_risky_actions": True,
        "safe_workflow": [
            "Classify intent",
            "Recall relevant semantic memory",
            "Route to capability/tool",
            "If action exists, send through action kernel",
            "If risky, ask approval",
            "Verify result",
            "Answer based on verified facts"
        ],
        "semantic_context": semantic_context
    }

    try:
        with open(SEED_WORKFLOW_BRAIN_STATE_FILE, "w") as file:
            json.dump(plan, file, indent=4)
    except Exception:
        pass

    return plan


def workflow_answer_hint(user_text):
    plan = build_workflow_plan(user_text)

    text = "=== WORKFLOW BRAIN CONTEXT ===\n"
    text += f"Intent: {plan.get('intent')}\n"
    text += f"Action candidate: {plan.get('action_candidate')}\n"
    text += f"Route: {plan.get('route', {}).get('best_capability')}\n"

    if plan.get("semantic_memory_matches"):
        text += "Top semantic memory:\n"
        for result in plan["semantic_memory_matches"][:3]:
            text += f"- {result.get('path')} score={result.get('score')}: {result.get('snippet')[:250]}\n"
    else:
        text += "Top semantic memory: none\n"

    text += "Rule: answer from verified action results and retrieved memory; do not invent.\n"
    return text


def show_workflow_plan():
    text = input("Workflow task: ").strip()
    plan = build_workflow_plan(text)
    print("\n=== SEED WORKFLOW BRAIN PLAN ===")
    print(json.dumps(plan, indent=4))


def show_workflow_context():
    text = input("Workflow context task: ").strip()
    print(workflow_answer_hint(text))


if __name__ == "__main__":
    show_workflow_plan()
