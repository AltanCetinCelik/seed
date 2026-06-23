import json
import os
from datetime import datetime


try:
    from seed_config import SEED_AGENCY_HARDENING_STATE_FILE
except Exception:
    SEED_AGENCY_HARDENING_STATE_FILE = "seed_agency_hardening_state.json"


try:
    from seed_companion_os import (
        load_companion_os_state,
        save_companion_os_state,
        append_companion_os_event,
        append_companion_os_journal
    )
    COMPANION_OS_AVAILABLE = True
except Exception:
    COMPANION_OS_AVAILABLE = False


try:
    from seed_trace_engine import append_trace, record_permission_trace
    TRACE_AVAILABLE = True
except Exception:
    TRACE_AVAILABLE = False


try:
    from seed_tool_manifest_v2 import (
        find_tool,
        explain_tool_decision,
        get_tool_manifest
    )
    TOOL_MANIFEST_AVAILABLE = True
except Exception:
    TOOL_MANIFEST_AVAILABLE = False


try:
    from seed_trust_center import (
        emergency_stop_is_active,
        guardian_decision_for_action,
        guardian_review_text
    )
    TRUST_AVAILABLE = True
except Exception:
    TRUST_AVAILABLE = False


try:
    from seed_v2_hardening_metrics import mark_hardening_signal
    HARDENING_METRICS_AVAILABLE = True
except Exception:
    HARDENING_METRICS_AVAILABLE = False


AUTONOMY_LADDER = [
    {
        "level": 0,
        "name": "Silent",
        "meaning": "Seed only answers. No tools, no proposals, no actions.",
        "allowed": ["answer"],
        "requires_approval": []
    },
    {
        "level": 1,
        "name": "Advisor",
        "meaning": "Seed can suggest actions but cannot queue or execute anything.",
        "allowed": ["answer", "suggest"],
        "requires_approval": ["all_actions"]
    },
    {
        "level": 2,
        "name": "Proposer",
        "meaning": "Seed can prepare approval-queued actions and dry-run simulations.",
        "allowed": ["answer", "suggest", "queue_action", "simulate_action"],
        "requires_approval": ["tool_execution", "file_writes", "memory_writes", "local_actions"]
    },
    {
        "level": 3,
        "name": "Operator",
        "meaning": "Seed can run low-risk approved actions after explicit user approval.",
        "allowed": ["answer", "suggest", "queue_action", "simulate_action", "run_approved_low_risk"],
        "requires_approval": ["write_actions", "dangerous_actions", "local_shell"]
    },
    {
        "level": 4,
        "name": "Maintainer",
        "meaning": "Seed can help maintain itself through approved workflows and tests.",
        "allowed": ["answer", "suggest", "queue_action", "simulate_action", "run_approved_low_risk", "prepare_self_edit"],
        "requires_approval": ["self_edit_apply", "dangerous_actions", "local_shell", "external_tools"]
    },
    {
        "level": 5,
        "name": "Restricted Autopilot",
        "meaning": "Future-only mode. Not enabled. Would require strong safety, logs, rollback, and explicit user scope.",
        "allowed": ["future_only"],
        "requires_approval": ["everything_sensitive"]
    }
]


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def load_json(path, default):
    try:
        with open(path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return default() if callable(default) else default
    except json.JSONDecodeError:
        return default() if callable(default) else default


def save_json(path, data):
    with open(path, "w") as file:
        json.dump(data, file, indent=4)


def default_agency_state():
    return {
        "created_at": now_timestamp(),
        "updated_at": now_timestamp(),
        "version": "v1.18.0",
        "purpose": "Approval-first agency hardening for Seed.",
        "truth": (
            "Seed may propose and simulate actions, but risky actions require explicit approval. "
            "Seed does not gain unsafe autonomy."
        ),
        "current_autonomy_level": 2,
        "current_autonomy_name": "Proposer",
        "max_allowed_autonomy_level": 3,
        "autonomy_ladder": AUTONOMY_LADDER,
        "approval_queue": [],
        "approval_history": [],
        "simulation_history": [],
        "tool_decision_history": [],
        "emergency_bridge": {
            "companion_os_stop_seen": False,
            "trust_center_stop_seen": False,
            "last_checked_at": None
        },
        "rules": [
            "All write actions require explicit approval.",
            "All dangerous local actions require explicit approval.",
            "Seed may dry-run/simulate actions without executing them.",
            "Approval queue is not execution.",
            "Approved status still does not execute by itself.",
            "Emergency stop blocks all approval and execution paths.",
            "Seed must disclose side effects before action."
        ]
    }


def load_agency_state():
    return load_json(SEED_AGENCY_HARDENING_STATE_FILE, default_agency_state)


def save_agency_state(state):
    state["updated_at"] = now_timestamp()
    save_json(SEED_AGENCY_HARDENING_STATE_FILE, state)


def mark_agency_signal(key, value=True):
    if HARDENING_METRICS_AVAILABLE:
        try:
            mark_hardening_signal("agency", key, value)
        except Exception:
            pass


def sync_companion_os_agency():
    if not COMPANION_OS_AVAILABLE:
        return

    agency_state = load_agency_state()
    companion_state = load_companion_os_state()

    companion_state.setdefault("agency", {})
    companion_state["agency"]["autonomy_level"] = agency_state.get("current_autonomy_level", 2)
    companion_state["agency"]["autonomy_name"] = agency_state.get("current_autonomy_name", "Proposer")
    companion_state["agency"]["approval_queue_count"] = len([
        item for item in agency_state.get("approval_queue", [])
        if item.get("status") == "pending"
    ])
    companion_state["agency"]["hardening"] = {
        "approval_queue": True,
        "dry_run_simulator": True,
        "autonomy_ladder": True,
        "tool_decisions": TOOL_MANIFEST_AVAILABLE,
        "emergency_stop_bridge": TRUST_AVAILABLE
    }

    save_companion_os_state(companion_state)


def initialize_agency_hardening():
    state = load_agency_state()
    save_agency_state(state)

    mark_agency_signal("approval_queue", True)
    mark_agency_signal("dry_run_simulator", True)
    mark_agency_signal("autonomy_ladder", True)
    mark_agency_signal("tool_decisions", TOOL_MANIFEST_AVAILABLE)
    mark_agency_signal("emergency_stop_bridge", TRUST_AVAILABLE)

    if TRACE_AVAILABLE:
        try:
            record_permission_trace(
                action="Agency hardening initialized",
                decision="initialized",
                reason="Approval queue, dry-run simulator, autonomy ladder, and emergency bridge are available.",
                risk="low",
                command="seed_agency_hardening.py"
            )
            mark_agency_signal("permission_traces", True)
        except Exception:
            pass

    sync_companion_os_agency()

    if COMPANION_OS_AVAILABLE:
        try:
            append_companion_os_event(
                "agency_hardening_initialized",
                "Agency hardening initialized",
                {
                    "current_autonomy_level": state.get("current_autonomy_level"),
                    "approval_queue": True,
                    "dry_run_simulator": True
                },
                source="agency_hardening",
                importance=4
            )
        except Exception:
            pass

    print("Agency hardening initialized.")
    return state


def next_request_id(queue):
    return f"ACT-{len(queue) + 1:03d}"


def emergency_blocks_action():
    if TRUST_AVAILABLE:
        try:
            return emergency_stop_is_active()
        except Exception:
            return False

    return False


def get_tool_risk(tool_id):
    if not TOOL_MANIFEST_AVAILABLE or not tool_id:
        return {
            "risk": "unknown",
            "approval_policy": "unknown",
            "side_effects": [],
            "tool": None
        }

    tool = find_tool(tool_id)

    if tool is None:
        return {
            "risk": "unknown",
            "approval_policy": "tool_not_found",
            "side_effects": [],
            "tool": None
        }

    return {
        "risk": tool.get("risk"),
        "approval_policy": tool.get("approval_policy"),
        "side_effects": tool.get("side_effects", []),
        "tool": tool
    }


def simulate_action(action_text, tool_id=None, requested_by="Altan"):
    state = load_agency_state()
    tool_info = get_tool_risk(tool_id)

    blocked_by_emergency = emergency_blocks_action()

    if TRUST_AVAILABLE:
        try:
            guardian = guardian_decision_for_action(action_text, tool_id=tool_id)
        except Exception as error:
            guardian = {
                "decision": "unknown",
                "risk": "unknown",
                "reason": str(error),
                "issues": []
            }
    else:
        guardian = {
            "decision": "not_available",
            "risk": tool_info.get("risk"),
            "reason": "Trust Center unavailable.",
            "issues": []
        }

    predicted_side_effects = tool_info.get("side_effects", [])

    approval_required = True

    if tool_info.get("risk") in ["read_only", "diagnostic"] and guardian.get("decision") in ["allowed", "allowed_or_low_risk"]:
        approval_required = False

    if guardian.get("decision") in ["approval_required", "blocked"]:
        approval_required = True

    if blocked_by_emergency:
        approval_required = True

    simulation = {
        "created_at": now_timestamp(),
        "action_text": action_text,
        "tool_id": tool_id,
        "requested_by": requested_by,
        "risk": tool_info.get("risk"),
        "approval_policy": tool_info.get("approval_policy"),
        "approval_required": approval_required,
        "blocked_by_emergency": blocked_by_emergency,
        "guardian_decision": guardian,
        "predicted_side_effects": predicted_side_effects,
        "execution": "not_executed_dry_run_only"
    }

    state.setdefault("simulation_history", []).append(simulation)
    save_agency_state(state)

    mark_agency_signal("dry_run_simulator", True)

    if TRACE_AVAILABLE:
        try:
            record_permission_trace(
                action=f"Dry-run simulation: {action_text[:200]}",
                decision="simulated",
                reason=json.dumps(simulation, indent=2)[:1500],
                risk=tool_info.get("risk", "unknown"),
                command=tool_id
            )
            mark_agency_signal("permission_traces", True)
        except Exception:
            pass

    if COMPANION_OS_AVAILABLE:
        try:
            append_companion_os_event(
                "agency_action_simulated",
                f"Action simulated: {action_text[:80]}",
                simulation,
                source="agency_hardening",
                importance=3
            )
        except Exception:
            pass

    return simulation


def request_action_approval(action_text, tool_id=None, reason="", requested_by="Altan"):
    state = load_agency_state()

    simulation = simulate_action(
        action_text=action_text,
        tool_id=tool_id,
        requested_by=requested_by
    )

    queue = state.setdefault("approval_queue", [])

    request = {
        "id": next_request_id(queue),
        "created_at": now_timestamp(),
        "updated_at": now_timestamp(),
        "status": "pending",
        "action_text": action_text,
        "tool_id": tool_id,
        "reason": reason,
        "requested_by": requested_by,
        "simulation": simulation,
        "approval_required": simulation.get("approval_required"),
        "risk": simulation.get("risk"),
        "approval_policy": simulation.get("approval_policy"),
        "decision_note": None
    }

    queue.append(request)
    save_agency_state(state)

    mark_agency_signal("approval_queue", True)

    if COMPANION_OS_AVAILABLE:
        try:
            append_companion_os_event(
                "agency_approval_requested",
                f"Approval requested: {request['id']}",
                request,
                source="agency_hardening",
                importance=4
            )
        except Exception:
            pass

    return request


def request_action_approval_interactive():
    print("\n=== REQUEST ACTION APPROVAL ===")
    action_text = input("Action text: ").strip()
    tool_id = input("Tool ID, optional: ").strip()
    reason = input("Reason: ").strip()

    if not action_text:
        print("Action text required.")
        return

    request = request_action_approval(
        action_text=action_text,
        tool_id=tool_id or None,
        reason=reason,
        requested_by="interactive"
    )

    print(f"Approval request queued: {request['id']}")


def find_request(request_id):
    state = load_agency_state()

    for item in state.get("approval_queue", []):
        if item.get("id", "").lower() == request_id.lower():
            return item

    return None


def update_request(updated):
    state = load_agency_state()

    for index, item in enumerate(state.get("approval_queue", [])):
        if item.get("id") == updated.get("id"):
            updated["updated_at"] = now_timestamp()
            state["approval_queue"][index] = updated
            state.setdefault("approval_history", []).append(updated)
            save_agency_state(state)
            sync_companion_os_agency()
            return True

    return False


def approve_request(request_id, note="Approved by Altan. Not executed automatically."):
    request = find_request(request_id)

    if request is None:
        return {
            "ok": False,
            "message": "Approval request not found."
        }

    if emergency_blocks_action():
        request["status"] = "blocked_emergency_stop"
        request["decision_note"] = "Emergency stop active; approval blocked."
        update_request(request)
        return {
            "ok": False,
            "message": "Emergency stop is active. Approval blocked."
        }

    request["status"] = "approved_not_executed"
    request["decision_note"] = note
    update_request(request)

    if TRACE_AVAILABLE:
        try:
            record_permission_trace(
                action=request.get("action_text", ""),
                decision="approved_not_executed",
                reason=note,
                risk=request.get("risk", "unknown"),
                command=request.get("tool_id")
            )
        except Exception:
            pass

    if COMPANION_OS_AVAILABLE:
        try:
            append_companion_os_event(
                "agency_request_approved",
                f"Agency request approved: {request_id}",
                request,
                source="agency_hardening",
                importance=4
            )
        except Exception:
            pass

    return {
        "ok": True,
        "message": "Approved, but not executed automatically.",
        "request": request
    }


def reject_request(request_id, note="Rejected by Altan."):
    request = find_request(request_id)

    if request is None:
        return {
            "ok": False,
            "message": "Approval request not found."
        }

    request["status"] = "rejected"
    request["decision_note"] = note
    update_request(request)

    if TRACE_AVAILABLE:
        try:
            record_permission_trace(
                action=request.get("action_text", ""),
                decision="rejected",
                reason=note,
                risk=request.get("risk", "unknown"),
                command=request.get("tool_id")
            )
        except Exception:
            pass

    if COMPANION_OS_AVAILABLE:
        try:
            append_companion_os_event(
                "agency_request_rejected",
                f"Agency request rejected: {request_id}",
                request,
                source="agency_hardening",
                importance=3
            )
        except Exception:
            pass

    return {
        "ok": True,
        "message": "Rejected.",
        "request": request
    }


def approve_request_interactive():
    show_approval_queue()
    request_id = input("\nRequest ID to approve: ").strip()
    note = input("Approval note: ").strip() or "Approved by Altan. Not executed automatically."

    result = approve_request(request_id, note=note)
    print(result["message"])


def reject_request_interactive():
    show_approval_queue()
    request_id = input("\nRequest ID to reject: ").strip()
    note = input("Rejection note: ").strip() or "Rejected by Altan."

    result = reject_request(request_id, note=note)
    print(result["message"])


def show_approval_queue():
    state = load_agency_state()
    queue = state.get("approval_queue", [])

    print("\n=== AGENCY APPROVAL QUEUE ===")

    if not queue:
        print("No approval requests.")
        return

    for item in queue[-20:]:
        print(f"\n{item.get('id')} — {item.get('status')}")
        print(f"Action: {item.get('action_text')}")
        print(f"Tool: {item.get('tool_id')}")
        print(f"Risk: {item.get('risk')}")
        print(f"Approval policy: {item.get('approval_policy')}")
        print(f"Approval required: {item.get('approval_required')}")
        print(f"Reason: {item.get('reason')}")
        print(f"Decision note: {item.get('decision_note')}")


def show_simulation_history():
    state = load_agency_state()
    simulations = state.get("simulation_history", [])

    print("\n=== AGENCY SIMULATION HISTORY ===")

    if not simulations:
        print("No simulations.")
        return

    for item in simulations[-20:]:
        print(f"\n{item.get('created_at')} — {item.get('action_text')}")
        print(f"Tool: {item.get('tool_id')}")
        print(f"Risk: {item.get('risk')}")
        print(f"Approval required: {item.get('approval_required')}")
        print(f"Blocked by emergency: {item.get('blocked_by_emergency')}")
        print(f"Guardian: {item.get('guardian_decision', {}).get('decision')}")


def simulate_action_interactive():
    print("\n=== DRY-RUN ACTION SIMULATOR ===")
    action_text = input("Action text: ").strip()
    tool_id = input("Tool ID, optional: ").strip()

    if not action_text:
        print("Action text required.")
        return

    simulation = simulate_action(
        action_text=action_text,
        tool_id=tool_id or None,
        requested_by="interactive"
    )

    print(json.dumps(simulation, indent=4))


def show_autonomy_ladder():
    state = load_agency_state()

    print("\n=== SEED AUTONOMY LADDER ===")
    print(f"Current level: {state.get('current_autonomy_level')} — {state.get('current_autonomy_name')}")
    print(f"Max allowed level: {state.get('max_allowed_autonomy_level')}")

    for item in state.get("autonomy_ladder", AUTONOMY_LADDER):
        marker = " <==" if item.get("level") == state.get("current_autonomy_level") else ""
        print(f"\nLevel {item.get('level')} — {item.get('name')}{marker}")
        print(item.get("meaning"))
        print(f"Allowed: {', '.join(item.get('allowed', []))}")
        print(f"Requires approval: {', '.join(item.get('requires_approval', []))}")


def set_autonomy_level(level, note=""):
    state = load_agency_state()

    try:
        level = int(level)
    except ValueError:
        return {
            "ok": False,
            "message": "Level must be an integer."
        }

    max_allowed = int(state.get("max_allowed_autonomy_level", 3))

    if level > max_allowed:
        return {
            "ok": False,
            "message": f"Level {level} exceeds max allowed level {max_allowed}."
        }

    chosen = None

    for item in state.get("autonomy_ladder", AUTONOMY_LADDER):
        if int(item.get("level")) == level:
            chosen = item
            break

    if chosen is None:
        return {
            "ok": False,
            "message": "Autonomy level not found."
        }

    state["current_autonomy_level"] = level
    state["current_autonomy_name"] = chosen.get("name")
    state.setdefault("autonomy_history", []).append({
        "created_at": now_timestamp(),
        "level": level,
        "name": chosen.get("name"),
        "note": note
    })

    save_agency_state(state)
    sync_companion_os_agency()

    if COMPANION_OS_AVAILABLE:
        try:
            append_companion_os_event(
                "autonomy_level_changed",
                f"Autonomy level changed: {level} {chosen.get('name')}",
                {
                    "level": level,
                    "name": chosen.get("name"),
                    "note": note
                },
                source="agency_hardening",
                importance=4
            )
        except Exception:
            pass

    return {
        "ok": True,
        "message": f"Autonomy level set to {level} — {chosen.get('name')}",
        "level": chosen
    }


def set_autonomy_level_interactive():
    show_autonomy_ladder()
    level = input("\nNew autonomy level: ").strip()
    note = input("Note: ").strip()

    result = set_autonomy_level(level, note=note)
    print(result["message"])


def check_emergency_bridge():
    state = load_agency_state()

    companion_stop = False
    trust_stop = False

    if COMPANION_OS_AVAILABLE:
        try:
            companion_state = load_companion_os_state()
            companion_stop = bool(companion_state.get("trust", {}).get("emergency_stop"))
        except Exception:
            companion_stop = False

    if TRUST_AVAILABLE:
        try:
            trust_stop = emergency_stop_is_active()
        except Exception:
            trust_stop = False

    state["emergency_bridge"] = {
        "companion_os_stop_seen": companion_stop,
        "trust_center_stop_seen": trust_stop,
        "last_checked_at": now_timestamp()
    }

    save_agency_state(state)
    mark_agency_signal("emergency_stop_bridge", True)

    return state["emergency_bridge"]


def show_emergency_bridge():
    bridge = check_emergency_bridge()

    print("\n=== AGENCY EMERGENCY BRIDGE ===")
    print(f"Companion OS stop seen: {bridge.get('companion_os_stop_seen')}")
    print(f"Trust Center stop seen: {bridge.get('trust_center_stop_seen')}")
    print(f"Last checked: {bridge.get('last_checked_at')}")


def tool_decision_interactive():
    print("\n=== AGENCY TOOL DECISION ===")
    tool_id = input("Tool ID: ").strip()

    if not tool_id:
        print("Tool ID required.")
        return

    if not TOOL_MANIFEST_AVAILABLE:
        print("Tool Manifest v2 unavailable.")
        return

    decision = explain_tool_decision(tool_id)

    state = load_agency_state()
    state.setdefault("tool_decision_history", []).append({
        "created_at": now_timestamp(),
        "tool_id": tool_id,
        "decision": decision
    })
    save_agency_state(state)

    mark_agency_signal("tool_decisions", True)

    print(json.dumps(decision, indent=4))


def agency_hardening_status_data():
    state = load_agency_state()
    pending = [
        item for item in state.get("approval_queue", [])
        if item.get("status") == "pending"
    ]
    approved = [
        item for item in state.get("approval_queue", [])
        if item.get("status") == "approved_not_executed"
    ]
    rejected = [
        item for item in state.get("approval_queue", [])
        if item.get("status") == "rejected"
    ]

    bridge = check_emergency_bridge()

    return {
        "created_at": now_timestamp(),
        "current_autonomy_level": state.get("current_autonomy_level"),
        "current_autonomy_name": state.get("current_autonomy_name"),
        "max_allowed_autonomy_level": state.get("max_allowed_autonomy_level"),
        "approval_queue_count": len(state.get("approval_queue", [])),
        "pending_count": len(pending),
        "approved_count": len(approved),
        "rejected_count": len(rejected),
        "simulation_count": len(state.get("simulation_history", [])),
        "tool_decision_count": len(state.get("tool_decision_history", [])),
        "emergency_bridge": bridge,
        "rules": state.get("rules", [])
    }


def show_agency_hardening_status():
    data = agency_hardening_status_data()

    print("\n=== AGENCY HARDENING STATUS ===")
    print(f"Autonomy: {data['current_autonomy_level']} — {data['current_autonomy_name']}")
    print(f"Max allowed: {data['max_allowed_autonomy_level']}")
    print(f"Approval queue: {data['approval_queue_count']}")
    print(f"Pending: {data['pending_count']}")
    print(f"Approved-not-executed: {data['approved_count']}")
    print(f"Rejected: {data['rejected_count']}")
    print(f"Simulations: {data['simulation_count']}")
    print(f"Tool decisions: {data['tool_decision_count']}")
    print(f"Emergency bridge: {data['emergency_bridge']}")

    print("\nRules:")
    for rule in data["rules"]:
        print(f"- {rule}")


def get_agency_hardening_context_for_prompt():
    data = agency_hardening_status_data()

    text = "=== AGENCY HARDENING CONTEXT ===\n"
    text += f"Autonomy: {data['current_autonomy_level']} — {data['current_autonomy_name']}\n"
    text += f"Approval queue: {data['approval_queue_count']} total, {data['pending_count']} pending\n"
    text += f"Simulations: {data['simulation_count']}\n"
    text += f"Tool decisions: {data['tool_decision_count']}\n"
    text += f"Emergency bridge: {data['emergency_bridge']}\n"

    text += """
Agency rule:
Seed may queue, simulate, explain, and request approval.
Seed does not execute queued actions automatically.
Approved-not-executed means user approved the proposal, not that Seed ran it.
Emergency stop blocks approval/execution paths.
"""

    return text


if __name__ == "__main__":
    initialize_agency_hardening()
    show_agency_hardening_status()
