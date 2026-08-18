import json
from datetime import datetime, timedelta
from pathlib import Path


STATE_FILE = Path("seed_presence_state.json")


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def load_state():
    if not STATE_FILE.exists():
        return {
            "version": "v20.3.0",
            "created_at": now_timestamp(),
            "last_spoke_at": None,
            "messages_today_date": datetime.now().date().isoformat(),
            "messages_today": 0,
            "last_trigger_id": None,
            "ticks": 0
        }

    try:
        return json.loads(STATE_FILE.read_text())
    except Exception:
        return {
            "version": "v20.3.0",
            "created_at": now_timestamp(),
            "last_spoke_at": None,
            "messages_today_date": datetime.now().date().isoformat(),
            "messages_today": 0,
            "last_trigger_id": None,
            "ticks": 0
        }


def save_state(state):
    state["updated_at"] = now_timestamp()
    STATE_FILE.write_text(json.dumps(state, indent=4))
    return state


def reset_daily_if_needed(state):
    today = datetime.now().date().isoformat()
    if state.get("messages_today_date") != today:
        state["messages_today_date"] = today
        state["messages_today"] = 0
    return state


def minutes_since(timestamp):
    if not timestamp:
        return 999999

    try:
        last = datetime.fromisoformat(timestamp)
        return (datetime.now() - last).total_seconds() / 60
    except Exception:
        return 999999


def evaluate_presence_once(force=False):
    from seed_interrupt_policy import load_policy, is_quiet_hour
    from seed_curiosity_engine import collect_curiosity_context, detect_curiosity_triggers

    policy = load_policy()
    state = reset_daily_if_needed(load_state())
    context = collect_curiosity_context()
    triggers = detect_curiosity_triggers(context)

    state["ticks"] = int(state.get("ticks", 0)) + 1

    result = {
        "created_at": now_timestamp(),
        "version": "v20.3.0",
        "ok": True,
        "force": force,
        "should_speak": False,
        "reason": None,
        "message": None,
        "blocked_by": [],
        "trigger_count": len(triggers),
        "selected_trigger": None,
        "policy": policy,
        "state": state
    }

    if not policy.get("presence_enabled", True) and not force:
        result["blocked_by"].append("presence_disabled")

    if policy.get("focus_mode", False) and not force:
        result["blocked_by"].append("focus_mode")

    if is_quiet_hour(policy) and not force:
        result["blocked_by"].append("quiet_hours")

    cooldown = float(policy.get("min_cooldown_minutes", 45))
    if minutes_since(state.get("last_spoke_at")) < cooldown and not force:
        result["blocked_by"].append("cooldown")

    max_daily = int(policy.get("max_messages_per_day", 8))
    if int(state.get("messages_today", 0)) >= max_daily and not force:
        result["blocked_by"].append("daily_limit")

    min_priority = float(policy.get("min_priority", 0.65))
    candidates = [t for t in triggers if float(t.get("priority", 0)) >= min_priority]

    if not candidates:
        result["blocked_by"].append("no_high_priority_trigger")

    if result["blocked_by"]:
        save_state(state)
        return result

    selected = candidates[0]
    result["should_speak"] = True
    result["reason"] = selected.get("category")
    result["message"] = selected.get("message")
    result["selected_trigger"] = selected

    from seed_notification_queue import enqueue_notification
    notification = enqueue_notification(
        message=result["message"],
        reason=result["reason"],
        priority=selected.get("priority", 0.65),
        source="seed_presence"
    )

    state["last_spoke_at"] = now_timestamp()
    state["messages_today"] = int(state.get("messages_today", 0)) + 1
    state["last_trigger_id"] = selected.get("id")
    state["last_notification_id"] = notification.get("id") if notification else None
    result["notification"] = notification
    result["state"] = state

    save_state(state)

    return result


def show_presence_status():
    from seed_interrupt_policy import load_policy
    from seed_notification_queue import read_notifications

    state = load_state()
    policy = load_policy()
    pending = read_notifications(limit=20, status="pending")

    print("\n=== SEED PRESENCE RUNTIME v20.3 ===")
    print(f"Enabled: {policy.get('presence_enabled')}")
    print(f"Focus mode: {policy.get('focus_mode')}")
    print(f"Cooldown minutes: {policy.get('min_cooldown_minutes')}")
    print(f"Messages today: {state.get('messages_today')}/{policy.get('max_messages_per_day')}")
    print(f"Pending notifications: {len(pending)}")
    print(f"Last spoke at: {state.get('last_spoke_at')}")
    print(f"Ticks: {state.get('ticks')}")


def show_presence_tick(force=False):
    result = evaluate_presence_once(force=force)
    print("\n=== SEED PRESENCE TICK ===")
    print(json.dumps({
        "should_speak": result.get("should_speak"),
        "reason": result.get("reason"),
        "message": result.get("message"),
        "blocked_by": result.get("blocked_by"),
        "selected_trigger": result.get("selected_trigger")
    }, indent=4))


if __name__ == "__main__":
    show_presence_tick(force=True)

# v20.3.1 compatibility: compact presence context for Seed prompt.
def get_presence_context_for_prompt(user_prompt=""):
    try:
        from seed_interrupt_policy import load_policy
        from seed_notification_queue import read_notifications
        from seed_curiosity_engine import collect_curiosity_context, detect_curiosity_triggers

        policy = load_policy()
        state = load_state()
        pending = read_notifications(limit=5, status="pending")
        context = collect_curiosity_context()
        triggers = detect_curiosity_triggers(context)

        lines = [
            "=== SEED PRESENCE CONTEXT v20.3 ===",
            f"presence_enabled={policy.get('presence_enabled')}",
            f"focus_mode={policy.get('focus_mode')}",
            f"queue_only={policy.get('queue_only')}",
            f"messages_today={state.get('messages_today')}",
            f"pending_notifications={len(pending)}",
            f"top_trigger={(triggers[0].get('id') if triggers else None)}",
            "Presence rule: Seed may suggest or queue messages, but should not randomly interrupt User."
        ]

        if pending:
            lines.append("Pending presence messages:")
            for item in pending[:3]:
                lines.append(f"- {item.get('reason')}: {item.get('message')}")

        return "\n".join(lines)
    except Exception as error:
        return f"=== SEED PRESENCE CONTEXT ===\nPresence context unavailable: {error}"

# v20.3.2 compatibility: old awareness modules expect this function.
def update_presence_after_action(action_name=None, result=None, metadata=None, *args, **kwargs):
    try:
        state = load_state()
        actions = state.get("recent_actions", [])

        item = {
            "created_at": now_timestamp(),
            "version": "v20.3.2",
            "action_name": action_name or kwargs.get("action") or "unknown_action",
            "result": result,
            "metadata": metadata or kwargs,
        }

        actions.append(item)
        state["recent_actions"] = actions[-25:]
        state["last_action_at"] = item["created_at"]
        state["last_action_name"] = item["action_name"]

        save_state(state)

        try:
            from seed_event_bus import emit_event
            emit_event(
                "presence_action_observed",
                payload={"action_name": item["action_name"]},
                source="seed_presence",
                risk="read_only"
            )
        except Exception:
            pass

        return item
    except Exception as error:
        return {
            "ok": False,
            "error": str(error),
            "action_name": action_name
        }


# Extra aliases for older modules that may call presence in different wording.
def update_presence_after_chat(user_message=None, seed_answer=None, *args, **kwargs):
    return update_presence_after_action(
        action_name="chat",
        result={"user_message": user_message, "seed_answer": seed_answer},
        metadata=kwargs
    )


def record_presence_event(event_type="presence_event", payload=None, *args, **kwargs):
    return update_presence_after_action(
        action_name=event_type,
        result=payload or {},
        metadata=kwargs
    )


def note_presence_event(event_type="presence_event", payload=None, *args, **kwargs):
    return record_presence_event(event_type=event_type, payload=payload, *args, **kwargs)

# v20.3.3 compatibility pack for older local-control / awareness modules.
def load_presence_state():
    return load_state()


def save_presence_state(state=None):
    if state is None:
        state = load_state()
    return save_state(state)


def get_presence_state():
    return load_state()


def set_presence_state(key=None, value=None, **kwargs):
    state = load_state()

    if key is not None:
        state[key] = value

    for k, v in kwargs.items():
        state[k] = v

    return save_state(state)


def update_presence_state(**kwargs):
    state = load_state()
    state.update(kwargs)
    return save_state(state)


def get_presence_summary():
    try:
        from seed_interrupt_policy import load_policy
        from seed_notification_queue import read_notifications

        state = load_state()
        policy = load_policy()
        pending = read_notifications(limit=20, status="pending")

        return {
            "ok": True,
            "version": "v20.3.3",
            "presence_enabled": policy.get("presence_enabled"),
            "focus_mode": policy.get("focus_mode"),
            "messages_today": state.get("messages_today"),
            "pending_notifications": len(pending),
            "last_spoke_at": state.get("last_spoke_at"),
            "ticks": state.get("ticks"),
        }
    except Exception as error:
        return {
            "ok": False,
            "error": str(error)
        }


def presence_status_data():
    return get_presence_summary()


def set_presence_mode(mode="ready"):
    state = load_state()
    state["mode"] = mode
    state["last_mode_update_at"] = now_timestamp()
    return save_state(state)


def set_presence_focus(enabled=True):
    try:
        from seed_interrupt_policy import set_focus_mode
        return set_focus_mode(bool(enabled))
    except Exception:
        state = load_state()
        state["focus_mode"] = bool(enabled)
        return save_state(state)


def note_local_control_action(action_name=None, result=None, metadata=None, *args, **kwargs):
    return update_presence_after_action(
        action_name=action_name or "local_control_action",
        result=result,
        metadata=metadata or kwargs
    )


def get_local_presence_context_for_prompt(user_prompt=""):
    return get_presence_context_for_prompt(user_prompt)


def __getattr__(name):
    """
    Last-resort compatibility fallback for older Seed modules.
    """
    if name.startswith("load") and "presence" in name:
        return load_presence_state

    if name.startswith("save") and "presence" in name:
        return save_presence_state

    if name.startswith("get") and "presence" in name and "context" in name:
        return get_presence_context_for_prompt

    if name.startswith("get") and "presence" in name:
        return get_presence_state

    if name.startswith("update") and "presence" in name:
        return update_presence_after_action

    if name.startswith("set") and "presence" in name:
        return set_presence_state

    if "local_control" in name:
        return note_local_control_action

    raise AttributeError(f"module 'seed_presence' has no attribute '{name}'")

# v20.3.4 explicit legacy display aliases.
def show_presence_state():
    print("\n=== SEED PRESENCE STATE ===")
    import json
    print(json.dumps(load_state(), indent=4))
    return load_state()


def show_presence_policy():
    try:
        from seed_interrupt_policy import show_interrupt_policy
        return show_interrupt_policy()
    except Exception:
        print("\nPresence policy unavailable.")
        return None


def show_presence_context(user_prompt=""):
    print(get_presence_context_for_prompt(user_prompt))
    return get_presence_context_for_prompt(user_prompt)


def show_presence_summary():
    import json
    data = get_presence_summary()
    print("\n=== SEED PRESENCE SUMMARY ===")
    print(json.dumps(data, indent=4))
    return data


def show_presence_notifications():
    try:
        from seed_notification_queue import show_notification_inbox
        return show_notification_inbox()
    except Exception:
        print("Presence notification queue unavailable.")
        return None


def update_presence_after_message(user_message=None, seed_answer=None, *args, **kwargs):
    return update_presence_after_chat(
        user_message=user_message,
        seed_answer=seed_answer,
        *args,
        **kwargs
    )


def update_presence_after_response(user_message=None, seed_answer=None, *args, **kwargs):
    return update_presence_after_chat(
        user_message=user_message,
        seed_answer=seed_answer,
        *args,
        **kwargs
    )


def enable_presence():
    try:
        from seed_interrupt_policy import set_presence_enabled
        return set_presence_enabled(True)
    except Exception:
        return set_presence_state("presence_enabled", True)


def disable_presence():
    try:
        from seed_interrupt_policy import set_presence_enabled
        return set_presence_enabled(False)
    except Exception:
        return set_presence_state("presence_enabled", False)


def focus_on():
    return set_presence_focus(True)


def focus_off():
    return set_presence_focus(False)


# v20.3.5 auto-generated legacy compatibility wrappers.
# These keep old Seed modules working after the Presence Runtime rewrite.
def _seed_presence_legacy_dispatch(name, *args, **kwargs):
    try:
        state = load_state()

        # Emergency / lock compatibility.
        if "emergency" in name or "lock" in name:
            if name.startswith(("set", "enable", "activate")):
                state["emergency_lock"] = True
                state["emergency_lock_reason"] = (
                    args[0] if args else kwargs.get("reason", "legacy_presence_call")
                )
                state["emergency_lock_at"] = now_timestamp()
                return save_state(state)

            if name.startswith(("clear", "disable", "release", "unlock")):
                state["emergency_lock"] = False
                state["emergency_lock_cleared_at"] = now_timestamp()
                return save_state(state)

            if name.startswith(("is", "has")):
                return bool(state.get("emergency_lock", False))

            if name.startswith("show"):
                import json
                print("\n=== SEED PRESENCE EMERGENCY LOCK ===")
                print(json.dumps({
                    "emergency_lock": state.get("emergency_lock", False),
                    "reason": state.get("emergency_lock_reason"),
                    "at": state.get("emergency_lock_at")
                }, indent=4))
                return state

        # Context compatibility.
        if "context" in name:
            user_prompt = args[0] if args else kwargs.get("user_prompt", "")
            return get_presence_context_for_prompt(user_prompt)

        # Display compatibility.
        if name.startswith("show"):
            import json
            data = get_presence_summary()
            print(f"\n=== {name} ===")
            print(json.dumps(data, indent=4))
            return data

        # Load/save state compatibility.
        if name.startswith("load") or name.startswith("get"):
            return load_state()

        if name.startswith("save"):
            return save_state(args[0] if args else state)

        # Set/update compatibility.
        if name.startswith("set"):
            key = name.replace("set_", "")
            state[key] = args[0] if args else kwargs.get("value", True)
            return save_state(state)

        if name.startswith(("update", "record", "note")):
            return update_presence_after_action(
                action_name=name,
                result=args[0] if args else kwargs.get("result"),
                metadata=kwargs
            )

        return get_presence_summary()
    except Exception as error:
        return {
            "ok": False,
            "compat_name": name,
            "error": str(error)
        }



def format_presence_state(*args, **kwargs):
    return _seed_presence_legacy_dispatch("format_presence_state", *args, **kwargs)

def get_presence_hud_lines(*args, **kwargs):
    return _seed_presence_legacy_dispatch("get_presence_hud_lines", *args, **kwargs)

def set_emergency_lock(*args, **kwargs):
    return _seed_presence_legacy_dispatch("set_emergency_lock", *args, **kwargs)

def set_presence_mode_interactive(*args, **kwargs):
    return _seed_presence_legacy_dispatch("set_presence_mode_interactive", *args, **kwargs)


# v20.3.5 broader fallback for future old imports.
def __getattr__(name):
    if (
        "presence" in name
        or "emergency" in name
        or "lock" in name
        or "local_control" in name
        or name.startswith(("show_", "load_", "save_", "get_", "set_", "update_", "record_", "note_", "clear_", "enable_", "disable_", "is_"))
    ):
        def _compat(*args, **kwargs):
            return _seed_presence_legacy_dispatch(name, *args, **kwargs)
        return _compat

    raise AttributeError(f"module 'seed_presence' has no attribute '{name}'")
