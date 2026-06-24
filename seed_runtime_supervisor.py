import json
import platform
import shutil
from datetime import datetime
from pathlib import Path


try:
    from seed_config import SEED_RUNTIME_SUPERVISOR_STATE_FILE
except Exception:
    SEED_RUNTIME_SUPERVISOR_STATE_FILE = "seed_runtime_supervisor_state.json"


WATCH_FILES = [
    "seed_cli.py",
    "seed_brain.py",
    "seed_commands.py",
    "seed_action_kernel.py",
    "seed_skill_kernel.py",
    "seed_mission_control.py",
    "seed_control_plane_server.py",
    "seed_fast_voice_context.py"
]


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def safe_call(fn):
    try:
        return {"ok": True, "data": fn()}
    except Exception as error:
        return {"ok": False, "error": str(error)}


def file_status():
    out = []
    for name in WATCH_FILES:
        path = Path(name)
        out.append({
            "file": name,
            "exists": path.exists(),
            "size": path.stat().st_size if path.exists() else None
        })
    return out


def tool_status():
    tools = ["python", "git", "ffmpeg", "ollama", "aider", "npx", "node", "npm", "brew"]
    return {
        tool: {
            "available": shutil.which(tool) is not None,
            "path": shutil.which(tool)
        }
        for tool in tools
    }


def runtime_supervisor_snapshot():
    snapshot = {
        "created_at": now_timestamp(),
        "version": "v3.0.0",
        "ok": True,
        "system": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "machine": platform.machine()
        },
        "files": file_status(),
        "tools": tool_status(),
        "git": safe_call(lambda: __import__("seed_skill_kernel", fromlist=["run_skill"]).run_skill("git", "status")),
        "mission": safe_call(lambda: __import__("seed_mission_control", fromlist=["mission_control_snapshot"]).mission_control_snapshot()),
        "agents": safe_call(lambda: __import__("seed_agent_run_lifecycle", fromlist=["list_agent_runs"]).list_agent_runs(limit=5)),
        "aider": safe_call(lambda: __import__("seed_aider_bridge", fromlist=["detect_aider"]).detect_aider())
    }

    snapshot["ok"] = all(item["exists"] for item in snapshot["files"] if item["file"] != "seed_control_plane_server.py")

    with open(SEED_RUNTIME_SUPERVISOR_STATE_FILE, "w") as file:
        json.dump(snapshot, file, indent=4)

    return snapshot


def runtime_supervisor_context(user_prompt=""):
    snap = runtime_supervisor_snapshot()
    missing_files = [item["file"] for item in snap["files"] if not item["exists"]]
    available_tools = [tool for tool, data in snap["tools"].items() if data["available"]]

    return (
        "=== SEED RUNTIME SUPERVISOR ===\n"
        f"OK: {snap['ok']}\n"
        f"Available tools: {', '.join(available_tools)}\n"
        f"Missing watched files: {', '.join(missing_files) if missing_files else 'none'}\n"
    )


def show_runtime_supervisor():
    snap = runtime_supervisor_snapshot()

    print("\n=== SEED RUNTIME SUPERVISOR ===")
    print(f"OK: {snap['ok']}")
    print(f"Python: {snap['system']['python']}")
    print("\nWatched files:")
    for item in snap["files"]:
        print(f"- {item['file']}: exists={item['exists']} size={item['size']}")

    print("\nTools:")
    for tool, data in snap["tools"].items():
        print(f"- {tool}: available={data['available']} path={data['path']}")


if __name__ == "__main__":
    show_runtime_supervisor()
