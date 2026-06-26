import json, os, signal, subprocess, sys, time
from pathlib import Path
from datetime import datetime
import seed_output_compactor_v1371 as compactor

VERSION = "v137.1.1"
EVENTS = Path("seed_service_supervisor_v1371_events.jsonl")
STATE = Path("seed_service_supervisor_v1371_state.json")

SERVICES = {
    "voice_runtime": {"script": "seed_voice_runtime_v136.py", "start": ["start", "--no-speak"], "stop": ["stop"], "status": ["status"], "required": True, "compact": True},
    "approval_autopilot": {"script": "seed_approval_autopilot_v13623.py", "start": ["start"], "stop": ["stop"], "status": ["status"], "required": True, "compact": False},
    "companion": {"script": "seed_companion_v137.py", "start": ["start"], "stop": ["stop"], "status": ["status"], "required": True, "compact": False},
    "dashboard": {"script": "seed_dashboard_v106.py", "start": ["start"], "stop": ["stop"], "status": ["status"], "required": False, "compact": False},
    "avatar": {"script": "seed_avatar2_v129.py", "start": ["start"], "stop": ["stop"], "status": ["status"], "required": False, "compact": False},
    "proactive": {"script": "seed_proactive_rhythm_v108.py", "start": ["start"], "stop": ["stop"], "status": ["status"], "required": False, "compact": False},
}

def now():
    return datetime.now().isoformat(timespec="seconds")

def event(row):
    row.setdefault("created_at", now())
    row.setdefault("version", VERSION)
    with EVENTS.open("a") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row

def run(cmd, timeout=60, compact=False):
    try:
        p=subprocess.run(cmd,capture_output=True,text=True,timeout=timeout)
        if compact:
            data = compactor.compact(p.stdout, p.stderr, p.returncode, {"cmd": cmd, "supervisor": True, "version": VERSION})
            # Supervisor must stay tiny. Full raw is archived by compactor.
            return {"ok":p.returncode==0,"returncode":p.returncode,"data":data,"stdout_bytes":len(p.stdout or ""),"stderr_tail":(p.stderr or "")[-500:]}
        data=None
        if p.stdout.strip():
            try: data=json.loads(p.stdout)
            except Exception: data={"raw":p.stdout.strip()[-1200:]}
        return {"ok":p.returncode==0,"returncode":p.returncode,"stdout":p.stdout[-1200:],"stderr":p.stderr[-700:],"data":data,"stdout_bytes":len(p.stdout or "")}
    except Exception as e:
        return {"ok":False,"error":str(e)}

def py(script,*args):
    return [sys.executable,script,*args]

def service_call(name, action):
    spec=SERVICES[name]
    if not Path(spec["script"]).exists():
        return {"ok": False, "missing": spec["script"]}
    return run(py(spec["script"], *spec[action]), compact=(action=="status" and spec.get("compact")))

def service_alive_from_status(res):
    data=res.get("data") if isinstance(res,dict) else None
    if isinstance(data,dict):
        if data.get("alive") is True:
            return True
        if data.get("ok") is True and data.get("pid"):
            return True
        if data.get("already_running") is True:
            return True
        # compacted voice runtime status
        if data.get("ok") is True and ("Seed status" in str(data.get("answer","")) or data.get("returncode") == 0):
            return True
    return False

def tiny_service_row(name, res):
    data = res.get("data") if isinstance(res, dict) else None
    row = {
        "ok": bool(res.get("ok")) if isinstance(res, dict) else False,
        "alive": service_alive_from_status(res),
        "required": SERVICES[name]["required"],
        "stdout_bytes": res.get("stdout_bytes") if isinstance(res, dict) else None,
    }
    if isinstance(data, dict):
        row["pid"] = data.get("pid")
        row["url"] = data.get("url")
        row["answer"] = data.get("answer")
        row["intent"] = data.get("intent")
        row["full_output_file"] = data.get("full_output_file")
        if isinstance(data.get("state"), dict):
            row["state_alive"] = data["state"].get("alive")
    return row

def status(full=False):
    rows={}
    compact_rows={}
    for name in SERVICES:
        res=service_call(name,"status")
        rows[name]={"status":res,"alive":service_alive_from_status(res),"required":SERVICES[name]["required"]}
        compact_rows[name]=tiny_service_row(name,res)
    required_ok=all(v["alive"] for k,v in rows.items() if v["required"])
    state={"created_at":now(),"version":VERSION,"ok":True,"required_ok":required_ok,"services":rows if full else compact_rows}
    STATE.write_text(json.dumps(state,indent=4,ensure_ascii=False))
    return state

def start(all_services=False):
    actions=[]
    order=["voice_runtime","approval_autopilot","dashboard","avatar","proactive","companion"] if all_services else ["voice_runtime","approval_autopilot","companion"]
    for name in order:
        if name in SERVICES:
            res=service_call(name,"start")
            actions.append({"service":name,"ok":res.get("ok"),"data":res.get("data")})
    event({"event":"start","all_services":all_services,"actions":actions})
    return {"ok":True,"actions":actions,"status":status()}

def stop(all_services=False):
    actions=[]
    order=["companion","approval_autopilot","voice_runtime","proactive","avatar","dashboard"] if all_services else ["companion","approval_autopilot","voice_runtime"]
    for name in order:
        if name in SERVICES:
            res=service_call(name,"stop")
            actions.append({"service":name,"ok":res.get("ok"),"data":res.get("data")})
    event({"event":"stop","all_services":all_services,"actions":actions})
    return {"ok":True,"actions":actions,"status":status()}

def heal():
    st=status()
    actions=[]
    for name,row in st["services"].items():
        if SERVICES[name]["required"] and not row.get("alive"):
            res=service_call(name,"start")
            actions.append({"service":name,"action":"restart","ok":res.get("ok"),"data":res.get("data")})
    after=status()
    event({"event":"heal","actions":actions,"required_ok_after":after.get("required_ok")})
    return {"ok":True,"actions":actions,"after":after}

def text(st):
    lines = ["Seed Service Supervisor v137.1.1", f"Required OK: {st.get('required_ok')}"]
    for name,row in st.get("services",{}).items():
        lines.append(f"- {name}: alive={row.get('alive')} ok={row.get('ok')} pid={row.get('pid')}")
    return "\n".join(lines)

def test():
    return {"ok":True,"start":start(False),"heal":heal(),"status":status()}

if __name__=="__main__":
    cmd=sys.argv[1] if len(sys.argv)>1 else "status"
    as_json = "--json" in sys.argv
    if cmd=="start":
        out=start("--all" in sys.argv)
    elif cmd=="stop":
        out=stop("--all" in sys.argv)
    elif cmd=="heal":
        out=heal()
    elif cmd=="test":
        out=test()
    elif cmd=="status-full":
        out=status(full=True)
    else:
        out=status()
    if as_json or cmd in {"start","stop","heal","test","status-full"}:
        print(json.dumps(out,indent=4,ensure_ascii=False))
    else:
        print(text(out))
