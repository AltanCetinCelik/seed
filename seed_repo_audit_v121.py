import json
from pathlib import Path
from datetime import datetime
ROOT=Path("third_party_repos"); MD=Path("seed_repo_audit_v121.md")
TARGETS=["screen-voice-agent","openWakeWord","whisper.cpp","piper","mem0","letta","leon","nanobot","mac-echo","OpenBlob","skales","QwenPaw","ora","PikoChan","odysseus"]
def now(): return datetime.now().isoformat(timespec="seconds")
def audit_repo(p):
    txt=""; rs=list(p.glob("README*"))
    if rs:
        try: txt=rs[0].read_text(errors='ignore')[:3000]
        except Exception: pass
    low=(txt+" "+p.name).lower(); cats=[c for k,c in [("wake","wake"),("voice","voice"),("memory","memory"),("mcp","mcp"),("desktop","desktop"),("agent","agent"),("research","research")] if k in low]
    return {"name":p.name,"path":str(p),"categories":cats,"has_readme":bool(rs)}
def audit():
    repos=[audit_repo(p) for p in ROOT.iterdir() if p.is_dir()] if ROOT.exists() else []
    missing=[x for x in TARGETS if not any(x.lower() in r["name"].lower() for r in repos)]
    data={"created_at":now(),"version":"v121.0.0","ok":True,"repo_count":len(repos),"repos":repos,"missing_priority_repos":missing}
    MD.write_text("# Seed v121 Repo Audit\n\n"+"\n".join("- "+r["name"]+": "+(",".join(r["categories"]) or "uncategorized") for r in repos)+"\n"); return data
def status(): return audit()
if __name__=="__main__":
    import json; print(json.dumps(audit(),indent=4,ensure_ascii=False))
