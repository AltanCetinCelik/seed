def norm(text):
    return " ".join(str(text or "").strip().lower().split())

def handle_natural_intent_v88(user_message):
    raw = str(user_message or "").strip()
    text = norm(raw)
    if not text or raw.startswith("/"):
        return None

    if any(p in text for p in ["v88 status", "mac body status", "body alive status"]):
        from seed_v88_systems import show_v88_status
        show_v88_status()
        return "handled"

    if any(p in text for p in ["start body alive", "start mac body", "start fast wake", "start seed body"]):
        from seed_body_alive_v88 import start_body_alive
        start_body_alive()
        return "handled"

    if any(p in text for p in ["stop body alive", "stop mac body", "stop fast wake", "stop seed body"]):
        from seed_body_alive_v88 import stop_body_alive
        stop_body_alive()
        return "handled"

    if any(p in text for p in ["fast wake status", "wake fast status"]):
        from seed_wake_fast_v872 import show_status
        show_status()
        return "handled"

    if any(p in text for p in ["warm wake model", "warm model"]):
        from seed_wake_fast_v872 import warm_model
        print(warm_model())
        return "handled"

    try:
        from seed_mac_body_router_v88 import handle_mac_body_intent
        handled = handle_mac_body_intent(raw)
        if handled == "handled":
            return "handled"
    except Exception as e:
        print(f"Mac body router error: {e}")
        return "handled"

    return None
