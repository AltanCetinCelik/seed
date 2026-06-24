import importlib.util
import json
from datetime import datetime
from urllib.parse import urlparse


try:
    from seed_config import SEED_BROWSER_SANDBOX_FILE
except Exception:
    SEED_BROWSER_SANDBOX_FILE = "seed_browser_sandbox_v10.json"


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def validate_url(url):
    parsed = urlparse(url)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def build_browser_sandbox(url=None, purpose="research"):
    data = {
        "created_at": now_timestamp(),
        "version": "v20.0.0",
        "ok": True,
        "engine": "Seed Browser Sandbox v10",
        "browser_use_installed": importlib.util.find_spec("browser_use") is not None,
        "policy": {
            "no_account_actions_without_approval": True,
            "no_forms_without_approval": True,
            "no_purchases": True,
            "no_hidden_browser": True,
            "read_only_default": True
        },
        "requested_url": url,
        "url_valid": validate_url(url) if url else None,
        "purpose": purpose,
        "next_steps": [
            "validate URL",
            "open read-only browser sandbox later",
            "summarize page",
            "ask approval before any form/account action"
        ]
    }

    with open(SEED_BROWSER_SANDBOX_FILE, "w") as file:
        json.dump(data, file, indent=4)

    return data


def show_browser_sandbox():
    url = input("URL optional: ").strip() or None
    purpose = input("Purpose [research]: ").strip() or "research"
    print(json.dumps(build_browser_sandbox(url, purpose), indent=4))


if __name__ == "__main__":
    show_browser_sandbox()
