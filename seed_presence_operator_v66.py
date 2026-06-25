import json
from pathlib import Path
from datetime import datetime
STATE_FILE=Path("seed_presence_operator_v66.json")
def now(): return datetime.now().isoformat(timespec="seconds")
def best_next_move():
    try:
        from seed_model_real_mode_v61 import list_models, install_plan
        if len(list_models().get("models",[])) < 2: return {"message":"You have not installed enough local models yet. Model routing cannot become real until starter models are pulled.","reason":"model_benchmarking"}
        if install_plan().get("missing_starter"): return {"message":"Some starter models are still missing, so model routing is incomplete.","reason":"finish_model_set"}
    except Exception: pass
    try:
        from seed_memory_review_inbox_v64 import build_inbox
        inbox=build_inbox()
        if inbox.get("pending",0)>0: return {"message":f"Seed found {inbox.get('pending')} memory candidates. Reviewing them will improve continuity.","reason":"memory_review"}
    except Exception: pass
    return {"message":"Seed is stable. The next useful move is polishing the companion terminal and Control Plane.","reason":"no_urgent_missing_system"}
def presence_brief():
    move=best_next_move(); data={"created_at":now(),"version":"v70.0.0","ok":True,"message":move["message"],"why":move["reason"],"rules":["Never spam","Always explain why","One useful question max","No fake consciousness claims"]}; STATE_FILE.write_text(json.dumps(data,indent=4)); return data
def show_presence_operator(): print(json.dumps(presence_brief(),indent=4))
if __name__=="__main__": show_presence_operator()
