import json
from datetime import datetime
from pathlib import Path
OUT=Path("seed_repo_patterns_v72.json")
LIB={
 "hermes":{"tasks":["Turn repo skill patterns into Seed skill cards.","Add experience-to-memory promotion.","Add after-success/failure rituals."]},
 "moltbot":{"tasks":["Polish local web chat.","Prepare Telegram/Discord adapters later.","Add personality/channel tone rules."]},
 "openclaw":{"tasks":["Normalize tools as capability cards.","Add approval levels per action.","Map tools to Control Plane buttons."]}
}
def now(): return datetime.now().isoformat(timespec="seconds")
def build_repo_patterns():
    try:
        from seed_fusion_lab_clean_v602 import build_clean_fusion
        found={x.get("label"):x for x in build_clean_fusion().get("items",[])}
    except Exception: found={}
    patterns=[]
    for label,spec in LIB.items():
        repo=found.get(label,{})
        patterns.append({"label":label,"detected":bool(repo),"repo":repo.get("repo"),"takeaway":repo.get("takeaway","Not scanned."),"seed_native_tasks":spec["tasks"]})
    data={"created_at":now(),"version":"v72.0.0","ok":True,"patterns":patterns,"principle":"Extract patterns, do not clone repos."}
    OUT.write_text(json.dumps(data,indent=4,ensure_ascii=False)); return data
def show_repo_patterns():
    print("\n=== SEED REPO PATTERNS v72 ===")
    for p in build_repo_patterns()["patterns"]:
        print(f"- {p['label']} detected={p['detected']} takeaway={p['takeaway']}")
        for t in p["seed_native_tasks"]: print("  •",t)
if __name__ == "__main__": show_repo_patterns()
