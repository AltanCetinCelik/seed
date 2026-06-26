import json
from datetime import datetime
SYSTEMS=[("Voice Input","seed_voice_input_v131","status"),("Real Wake","seed_real_wake_v132","status"),("Voice Conversation","seed_voice_conversation_v133","status"),("Proactive Presence","seed_proactive_presence_v134","status"),("Repo Assimilation","seed_repo_assimilation_v135","status")]
def now(): return datetime.now().isoformat(timespec="seconds")
def status():
    cards=[]
    for title,mod,fn in SYSTEMS:
        try:
            m=__import__(mod,fromlist=[fn]); d=getattr(m,fn)(); cards.append({"title":title,"ok":bool(d.get("ok",True)),"data":d})
        except Exception as e: cards.append({"title":title,"ok":False,"error":str(e)})
    return {"created_at":now(),"version":"v131-v135.0.0","ok":all(c["ok"] for c in cards),"ok_count":sum(c["ok"] for c in cards),"total":len(cards),"cards":cards}
if __name__=="__main__": print(json.dumps(status(),indent=4,ensure_ascii=False))
