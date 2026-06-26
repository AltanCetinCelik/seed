import json
from datetime import datetime
SYSTEMS=[("Deep Research","seed_deep_research_v123","status"),("Knowledge Graph","seed_knowledge_graph_v124","status"),("Device Router","seed_device_router_v125","status"),("Pi Satellite","seed_pi_satellite_v126","status"),("Windows Worker","seed_windows_worker_v127","status"),("Menu Bar","seed_menu_bar_v128","status"),("Avatar 2","seed_avatar2_v129","status"),("Release Packaging","seed_release_packaging_v130","status")]
def now(): return datetime.now().isoformat(timespec="seconds")
def status():
    cards=[]
    for t,m,f in SYSTEMS:
        try:
            mod=__import__(m,fromlist=[f]); d=getattr(mod,f)(); cards.append({"title":t,"ok":bool(d.get("ok",True)),"data":d})
        except Exception as e: cards.append({"title":t,"ok":False,"error":str(e)})
    return {"created_at":now(),"version":"v123-v130.0.0","ok":all(c["ok"] for c in cards),"ok_count":sum(c["ok"] for c in cards),"total":len(cards),"cards":cards}
if __name__=="__main__": print(json.dumps(status(),indent=4))
