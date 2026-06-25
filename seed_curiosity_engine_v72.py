import json
from datetime import datetime
from pathlib import Path
OUT=Path("seed_curiosity_v72.json")
def now(): return datetime.now().isoformat(timespec="seconds")
def generate_curiosities(user_message=""):
    items=[]
    def add(title,body,cat,why,score): items.append({"title":title,"body":body,"category":cat,"why":why,"relevance_score":score})
    try:
        from seed_memory_review_inbox_v64 import build_inbox
        p=build_inbox().get("pending",0)
        if p>0: add("Review memory candidates",f"There are {p} pending memory candidates. This directly improves Seed continuity.","memory","Seed noticed pending memory review.",9)
    except Exception: pass
    try:
        from seed_avatar_state_v72 import compute_avatar_state
        a=compute_avatar_state(); add("Avatar state is ready",f"Avatar mood is {a.get('mood')} because: {a.get('reason')}","avatar","Avatar can reflect real system state.",7)
    except Exception: pass
    try:
        from seed_repo_pattern_extractor_v72 import build_repo_patterns
        p=build_repo_patterns(); add("Convert repo patterns into real features",f"{len(p.get('patterns',[]))} pattern groups are ready from Hermes/Moltbot/OpenClaw.","repo","Repo fusion should become actionable features.",8)
    except Exception: pass
    add("Protect the build rhythm","Because Seed is green, work in checkpoints, commit after wins, and avoid adding huge models until storage is checked.","life","Relevant to Altan's current Seed work and Mac storage.",6)
    data={"created_at":now(),"version":"v72.0.0","ok":True,"items":sorted(items,key=lambda x:x["relevance_score"], reverse=True)}
    OUT.write_text(json.dumps(data,indent=4,ensure_ascii=False)); return data
def best_curiosity(user_message=""):
    xs=generate_curiosities(user_message).get("items",[])
    return xs[0] if xs else {"title":"No strong curiosity","body":"Nothing urgent.","category":"none","why":"No signal.","relevance_score":0}
def show_curiosity():
    print("\n=== SEED CURIOSITY v72 ===")
    for x in generate_curiosities()["items"]:
        print(f"- {x['title']} [{x['category']}] score={x['relevance_score']}\n  {x['body']}\n  why: {x['why']}")
if __name__ == "__main__": show_curiosity()
