import json
from datetime import datetime
from pathlib import Path
TASK_FILE=Path("seed_action_tasks_v74.json")

def now_timestamp(): return datetime.now().isoformat(timespec="seconds")
def _task_id(n): return f"task_{n:04d}"

def build_action_tasks():
    tasks=[]
    def add(title,category,reason,source,priority="normal"):
        tasks.append({"id":_task_id(len(tasks)+1),"title":title,"category":category,"reason":reason,"source":source,"priority":priority,"status":"candidate"})
    try:
        from seed_friend_advice_ingestor_v72 import build_advice_backlog
        for item in build_advice_backlog().get("tasks",[]):
            add(item.get("title","Friend advice task"), item.get("category","advice"), item.get("reason",""), "friend_advice_v72", "high" if item.get("category") in {"voice","avatar","curiosity","life"} else "normal")
    except Exception as e: add("Repair friend advice ingestion","system",str(e),"v74_diagnostic","high")
    try:
        from seed_repo_pattern_extractor_v72 import build_repo_patterns
        for group in build_repo_patterns().get("patterns",[]):
            for task in group.get("seed_native_tasks",[]): add(task, group.get("label","repo"), group.get("takeaway",""), "repo_patterns_v72","normal")
    except Exception as e: add("Repair repo pattern extraction","system",str(e),"v74_diagnostic","high")
    try:
        from seed_curiosity_engine_v72 import generate_curiosities
        for c in generate_curiosities().get("items",[]): add(c.get("title","Curiosity task"), c.get("category","curiosity"), c.get("body",""), "curiosity_v72","normal")
    except Exception as e: add("Repair curiosity engine","system",str(e),"v74_diagnostic","high")
    data={"created_at":now_timestamp(),"version":"v74.0.0","ok":True,"count":len(tasks),"tasks":tasks}
    TASK_FILE.write_text(json.dumps(data,indent=4,ensure_ascii=False)); return data

def show_action_tasks():
    data=build_action_tasks()
    print("\n=== SEED v74 ACTION TASKS ==="); print("Tasks:",data["count"])
    for task in data["tasks"][:40]:
        print(f"- {task['id']} [{task['category']}/{task['priority']}] {task['title']}")
        if task.get("reason"): print(f"  why: {task['reason'][:180]}")
if __name__=="__main__": show_action_tasks()
