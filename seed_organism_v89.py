import json
from datetime import datetime
from pathlib import Path
STATE_FILE=Path("seed_organism_v89_state.json")
def now(): return datetime.now().isoformat(timespec="seconds")
def safe(fn):
    try: return fn()
    except Exception as e: return {"ok":False,"error":str(e)}
def start_organism():
    print("=== SEED v89.2 ORGANISM MODE ===")
    av=safe(lambda:__import__("seed_avatar_v89",fromlist=["start_server"]).start_server())
    he=safe(lambda:__import__("seed_ambient_hearing_v89",fromlist=["start_daemon"]).start_daemon())
    vi=safe(lambda:__import__("seed_ambient_vision_v89",fromlist=["start_daemon"]).start_daemon())
    try: __import__("seed_organism_notes_v89",fromlist=["add_note"]).add_note("organism","Seed organism mode started in note-only mode.",70,"",["organism"])
    except Exception: pass
    d={"created_at":now(),"version":"v89.2.0","ok":av.get("ok") and he.get("ok") and vi.get("ok"),"avatar":av,"hearing":he,"vision":vi}; STATE_FILE.write_text(json.dumps(d,indent=4,ensure_ascii=False)); print(json.dumps(d,indent=4,ensure_ascii=False)); return d
def stop_organism():
    he=safe(lambda:__import__("seed_ambient_hearing_v89",fromlist=["stop_daemon"]).stop_daemon())
    vi=safe(lambda:__import__("seed_ambient_vision_v89",fromlist=["stop_daemon"]).stop_daemon())
    try: __import__("seed_avatar_v89",fromlist=["set_avatar_state"]).set_avatar_state(mode="idle",emotion="calm",message="Organism mode stopped.",hearing=False,seeing=False,thinking=False,speaking=False)
    except Exception: pass
    d={"created_at":now(),"version":"v89.2.0","ok":True,"hearing":he,"vision":vi}; STATE_FILE.write_text(json.dumps(d,indent=4,ensure_ascii=False)); print(json.dumps(d,indent=4,ensure_ascii=False)); return d
def organism_status():
    av=safe(lambda:__import__("seed_avatar_v89",fromlist=["avatar_status"]).avatar_status())
    he=safe(lambda:__import__("seed_ambient_hearing_v89",fromlist=["hearing_status"]).hearing_status())
    vi=safe(lambda:__import__("seed_ambient_vision_v89",fromlist=["vision_status"]).vision_status())
    no=safe(lambda:__import__("seed_organism_notes_v89",fromlist=["note_stats"]).note_stats())
    return {"created_at":now(),"version":"v89.2.0","ok":True,"avatar":av,"hearing":he,"vision":vi,"notes":no}
if __name__=="__main__":
    import sys
    a=sys.argv[1] if len(sys.argv)>1 else "status"
    if a=="start": start_organism()
    elif a=="stop": stop_organism()
    else: print(json.dumps(organism_status(),indent=4,ensure_ascii=False))
