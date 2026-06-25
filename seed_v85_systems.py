import json
from datetime import datetime
from pathlib import Path

STATE_FILE = Path("seed_v85_systems_state.json")

def now():
    return datetime.now().isoformat(timespec="seconds")

def safe(title, summary, fn):
    try:
        data = fn()
        return {"title": title, "summary": summary, "status": "ok" if data.get("ok", True) else "warning", "data": data}
    except Exception as e:
        return {"title": title, "summary": summary, "status": "error", "error": str(e)}

def build_v85_state():
    cards = [
        safe("v82 Recovery", "AST recursion guard, fast core runtime checks, rollback notes.", lambda: __import__("seed_recovery_v82", fromlist=["recovery_summary"]).recovery_summary()),
        safe("v83 One-Command Runtime", "Seed can start via ./seed or seed_start.sh.", lambda: __import__("seed_runtime_v83", fromlist=["runtime_status"]).runtime_status()),
        safe("v84 Backup/Privacy", "Backup, export memory, forget by keyword.", lambda: __import__("seed_privacy_backup_v84", fromlist=["privacy_status"]).privacy_status()),
        safe("v85 Release Candidate", "RC report and README generation.", lambda: __import__("seed_release_candidate_v85", fromlist=["release_candidate_summary"]).release_candidate_summary()),
        safe("Self-State Truth", "Current version override is v85.x.", lambda: __import__("seed_self_state_v85", fromlist=["build_self_state"]).build_self_state()),
    ]
    data = {"created_at": now(), "version": "v85.3.0", "ok": all(c["status"] != "error" for c in cards), "cards": cards}
    STATE_FILE.write_text(json.dumps(data, indent=4, ensure_ascii=False))
    return data

def show_v85_status():
    data = build_v85_state()
    print("\n=== SEED v85.3 FAST REAL V1 PREP STATUS ===")
    print(f"OK: {data['ok']}")
    for c in data["cards"]:
        print(f"- {c['title']}: {c['status']} — {c['summary']}")

if __name__ == "__main__":
    show_v85_status()
