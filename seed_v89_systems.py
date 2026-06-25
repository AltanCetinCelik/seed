import json
from datetime import datetime
from pathlib import Path
STATE_FILE=Path("seed_v89_systems_state.json")
def now(): return datetime.now().isoformat(timespec="seconds")
def safe(title,summary,fn):
    try:
        d=fn(); return {"title":title,"summary":summary,"status":"ok" if d.get("ok",True) else "warning","data":d}
    except Exception as e: return {"title":title,"summary":summary,"status":"error","error":str(e)}
def build_v89_state():
    cards=[
        safe("Avatar","Local animated avatar.",lambda:__import__("seed_avatar_v89",fromlist=["avatar_status"]).avatar_status()),
        safe("Notes","Important notes only; no raw media.",lambda:__import__("seed_organism_notes_v89",fromlist=["note_stats"]).note_stats()),
        safe("Ambient Hearing","Deletes audio after transcription.",lambda:__import__("seed_ambient_hearing_v89",fromlist=["hearing_status"]).hearing_status()),
        safe("Ambient Vision","Deletes screenshots after note extraction.",lambda:__import__("seed_ambient_vision_v89",fromlist=["vision_status"]).vision_status()),
        safe("Organism Runtime","Avatar + hearing + vision + notes.",lambda:__import__("seed_organism_v89",fromlist=["organism_status"]).organism_status()),
    ]
    d={"created_at":now(),"version":"v89.0.0","ok":all(c["status"]!="error" for c in cards),"cards":cards}; STATE_FILE.write_text(json.dumps(d,indent=4,ensure_ascii=False)); return d
def show_v89_status():
    d=build_v89_state(); print("\n=== SEED v89 ORGANISM STATUS ==="); print(f"OK: {d['ok']}")
    for c in d["cards"]: print(f"- {c['title']}: {c['status']} — {c['summary']}")
if __name__=="__main__": show_v89_status()
