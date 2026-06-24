import json
import shutil
from datetime import datetime


try:
    from seed_config import SEED_APP_MANIFEST_FILE
except Exception:
    SEED_APP_MANIFEST_FILE = "seed_local_app_manifest.json"


TOOLS = [
    "python", "git", "ffmpeg", "ollama", "aider", "npx", "uvx",
    "pipx", "uv", "node", "npm", "brew"
]


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def build_app_manifest():
    tools = {}

    for tool in TOOLS:
        path = shutil.which(tool)
        tools[tool] = {
            "available": bool(path),
            "path": path
        }

    manifest = {
        "created_at": now_timestamp(),
        "version": "v2.9.0",
        "ok": True,
        "tools": tools,
        "notes": [
            "This is read-only detection.",
            "Seed must not install tools automatically.",
            "Missing tools should produce install plans only."
        ]
    }

    with open(SEED_APP_MANIFEST_FILE, "w") as file:
        json.dump(manifest, file, indent=4)

    return manifest


def app_manifest_context(user_prompt=""):
    manifest = build_app_manifest()
    available = [k for k, v in manifest["tools"].items() if v["available"]]
    missing = [k for k, v in manifest["tools"].items() if not v["available"]]
    return (
        "=== SEED LOCAL APP MANIFEST ===\n"
        f"Available: {', '.join(available)}\n"
        f"Missing: {', '.join(missing)}\n"
        "No auto-installs."
    )


def show_app_manifest():
    manifest = build_app_manifest()

    print("\n=== SEED LOCAL APP MANIFEST ===")
    for tool, data in manifest["tools"].items():
        print(f"- {tool}: available={data['available']} path={data['path']}")


if __name__ == "__main__":
    show_app_manifest()
