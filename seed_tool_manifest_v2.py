import json
from datetime import datetime


try:
    from seed_trace_engine import record_tool_trace
    TRACE_AVAILABLE = True
except Exception:
    TRACE_AVAILABLE = False


try:
    from seed_companion_os import append_companion_os_event
    COMPANION_OS_AVAILABLE = True
except Exception:
    COMPANION_OS_AVAILABLE = False


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


TOOL_MANIFEST_V2 = [
    {
        "id": "core.status",
        "name": "Seed Status",
        "owner": "core",
        "risk": "read_only",
        "approval_policy": "not_required",
        "inputs": [],
        "outputs": ["text_status_report"],
        "side_effects": [],
        "allowed_auto_run": True,
        "blocked_conditions": [],
        "commands": ["/status"],
        "source_repos": [],
        "v2_pillars": ["Safety", "Cockpit"]
    },
    {
        "id": "memory.save_smart",
        "name": "Smart Memory Save",
        "owner": "smart_memory",
        "risk": "write",
        "approval_policy": "user_must_approve_memory_draft",
        "inputs": ["natural_language_memory"],
        "outputs": ["memory_draft", "saved_memory_if_approved"],
        "side_effects": ["writes_to_seed_memory_json", "may_update_semantic_index"],
        "allowed_auto_run": False,
        "blocked_conditions": ["sensitive_memory_without_clear_user_request"],
        "commands": ["/save", "/remember", "/memory-approve"],
        "source_repos": ["Letta", "Khoj", "AnythingLLM"],
        "v2_pillars": ["Memory", "Continuity"]
    },
    {
        "id": "memory.semantic_search",
        "name": "Semantic Memory Search",
        "owner": "semantic_memory",
        "risk": "read_only",
        "approval_policy": "not_required",
        "inputs": ["query"],
        "outputs": ["semantic_memory_results"],
        "side_effects": [],
        "allowed_auto_run": True,
        "blocked_conditions": [],
        "commands": ["/semantic-search", "/semantic-context"],
        "source_repos": ["Letta", "Khoj"],
        "v2_pillars": ["Memory", "Continuity"]
    },
    {
        "id": "project.inspect",
        "name": "Project Inspector",
        "owner": "project_inspector",
        "risk": "read_only",
        "approval_policy": "not_required",
        "inputs": ["project_root"],
        "outputs": ["file_report", "module_report", "version_report"],
        "side_effects": [],
        "allowed_auto_run": True,
        "blocked_conditions": [],
        "commands": ["/project", "/files", "/modules", "/version"],
        "source_repos": ["Aider", "SWE-agent"],
        "v2_pillars": ["Self-improvement"]
    },
    {
        "id": "code.map",
        "name": "Code Map",
        "owner": "code_map",
        "risk": "diagnostic",
        "approval_policy": "not_required",
        "inputs": ["project_files"],
        "outputs": ["seed_code_map_json", "code_map_report"],
        "side_effects": ["writes_seed_code_map_json"],
        "allowed_auto_run": True,
        "blocked_conditions": [],
        "commands": ["/code-map-build", "/code-map"],
        "source_repos": ["Aider", "SWE-agent", "mini-SWE-agent"],
        "v2_pillars": ["Self-improvement"]
    },
    {
        "id": "self_edit.propose",
        "name": "Self-Edit Proposal",
        "owner": "self_editor",
        "risk": "write",
        "approval_policy": "proposal_only_until_user_reviews_diff",
        "inputs": ["target_file", "edit_instruction"],
        "outputs": ["pending_edit", "diff"],
        "side_effects": ["writes_seed_pending_edit_json"],
        "allowed_auto_run": False,
        "blocked_conditions": ["protected_file", "protected_folder", "unsupported_extension"],
        "commands": ["/self-edit", "/self-diff"],
        "source_repos": ["Cline", "Aider", "OpenHands"],
        "v2_pillars": ["Self-improvement", "Safety"]
    },
    {
        "id": "self_edit.apply",
        "name": "Apply Self-Edit",
        "owner": "self_editor",
        "risk": "write",
        "approval_policy": "exact_apply_confirmation_required",
        "inputs": ["pending_edit"],
        "outputs": ["edited_file", "backup"],
        "side_effects": ["edits_project_file", "creates_backup"],
        "allowed_auto_run": False,
        "blocked_conditions": ["missing_pending_edit", "failed_syntax_check", "protected_file"],
        "commands": ["/self-apply"],
        "source_repos": ["Cline", "Aider"],
        "v2_pillars": ["Self-improvement", "Safety"]
    },
    {
        "id": "local.shell",
        "name": "Local Shell Command",
        "owner": "local_control",
        "risk": "dangerous",
        "approval_policy": "allowlist_or_exact_approval_phrase",
        "inputs": ["shell_command"],
        "outputs": ["stdout", "stderr", "returncode"],
        "side_effects": ["runs_local_shell_command", "writes_action_history"],
        "allowed_auto_run": False,
        "blocked_conditions": ["emergency_lock", "forbidden_command_substring", "not_allowlisted_without_approval"],
        "commands": ["/local-shell", "/action-approve", "/action-reject"],
        "source_repos": ["Open Interpreter", "Cline"],
        "v2_pillars": ["Agency", "Safety"]
    },
    {
        "id": "local.open_app",
        "name": "Open Allowed App",
        "owner": "local_control",
        "risk": "diagnostic",
        "approval_policy": "allowlisted_apps_only",
        "inputs": ["app_name"],
        "outputs": ["app_open_result"],
        "side_effects": ["opens_local_application"],
        "allowed_auto_run": False,
        "blocked_conditions": ["emergency_lock", "app_not_allowlisted"],
        "commands": ["/open-app"],
        "source_repos": ["Open Interpreter", "Moltbot AI Assistant"],
        "v2_pillars": ["Agency", "Presence"]
    },
    {
        "id": "local.open_folder",
        "name": "Open Allowed Folder",
        "owner": "local_control",
        "risk": "diagnostic",
        "approval_policy": "allowlisted_folders_only",
        "inputs": ["folder_path"],
        "outputs": ["folder_open_result"],
        "side_effects": ["opens_local_folder"],
        "allowed_auto_run": False,
        "blocked_conditions": ["emergency_lock", "folder_not_allowlisted"],
        "commands": ["/open-folder"],
        "source_repos": ["Open Interpreter", "OpenClaw"],
        "v2_pillars": ["Agency", "Presence"]
    },
    {
        "id": "foundry.evolve",
        "name": "Evolution Proposal Generator",
        "owner": "evolution_foundry",
        "risk": "diagnostic",
        "approval_policy": "not_required_for_proposals",
        "inputs": ["seed_context", "repo_dna", "companion_state"],
        "outputs": ["evolution_proposals"],
        "side_effects": ["writes_foundry_state", "writes_foundry_journal"],
        "allowed_auto_run": False,
        "blocked_conditions": ["foundry_emergency_stop", "autonomy_too_low"],
        "commands": ["/evolve", "/evolution-proposals"],
        "source_repos": ["Aider", "SWE-agent", "OpenHands", "Cline", "LangGraph"],
        "v2_pillars": ["Self-improvement", "Agency", "Growth"]
    },
    {
        "id": "companion.ritual",
        "name": "Companion Ritual",
        "owner": "companion_growth",
        "risk": "diagnostic",
        "approval_policy": "not_required",
        "inputs": ["ritual_id_or_name"],
        "outputs": ["ritual_response"],
        "side_effects": ["may_write_growth_milestone"],
        "allowed_auto_run": False,
        "blocked_conditions": [],
        "commands": ["/ritual-run"],
        "source_repos": ["Hermes Agent", "Moltbot AI Assistant", "OpenClaw"],
        "v2_pillars": ["Growth", "Presence"]
    },
    {
        "id": "companion.pulse",
        "name": "Companion Pulse",
        "owner": "companion_growth",
        "risk": "diagnostic",
        "approval_policy": "not_required",
        "inputs": ["companion_state"],
        "outputs": ["pulse_report"],
        "side_effects": ["may_write_growth_milestone"],
        "allowed_auto_run": False,
        "blocked_conditions": [],
        "commands": ["/companion-pulse"],
        "source_repos": ["Hermes Agent", "Letta", "OpenClaw"],
        "v2_pillars": ["Growth", "Continuity", "Presence"]
    },
    {
        "id": "companion_os.state",
        "name": "Companion OS State",
        "owner": "companion_os",
        "risk": "read_only",
        "approval_policy": "not_required",
        "inputs": [],
        "outputs": ["companion_os_status"],
        "side_effects": [],
        "allowed_auto_run": True,
        "blocked_conditions": [],
        "commands": ["/companion-os"],
        "source_repos": ["all_cloned_repos"],
        "v2_pillars": ["Continuity", "Memory", "Growth", "Presence", "Agency", "World", "Safety"]
    },
    {
        "id": "v2.release_gate",
        "name": "V2 Release Gate",
        "owner": "v2_release_gate",
        "risk": "diagnostic",
        "approval_policy": "not_required",
        "inputs": ["system_state"],
        "outputs": ["v2_score", "v2_blockers", "release_report"],
        "side_effects": ["may_update_v2_score_state"],
        "allowed_auto_run": True,
        "blocked_conditions": [],
        "commands": ["/v2-check"],
        "source_repos": ["Cline", "Aider", "Open WebUI"],
        "v2_pillars": ["Safety", "Self-improvement", "Cockpit"]
    },
    {
        "id": "voice.say",
        "name": "Voice Output",
        "owner": "voice_session",
        "risk": "diagnostic",
        "approval_policy": "user_invoked_voice_only",
        "inputs": ["text"],
        "outputs": ["spoken_audio"],
        "side_effects": ["speaks_through_system_voice"],
        "allowed_auto_run": False,
        "blocked_conditions": ["voice_disabled", "not_user_invoked"],
        "commands": ["/voice-test", "/voice-pulse", "/voice-ritual"],
        "source_repos": ["Moltbot AI Assistant", "LiveKit/Pipecat advice", "Kokoro/Chatterbox advice"],
        "v2_pillars": ["Voice", "Presence"]
    },
    {
        "id": "cockpit.launch",
        "name": "Companion Cockpit",
        "owner": "cockpit",
        "risk": "diagnostic",
        "approval_policy": "user_invoked_only",
        "inputs": [],
        "outputs": ["local_web_ui"],
        "side_effects": ["starts_local_server"],
        "allowed_auto_run": False,
        "blocked_conditions": ["port_unavailable"],
        "commands": ["/cockpit2"],
        "source_repos": ["Open WebUI", "AnythingLLM", "OpenClaw"],
        "v2_pillars": ["Cockpit", "Presence", "World"]
    }
]


def get_tool_manifest():
    return TOOL_MANIFEST_V2


def find_tool(tool_id):
    normalized = tool_id.strip().lower()

    for tool in TOOL_MANIFEST_V2:
        if tool.get("id", "").lower() == normalized:
            return tool

    return None


def tools_by_owner():
    grouped = {}

    for tool in TOOL_MANIFEST_V2:
        grouped.setdefault(tool.get("owner", "unknown"), []).append(tool)

    return grouped


def tools_by_risk():
    grouped = {}

    for tool in TOOL_MANIFEST_V2:
        grouped.setdefault(tool.get("risk", "unknown"), []).append(tool)

    return grouped


def tools_by_pillar():
    grouped = {}

    for tool in TOOL_MANIFEST_V2:
        for pillar in tool.get("v2_pillars", []):
            grouped.setdefault(pillar, []).append(tool)

    return grouped


def validate_tool_manifest():
    required_fields = [
        "id",
        "name",
        "owner",
        "risk",
        "approval_policy",
        "inputs",
        "outputs",
        "side_effects",
        "allowed_auto_run",
        "blocked_conditions",
        "commands",
        "source_repos",
        "v2_pillars"
    ]

    failures = []
    seen_ids = set()

    for tool in TOOL_MANIFEST_V2:
        for field in required_fields:
            if field not in tool:
                failures.append(f"{tool.get('id', 'unknown')} missing {field}")

        tool_id = tool.get("id")

        if tool_id in seen_ids:
            failures.append(f"Duplicate tool id: {tool_id}")

        seen_ids.add(tool_id)

        if tool.get("risk") in ["write", "dangerous"] and tool.get("allowed_auto_run"):
            failures.append(f"{tool_id} is risky but allowed_auto_run=True")

    return failures


def show_tools_v2():
    print("\n=== TOOL MANIFEST V2 ===")
    print(f"Tools: {len(TOOL_MANIFEST_V2)}")

    for tool in TOOL_MANIFEST_V2:
        print(f"\n{tool.get('id')} — {tool.get('name')}")
        print(f"Owner: {tool.get('owner')}")
        print(f"Risk: {tool.get('risk')}")
        print(f"Approval: {tool.get('approval_policy')}")
        print(f"Auto-run: {tool.get('allowed_auto_run')}")
        print(f"Commands: {', '.join(tool.get('commands', []))}")
        print(f"V2 pillars: {', '.join(tool.get('v2_pillars', []))}")


def show_tool_v2(tool_id=None):
    if tool_id is None:
        tool_id = input("Tool ID: ").strip()

    tool = find_tool(tool_id)

    print("\n=== TOOL V2 DETAIL ===")

    if tool is None:
        print("Tool not found.")
        return

    print(json.dumps(tool, indent=4))


def show_tool_permissions():
    print("\n=== TOOL PERMISSIONS ===")

    for tool in TOOL_MANIFEST_V2:
        print(f"\n{tool.get('id')} — {tool.get('name')}")
        print(f"Risk: {tool.get('risk')}")
        print(f"Approval policy: {tool.get('approval_policy')}")
        print(f"Allowed auto-run: {tool.get('allowed_auto_run')}")
        print("Blocked conditions:")
        for condition in tool.get("blocked_conditions", []):
            print(f"- {condition}")


def show_tool_side_effects():
    print("\n=== TOOL SIDE EFFECTS ===")

    for tool in TOOL_MANIFEST_V2:
        print(f"\n{tool.get('id')} — {tool.get('name')}")

        side_effects = tool.get("side_effects", [])

        if not side_effects:
            print("- none")
        else:
            for side_effect in side_effects:
                print(f"- {side_effect}")


def show_tool_audit():
    print("\n=== TOOL MANIFEST AUDIT ===")

    failures = validate_tool_manifest()

    if not failures:
        print("Tool manifest valid.")
    else:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")

    print("\nBy owner:")
    for owner, tools in sorted(tools_by_owner().items()):
        print(f"- {owner}: {len(tools)}")

    print("\nBy risk:")
    for risk, tools in sorted(tools_by_risk().items()):
        print(f"- {risk}: {len(tools)}")

    print("\nBy v2 pillar:")
    for pillar, tools in sorted(tools_by_pillar().items()):
        print(f"- {pillar}: {len(tools)}")


def explain_tool_decision(tool_id, desired_action="use"):
    tool = find_tool(tool_id)

    if tool is None:
        return {
            "allowed": False,
            "decision": "blocked",
            "reason": "Tool not found in manifest.",
            "risk": "unknown"
        }

    risk = tool.get("risk")

    if risk in ["read_only", "diagnostic"] and tool.get("allowed_auto_run"):
        decision = {
            "allowed": True,
            "decision": "allowed",
            "reason": "Tool is read-only/diagnostic and allowed_auto_run=True.",
            "risk": risk
        }
    elif risk in ["read_only", "diagnostic"]:
        decision = {
            "allowed": True,
            "decision": "allowed_when_user_invoked",
            "reason": "Tool is low-risk but should be user-invoked unless a caller has explicit permission.",
            "risk": risk
        }
    else:
        decision = {
            "allowed": False,
            "decision": "approval_required",
            "reason": f"Tool risk is {risk}. Approval policy: {tool.get('approval_policy')}",
            "risk": risk
        }

    if TRACE_AVAILABLE:
        try:
            record_tool_trace(
                command=", ".join(tool.get("commands", [])),
                tool_name=tool.get("name"),
                decision=decision["decision"],
                reason=decision["reason"],
                risk=risk,
                side_effects=tool.get("side_effects", [])
            )
        except Exception:
            pass

    if COMPANION_OS_AVAILABLE:
        try:
            append_companion_os_event(
                "tool_decision_explained",
                f"Tool decision: {tool.get('id')}",
                decision,
                source="tool_manifest_v2",
                importance=3
            )
        except Exception:
            pass

    return decision


def get_tool_manifest_context_for_prompt():
    risks = tools_by_risk()
    owners = tools_by_owner()

    text = "=== TOOL MANIFEST V2 CONTEXT ===\n"
    text += f"Tools: {len(TOOL_MANIFEST_V2)}\n"

    text += "\nRisk groups:\n"
    for risk, tools in sorted(risks.items()):
        text += f"- {risk}: {len(tools)}\n"

    text += "\nOwners:\n"
    for owner, tools in sorted(owners.items()):
        text += f"- {owner}: {len(tools)}\n"

    text += "\nHigh-risk tools:\n"
    for tool in TOOL_MANIFEST_V2:
        if tool.get("risk") in ["write", "dangerous"]:
            text += (
                f"- {tool.get('id')}: {tool.get('name')} "
                f"| approval={tool.get('approval_policy')}\n"
            )

    text += """
Tool manifest rule:
Seed must not invent tools beyond this manifest.
Risky tools require approval.
Side effects must be disclosed.
Allowed auto-run is only acceptable for read-only or diagnostic tools.
"""

    return text


if __name__ == "__main__":
    show_tool_audit()
