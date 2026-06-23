import json
from datetime import datetime


try:
    from seed_config import SEED_COCKPIT_HARDENING_STATE_FILE
except Exception:
    SEED_COCKPIT_HARDENING_STATE_FILE = "seed_cockpit_hardening_state.json"


try:
    from seed_companion_os import (
        append_companion_os_event,
        append_companion_os_journal,
        load_companion_os_state,
        save_companion_os_state
    )
    COMPANION_OS_AVAILABLE = True
except Exception:
    COMPANION_OS_AVAILABLE = False


try:
    from seed_trace_engine import append_trace
    TRACE_AVAILABLE = True
except Exception:
    TRACE_AVAILABLE = False


try:
    from seed_v2_hardening_metrics import mark_hardening_signal
    HARDENING_AVAILABLE = True
except Exception:
    HARDENING_AVAILABLE = False


try:
    from seed_voice_hardening import (
        run_voice_privacy_check,
        dry_run_voice_pulse,
        voice_hardening_status_data
    )
    VOICE_HARDENING_AVAILABLE = True
except Exception:
    VOICE_HARDENING_AVAILABLE = False


try:
    from seed_agency_hardening import (
        simulate_action,
        request_action_approval,
        agency_hardening_status_data
    )
    AGENCY_HARDENING_AVAILABLE = True
except Exception:
    AGENCY_HARDENING_AVAILABLE = False


try:
    from seed_self_improvement_hardening import (
        build_module_health_matrix,
        build_test_matrix,
        build_release_readiness_report,
        get_self_improvement_hardening_context_for_prompt
    )
    SELF_HARDENING_AVAILABLE = True
except Exception:
    SELF_HARDENING_AVAILABLE = False


try:
    from seed_world_engine import apply_world_event, show_world
    WORLD_AVAILABLE = True
except Exception:
    WORLD_AVAILABLE = False


try:
    from seed_avatar_state import avatar_for_mode, get_avatar_state
    AVATAR_AVAILABLE = True
except Exception:
    AVATAR_AVAILABLE = False


try:
    from seed_v2_release_gate import run_v2_release_gate
    V2_GATE_AVAILABLE = True
except Exception:
    V2_GATE_AVAILABLE = False


try:
    from seed_release_manager import run_release_check
    RELEASE_AVAILABLE = True
except Exception:
    RELEASE_AVAILABLE = False


COCKPIT_ACTIONS = [
    {
        "id": "voice_privacy_check",
        "label": "Run voice privacy check",
        "risk": "diagnostic",
        "payload_fields": []
    },
    {
        "id": "voice_pulse_dry",
        "label": "Dry-run voice pulse",
        "risk": "diagnostic",
        "payload_fields": []
    },
    {
        "id": "agency_simulate",
        "label": "Simulate action",
        "risk": "diagnostic",
        "payload_fields": ["action_text", "tool_id"]
    },
    {
        "id": "agency_request",
        "label": "Queue approval request",
        "risk": "write_local_state",
        "payload_fields": ["action_text", "tool_id", "reason"]
    },
    {
        "id": "module_health",
        "label": "Build module health matrix",
        "risk": "diagnostic",
        "payload_fields": []
    },
    {
        "id": "test_matrix",
        "label": "Run test matrix",
        "risk": "diagnostic",
        "payload_fields": []
    },
    {
        "id": "release_readiness",
        "label": "Build release readiness report",
        "risk": "diagnostic",
        "payload_fields": []
    },
    {
        "id": "v2_check",
        "label": "Run V2 release gate",
        "risk": "diagnostic",
        "payload_fields": []
    },
    {
        "id": "release_check",
        "label": "Run release check",
        "risk": "diagnostic",
        "payload_fields": []
    },
    {
        "id": "world_event",
        "label": "Apply symbolic world event",
        "risk": "symbolic_write",
        "payload_fields": ["event_type", "title", "note", "importance"]
    },
    {
        "id": "avatar_mode",
        "label": "Set avatar mode",
        "risk": "symbolic_write",
        "payload_fields": ["mode"]
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


def default_cockpit_state():
    return {
        "created_at": now_timestamp(),
        "updated_at": now_timestamp(),
        "version": "v1.18.0",
        "purpose": "Interactive local cockpit hardening for Seed Companion OS.",
        "truth": (
            "Cockpit is a local UI/API layer. It can trigger safe diagnostic and "
            "approval-queued actions. It must not bypass Trust Center or approval gates."
        ),
        "api_routes": [],
        "actions": COCKPIT_ACTIONS,
        "action_log": [],
        "self_tests": [],
        "interactive_ready": False,
        "last_action_at": None,
        "last_self_test_at": None,
        "rules": [
            "Cockpit may call diagnostic actions.",
            "Cockpit may queue approval requests.",
            "Cockpit must not execute risky actions directly.",
            "Cockpit does not bypass emergency stop.",
            "Cockpit actions must be logged.",
            "Cockpit chat is advisory unless connected to approval queue."
        ]
    }


def load_cockpit_state():
    return load_json(SEED_COCKPIT_HARDENING_STATE_FILE, default_cockpit_state)


def save_cockpit_state(state):
    state["updated_at"] = now_timestamp()
    save_json(SEED_COCKPIT_HARDENING_STATE_FILE, state)


def mark_cockpit_signal(key, value=True):
    if HARDENING_AVAILABLE:
        try:
            mark_hardening_signal("cockpit", key, value)
        except Exception:
            pass


def mark_presence_signal(key, value=True):
    if HARDENING_AVAILABLE:
        try:
            mark_hardening_signal("presence", key, value)
        except Exception:
            pass


def mark_cockpit_api_signals():
    mark_cockpit_signal("api_state", True)
    mark_cockpit_signal("api_chat", True)
    mark_cockpit_signal("api_commands", True)
    mark_cockpit_signal("api_tools", True)
    mark_cockpit_signal("api_workflows", True)
    mark_cockpit_signal("api_voice", VOICE_HARDENING_AVAILABLE)
    mark_cockpit_signal("api_agency", AGENCY_HARDENING_AVAILABLE)
    mark_cockpit_signal("api_hardening", True)
    mark_presence_signal("cockpit_integrated", True)


def sync_companion_os_cockpit():
    if not COMPANION_OS_AVAILABLE:
        return

    cockpit = load_cockpit_state()
    state = load_companion_os_state()

    state.setdefault("presence", {})
    state["presence"]["cockpit"] = {
        "status": "interactive_alpha",
        "interactive_ready": cockpit.get("interactive_ready"),
        "actions": len(cockpit.get("actions", [])),
        "action_log_count": len(cockpit.get("action_log", [])),
        "last_action_at": cockpit.get("last_action_at"),
        "rules": cockpit.get("rules", [])
    }

    save_companion_os_state(state)


def log_cockpit_action(action_id, payload, result, risk="diagnostic"):
    state = load_cockpit_state()

    record = {
        "created_at": now_timestamp(),
        "action_id": action_id,
        "risk": risk,
        "payload": payload,
        "result": result
    }

    state.setdefault("action_log", []).append(record)
    state["last_action_at"] = record["created_at"]
    state["interactive_ready"] = True
    save_cockpit_state(state)

    mark_cockpit_signal("interactive_actions", True)
    sync_companion_os_cockpit()

    if COMPANION_OS_AVAILABLE:
        try:
            append_companion_os_event(
                "cockpit_action_run",
                f"Cockpit action run: {action_id}",
                {
                    "action_id": action_id,
                    "risk": risk,
                    "ok": result.get("ok") if isinstance(result, dict) else None
                },
                source="cockpit_actions",
                importance=3
            )
        except Exception:
            pass

    if TRACE_AVAILABLE:
        try:
            append_trace(
                trace_type="tool_trace",
                title=f"Cockpit action: {action_id}",
                summary=json.dumps({
                    "payload": payload,
                    "result": result
                }, indent=2)[:2000],
                sources=["cockpit_actions", "companion_cockpit"],
                decision="executed_diagnostic_or_queued",
                risk=risk
            )
        except Exception:
            pass

    return record


def action_definitions():
    return COCKPIT_ACTIONS


def execute_cockpit_action(action_id, payload=None):
    if payload is None:
        payload = {}

    action = next((item for item in COCKPIT_ACTIONS if item["id"] == action_id), None)

    if action is None:
        result = {
            "ok": False,
            "error": f"Unknown cockpit action: {action_id}"
        }
        log_cockpit_action(action_id, payload, result, risk="unknown")
        return result

    risk = action.get("risk", "diagnostic")

    try:
        if action_id == "voice_privacy_check":
            if not VOICE_HARDENING_AVAILABLE:
                result = {"ok": False, "error": "Voice hardening unavailable."}
            else:
                check = run_voice_privacy_check()
                result = {"ok": check.get("ok"), "data": check}

        elif action_id == "voice_pulse_dry":
            if not VOICE_HARDENING_AVAILABLE:
                result = {"ok": False, "error": "Voice hardening unavailable."}
            else:
                check = dry_run_voice_pulse(use_llm=False)
                result = {"ok": check.get("ok"), "data": check}

        elif action_id == "agency_simulate":
            if not AGENCY_HARDENING_AVAILABLE:
                result = {"ok": False, "error": "Agency hardening unavailable."}
            else:
                action_text = payload.get("action_text", "").strip()
                tool_id = payload.get("tool_id") or None

                if not action_text:
                    result = {"ok": False, "error": "action_text required."}
                else:
                    simulation = simulate_action(
                        action_text=action_text,
                        tool_id=tool_id,
                        requested_by="cockpit"
                    )
                    result = {"ok": True, "data": simulation}

        elif action_id == "agency_request":
            if not AGENCY_HARDENING_AVAILABLE:
                result = {"ok": False, "error": "Agency hardening unavailable."}
            else:
                action_text = payload.get("action_text", "").strip()
                tool_id = payload.get("tool_id") or None
                reason = payload.get("reason", "Cockpit approval request.")

                if not action_text:
                    result = {"ok": False, "error": "action_text required."}
                else:
                    request = request_action_approval(
                        action_text=action_text,
                        tool_id=tool_id,
                        reason=reason,
                        requested_by="cockpit"
                    )
                    result = {
                        "ok": True,
                        "message": "Approval request queued. Not executed.",
                        "data": request
                    }

        elif action_id == "module_health":
            if not SELF_HARDENING_AVAILABLE:
                result = {"ok": False, "error": "Self-improvement hardening unavailable."}
            else:
                report = build_module_health_matrix()
                result = {"ok": report.get("failed") == 0 and report.get("missing") == 0, "data": report}

        elif action_id == "test_matrix":
            if not SELF_HARDENING_AVAILABLE:
                result = {"ok": False, "error": "Self-improvement hardening unavailable."}
            else:
                report = build_test_matrix()
                result = {"ok": report.get("failed") == 0, "data": report}

        elif action_id == "release_readiness":
            if not SELF_HARDENING_AVAILABLE:
                result = {"ok": False, "error": "Self-improvement hardening unavailable."}
            else:
                report = build_release_readiness_report()
                result = {"ok": report.get("release_ready"), "data": report}

        elif action_id == "v2_check":
            if not V2_GATE_AVAILABLE:
                result = {"ok": False, "error": "V2 gate unavailable."}
            else:
                report = run_v2_release_gate()
                result = {"ok": report.get("is_v2_ready"), "data": report}

        elif action_id == "release_check":
            if not RELEASE_AVAILABLE:
                result = {"ok": False, "error": "Release manager unavailable."}
            else:
                report = run_release_check()
                result = {"ok": report.get("ok"), "data": report}

        elif action_id == "world_event":
            if not WORLD_AVAILABLE:
                result = {"ok": False, "error": "World engine unavailable."}
            else:
                importance = payload.get("importance", 3)
                try:
                    importance = int(importance)
                except Exception:
                    importance = 3

                event = apply_world_event(
                    event_type=payload.get("event_type", "companion"),
                    title=payload.get("title") or "Cockpit world event",
                    note=payload.get("note", ""),
                    importance=importance
                )
                result = {"ok": True, "data": event}

        elif action_id == "avatar_mode":
            if not AVATAR_AVAILABLE:
                result = {"ok": False, "error": "Avatar state unavailable."}
            else:
                mode = payload.get("mode", "focused")
                avatar = avatar_for_mode(mode)
                result = {"ok": avatar.get("ok", False), "data": avatar}

        else:
            result = {"ok": False, "error": f"Unhandled cockpit action: {action_id}"}

    except Exception as error:
        result = {
            "ok": False,
            "error": str(error)
        }

    log_cockpit_action(action_id, payload, result, risk=risk)
    return result


def cockpit_hardening_status_data():
    state = load_cockpit_state()

    voice_status = {}
    agency_status = {}

    if VOICE_HARDENING_AVAILABLE:
        try:
            voice_status = voice_hardening_status_data()
        except Exception as error:
            voice_status = {"error": str(error)}

    if AGENCY_HARDENING_AVAILABLE:
        try:
            agency_status = agency_hardening_status_data()
        except Exception as error:
            agency_status = {"error": str(error)}

    return {
        "created_at": now_timestamp(),
        "interactive_ready": state.get("interactive_ready"),
        "action_count": len(state.get("actions", [])),
        "action_log_count": len(state.get("action_log", [])),
        "last_action_at": state.get("last_action_at"),
        "api_routes": state.get("api_routes", []),
        "rules": state.get("rules", []),
        "voice_status": voice_status,
        "agency_status": agency_status,
        "available": {
            "voice_hardening": VOICE_HARDENING_AVAILABLE,
            "agency_hardening": AGENCY_HARDENING_AVAILABLE,
            "self_hardening": SELF_HARDENING_AVAILABLE,
            "world": WORLD_AVAILABLE,
            "avatar": AVATAR_AVAILABLE,
            "v2_gate": V2_GATE_AVAILABLE,
            "release": RELEASE_AVAILABLE
        }
    }


def run_cockpit_self_test():
    mark_cockpit_api_signals()

    state = load_cockpit_state()

    routes = [
        "/api/state",
        "/api/chat",
        "/api/commands",
        "/api/tools",
        "/api/workflows",
        "/api/cockpit/actions",
        "/api/cockpit/action",
        "/api/cockpit/hardening",
        "/api/voice/hardening",
        "/api/agency/hardening"
    ]

    state["api_routes"] = routes
    state["interactive_ready"] = True
    state["last_self_test_at"] = now_timestamp()

    check = {
        "created_at": now_timestamp(),
        "ok": True,
        "routes": routes,
        "actions": len(COCKPIT_ACTIONS),
        "available": cockpit_hardening_status_data().get("available")
    }

    state.setdefault("self_tests", []).append(check)
    save_cockpit_state(state)
    sync_companion_os_cockpit()

    if COMPANION_OS_AVAILABLE:
        try:
            append_companion_os_event(
                "cockpit_self_test_run",
                "Cockpit hardening self-test run",
                check,
                source="cockpit_actions",
                importance=4
            )
        except Exception:
            pass

    return check



def show_cockpit_self_test():
    check = run_cockpit_self_test()

    print("\n=== COCKPIT HARDENING SELF-TEST ===")
    print(f"OK: {check.get('ok')}")
    print(f"Actions: {check.get('actions')}")

    print("\nRoutes:")
    for route in check.get("routes", []):
        print(f"- {route}")

    print("\nAvailable:")
    available = check.get("available") or {}
    for key, value in available.items():
        print(f"- {key}: {value}")

    return check

def show_cockpit_hardening_status():
    data = cockpit_hardening_status_data()

    print("\n=== COCKPIT HARDENING STATUS ===")
    print(f"Interactive ready: {data.get('interactive_ready')}")
    print(f"Actions: {data.get('action_count')}")
    print(f"Action log: {data.get('action_log_count')}")
    print(f"Last action: {data.get('last_action_at')}")

    print("\nAvailable:")
    for key, value in data.get("available", {}).items():
        print(f"- {key}: {value}")

    print("\nRules:")
    for rule in data.get("rules", []):
        print(f"- {rule}")


def show_cockpit_actions():
    print("\n=== COCKPIT ACTIONS ===")
    for action in COCKPIT_ACTIONS:
        print(f"\n{action.get('id')} — {action.get('label')}")
        print(f"Risk: {action.get('risk')}")
        print(f"Payload: {', '.join(action.get('payload_fields', []))}")


def show_cockpit_action_log():
    state = load_cockpit_state()
    logs = state.get("action_log", [])

    print("\n=== COCKPIT ACTION LOG ===")

    if not logs:
        print("No cockpit actions logged.")
        return

    for item in logs[-20:]:
        print(f"\n{item.get('created_at')} — {item.get('action_id')}")
        print(f"Risk: {item.get('risk')}")
        result = item.get("result")
        if isinstance(result, dict):
            print(f"OK: {result.get('ok')}")
            if result.get("error"):
                print(f"Error: {result.get('error')}")
        else:
            print(result)


def execute_cockpit_action_interactive():
    show_cockpit_actions()
    action_id = input("\nAction ID: ").strip()

    payload = {}

    if action_id == "agency_simulate":
        payload["action_text"] = input("Action text: ").strip()
        payload["tool_id"] = input("Tool ID, optional: ").strip() or None

    elif action_id == "agency_request":
        payload["action_text"] = input("Action text: ").strip()
        payload["tool_id"] = input("Tool ID, optional: ").strip() or None
        payload["reason"] = input("Reason: ").strip()

    elif action_id == "world_event":
        payload["event_type"] = input("Event type: ").strip() or "companion"
        payload["title"] = input("Title: ").strip() or "Cockpit world event"
        payload["note"] = input("Note: ").strip()
        payload["importance"] = input("Importance 1-5: ").strip() or "3"

    elif action_id == "avatar_mode":
        payload["mode"] = input("Avatar mode: ").strip() or "focused"

    result = execute_cockpit_action(action_id, payload)
    print(json.dumps(result, indent=4))


def get_cockpit_hardening_context_for_prompt():
    data = cockpit_hardening_status_data()

    text = "=== COCKPIT HARDENING CONTEXT ===\n"
    text += f"Interactive ready: {data.get('interactive_ready')}\n"
    text += f"Actions: {data.get('action_count')}\n"
    text += f"Action log: {data.get('action_log_count')}\n"
    text += f"Last action: {data.get('last_action_at')}\n"
    text += f"Available: {json.dumps(data.get('available'))}\n"

    text += """
Cockpit hardening rule:
Cockpit can run diagnostics, dry-runs, symbolic state updates, and approval-queue requests.
Cockpit must not execute risky actions directly.
Cockpit actions must be logged.
"""

    return text


def attach_cockpit_action_routes(app):
    try:
        from fastapi.responses import JSONResponse
    except Exception:
        return app

    @app.get("/api/cockpit/actions")
    def api_cockpit_actions():
        mark_cockpit_api_signals()
        return JSONResponse({
            "actions": action_definitions(),
            "status": cockpit_hardening_status_data()
        })

    @app.post("/api/cockpit/action")
    async def api_cockpit_action(payload: dict):
        mark_cockpit_api_signals()
        action_id = payload.get("action_id")
        action_payload = payload.get("payload", {})
        result = execute_cockpit_action(action_id, action_payload)
        return JSONResponse(result)

    @app.get("/api/cockpit/hardening")
    def api_cockpit_hardening():
        mark_cockpit_api_signals()
        return JSONResponse(cockpit_hardening_status_data())

    @app.get("/api/voice/hardening")
    def api_voice_hardening():
        mark_cockpit_signal("api_voice", True)
        if VOICE_HARDENING_AVAILABLE:
            return JSONResponse(voice_hardening_status_data())
        return JSONResponse({"error": "voice hardening unavailable"})

    @app.get("/api/agency/hardening")
    def api_agency_hardening():
        mark_cockpit_signal("api_agency", True)
        if AGENCY_HARDENING_AVAILABLE:
            return JSONResponse(agency_hardening_status_data())
        return JSONResponse({"error": "agency hardening unavailable"})

    return app


if __name__ == "__main__":
    run_cockpit_self_test()
    show_cockpit_hardening_status()
    show_cockpit_actions()
