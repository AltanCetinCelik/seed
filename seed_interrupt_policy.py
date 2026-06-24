import json
from datetime import datetime
from pathlib import Path


POLICY_FILE = Path("seed_presence_policy.json")

DEFAULT_POLICY = {
    "version": "v20.3.0",
    "presence_enabled": True,
    "focus_mode": False,
    "quiet_hours_enabled": True,
    "quiet_start_hour": 1,
    "quiet_end_hour": 8,
    "min_cooldown_minutes": 45,
    "max_messages_per_day": 8,
    "min_priority": 0.65,
    "allow_voice_output": False,
    "allow_desktop_notifications": False,
    "queue_only": True,
    "no_random_chatter": True
}


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def load_policy():
    if not POLICY_FILE.exists():
        save_policy(DEFAULT_POLICY)
        return dict(DEFAULT_POLICY)

    try:
        data = json.loads(POLICY_FILE.read_text())
        merged = dict(DEFAULT_POLICY)
        merged.update(data)
        return merged
    except Exception:
        save_policy(DEFAULT_POLICY)
        return dict(DEFAULT_POLICY)


def save_policy(policy):
    policy["updated_at"] = now_timestamp()
    POLICY_FILE.write_text(json.dumps(policy, indent=4))
    return policy


def set_presence_enabled(enabled):
    policy = load_policy()
    policy["presence_enabled"] = bool(enabled)
    return save_policy(policy)


def set_focus_mode(enabled):
    policy = load_policy()
    policy["focus_mode"] = bool(enabled)
    return save_policy(policy)


def is_quiet_hour(policy, now=None):
    now = now or datetime.now()

    if not policy.get("quiet_hours_enabled", True):
        return False

    start = int(policy.get("quiet_start_hour", 1))
    end = int(policy.get("quiet_end_hour", 8))
    hour = now.hour

    if start < end:
        return start <= hour < end

    return hour >= start or hour < end


def show_interrupt_policy():
    print("\n=== SEED INTERRUPT POLICY ===")
    print(json.dumps(load_policy(), indent=4))


if __name__ == "__main__":
    show_interrupt_policy()
