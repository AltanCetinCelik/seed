import json
from datetime import datetime
from pathlib import Path
STATE_FILE=Path("seed_v74_systems_state.json")
def now_timestamp(): return datetime.now().isoformat(timespec="seconds")
def safe(title,summary,fn):
    try:
        data=fn(); return {"title":title,"summary":summary,"status":"ok" if data.get("ok",True) else "warning","data":data}
    except Exception as e: return {"title":title,"summary":summary,"status":"error","error":str(e)}
def build_v74_state():
    cards=[
        safe("Embodied State","Tracks listening/thinking/speaking/idle state.",lambda:__import__("seed_embodied_state_v74",fromlist=["load_state"]).load_state()),
        safe("Avatar Panel","Live avatar mood/face/color from real Seed state.",lambda:__import__("seed_avatar_panel_v74",fromlist=["build_avatar_panel_state"]).build_avatar_panel_state()),
        safe("Memory Actions","Interactive review overlay for memory candidates.",lambda:__import__("seed_memory_actions_v74",fromlist=["get_memory_candidates"]).get_memory_candidates(10)),
        safe("Action Tasks","Action board from advice, repo patterns, and curiosity.",lambda:__import__("seed_action_tasks_v74",fromlist=["build_action_tasks"]).build_action_tasks()),
        safe("Embodied Server","Local web companion panel on localhost.",lambda:{"ok":True,"url":"http://127.0.0.1:8794"}),
        safe("Voice Pipeline","Uses v73.1 voice record/transcribe/chat/say functions.",lambda:__import__("seed_live_voice_v731",fromlist=["voice_status"]).voice_status()),
    ]
    data={"created_at":now_timestamp(),"version":"v74.0.0","ok":all(c["status"]!="error" for c in cards),"cards":cards}
    STATE_FILE.write_text(json.dumps(data,indent=4,ensure_ascii=False)); return data
def show_v74_status():
    data=build_v74_state(); print("\n=== SEED v74 EMBODIED COMPANION STATUS ==="); print("OK:",data["ok"])
    for c in data["cards"]: print(f"- {c['title']}: {c['status']} — {c['summary']}")
if __name__=="__main__": show_v74_status()
