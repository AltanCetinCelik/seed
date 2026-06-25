import re

def norm(text):
    return " ".join(str(text or "").strip().lower().split())

def handle_mac_body_intent(user_message):
    raw = str(user_message or "").strip()
    text = norm(raw)
    if not text:
        return None

    if text in {"body status", "mac body status", "computer body status", "device body status"}:
        from seed_mac_body_v88 import show_status
        show_status()
        return "handled"

    if text in {"body permissions", "open body permissions", "mac permissions"}:
        from seed_mac_body_v88 import open_permissions
        print(open_permissions("all"))
        return "handled"

    m = re.match(r"open app\s+(.+)$", raw, flags=re.I)
    if m:
        from seed_mac_body_v88 import open_app
        print(open_app(m.group(1).strip()))
        return "handled"

    m = re.match(r"open url\s+(.+)$", raw, flags=re.I)
    if m:
        from seed_mac_body_v88 import open_url
        print(open_url(m.group(1).strip()))
        return "handled"

    if text in {"take screenshot", "screenshot", "look at screen body"}:
        from seed_mac_body_v88 import screenshot
        print(screenshot())
        return "handled"

    m = re.match(r"type text\s+(.+)$", raw, flags=re.I)
    if m:
        from seed_mac_body_v88 import type_text
        print(type_text(m.group(1)))
        return "handled"

    m = re.match(r"press\s+(.+)$", raw, flags=re.I)
    if m:
        from seed_mac_body_v88 import press_key
        print(press_key(m.group(1)))
        return "handled"

    m = re.match(r"click\s+(\d+)\s+(\d+)$", text)
    if m:
        from seed_mac_body_v88 import click_xy
        print(click_xy(m.group(1), m.group(2)))
        return "handled"

    if text == "body trust on":
        from seed_mac_body_v88 import set_mode
        print(set_mode("trusted"))
        return "handled"

    if text == "body trust off":
        from seed_mac_body_v88 import set_mode
        print(set_mode("assist"))
        return "handled"

    if text == "allow shell on":
        from seed_mac_body_v88 import allow_shell
        print(allow_shell(True))
        return "handled"

    if text == "allow shell off":
        from seed_mac_body_v88 import allow_shell
        print(allow_shell(False))
        return "handled"

    m = re.match(r"run shell\s+(.+)$", raw, flags=re.I)
    if m:
        from seed_mac_body_v88 import run_shell
        print(run_shell(m.group(1).strip()))
        return "handled"

    return None
