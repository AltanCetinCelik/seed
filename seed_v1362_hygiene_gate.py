import json, subprocess, sys
from pathlib import Path
from datetime import datetime
MODULES=["seed_hygiene_center_v1362.py","seed_hygiene_panel_v1362.py","seed_daily_brief_v1362.py","seed_start_v1362.py","seed_v1362_hygiene_gate.py"]
def now(): return datetime.now().isoformat(timespec="seconds")
def comp(m):
    p=subprocess.run([sys.executable,"-m","py_compile",m],capture_output=True,text=True,timeout=30)
    return {"module":m,"ok":p.returncode==0,"stderr":p.stderr[-1000:]}
def run_gate():
    checks=[comp(m) for m in MODULES]; modules_ok=all(c["ok"] for c in checks); details={}
    try:
        import seed_hygiene_center_v1362 as h
        ht=h.test(); sc=h.scan(); details["hygiene_test"]=ht; details["scan_summary"]={"score":sc.get("hygiene"),"approval_pending":sc.get("approval",{}).get("pending_count"),"test_tasks":sc.get("tasks",{}).get("test_task_count"),"duplicate_memory_entries":sc.get("memory",{}).get("duplicate_count")}; hygiene_ok=ht.get("ok") is True and "hygiene" in sc
    except Exception as e: hygiene_ok=False; details["hygiene_test"]={"ok":False,"error":str(e)}
    try:
        import seed_daily_brief_v1362 as b
        br=b.brief(); details["brief"]=br; brief_ok=br.get("ok") is True and "Hygiene:" in br.get("text","")
    except Exception as e: brief_ok=False; details["brief"]={"ok":False,"error":str(e)}
    try:
        import seed_hygiene_panel_v1362 as p
        ps=p.status(); details["panel"]=ps; panel_ok=ps.get("ok") is True
    except Exception as e: panel_ok=False; details["panel"]={"ok":False,"error":str(e)}
    try:
        import seed_start_v1362 as s
        ss=s.status(); details["start_v1362"]=ss; start_ok=ss.get("ok") in {True,False} and "hygiene" in ss
    except Exception as e: start_ok=False; details["start_v1362"]={"ok":False,"error":str(e)}
    r={"created_at":now(),"version":"v136.2.0","ready":modules_ok and hygiene_ok and brief_ok and panel_ok and start_ok,"modules_ok":modules_ok,"hygiene_ok":hygiene_ok,"brief_ok":brief_ok,"panel_ok":panel_ok,"start_ok":start_ok,"checks":checks,"details":details}
    Path("seed_v1362_hygiene_gate_report.json").write_text(json.dumps(r,indent=4,ensure_ascii=False)); return r
def show():
    r=run_gate(); print("\n=== SEED v136.2 HYGIENE CENTER GATE ==="); print(f"Ready: {r['ready']}"); print(f"Modules OK: {r['modules_ok']}"); print(f"Hygiene OK: {r['hygiene_ok']}"); print(f"Brief OK: {r['brief_ok']}"); print(f"Panel OK: {r['panel_ok']}"); print(f"Start Wrapper OK: {r['start_ok']}")
    s=r.get("details",{}).get("scan_summary",{})
    if s: print(f"Hygiene score: {s.get('score',{}).get('score')}/100"); print(f"Approvals pending: {s.get('approval_pending')}"); print(f"Test tasks: {s.get('test_tasks')}"); print(f"Duplicate memory entries: {s.get('duplicate_memory_entries')}")
if __name__=="__main__": show()
