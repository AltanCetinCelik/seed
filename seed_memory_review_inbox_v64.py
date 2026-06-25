import json
from pathlib import Path
from datetime import datetime
INBOX_FILE=Path("seed_memory_review_inbox_v64.json")
def now(): return datetime.now().isoformat(timespec="seconds")
def candidates():
    try:
        from seed_memory_auto_extractor_v60 import extract_candidates
        return extract_candidates(limit=60).get("candidates",[])
    except Exception: return []
def build_inbox():
    old={}
    if INBOX_FILE.exists():
        try: old={x.get("content"):x for x in json.loads(INBOX_FILE.read_text(errors="ignore")).get("items",[])}
        except Exception: old={}
    items=[]
    for cand in candidates():
        cand["review_status"]=old.get(cand.get("content"),{}).get("review_status","pending"); items.append(cand)
    data={"created_at":now(),"version":"v70.0.0","ok":True,"count":len(items),"pending":len([x for x in items if x.get("review_status")=="pending"]),"saved":len([x for x in items if x.get("review_status")=="saved"]),"ignored":len([x for x in items if x.get("review_status")=="ignored"]),"items":items}; INBOX_FILE.write_text(json.dumps(data,indent=4)); return data
def save_memory(candidate_id):
    data=build_inbox(); item=next((x for x in data["items"] if x.get("id")==candidate_id),None)
    if not item: return {"ok":False,"error":"Candidate not found"}
    from seed_memory_brain_max_v32 import add_memory
    mem=add_memory(content=item["content"],layer=item.get("suggested_layer","project"),source=f"review_inbox:{item.get('source')}",confidence=.9,tags=["reviewed","v64"])
    for x in data["items"]:
        if x.get("id")==candidate_id: x["review_status"]="saved"; x["memory_id"]=mem.get("id")
    INBOX_FILE.write_text(json.dumps(data,indent=4)); return {"ok":True,"memory":mem}
def auto_save_high_confidence(limit=8):
    data=build_inbox(); pending=sorted([x for x in data["items"] if x.get("review_status")=="pending"],key=lambda x:x.get("score",0),reverse=True)[:limit]; results=[save_memory(x["id"]) for x in pending if x.get("score",0)>=4]; return {"ok":True,"saved":len([r for r in results if r.get("ok")]),"results":results}
def show_memory_review():
    data=build_inbox(); print(f"Pending: {data['pending']} Saved: {data['saved']} Ignored: {data['ignored']}")
    for x in data["items"][:20]: print(f"- {x['id']} score={x.get('score')} status={x.get('review_status')}: {x.get('content')[:180]}")
def show_memory_review_auto_save(): print(json.dumps(auto_save_high_confidence(),indent=4))
def show_memory_review_save(): print(json.dumps(save_memory(input("Candidate ID to save: ").strip()),indent=4))
def show_memory_review_ignore(): print("Manual ignore can be added after first review pass.")
if __name__=="__main__": show_memory_review()
