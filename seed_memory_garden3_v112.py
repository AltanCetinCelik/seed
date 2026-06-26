import json,re,time
from datetime import datetime
from pathlib import Path
MEM=Path("seed_memory_garden3_v112.jsonl")
def now(): return datetime.now().isoformat(timespec="seconds")
def write(row):
    row.setdefault("memory_id",f"m3_{int(time.time()*1000)}"); row.setdefault("created_at",now()); row.setdefault("version","v112.0.0"); row.setdefault("trust",0.75); row.setdefault("forgotten",False)
    with MEM.open("a") as f:f.write(json.dumps(row,ensure_ascii=False)+"\n")
    return row
def read():
    if not MEM.exists(): return []
    out=[]
    for l in MEM.read_text(errors="ignore").splitlines():
        try: out.append(json.loads(l))
        except Exception: pass
    return out
def add(memory_type,summary,tags=None,source="manual",trust=0.75): return {"ok":True,"memory":write({"memory_type":memory_type,"summary":summary,"tags":tags or [],"source":source,"trust":trust})}
def import_legacy():
    existing={m.get("summary") for m in read()}; n=0
    try:
        import seed_memory_garden2_v96 as m2
        for h in m2.search("seed milestone"):
            m=h.get("memory",{}); s=m.get("summary")
            if s and s not in existing: write({"memory_type":m.get("memory_type","milestone"),"summary":s,"tags":m.get("tags",[]),"source":"legacy_v96","trust":0.9}); n+=1
    except Exception: pass
    return {"ok":True,"imported":n}
def search(q,limit=20):
    terms=[x for x in re.sub(r"[^a-z0-9çğıöşü\s]"," ",q.lower()).split() if len(x)>1]; hits=[]
    for m in read():
        if m.get("forgotten"): continue
        hay=(m.get("summary","")+" "+" ".join(m.get("tags",[]))+" "+m.get("memory_type","")).lower(); sc=sum(hay.count(t) for t in terms)+float(m.get("trust",0.5))
        if sc>0.5: hits.append({"score":round(sc,2),"memory":m})
    return sorted(hits,key=lambda x:x["score"],reverse=True)[:int(limit)]
def status():
    import_legacy(); items=read(); by={}
    for m in items: by[m.get("memory_type","unknown")]=by.get(m.get("memory_type","unknown"),0)+1
    return {"created_at":now(),"version":"v112.0.0","ok":True,"count":len(items),"by_type":by,"latest":items[-5:]}
if __name__=="__main__":
    import sys
    a=sys.argv[1] if len(sys.argv)>1 else "status"
    print(json.dumps(add(sys.argv[2]," ".join(sys.argv[3:])) if a=="add" else search(" ".join(sys.argv[2:])) if a=="search" else import_legacy() if a=="import" else status(),indent=4,ensure_ascii=False))
