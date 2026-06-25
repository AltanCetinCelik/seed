import json
import shutil
import uuid
from datetime import datetime
from pathlib import Path


SANDBOX_FILE = Path("seed_heavy_agent_sandbox_v37.json")


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


AGENTS = {
    "openhands": ["openhands"],
    "swe-agent": ["swe-agent", "sweagent"],
    "mini-swe-agent": ["mini-swe-agent"],
    "cline": ["cline"],
    "open-interpreter": ["interpreter", "open-interpreter"],
}


def detect_commands():
    out = {}
    for agent, commands in AGENTS.items():
        out[agent] = next((shutil.which(c) for c in commands if shutil.which(c)), None)
    return out


def create_sandbox(agent, task):
    sid = uuid.uuid4().hex[:10]
    run_dir = Path("seed_agent_runs") / f"{agent}_{sid}"
    run_dir.mkdir(parents=True, exist_ok=True)

    spec = {
        "id": sid,
        "created_at": now_timestamp(),
        "version": "v45.0.0",
        "agent": agent,
        "task": task,
        "run_dir": str(run_dir),
        "status": "planned",
        "commands_detected": detect_commands(),
        "rules": {
            "sandbox_only": True,
            "no_core_mutation": True,
            "compare_against_aider": True,
            "manual_promotion": True
        }
    }

    Path(run_dir / "task_spec.json").write_text(json.dumps(spec, indent=4))
    SANDBOX_FILE.write_text(json.dumps(spec, indent=4))
    return spec


def show_heavy_agent_status():
    data = {
        "created_at": now_timestamp(),
        "version": "v45.0.0",
        "ok": True,
        "commands": detect_commands(),
        "agents": AGENTS
    }
    print("\n=== SEED HEAVY AGENT SANDBOX v37 ===")
    print(json.dumps(data, indent=4))


def show_heavy_agent_new():
    agent = input("Agent [openhands/swe-agent/mini-swe-agent/cline/open-interpreter]: ").strip()
    task = input("Task: ").strip()
    print(json.dumps(create_sandbox(agent, task), indent=4))


if __name__ == "__main__":
    show_heavy_agent_status()
