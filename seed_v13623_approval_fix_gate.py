import json, subprocess, sys
from pathlib import Path
from datetime import datetime

MODULES=["seed_approval_resolver_v13623.py","seed_approval_autopilot_v13623.py","seed_hygiene_status_v13623.py","seed_v13623_approval_fix_gate.py"]

def now():
    return datetime.now().isoformat(timespec="seconds")

def comp(m):
    p=subprocess.run([sys.executable,"-m","py_compile",m],capture_output=True,text=True,timeout=30)
    return {"module":m,"ok":p.returncode==0,"stderr":p.stderr[-1000:]}

def run_gate():
    checks=[comp(m) for m in MODULES]
    modules_ok=all(c["ok"] for c in checks)
    details={}
    try:
        import seed_approval_resolver_v13623 as r
        rt=r.test()
        details["resolver_test"]=rt
        resolver_ok=rt.get("ok") is True
    except Exception as e:
        resolver_ok=False; details["resolver_error"]=str(e)
    try:
        import seed_approval_autopilot_v13623 as a
        at=a.test()
        details["autopilot_test"]=at
        autopilot_ok=at.get("ok") is True
    except Exception as e:
        autopilot_ok=False; details["autopilot_error"]=str(e)
    try:
        import seed_hygiene_status_v13623 as h
        hs=h.scan()
        details["hygiene_status"]={"hygiene_v13623":hs.get("hygiene_v13623"),"approval_v13623":hs.get("approval_v13623")}
        hygiene_ok="hygiene_v13623" in hs
    except Exception as e:
        hygiene_ok=False; details["hygiene_error"]=str(e)
    report={"created_at":now(),"version":"v136.2.3","ready":modules_ok and resolver_ok and autopilot_ok and hygiene_ok,"modules_ok":modules_ok,"resolver_ok":resolver_ok,"autopilot_ok":autopilot_ok,"hygiene_ok":hygiene_ok,"checks":checks,"details":details}
    Path("seed_v13623_approval_fix_gate_report.json").write_text(json.dumps(report,indent=4,ensure_ascii=False))
    return report

def show():
    r=run_gate()
    print("\n=== SEED v136.2.3 APPROVAL LOOP FIX GATE ===")
    print(f"Ready: {r['ready']}")
    print(f"Modules OK: {r['modules_ok']}")
    print(f"Resolver OK: {r['resolver_ok']}")
    print(f"Autopilot OK: {r['autopilot_ok']}")
    print(f"Hygiene Status OK: {r['hygiene_ok']}")
    try:
        eff=r["details"]["hygiene_status"]["approval_v13623"]
        hyg=r["details"]["hygiene_status"]["hygiene_v13623"]
        print(f"Effective approvals pending: {eff.get('effective_pending_count')}")
        print(f"Raw approvals pending: {eff.get('raw_pending_count')}")
        print(f"Effective hygiene score: {hyg.get('score')}/100")
    except Exception:
        pass

if __name__=="__main__":
    show()
