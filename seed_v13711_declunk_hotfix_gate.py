import json, subprocess, sys
from pathlib import Path
from datetime import datetime

MODULES=[
    "seed_runtime_proxy_v1371.py",
    "seed_service_supervisor_v1371.py",
    "seed_companion_v1371.py",
    "seed_v13711_declunk_hotfix_gate.py"
]

def now():
    return datetime.now().isoformat(timespec="seconds")

def comp(m):
    p=subprocess.run([sys.executable,"-m","py_compile",m],capture_output=True,text=True,timeout=30)
    return {"module":m,"ok":p.returncode==0,"stderr":p.stderr[-1000:]}

def run(cmd,timeout=180):
    p=subprocess.run(cmd,capture_output=True,text=True,timeout=timeout)
    data=None
    if p.stdout.strip():
        try: data=json.loads(p.stdout)
        except Exception: data={"raw":p.stdout.strip()[-1600:]}
    return {"ok":p.returncode==0,"stdout":p.stdout[-2000:],"stderr":p.stderr[-1000:],"data":data,"stdout_bytes":len(p.stdout or "")}

def run_gate():
    checks=[comp(m) for m in MODULES]
    modules_ok=all(c["ok"] for c in checks)
    details={}
    proxy_ok=False; supervisor_ok=False; companion_ok=False
    try:
        details["proxy"]=run([sys.executable,"seed_runtime_proxy_v1371.py","wake-text","status","--json"],240)
        d=details["proxy"].get("data") or {}
        proxy_ok=details["proxy"].get("ok") and d.get("answer")=="Seed status: 8/8 systems green." and "--json" not in str(d.get("transcript",""))
    except Exception as e:
        details["proxy_error"]=str(e)
    try:
        details["supervisor"]=run([sys.executable,"seed_service_supervisor_v1371.py","status","--json"],180)
        supervisor_ok=details["supervisor"].get("ok") and details["supervisor"].get("stdout_bytes",999999) < 20000
    except Exception as e:
        details["supervisor_error"]=str(e)
    try:
        details["companion"]=run([sys.executable,"seed_companion_v1371.py","test"],300)
        d=details["companion"].get("data") or {}
        companion_ok=details["companion"].get("ok") and d.get("transcript_clean") is True
    except Exception as e:
        details["companion_error"]=str(e)
    report={
        "created_at":now(),"version":"v137.1.1",
        "ready":modules_ok and proxy_ok and supervisor_ok and companion_ok,
        "modules_ok":modules_ok,"proxy_ok":proxy_ok,"supervisor_ok":supervisor_ok,"companion_ok":companion_ok,
        "checks":checks,"details":details
    }
    Path("seed_v13711_declunk_hotfix_gate_report.json").write_text(json.dumps(report,indent=4,ensure_ascii=False))
    return report

def show():
    r=run_gate()
    print("\n=== SEED v137.1.1 DE-CLUNK HOTFIX GATE ===")
    print(f"Ready: {r['ready']}")
    print(f"Modules OK: {r['modules_ok']}")
    print(f"Proxy Clean OK: {r['proxy_ok']}")
    print(f"Supervisor Compact OK: {r['supervisor_ok']}")
    print(f"Companion Clean OK: {r['companion_ok']}")
    try:
        d=r["details"]["proxy"]["data"]
        print("Answer:", d.get("answer"))
        print("Transcript:", d.get("transcript"))
    except Exception:
        pass

if __name__=="__main__":
    show()
