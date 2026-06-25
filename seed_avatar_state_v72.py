import json
from datetime import datetime
from pathlib import Path
OUT=Path("seed_avatar_state_v72.json")
def now(): return datetime.now().isoformat(timespec="seconds")
def compute_avatar_state():
    mood,color,face,reason="steady","green","calm","Seed is stable."
    try:
        from seed_memory_review_inbox_v64 import build_inbox
        pending=build_inbox().get("pending",0)
        if pending>0: mood,color,face,reason="curious","blue","curious",f"{pending} memory candidates are waiting."
    except Exception: pass
    data={"created_at":now(),"version":"v72.0.0","ok":True,"mood":mood,"color":color,"face":face,"reason":reason,"note":"Avatar mood is expressive simulation, not biological feeling."}
    OUT.write_text(json.dumps(data,indent=4,ensure_ascii=False)); return data
def show_avatar(): print("\n=== SEED AVATAR STATE v72 ==="); print(json.dumps(compute_avatar_state(),indent=4,ensure_ascii=False))
if __name__ == "__main__": show_avatar()
