import json,re
from datetime import datetime
SENSITIVE={'health','medical','religion','politics','address','password','token','api key'}
def now(): return datetime.now().isoformat(timespec="seconds")
def domain(t):
    s=set(re.sub(r"[^a-z0-9\s]"," ",str(t).lower()).split())
    if s & {'seed','memory','wake','dashboard','operator','rag'}: return 'seed'
    if s & {'pain','doctor','medical','heart'}: return 'health'
    return 'general'
def gate_memory(m,q):
    md=domain(m.get("summary","")+" "+" ".join(m.get("tags",[]))); qd=domain(q); sens=[x for x in SENSITIVE if x in m.get("summary","").lower()]; allowed=not(sens and md!=qd) and float(m.get("trust",0.5))>=0.35 and not m.get("forgotten")
    return {"allowed":allowed,"domain":qd,"memory_domain":md,"sensitive":sens}
def retrieve(q,limit=12):
    import seed_memory_garden3_v112 as mg
    out=[]
    for h in mg.search(q,limit*3):
        g=gate_memory(h["memory"],q)
        if g["allowed"]: out.append({"score":h["score"],"gate":g,"memory":h["memory"]})
        if len(out)>=limit: break
    return out
def test():
    return {"ok":gate_memory({"summary":"Seed dashboard green","trust":.9},"seed")["allowed"] and not gate_memory({"summary":"medical pain note health","trust":.9},"seed")["allowed"]}
def status(): return {"created_at":now(),"version":"v113.0.0","ok":True,"test":test()}
if __name__=="__main__":
    import sys; print(json.dumps(retrieve(" ".join(sys.argv[2:])) if len(sys.argv)>1 and sys.argv[1]=="retrieve" else test() if len(sys.argv)>1 and sys.argv[1]=="test" else status(),indent=4,ensure_ascii=False))
