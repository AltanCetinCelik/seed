import json,re
from pathlib import Path
from datetime import datetime
INDEX=Path("seed_rag2_v122_index.jsonl")
SETTINGS=Path("seed_rag2_v122_settings.json")
DEFAULT={"version":"v122.0.0","extensions":[".py",".md",".txt",".json"],"max_file_kb":220,"chunk_chars":1200,"modes":{"seed":{"roots":["."],"exclude_dirs":["third_party_repos","seed_checkpoints",".git","__pycache__","node_modules","venv",".venv"]},"audit":{"roots":["third_party_repos"],"exclude_dirs":[".git","node_modules","venv",".venv"]}}}
def now(): return datetime.now().isoformat(timespec="seconds")
def settings():
    if SETTINGS.exists():
        try:
            d=DEFAULT.copy(); d.update(json.loads(SETTINGS.read_text(errors='ignore'))); d["version"]="v122.0.0"; return d
        except Exception: pass
    SETTINGS.write_text(json.dumps(DEFAULT,indent=4)); return DEFAULT.copy()
def index(mode="seed"):
    s=settings(); m=s["modes"].get(mode,s["modes"]["seed"]); rows=[]
    for root in m["roots"]:
        if not Path(root).exists(): continue
        for p in Path(root).rglob("*"):
            try:
                if set(p.parts)&set(m.get("exclude_dirs",[])): continue
                if not p.is_file() or p.suffix not in set(s["extensions"]) or p.stat().st_size>int(s["max_file_kb"])*1024: continue
                txt=p.read_text(errors='ignore'); n=int(s["chunk_chars"])
                for i in range(0,len(txt),n): rows.append({"mode":mode,"path":str(p),"chunk":i//n,"text":txt[i:i+n],"modified_at":datetime.fromtimestamp(p.stat().st_mtime).isoformat(timespec='seconds'),"indexed_at":now()})
            except Exception: pass
    INDEX.write_text("\n".join(json.dumps(r,ensure_ascii=False) for r in rows)+("\n" if rows else "")); return {"ok":True,"version":"v122.0.0","mode":mode,"chunks":len(rows)}
def rows():
    if not INDEX.exists(): return []
    out=[]
    for l in INDEX.read_text(errors='ignore').splitlines():
        try: out.append(json.loads(l))
        except Exception: pass
    return out
def search(q,limit=10):
    terms=[x for x in re.sub(r"[^a-z0-9çğıöşü\s]"," ",q.lower()).split() if len(x)>1]; hits=[]
    for r in rows():
        hay=(r["path"]+" "+r["text"]).lower(); sc=sum(hay.count(t) for t in terms)
        if sc>0: hits.append({"score":sc,"source":f"{r['path']}#chunk={r['chunk']}","preview":r["text"][:450],"modified_at":r["modified_at"]})
    return sorted(hits,key=lambda x:x["score"],reverse=True)[:int(limit)]
def status():
    rs=rows(); by={}
    for r in rs: by[r.get("mode","unknown")]=by.get(r.get("mode","unknown"),0)+1
    return {"created_at":now(),"version":"v122.0.0","ok":True,"chunks":len(rs),"by_mode":by,"settings":settings()}
if __name__=="__main__":
    import sys
    a=sys.argv[1] if len(sys.argv)>1 else "status"
    print(json.dumps(index(sys.argv[2] if len(sys.argv)>2 else "seed") if a=="index" else search(" ".join(sys.argv[2:])) if a=="search" else status(),indent=4,ensure_ascii=False))
