import json,subprocess,sys
from datetime import datetime
from pathlib import Path
ROOT=Path("third_party_repos")
REPOS={"screen-voice-agent":"https://github.com/sambuild04/screen-voice-agent.git","openWakeWord":"https://github.com/dscripka/openWakeWord.git","whisper.cpp":"https://github.com/ggml-org/whisper.cpp.git","piper":"https://github.com/rhasspy/piper.git","mem0":"https://github.com/mem0ai/mem0.git","leon":"https://github.com/leon-ai/leon.git","nanobot":"https://github.com/HKUDS/nanobot.git","odysseus":"https://github.com/pewdiepie-archdaemon/odysseus.git"}
def now(): return datetime.now().isoformat(timespec="seconds")
def plan():
    ROOT.mkdir(exist_ok=True); rows=[]
    for name,url in REPOS.items():
        path=ROOT/name; rows.append({"name":name,"url":url,"path":str(path),"exists":path.exists(),"command":f"git clone --depth 1 {url} {path}"})
    return {"created_at":now(),"version":"v122.1.0","ok":True,"repos":rows,"note":"Audit-only shallow clones. No dependencies are installed."}
def clone(selected=None):
    ROOT.mkdir(exist_ok=True); selected=selected or list(REPOS); results=[]
    for name in selected:
        if name not in REPOS: results.append({"name":name,"ok":False,"error":"unknown repo"}); continue
        path=ROOT/name
        if path.exists(): results.append({"name":name,"ok":True,"already_exists":True,"path":str(path)}); continue
        try:
            p=subprocess.run(["git","clone","--depth","1",REPOS[name],str(path)],capture_output=True,text=True,timeout=240)
            results.append({"name":name,"ok":p.returncode==0,"returncode":p.returncode,"stdout":p.stdout[-1000:],"stderr":p.stderr[-1000:]})
        except Exception as e: results.append({"name":name,"ok":False,"error":str(e)})
    return {"created_at":now(),"version":"v122.1.0","ok":all(r.get("ok") for r in results),"results":results}
def status(): return plan()
if __name__=="__main__":
    a=sys.argv[1] if len(sys.argv)>1 else "status"
    if a=="clone":
        if "--yes" not in sys.argv: print(json.dumps({"ok":False,"error":"Refusing to clone without --yes","plan":plan()},indent=4,ensure_ascii=False))
        else: print(json.dumps(clone([x for x in sys.argv[2:] if x!="--yes"] or None),indent=4,ensure_ascii=False))
    else: print(json.dumps(status(),indent=4,ensure_ascii=False))
