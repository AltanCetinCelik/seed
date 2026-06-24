import json
from datetime import datetime
from pathlib import Path


try:
    from seed_config import SEED_INTEGRATION_SANDBOX_STATE_FILE
except Exception:
    SEED_INTEGRATION_SANDBOX_STATE_FILE = "seed_integration_sandbox_state.json"


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def create_sandbox(name, purpose):
    safe_name = "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in name.lower()).strip("-") or "sandbox"
    root = Path("seed_agent_runs") / f"sandbox_{safe_name}"
    root.mkdir(parents=True, exist_ok=True)

    files = {
        "README.md": f"# Seed Integration Sandbox: {name}\n\nPurpose: {purpose}\n\nRules:\n- Prototype only.\n- Do not merge into Seed core directly.\n- Create adapter after proof.\n- Run gates before promotion.\n",
        "SANDBOX_PLAN.json": json.dumps({
            "created_at": now_timestamp(),
            "name": name,
            "purpose": purpose,
            "status": "created",
            "promotion_rules": [
                "No direct repo code dump",
                "Adapter boundary",
                "Tests/gates pass",
                "Approval before core merge"
            ]
        }, indent=4)
    }

    for file_name, content in files.items():
        (root / file_name).write_text(content)

    state = {
        "created_at": now_timestamp(),
        "version": "v3.6.0",
        "ok": True,
        "sandbox_dir": str(root),
        "name": name,
        "purpose": purpose
    }

    with open(SEED_INTEGRATION_SANDBOX_STATE_FILE, "w") as file:
        json.dump(state, file, indent=4)

    return state


def show_sandbox_create():
    name = input("Sandbox name: ").strip()
    purpose = input("Purpose: ").strip()
    print(json.dumps(create_sandbox(name, purpose), indent=4))


def sandbox_context(user_prompt=""):
    return (
        "=== SEED INTEGRATION SANDBOX ===\n"
        "Use sandboxes for high-risk repo integrations before core merge.\n"
        "No auto external execution.\n"
    )


if __name__ == "__main__":
    show_sandbox_create()
