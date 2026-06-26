import json, subprocess, sys
from pathlib import Path
from datetime import datetime

MODULES=["seed_companion_v137.py","seed_companion_panel_v137.py","seed_v137_companion_gate.py"]

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
        import seed_companion_v137 as c
        test=c.test()
        st=c.status()
        details["companion_test"]=test
        details["companion_status"]=st
        companion_ok=test.get("ok") is True and test.get("wake_good",{}).get("matched") is True and test.get("wake_bad",{}).get("matched") is False
    except Exception as e:
        companion_ok=False; details["companion_error"]=str(e)
    try:
        import seed_companion_panel_v137 as p
        ps=p.status()
        details["panel_status"]=ps
        panel_ok=ps.get("ok") is True
    except Exception as e:
        panel_ok=False; details["panel_error"]=str(e)
    try:
        if Path("seed_hygiene_status_v13623.py").exists():
            p=subprocess.run([sys.executable,"seed_hygiene_status_v13623.py","--json"],capture_output=True,text=True,timeout=60)
            data=json.loads(p.stdout) if p.stdout.strip() else {}
            details["hygiene"]=data.get("hygiene_v13623") or data.get("hygiene")
            hygiene_ok=p.returncode==0
        else:
            hygiene_ok=False; details["hygiene_error"]="missing seed_hygiene_status_v13623.py"
    except Exception as e:
        hygiene_ok=False; details["hygiene_error"]=str(e)
    report={
        "created_at":now(),
        "version":"v137.0.0",
        "ready":modules_ok and companion_ok and panel_ok and hygiene_ok,
        "modules_ok":modules_ok,
        "companion_ok":companion_ok,
        "panel_ok":panel_ok,
        "hygiene_ok":hygiene_ok,
        "checks":checks,
        "details":details
    }
    Path("seed_v137_companion_gate_report.json").write_text(json.dumps(report,indent=4,ensure_ascii=False))
    return report

def show():
    r=run_gate()
    print("\n=== SEED v137 REAL WAKE / ALWAYS-ON COMPANION GATE ===")
    print(f"Ready: {r['ready']}")
    print(f"Modules OK: {r['modules_ok']}")
    print(f"Companion OK: {r['companion_ok']}")
    print(f"Panel OK: {r['panel_ok']}")
    print(f"Hygiene OK: {r['hygiene_ok']}")
    try:
        h=r["details"].get("hygiene") or {}
        print(f"Hygiene score: {h.get('score')}/100")
    except Exception:
        pass

if __name__=="__main__":
    show()
