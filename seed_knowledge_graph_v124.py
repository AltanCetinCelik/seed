import json,time
from pathlib import Path
from datetime import datetime
KG=Path("seed_knowledge_graph_v124.jsonl")
def now(): return datetime.now().isoformat(timespec="seconds")
def read():
    if not KG.exists(): return []
    out=[]
    for l in KG.read_text(errors="ignore").splitlines():
        try: out.append(json.loads(l))
        except Exception: pass
    return out
def add(s,p,o,source="manual",trust=.8):
    row={"triple_id":f"kg_{int(time.time()*1000)}","subject":s,"predicate":p,"object":o,"source":source,"trust":trust,"created_at":now(),"version":"v124.0.0"}
    with KG.open("a") as f: f.write(json.dumps(row,ensure_ascii=False)+"\n")
    return {"ok":True,"triple":row}
def bootstrap():
    base=[("Seed","has_module","Deep Research v123"),("Seed","has_module","Knowledge Graph v124"),("Seed","routes_tasks_with","Device Router v125"),("Pi Satellite","role","room wake/listen"),("Windows Worker","role","heavy GPU worker"),("Risky Action","requires","Approval Center")]
    old={(x.get("subject"),x.get("predicate"),x.get("object")) for x in read()}; n=0
    for s,p,o in base:
        if (s,p,o) not in old: add(s,p,o,"bootstrap",.9); n+=1
    return n
def search(q):
    q=q.lower(); return [x for x in read() if q in json.dumps(x,ensure_ascii=False).lower()][:50]
def dot():
    lines=["digraph SeedKG {"]
    for t in read(): lines.append(f'"{t.get("subject")}" -> "{t.get("object")}" [label="{t.get("predicate")}"];')
    lines.append("}"); Path("seed_knowledge_graph_v124.dot").write_text("\n".join(lines)); return {"ok":True,"path":"seed_knowledge_graph_v124.dot","triples":len(read())}
def status():
    bootstrap(); return {"created_at":now(),"version":"v124.0.0","ok":True,"triples":len(read()),"latest":read()[-8:]}
if __name__=="__main__":
    import sys
    a=sys.argv[1] if len(sys.argv)>1 else "status"
    if a=="add": print(json.dumps(add(sys.argv[2],sys.argv[3]," ".join(sys.argv[4:])),indent=4,ensure_ascii=False))
    elif a=="search": print(json.dumps(search(" ".join(sys.argv[2:])),indent=4,ensure_ascii=False))
    elif a=="dot": print(json.dumps(dot(),indent=4,ensure_ascii=False))
    else: print(json.dumps(status(),indent=4,ensure_ascii=False))
