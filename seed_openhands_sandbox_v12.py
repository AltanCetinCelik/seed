import importlib.util
import json
import shutil
from datetime import datetime
from pathlib import Path


try:
    from seed_config import SEED_OPENHANDS_SANDBOX_FILE
except Exception:
    SEED_OPENHANDS_SANDBOX_FILE = "seed_openhands_sandbox_v12.json"


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def build_openhands_sandbox(task="future coding agent sandbox"):
    sandbox_dir = Path("seed_agent_runs") / "openhands_sandbox_v12"
    sandbox_dir.mkdir(parents=True, exist_ok=True)

    data = {
        "created_at": now_timestamp(),
        "version": "v20.0.0",
        "ok": True,
        "engine": "Seed OpenHands Sandbox v12",
        "task": task,
        "openhands_import_installed": importlib.util.find_spec("openhands") is not None,
        "openhands_command": shutil.which("openhands"),
        "sandbox_dir": str(sandbox_dir),
        "policy": {
            "sandbox_only": True,
            "aider_first_executor": True,
            "no_core_repo_mutation_without_approval": True,
            "no_network_or_account_action_by_default": True
        },
        "promotion_rules": [
            "Aider workflow stable first",
            "OpenHands plan created inside sandbox",
            "Checkpoint before promotion",
            "Human approval required"
        ]
    }

    (sandbox_dir / "README.md").write_text(
        "# OpenHands Sandbox v12\n\n"
        "This sandbox is for future broad coding-agent experiments.\n"
        "Do not merge into Seed core without gate + approval.\n"
    )

    with open(SEED_OPENHANDS_SANDBOX_FILE, "w") as file:
        json.dump(data, file, indent=4)

    return data


def show_openhands_sandbox():
    task = input("OpenHands sandbox task: ").strip() or "future coding agent sandbox"
    print(json.dumps(build_openhands_sandbox(task), indent=4))


if __name__ == "__main__":
    show_openhands_sandbox()
