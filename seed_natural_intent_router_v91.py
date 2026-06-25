import re

def norm(text):
    return " ".join(str(text or "").strip().lower().split())

def handle_natural_intent_v91(user_message):
    raw = str(user_message or "").strip()
    text = norm(raw)
    if not text or raw.startswith("/"):
        return None

    if text in {"v91 status", "context status", "companion context status"}:
        from seed_v91_systems import show_v91_status
        show_v91_status()
        return "handled"

    if text in {"seed context", "show context", "companion context"}:
        from seed_companion_context_v91 import show_context
        show_context()
        return "handled"

    if text in {"bootstrap context", "bootstrap memory", "seed baseline memory"}:
        from seed_companion_context_v91 import ensure_baseline_memory
        print(ensure_baseline_memory())
        return "handled"

    if text in {"start contextual wake", "start v91 wake"}:
        from seed_wake_context_v91 import start_daemon
        print(start_daemon())
        return "handled"

    if text in {"stop contextual wake", "stop v91 wake"}:
        from seed_wake_context_v91 import stop_daemon
        print(stop_daemon())
        return "handled"

    m = re.match(r"context ask\s+(.+)$", raw, flags=re.I)
    if m:
        from seed_contextual_chat_v91 import ask
        print(ask(m.group(1).strip()).get("reply", ""))
        return "handled"

    return None
