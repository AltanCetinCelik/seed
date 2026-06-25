import json
from datetime import datetime
from pathlib import Path
ACTION_FILE=Path("seed_memory_review_actions_v74.jsonl")

def now_timestamp(): return datetime.now().isoformat(timespec="seconds")

def _candidate_text(item):
    if isinstance(item,str): return item
    if isinstance(item,dict):
        for k in ["content","text","memory","candidate","summary","body","message"]:
            if item.get(k): return str(item[k])
        return json.dumps(item,ensure_ascii=False)[:800]
    return str(item)

def get_memory_candidates(limit=10):
    candidates=[]
    try:
        from seed_memory_review_inbox_v64 import build_inbox
        inbox=build_inbox(); raw=[]
        for k in ["candidates","pending_items","items","memories"]:
            if isinstance(inbox.get(k),list): raw=inbox[k]; break
        if not raw and isinstance(inbox.get("pending"),list): raw=inbox["pending"]
        for i,item in enumerate(raw[:limit],1):
            candidates.append({"id": item.get("id",f"candidate_{i:04d}") if isinstance(item,dict) else f"candidate_{i:04d}","text":_candidate_text(item),"source":"seed_memory_review_inbox_v64","raw": item if isinstance(item,dict) else {"value":item}})
    except Exception:
        pass
    if not candidates:
        try:
            from seed_curiosity_engine_v72 import generate_curiosities
            for i,item in enumerate(generate_curiosities().get("items",[])[:limit],1):
                candidates.append({"id":f"curiosity_{i:04d}","text":f"{item.get('title')}: {item.get('body')}","source":"curiosity_fallback","raw":item})
        except Exception: pass
    return {"created_at":now_timestamp(),"version":"v74.0.0","ok":True,"count":len(candidates),"candidates":candidates[:limit],"note":"Actions are logged; base memory store is not destructively modified."}

def review_action(candidate_id, action, note=""):
    action=str(action).lower().strip()
    if action not in {"save","ignore","later","edit"}: action="later"
    row={"created_at":now_timestamp(),"version":"v74.0.0","candidate_id":candidate_id,"action":action,"note":note}
    with ACTION_FILE.open("a") as f: f.write(json.dumps(row,ensure_ascii=False)+"\n")
    return {"ok":True,"decision":row}

def load_actions(limit=100):
    if not ACTION_FILE.exists(): return []
    rows=[]
    for line in ACTION_FILE.read_text(errors="ignore").splitlines()[-limit:]:
        try: rows.append(json.loads(line))
        except Exception: pass
    return rows

def show_memory_actions():
    data=get_memory_candidates(10)
    print("\n=== SEED v74 MEMORY REVIEW ACTIONS ==="); print("Candidates:",data["count"])
    for item in data["candidates"]: print(f"- {item['id']}: {item['text'][:220]}")
    print("\nDecisions:")
    for row in load_actions(20): print(f"- {row['candidate_id']} -> {row['action']} {row.get('note','')}")
if __name__=="__main__": show_memory_actions()

# v75 backend compatibility override for v74 panel.
try:
    def get_memory_candidates(limit=10):
        from seed_memory_review_v75 import candidates
        cs = candidates(limit=limit)
        return {
            "version": "v75.0.0",
            "ok": True,
            "count": len(cs),
            "candidates": cs,
            "note": "v74 panel backed by v75 real memory review."
        }
    def review_action(candidate_id, action, note=""):
        from seed_memory_review_v75 import decide_memory
        return decide_memory(candidate_id, action=action, note=note)
    def load_actions(limit=100):
        from seed_memory_review_v75 import decision_rows
        return decision_rows(limit)
    def show_memory_actions():
        from seed_memory_review_v75 import show_memory_review
        show_memory_review()
except Exception:
    pass
