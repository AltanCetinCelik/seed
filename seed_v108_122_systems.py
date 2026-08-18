import json
from datetime import datetime
SYSTEMS=[("Proactive","seed_proactive_rhythm_v108","status"),("Native Wake","seed_native_wake_v109","status"),("STT","seed_stt_v110","status"),("TTS","seed_tts_v111","status"),("Memory3","seed_memory_garden3_v112","status"),("Memory Gate","seed_memory_gate_v113","status"),("Project Memory","seed_project_memory_v114","status"),("Operator2","seed_operator2_v115","status"),("Screen2","seed_screen_understanding_v116","status"),("ApprovalUI2","seed_approval_ui2_v117","status"),("Skills2","seed_skill_registry2_v118","status"),("MCP","seed_mcp_bridge_v119","status"),("Odysseus","seed_odysseus_audit_v120","status"),("RepoAudit","seed_repo_audit_v121","status"),("RAG2","seed_rag2_v122","status")]
def now(): return datetime.now().isoformat(timespec='seconds')
def status():
    cards=[]
    for t,m,f in SYSTEMS:
        try:
            mod=__import__(m,fromlist=[f]); d=getattr(mod,f)(); cards.append({"title":t,"ok":bool(d.get("ok",True)),"data":d})
        except Exception as e: cards.append({"title":t,"ok":False,"error":str(e)})
    return {"created_at":now(),"version":"v108-v122.0.0","ok":all(c["ok"] for c in cards),"ok_count":sum(c["ok"] for c in cards),"total":len(cards),"cards":cards}
if __name__=="__main__": print(json.dumps(status(),indent=4,ensure_ascii=False))
