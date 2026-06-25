import json
from datetime import datetime
from pathlib import Path
AVATAR_PANEL_FILE=Path("seed_avatar_panel_v74_state.json")

def now_timestamp(): return datetime.now().isoformat(timespec="seconds")

def build_avatar_panel_state():
    try:
        from seed_avatar_state_v72 import compute_avatar_state
        avatar=compute_avatar_state()
    except Exception as e:
        avatar={"ok":False,"mood":"cautious","color":"red","face":"alert","reason":f"Avatar v72 unavailable: {e}"}
    try:
        from seed_embodied_state_v74 import load_state
        embodied=load_state()
    except Exception:
        embodied={"mode":"idle"}
    mode=embodied.get("mode","idle")
    colors={"idle":avatar.get("color","green"),"listening":"blue","thinking":"orange","speaking":"purple","warning":"red"}
    face={"listening":"listening","thinking":"thinking","speaking":"speaking"}.get(mode, avatar.get("face","calm"))
    data={"created_at":now_timestamp(),"version":"v74.0.0","ok":True,"mode":mode,"mood":avatar.get("mood","steady"),"face":face,"color":colors.get(mode,avatar.get("color","green")),"reason":embodied.get("mode_reason") or avatar.get("reason","Seed is online."),"last_user":embodied.get("last_user",""),"last_reply":embodied.get("last_reply",""),"last_transcript":embodied.get("last_transcript",""),"last_model":embodied.get("last_model"),"last_role":embodied.get("last_role"),"note":"Avatar is an expressive simulated interface state, not biological emotion."}
    AVATAR_PANEL_FILE.write_text(json.dumps(data,indent=4,ensure_ascii=False)); return data

def show_avatar_panel():
    print("\n=== SEED v74 AVATAR PANEL STATE ==="); print(json.dumps(build_avatar_panel_state(), indent=4, ensure_ascii=False))
if __name__=="__main__": show_avatar_panel()
