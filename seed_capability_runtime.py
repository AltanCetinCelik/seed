from seed_skill_kernel import get_capability
from seed_permission_engine import (
    describe_permission,
    risk_allows_auto_run
)
from seed_tool_kernel import execute_tool
from seed_chat_logger import log_system_event


def format_capability(capability_query):
    item = get_capability(capability_query)

    if item is None:
        return f"No capability found for: {capability_query}"

    capability = item["capability"]
    permission = describe_permission(capability)

    text = f"=== CAPABILITY: {capability.get('name')} ===\n"
    text += f"ID: {capability.get('id')}\n"
    text += f"Skill: {item.get('skill_name')}\n"
    text += f"Category: {item.get('skill_category')}\n"
    text += f"Risk: {capability.get('risk')}\n"
    text += f"Description: {capability.get('description')}\n"
    text += f"Permission: {permission.get('message')}\n"

    if "tool" in capability:
        text += f"Tool: {capability.get('tool')}\n"

    if "command" in capability:
        text += f"Command: {capability.get('command')}\n"

    return text


def show_capability(capability_query):
    print("\n" + format_capability(capability_query))


def run_capability(capability_query, chat_state=None, approval_phrase=None):
    item = get_capability(capability_query)

    if item is None:
        return f"No capability found for: {capability_query}"

    capability = item["capability"]
    risk = capability.get("risk")
    capability_id = capability.get("id")

    permission = describe_permission(capability)

    if not risk_allows_auto_run(risk):
        expected_phrase = permission.get("approval_phrase")

        if approval_phrase != expected_phrase:
            text = "Capability not executed.\n"
            text += permission.get("message", "Approval required.") + "\n"

            if "command" in capability:
                text += (
                    f"Use the existing command instead when ready: "
                    f"{capability.get('command')}\n"
                )

            return text

    if "tool" in capability:
        result = execute_tool(capability.get("tool"), chat_state)

        if chat_state is not None:
            log_system_event(
                chat_state.get("log_path"),
                f"Capability executed: {capability_id}"
            )

        return result

    if "command" in capability:
        return (
            "This capability maps to an interactive command and was not "
            "auto-executed.\n"
            f"Run manually: {capability.get('command')}"
        )

    return "Capability has no executable tool or command."


def show_capability_result(capability_query, chat_state=None):
    print(f"\n=== RUN CAPABILITY: {capability_query} ===")
    print(run_capability(capability_query, chat_state))