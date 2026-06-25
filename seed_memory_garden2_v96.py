import json, re
from datetime import datetime
from pathlib import Path
PINS=Path("seed_memory_pins_v96.jsonl"); FORGET=Path("seed_memory_forget_v96.jsonl"); REFL=Path("seed_memory_reflections_v96.jsonl")
def now(): return datetime.now().isoformat(timespec="seconds")
def write(path,row):
    row.setdefault("created_at",now()); row.setdefault("version","v96.0.0")
    with path.open("a") as f: f.write(json.dumps(row,ensure_ascii=False)+"\n")
def read(path,limit=200):
    if not path.exists(): return []
    out=[]
    for l in path.read_text(errors="ignore").splitlines()[-limit:]:
        try: out.append(json.loads(l))
        except Exception: pass
    return out
def base_memories():
    try:
        from seed_memory_garden_v90 import memories
        return memories(5000)
    except Exception: return []
def pin(mid,reason="manual"): write(PINS,{"memory_id":mid,"reason":reason}); return {"ok":True,"pinned":mid}
def forget(mid,reason="manual"): write(FORGET,{"memory_id":mid,"reason":reason}); return {"ok":True,"forgotten":mid}
def search(q):
    terms=set(re.sub(r"[^a-z0-9çğıöşü\s]"," ",q.lower()).split()); forgotten={x.get("memory_id") for x in read(FORGET,9999)}
    hits=[]
    for m in base_memories():
        if m.get("memory_id") in forgotten: continue
        hay=(m.get("summary","")+" "+" ".join(m.get("tags",[]))).lower()
        score=sum(1 for t in terms if t in hay)
        if score: hits.append({"score":score,"memory":m})
    return sorted(hits,key=lambda x:x["score"],reverse=True)[:20]
def reflect():
    row={"summary":f"Memory Garden 2: {len(base_memories())} base memories, {len(read(PINS,9999))} pins, {len(read(FORGET,9999))} forgotten entries."}
    write(REFL,row); return {"ok":True,**row}
def status(): return {"created_at":now(),"version":"v96.0.0","ok":True,"base_memories":len(base_memories()),"pins":read(PINS,10),"forgotten":read(FORGET,10),"reflections":read(REFL,5)}
if __name__=="__main__":
    import sys
    a=sys.argv[1] if len(sys.argv)>1 else "status"
    if a=="pin": print(json.dumps(pin(sys.argv[2]," ".join(sys.argv[3:])),indent=4))
    elif a=="forget": print(json.dumps(forget(sys.argv[2]," ".join(sys.argv[3:])),indent=4))
    elif a=="search": print(json.dumps(search(" ".join(sys.argv[2:])),indent=4,ensure_ascii=False))
    elif a=="reflect": print(json.dumps(reflect(),indent=4,ensure_ascii=False))
    else: print(json.dumps(status(),indent=4,ensure_ascii=False))
