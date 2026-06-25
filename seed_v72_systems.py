import json
from datetime import datetime
from pathlib import Path
OUT=Path("seed_v72_systems_state.json")
def now(): return datetime.now().isoformat(timespec="seconds")
def safe(title,summary,fn):
    try:
        d=fn(); return {"title":title,"summary":summary,"status":"ok" if d.get("ok",True) else "warning","data":d}
    except Exception as e: return {"title":title,"summary":summary,"status":"error","error":str(e)}
def build_v72_state():
    cards=[
      safe("Presence Policy","Expressive simulated emotion + relevant life advice, without spam.",lambda:__import__("seed_presence_policy_v72",fromlist=["load_policy"]).load_policy()),
      safe("Friend Advice","Ingests friend advice into backlog categories.",lambda:__import__("seed_friend_advice_ingestor_v72",fromlist=["build_advice_backlog"]).build_advice_backlog()),
      safe("Repo Patterns","Turns Hermes/Moltbot/OpenClaw into Seed-native tasks.",lambda:__import__("seed_repo_pattern_extractor_v72",fromlist=["build_repo_patterns"]).build_repo_patterns()),
      safe("Avatar State","Expressive avatar state from real system status.",lambda:__import__("seed_avatar_state_v72",fromlist=["compute_avatar_state"]).compute_avatar_state()),
      safe("Presence Inbox","Collects grounded notices.",lambda:__import__("seed_presence_inbox_v72",fromlist=["build_notices"]).build_notices()),
      safe("Curiosity Engine","Relevant project/life suggestions.",lambda:__import__("seed_curiosity_engine_v72",fromlist=["generate_curiosities"]).generate_curiosities()),
      safe("Voice Session","Voice foundation state.",lambda:__import__("seed_voice_session_v72",fromlist=["voice_session_status"]).voice_session_status()),
    ]
    data={"created_at":now(),"version":"v72.0.0","ok":all(c["status"]!="error" for c in cards),"cards":cards}
    OUT.write_text(json.dumps(data,indent=4,ensure_ascii=False)); return data
def show_v72_status():
    d=build_v72_state(); print("\n=== SEED v72 PRESENCE MAX STATUS ==="); print("OK:",d["ok"])
    for c in d["cards"]: print(f"- {c['title']}: {c['status']} — {c['summary']}")
if __name__ == "__main__": show_v72_status()
