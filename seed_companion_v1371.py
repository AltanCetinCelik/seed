import json, subprocess, sys, time
from pathlib import Path
from datetime import datetime

VERSION="v137.1.1"
EVENTS=Path("seed_companion_v1371_events.jsonl")

def now():
    return datetime.now().isoformat(timespec="seconds")

def event(row):
    row.setdefault("created_at",now())
    row.setdefault("version",VERSION)
    with EVENTS.open("a") as f:
        f.write(json.dumps(row,ensure_ascii=False)+"\n")
    return row

def run(cmd, timeout=120):
    try:
        p=subprocess.run(cmd,capture_output=True,text=True,timeout=timeout)
        data=None
        if p.stdout.strip():
            try: data=json.loads(p.stdout)
            except Exception: data={"raw":p.stdout.strip()[-1200:]}
        return {"ok":p.returncode==0,"returncode":p.returncode,"data":data,"stdout_tail":p.stdout[-1200:],"stderr_tail":p.stderr[-700:],"stdout_bytes":len(p.stdout or "")}
    except Exception as e:
        return {"ok":False,"error":str(e)}

def py(script,*args):
    return [sys.executable,script,*args]

def optimize_settings():
    changed={}
    if Path("seed_companion_v137_settings.json").exists():
        try:
            s=json.loads(Path("seed_companion_v137_settings.json").read_text(errors="ignore"))
        except Exception:
            s={}
    else:
        s={}
    defaults={
        "loop_interval_seconds":3,
        "cooldown_seconds":10,
        "audio_wake_enabled":False,
        "speak_default":False,
        "max_events":600,
        "auto_start_services":True,
        "start_autopilot":True,
        "start_voice_runtime":True,
    }
    for k,v in defaults.items():
        if s.get(k)!=v:
            changed[k]={"old":s.get(k),"new":v}
            s[k]=v
    s["version"]="v137.1.1_optimized_profile"
    Path("seed_companion_v137_settings.json").write_text(json.dumps(s,indent=4,ensure_ascii=False))
    event({"event":"optimize_settings","changed":changed})
    return {"ok":True,"changed":changed,"settings":s}

def start(panel=False, all_services=False):
    optimize_settings()
    if Path("seed_service_supervisor_v1371.py").exists():
        sup=run(py("seed_service_supervisor_v1371.py","start","--all" if all_services else ""))
    else:
        sup=run(py("seed_companion_v137.py","start"))
    pan=None
    if panel and Path("seed_companion_panel_v137.py").exists():
        pan=run(py("seed_companion_panel_v137.py","start"))
    out={"ok":True,"supervisor":sup.get("data") or sup,"panel":pan.get("data") if isinstance(pan,dict) else pan,"status":status()}
    event({"event":"start","panel":panel,"all_services":all_services})
    return out

def stop(all_services=False):
    if Path("seed_service_supervisor_v1371.py").exists():
        return run(py("seed_service_supervisor_v1371.py","stop","--all" if all_services else ""))
    return run(py("seed_companion_v137.py","stop"))

def ask(text):
    cleaned = " ".join([p for p in (text or "status").split() if p not in {"--json","--speak","--no-speak"}]) or "status"
    if Path("seed_runtime_proxy_v1371.py").exists():
        res=run(py("seed_runtime_proxy_v1371.py","wake-text",cleaned,"--json"),timeout=240)
        data = res.get("data") or res
        event({"event":"ask","text":cleaned,"ok":data.get("ok"),"answer_preview":str(data.get("answer",""))[:160]})
        return data
    if Path("seed_companion_v137.py").exists():
        run(py("seed_companion_v137.py","enqueue","wake up "+cleaned))
        time.sleep(3)
        return run(py("seed_companion_v137.py","status"))
    return {"ok":False,"error":"missing v137 runtime"}

def status():
    rows={}
    for script,args,name in [
        ("seed_service_supervisor_v1371.py",["status","--json"],"supervisor"),
        ("seed_companion_v137.py",["status"],"companion"),
        ("seed_hygiene_status_v13623.py",[],"hygiene"),
        ("seed_log_optimizer_v1371.py",["status"],"logs"),
    ]:
        if Path(script).exists():
            rows[name]=run(py(script,*args),timeout=90)
    return {"created_at":now(),"version":VERSION,"ok":True,"rows":rows}

def daily(apply_logs=False):
    out={"created_at":now(),"version":VERSION,"optimize_settings":optimize_settings()}
    if Path("seed_log_optimizer_v1371.py").exists():
        out["log_optimizer"]=run(py("seed_log_optimizer_v1371.py","apply" if apply_logs else "dry-run"))
    if Path("seed_service_supervisor_v1371.py").exists():
        out["heal"]=run(py("seed_service_supervisor_v1371.py","heal"))
    if Path("seed_clunkiness_audit_v1371.py").exists():
        out["audit"]=run(py("seed_clunkiness_audit_v1371.py","--json"),timeout=240)
    event({"event":"daily","ok":True,"apply_logs":apply_logs})
    return out

def test():
    a = ask("status")
    transcript_clean = "--json" not in str(a.get("transcript",""))
    return {"ok":True,"transcript_clean":transcript_clean,"optimize":optimize_settings(),"ask":a,"daily":daily(False)}

if __name__=="__main__":
    args=sys.argv[1:]
    cmd=args[0] if args else "status"
    if cmd=="start":
        print(json.dumps(start(panel="--panel" in args, all_services="--all" in args),indent=4,ensure_ascii=False))
    elif cmd=="stop":
        print(json.dumps(stop(all_services="--all" in args),indent=4,ensure_ascii=False))
    elif cmd in {"ask","wake-text"}:
        print(json.dumps(ask(" ".join(args[1:]) or "status"),indent=4,ensure_ascii=False))
    elif cmd=="daily":
        print(json.dumps(daily(apply_logs="--apply-logs" in args),indent=4,ensure_ascii=False))
    elif cmd=="optimize":
        print(json.dumps(optimize_settings(),indent=4,ensure_ascii=False))
    elif cmd=="test":
        print(json.dumps(test(),indent=4,ensure_ascii=False))
    else:
        print(json.dumps(status(),indent=4,ensure_ascii=False))
