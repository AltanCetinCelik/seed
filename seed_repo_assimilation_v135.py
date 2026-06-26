import json
from pathlib import Path
from datetime import datetime
ROOT=Path("third_party_repos")
REPORT=Path("seed_repo_assimilation_v135_report.json")
LESSONS=Path("seed_repo_assimilation_v135_lessons.jsonl")
TARGETS=["openWakeWord","whisper.cpp","piper","mem0","odysseus","screen-voice-agent","leon","nanobot"]
def now(): return datetime.now().isoformat(timespec="seconds")
def write(row):
    row.setdefault("created_at",now()); row.setdefault("version","v135.0.0")
    with LESSONS.open("a") as f: f.write(json.dumps(row,ensure_ascii=False)+"\n")
def readme(repo):
    text=""
    for p in list(repo.glob("README*"))[:2]+list(repo.glob("docs/**/*.md"))[:3]:
        try: text += "\n# "+str(p)+"\n"+p.read_text(errors="ignore")[:5000]
        except Exception: pass
    return text
def cats(name,text):
    low=(name+" "+text).lower(); out=[]
    for k,c in [("wake","wake"),("whisper","stt"),("speech","voice"),("tts","tts"),("memory","memory"),("mcp","tools"),("desktop","desktop"),("agent","agent"),("research","research"),("security","security")]:
        if k in low: out.append(c)
    return sorted(set(out))
def lessons(name,categories):
    out=[]
    if "wake" in categories: out.append("Use for v132 wake, but keep v107 fallback and false-positive log.")
    if "stt" in categories: out.append("Use for v131 voice input, but keep no-raw-audio defaults.")
    if "tts" in categories: out.append("Use for local TTS only after model path is configured.")
    if "memory" in categories: out.append("Compare with Memory Garden 3 and Memory Gate before importing design ideas.")
    if "agent" in categories or "tools" in categories: out.append("Any tool execution pattern must pass Safety Ledger and Approval Center.")
    if not out: out.append("Audit manually before using; no automatic integration.")
    return out
def audit():
    ROOT.mkdir(exist_ok=True); repos=[p for p in ROOT.iterdir() if p.is_dir()]; rows=[]; missing=[]
    for target in TARGETS:
        repo=next((p for p in repos if target.lower() in p.name.lower()),None)
        if not repo: missing.append(target); continue
        text=readme(repo); cs=cats(repo.name,text); ls=lessons(repo.name,cs)
        item={"repo":repo.name,"path":str(repo),"categories":cs,"lessons":ls,"has_readme":bool(text)}
        rows.append(item)
        for lesson in ls: write({"repo":repo.name,"category":cs,"lesson":lesson})
    rep={"created_at":now(),"version":"v135.0.0","ok":True,"audited":len(rows),"missing":missing,"repos":rows}
    REPORT.write_text(json.dumps(rep,indent=4,ensure_ascii=False)); return rep
def promote():
    try: import seed_memory_garden3_v112 as mem
    except Exception as e: return {"ok":False,"error":str(e)}
    count=0
    if LESSONS.exists():
        for l in LESSONS.read_text(errors="ignore").splitlines():
            try:
                row=json.loads(l); mem.add("project",f"Repo lesson from {row.get('repo')}: {row.get('lesson')}",tags=["repo_audit","v135",row.get("repo","")],source="seed_repo_assimilation_v135",trust=.78); count+=1
            except Exception: pass
    return {"ok":True,"promoted":count}
def status(): return {"created_at":now(),"version":"v135.0.0","ok":True,"report":audit(),"lesson_count":len(LESSONS.read_text(errors='ignore').splitlines()) if LESSONS.exists() else 0}
if __name__=="__main__":
    import sys
    a=sys.argv[1] if len(sys.argv)>1 else "status"
    if a=="audit": print(json.dumps(audit(),indent=4,ensure_ascii=False))
    elif a=="promote": print(json.dumps(promote(),indent=4,ensure_ascii=False))
    else: print(json.dumps(status(),indent=4,ensure_ascii=False))
