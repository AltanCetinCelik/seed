import json
from pathlib import Path
from datetime import datetime
REPO=Path("third_party_repos/odysseus"); MD=Path("seed_odysseus_lessons_v120.md")
def now(): return datetime.now().isoformat(timespec="seconds")
def audit():
    lessons=[]; files=[]
    if REPO.exists():
        for n in ["README.md","ROADMAP.md","SECURITY.md","THREAT_MODEL.md"]:
            p=REPO/n
            if p.exists():
                t=p.read_text(errors='ignore')[:6000].lower(); files.append(str(p))
                if "security" in t or "threat" in t: lessons.append("Use Odysseus threat/security ideas for Seed tool approval.")
                if "mcp" in t: lessons.append("Keep MCP whitelist + approval only.")
                if "research" in t: lessons.append("Research flow can inspire Seed deep research.")
    else: lessons.append("Odysseus not cloned yet; audit-only clone later.")
    data={"created_at":now(),"version":"v120.0.0","ok":True,"repo_exists":REPO.exists(),"files":files,"lessons":sorted(set(lessons))}; MD.write_text("# Seed v120 Odysseus Audit\n"+"\n".join("- "+x for x in data["lessons"])+"\n"); return data
def status(): return audit()
if __name__=="__main__":
    import json; print(json.dumps(audit(),indent=4,ensure_ascii=False))
