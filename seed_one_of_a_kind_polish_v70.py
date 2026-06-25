import json
from pathlib import Path
from datetime import datetime
STATE_FILE=Path("seed_one_of_a_kind_polish_v70.json")
def build_polish_state():
    data={"created_at":datetime.now().isoformat(timespec="seconds"),"version":"v70.0.0","ok":True,"taste_system":{"style":"local-first, sharp, warm, technical, not robotic","ui":"dark professional, low clutter, one obvious next action","assistant_behavior":"reasoned initiative, memory continuity, no fake consciousness"},"rituals":["daily brief","after-success commit/backup reminder","after-failure diagnosis flow","night review","weekly model benchmark"],"progress_map":["v20 Sovereign OS","v30 Agent HQ","v45 Total Systems","v50 Nothing Left Behind","v60 Natural UX + Intelligence","v70 One-of-a-kind polish"],"achievements":["Local-first companion core","Repo assimilation engine","Agent HQ","Natural intent router","Model manager","Fusion notebooks","Memory review inbox","Real Aider loop","Multi-channel plan"],"why_explanations":True}; STATE_FILE.write_text(json.dumps(data,indent=4)); return data
def why_suggested_this():
    try:
        from seed_presence_operator_v66 import best_next_move; move=best_next_move()
    except Exception: move={"message":"Improve natural UX.","reason":"Seed should feel less like a dev console."}
    return {"ok":True,"suggestion":move.get("message"),"why":move.get("reason")}
def show_polish(): print(json.dumps(build_polish_state(),indent=4))
def show_why(): print(json.dumps(why_suggested_this(),indent=4))
if __name__=="__main__": show_polish()
