import json
from datetime import datetime
from pathlib import Path

TASK_FILE = Path("seed_action_tasks_v73.json")

def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")

def add_task(tasks, title, source, category, reason, priority="normal"):
    tasks.append({"id": f"task_{len(tasks)+1:04d}", "title": title, "source": source, "category": category, "reason": reason, "priority": priority, "status": "candidate"})

def build_tasks():
    tasks = []
    try:
        from seed_friend_advice_ingestor_v72 import build_advice_backlog
        for t in build_advice_backlog().get("tasks", []):
            add_task(tasks, t.get("title", "Friend advice task"), "friend_advice", t.get("category", "general"), t.get("reason", ""), "normal")
    except Exception:
        pass
    try:
        from seed_repo_pattern_extractor_v72 import build_repo_patterns
        for p in build_repo_patterns().get("patterns", []):
            for task in p.get("seed_native_tasks", []):
                add_task(tasks, task, f"repo:{p.get('label')}", "repo_pattern", p.get("takeaway", ""), "high")
    except Exception:
        pass
    try:
        from seed_curiosity_engine_v72 import generate_curiosities
        for c in generate_curiosities().get("items", []):
            add_task(tasks, c.get("title", "Curiosity task"), "curiosity", c.get("category", "project"), c.get("body", ""), "high" if c.get("relevance_score", 0) >= 8 else "normal")
    except Exception:
        pass
    data = {"created_at": now_timestamp(), "version": "v73.0.0", "ok": True, "task_count": len(tasks), "tasks": tasks}
    TASK_FILE.write_text(json.dumps(data, indent=4, ensure_ascii=False))
    return data

def show_tasks(limit=40):
    data = build_tasks()
    print("\n=== SEED v73 ACTION TASKS ===")
    print(f"Tasks: {data['task_count']}")
    for t in data["tasks"][:limit]:
        print(f"- {t['id']} [{t['priority']}/{t['category']}] {t['title']} — {t['source']}")
    return "handled"

if __name__ == "__main__":
    show_tasks()
