import json
from datetime import datetime
from pathlib import Path
OUT=Path("seed_presence_inbox_v72.json")
def now(): return datetime.now().isoformat(timespec="seconds")
def load():
    if OUT.exists():
        try: return json.loads(OUT.read_text(errors="ignore"))
        except Exception: pass
    return {"created_at":now(),"version":"v72.0.0","items":[]}
def add_notice(title,body,category="project",urgency="normal",speakable=True):
    data=load(); key=(title,body[:80])
    for x in data["items"]:
        if (x.get("title"),x.get("body","")[:80])==key: return x
    item={"id":f"notice_{len(data['items'])+1:04d}","created_at":now(),"title":title,"body":body,"category":category,"urgency":urgency,"speakable":speakable,"status":"new"}
    data["items"].append(item); data["updated_at"]=now(); OUT.write_text(json.dumps(data,indent=4,ensure_ascii=False)); return item
def build_notices():
    try:
        from seed_memory_review_inbox_v64 import build_inbox
        p=build_inbox().get("pending",0)
        if p>0: add_notice("Memory review is waiting",f"{p} memory candidates are pending. Reviewing them improves continuity.","memory","high")
    except Exception: pass
    try:
        from seed_model_real_mode_v61 import load_role_map
        add_notice("Model routing is active",f"Current role map: {load_role_map().get('role_map',{})}","model","normal",False)
    except Exception: pass
    try:
        from seed_repo_pattern_extractor_v72 import build_repo_patterns
        add_notice("Repo patterns are available",f"{len(build_repo_patterns().get('patterns',[]))} repo pattern groups can become Seed-native tasks.","repo","normal",False)
    except Exception: pass
    return load()
def show_presence_inbox():
    print("\n=== SEED PRESENCE INBOX v72 ===")
    for x in build_notices().get("items",[])[-20:]: print(f"- {x['id']} [{x['category']}/{x['urgency']}] {x['title']}: {x['body'][:180]}")
if __name__ == "__main__": show_presence_inbox()
