import json, re, time, urllib.request
from pathlib import Path
from datetime import datetime
SESS=Path("seed_deep_research_v123_sessions.jsonl"); SRC=Path("seed_deep_research_v123_sources.jsonl"); CLAIM=Path("seed_deep_research_v123_claims.jsonl")
def now(): return datetime.now().isoformat(timespec="seconds")
def w(p,r):
    r.setdefault("created_at",now()); r.setdefault("version","v123.0.0")
    with p.open("a") as f: f.write(json.dumps(r,ensure_ascii=False)+"\n")
    return r
def rows(p):
    if not p.exists(): return []
    out=[]
    for l in p.read_text(errors="ignore").splitlines():
        try: out.append(json.loads(l))
        except Exception: pass
    return out
def create(topic):
    sid=f"research_{int(time.time()*1000)}"; return {"ok":True,"session":w(SESS,{"session_id":sid,"topic":topic,"status":"open","plan":["collect sources","extract claims","compare","brief","save findings"]})}
def add_source(sid,title,text,url="manual"):
    src=f"src_{int(time.time()*1000)}"; row=w(SRC,{"source_id":src,"session_id":sid,"title":title,"url":url,"text":text[:12000],"chars":len(text)})
    return {"ok":True,"source":{k:v for k,v in row.items() if k!="text"}}
def fetch_url(sid,url):
    try:
        data=urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"SeedResearch/123"}),timeout=20).read(600000).decode("utf-8","ignore")
        text=re.sub(r"<script.*?</script>|<style.*?</style>"," ",data,flags=re.I|re.S); text=re.sub(r"<[^>]+>"," ",text); text=re.sub(r"\s+"," ",text).strip()
        return add_source(sid,text[:90],text,url)
    except Exception as e: return {"ok":False,"error":str(e)}
def local_rag(sid,q):
    try:
        import seed_rag2_v122 as rag
        hits=rag.search(q,limit=8)
        for h in hits: add_source(sid,h["source"],h.get("preview",""),h["source"])
        return {"ok":True,"added":len(hits),"hits":hits}
    except Exception as e: return {"ok":False,"error":str(e)}
def extract(sid):
    n=0
    for s in [x for x in rows(SRC) if x.get("session_id")==sid]:
        for sent in re.split(r"(?<=[.!?])\s+",s.get("text","")):
            sent=sent.strip()
            if 70<=len(sent)<=260:
                w(CLAIM,{"claim_id":f"claim_{int(time.time()*1000)}_{n}","session_id":sid,"source_id":s["source_id"],"claim":sent,"confidence":"medium"}); n+=1
            if n>=18: break
    return {"ok":True,"extracted":n}
def brief(sid):
    srcs={s["source_id"]:s for s in rows(SRC) if s.get("session_id")==sid}
    lines=["# Seed Research Brief",""]
    for c in [x for x in rows(CLAIM) if x.get("session_id")==sid][:12]:
        s=srcs.get(c.get("source_id"),{}); lines.append(f"- {c.get('claim')} [source: {s.get('title') or s.get('url')}]")
    return "\n".join(lines)
def status(): return {"created_at":now(),"version":"v123.0.0","ok":True,"sessions":rows(SESS)[-10:],"sources":len(rows(SRC)),"claims":len(rows(CLAIM))}
if __name__=="__main__":
    import sys
    a=sys.argv[1] if len(sys.argv)>1 else "status"
    if a=="create": print(json.dumps(create(" ".join(sys.argv[2:])),indent=4,ensure_ascii=False))
    elif a=="fetch-url": print(json.dumps(fetch_url(sys.argv[2],sys.argv[3]),indent=4,ensure_ascii=False))
    elif a=="local-rag": print(json.dumps(local_rag(sys.argv[2]," ".join(sys.argv[3:])),indent=4,ensure_ascii=False))
    elif a=="extract": print(json.dumps(extract(sys.argv[2]),indent=4,ensure_ascii=False))
    elif a=="brief": print(brief(sys.argv[2]))
    else: print(json.dumps(status(),indent=4,ensure_ascii=False))
