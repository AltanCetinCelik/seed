import json, subprocess, sys
from pathlib import Path
from datetime import datetime

MODULES=[
    "seed_output_compactor_v1371.py",
    "seed_runtime_proxy_v1371.py",
    "seed_log_optimizer_v1371.py",
    "seed_service_supervisor_v1371.py",
    "seed_clunkiness_audit_v1371.py",
    "seed_companion_v1371.py",
    "seed_v1371_optimization_gate.py"
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
        except Exception: data={"raw":p.stdout.strip()[-2000:]}
    return {"ok":p.returncode==0,"stdout":p.stdout[-3000:],"stderr":p.stderr[-1000:],"data":data}

def run_gate():
    checks=[comp(m) for m in MODULES]
    modules_ok=all(c["ok"] for c in checks)
    details={}
    proxy_ok=False; supervisor_ok=False; audit_ok=False; companion_ok=False
    try:
        details["proxy"]=run([sys.executable,"seed_runtime_proxy_v1371.py","wake-text","status","--json"],240)
        proxy_ok=details["proxy"].get("ok") and isinstance(details["proxy"].get("data"),dict) and details["proxy"]["data"].get("answer") is not None
    except Exception as e:
        details["proxy_error"]=str(e)
    try:
        details["supervisor"]=run([sys.executable,"seed_service_supervisor_v1371.py","heal"],180)
        supervisor_ok=details["supervisor"].get("ok")
    except Exception as e:
        details["supervisor_error"]=str(e)
    try:
        details["audit"]=run([sys.executable,"seed_clunkiness_audit_v1371.py","--json"],240)
        audit_ok=details["audit"].get("ok")
    except Exception as e:
        details["audit_error"]=str(e)
    try:
        details["companion"]=run([sys.executable,"seed_companion_v1371.py","optimize"],120)
        companion_ok=details["companion"].get("ok")
    except Exception as e:
        details["companion_error"]=str(e)
    report={
        "created_at":now(),"version":"v137.1.0",
        "ready":modules_ok and proxy_ok and supervisor_ok and audit_ok and companion_ok,
        "modules_ok":modules_ok,"proxy_ok":proxy_ok,"supervisor_ok":supervisor_ok,"audit_ok":audit_ok,"companion_ok":companion_ok,
        "checks":checks,"details":details
    }
    Path("seed_v1371_optimization_gate_report.json").write_text(json.dumps(report,indent=4,ensure_ascii=False))
    return report

def show():
    r=run_gate()
    print("\n=== SEED v137.1 BIG OPTIMIZATION / DE-CLUNK PACK GATE ===")
    print(f"Ready: {r['ready']}")
    print(f"Modules OK: {r['modules_ok']}")
    print(f"Proxy OK: {r['proxy_ok']}")
    print(f"Supervisor OK: {r['supervisor_ok']}")
    print(f"Audit OK: {r['audit_ok']}")
    print(f"Companion OK: {r['companion_ok']}")
    try:
        ans=(r["details"]["proxy"]["data"].get("answer") or "")[:140]
        print("Compact answer preview:", ans)
    except Exception:
        pass

if __name__=="__main__":
    show()
