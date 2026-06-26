import json, subprocess, sys
from pathlib import Path
from datetime import datetime
REG=Path("seed_skill_registry2_v118.json")
def now(): return datetime.now().isoformat(timespec="seconds")
def risk(n):
    n=n.lower(); return "risky" if any(x in n for x in ["delete","shell","operator","mcp","email","write"]) else "safe" if any(x in n for x in ["open","speak","screenshot"]) else "observe"
def discover():
    skills=[]
    if Path("seed_skills").exists():
        for p in Path("seed_skills").rglob("*.json"):
            try:
                d=json.loads(p.read_text(errors='ignore')); skills.append({"id":d.get("id",p.stem),"name":d.get("name",p.stem),"path":str(p),"risk":d.get("risk",risk(d.get("name",p.stem)))})
            except Exception as e: skills.append({"id":p.stem,"path":str(p),"risk":"unknown","error":str(e)})
    for p in Path(".").glob("seed_*_v*.py"): skills.append({"id":p.stem,"name":p.stem,"path":str(p),"risk":risk(p.stem)})
    data={"created_at":now(),"version":"v118.0.0","ok":True,"count":len(skills),"skills":skills}; REG.write_text(json.dumps(data,indent=4,ensure_ascii=False)); return data
def status():
    if not REG.exists(): return discover()
    try: return json.loads(REG.read_text(errors='ignore'))
    except Exception: return discover()
if __name__=="__main__":
    import sys; print(json.dumps(discover() if len(sys.argv)>1 and sys.argv[1]=="discover" else status(),indent=4,ensure_ascii=False))
