import io
from contextlib import redirect_stdout

from seed_system_snapshot import format_system_snapshot
from seed_project_inspector import (
    get_project_report,
    get_file_report,
    get_module_report
)
from seed_memory_tools import show_memory_stats, find_possible_duplicates
from seed_llm import show_llm_status
from seed_self_editor import show_editable_files, run_python_syntax_check
from seed_semantic_memory import show_semantic_memory_status
from seed_chat_logger import log_system_event
from seed_open_source_dna import (
    format_dna_status,
    format_borrow_map,
    format_borrow_candidates
)


def capture_printed_output(function, *args, **kwargs):
    buffer = io.StringIO()

    with redirect_stdout(buffer):
        function(*args, **kwargs)

    return buffer.getvalue()


TOOL_REGISTRY = {
    "system_snapshot": {
        "description": "Show Seed's current system state.",
        "risk": "read_only",
        "function": lambda chat_state=None: format_system_snapshot()
    },
    "project_report": {
        "description": "Show Seed project architecture report.",
        "risk": "read_only",
        "function": lambda chat_state=None: get_project_report()
    },
    "project_files": {
        "description": "List Seed project files.",
        "risk": "read_only",
        "function": lambda chat_state=None: get_file_report()
    },
    "open_source_dna_status": {
        "description": "Show open-source DNA research status.",
        "risk": "read_only",
        "function": lambda chat_state=None: format_dna_status()
    },
    "open_source_borrow_map": {
        "description": "Show Seed's borrow map from cloned open-source repos.",
        "risk": "read_only",
        "function": lambda chat_state=None: format_borrow_map()
    },
    "open_source_borrow_candidates": {
        "description": "Show candidate files from cloned repos worth studying.",
        "risk": "read_only",
        "function": lambda chat_state=None: format_borrow_candidates()
    },
    "project_modules": {
        "description": "List Seed Python modules.",
        "risk": "read_only",
        "function": lambda chat_state=None: get_module_report()
    },
    "memory_stats": {
        "description": "Show memory statistics.",
        "risk": "read_only",
        "function": lambda chat_state=None: capture_printed_output(show_memory_stats)
    },
    "memory_duplicates": {
        "description": "Find possible duplicate memories.",
        "risk": "read_only",
        "function": lambda chat_state=None: capture_printed_output(find_possible_duplicates)
    },
    "semantic_memory_status": {
        "description": "Show semantic memory cache status.",
        "risk": "read_only",
        "function": lambda chat_state=None: capture_printed_output(show_semantic_memory_status)
    },
    "llm_status": {
        "description": "Show LLM engine status.",
        "risk": "read_only",
        "function": lambda chat_state=None: capture_printed_output(show_llm_status, chat_state)
    },
    "self_edit_status": {
        "description": "Show self-editable file state.",
        "risk": "read_only",
        "function": lambda chat_state=None: capture_printed_output(show_editable_files)
    },
    "self_test": {
        "description": "Run Python syntax checks.",
        "risk": "diagnostic",
        "function": lambda chat_state=None: capture_printed_output(run_python_syntax_check, "")
    }
}


def list_tools():
    text = "=== SEED TOOL KERNEL ===\n"

    for tool_name, tool_info in TOOL_REGISTRY.items():
        text += f"\n{tool_name}\n"
        text += f"  Risk: {tool_info['risk']}\n"
        text += f"  Purpose: {tool_info['description']}\n"

    return text


def show_tools():
    print("\n" + list_tools())


def get_tool_info(tool_name):
    return TOOL_REGISTRY.get(tool_name)


def execute_tool(tool_name, chat_state=None):
    tool_info = get_tool_info(tool_name)

    if tool_info is None:
        return f"Unknown tool: {tool_name}"

    risk = tool_info["risk"]

    if risk not in ["read_only", "diagnostic"]:
        return f"Tool {tool_name} requires approval and cannot be auto-run."

    try:
        result = tool_info["function"](chat_state)
    except Exception as error:
        return f"Tool execution error for {tool_name}: {error}"

    if chat_state is not None:
        log_system_event(
            chat_state.get("log_path"),
            f"Tool executed: {tool_name}"
        )

    return result


def show_tool_result(tool_name, chat_state=None):
    print(f"\n=== TOOL: {tool_name} ===")
    print(execute_tool(tool_name, chat_state))


def get_tools_for_prompt():
    text = "=== AVAILABLE SEED TOOLS ===\n"

    for tool_name, tool_info in TOOL_REGISTRY.items():
        text += (
            f"- {tool_name}: "
            f"{tool_info['description']} "
            f"(risk: {tool_info['risk']})\n"
        )

    return text