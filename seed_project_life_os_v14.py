import json
from datetime import datetime
from pathlib import Path


try:
    from seed_config import SEED_PROJECT_LIFE_OS_FILE
except Exception:
    SEED_PROJECT_LIFE_OS_FILE = "seed_project_life_os_v14.json"


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def default_state():
    return {
        "created_at": now_timestamp(),
        "version": "v20.0.0",
        "ok": True,
        "engine": "Seed Project + Life OS v13/v14",
        "projects": [
            {
                "id": "seed",
                "name": "Seed Companion OS",
                "status": "active",
                "next_major": "v20 Sovereign Companion OS stabilization"
            }
        ],
        "life_tracks": [
            {"id": "learning", "name": "Learning / coding growth", "status": "active"},
            {"id": "money", "name": "Money / USD earning plans", "status": "planned"},
            {"id": "health", "name": "Health / routines", "status": "manual only"},
            {"id": "social", "name": "Social confidence", "status": "supportive"}
        ],
        "rules": {
            "do_not_overreach": True,
            "no_medical_or_financial_autonomy": True,
            "ask_before_sensitive_memory": True
        }
    }


def load_state():
    path = Path(SEED_PROJECT_LIFE_OS_FILE)
    if not path.exists():
        return default_state()
    try:
        return json.loads(path.read_text())
    except Exception:
        return default_state()


def save_state(data):
    data["updated_at"] = now_timestamp()
    with open(SEED_PROJECT_LIFE_OS_FILE, "w") as file:
        json.dump(data, file, indent=4)
    return data


def build_project_life_os():
    data = load_state()
    return save_state(data)


def add_project(name, next_step=""):
    data = load_state()
    project_id = "".join(ch if ch.isalnum() else "-" for ch in name.lower()).strip("-")[:40]
    data["projects"].append({
        "id": project_id,
        "name": name,
        "status": "active",
        "next_step": next_step,
        "created_at": now_timestamp()
    })
    return save_state(data)


def show_project_life_os():
    data = build_project_life_os()
    print("\n=== SEED PROJECT + LIFE OS ===")
    print("Projects:")
    for p in data["projects"]:
        print(f"- {p['name']} [{p.get('status')}]")
    print("Life tracks:")
    for t in data["life_tracks"]:
        print(f"- {t['name']} [{t.get('status')}]")


if __name__ == "__main__":
    show_project_life_os()
