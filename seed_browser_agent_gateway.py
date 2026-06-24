import json
import shutil
import urllib.parse
import webbrowser
from datetime import datetime


try:
    from seed_config import SEED_BROWSER_GATEWAY_STATE_FILE
except Exception:
    SEED_BROWSER_GATEWAY_STATE_FILE = "seed_browser_gateway_state.json"


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def command_exists(command):
    return shutil.which(command) is not None


def browser_gateway_data():
    data = {
        "created_at": now_timestamp(),
        "version": "v2.2.0",
        "browser_use_available": command_exists("browser-use"),
        "playwright_available": command_exists("playwright"),
        "plan_only_by_default": True,
        "ready_for_planning": True,
        "ready_for_execution": False,
        "execution_reason": "Browser agents can touch external websites/accounts. Execution requires approval."
    }

    with open(SEED_BROWSER_GATEWAY_STATE_FILE, "w") as file:
        json.dump(data, file, indent=4)

    return data


def build_browser_plan(task):
    return {
        "created_at": now_timestamp(),
        "task": task,
        "gateway": browser_gateway_data(),
        "approval_required": True,
        "execution_status": "plan_only",
        "safe_order": [
            "Identify exact website/page",
            "Ask approval before browser automation",
            "No login/account/purchase/send actions without explicit approval",
            "Open/read only first",
            "Summarize and cite source if external info is used",
            "Verify result"
        ]
    }


def open_safe_url(url):
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ["http", "https"]:
        return {
            "ok": False,
            "message": "Only http/https URLs are allowed."
        }

    ok = webbrowser.open(url)
    return {
        "ok": bool(ok),
        "url": url
    }


def show_browser_gateway():
    data = browser_gateway_data()
    print("\n=== BROWSER AGENT GATEWAY ===")
    print(f"browser-use available: {data['browser_use_available']}")
    print(f"playwright available: {data['playwright_available']}")
    print(f"Ready for planning: {data['ready_for_planning']}")
    print(f"Ready for execution: {data['ready_for_execution']}")


def show_browser_plan():
    task = input("Browser task: ").strip()
    print(json.dumps(build_browser_plan(task), indent=4))


def get_browser_context(task=""):
    data = browser_gateway_data()
    return (
        "=== BROWSER AGENT GATEWAY CONTEXT ===\n"
        f"browser-use available: {data['browser_use_available']}\n"
        f"Ready for execution: {data['ready_for_execution']}\n"
        "Rule: browser automation requires approval; no account actions without explicit approval.\n"
    )


if __name__ == "__main__":
    show_browser_gateway()
