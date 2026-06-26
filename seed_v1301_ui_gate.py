import json, subprocess, sys
from pathlib import Path
from datetime import datetime
MODULES=["seed_dashboard_v106.py","seed_avatar2_v129.py","seed_v1301_ui_gate.py"]
def now(): return datetime.now().isoformat(timespec="seconds")
def comp(m):
    p=subprocess.run([sys.executable,"-m","py_compile",m],capture_output=True,text=True,timeout=30)
    return {"module":m,"ok":p.returncode==0,"stderr":p.stderr[-1000:]}
def run_gate():
    checks=[comp(m) for m in MODULES]; modules_ok=all(c["ok"] for c in checks); details={}
    try:
        import seed_dashboard_v106 as d
        vm=d.gather()
        dashboard_ok=vm.get("total",0)>=20 and "groups" in vm and vm.get("health",0)>0 and "Control Room" in d.HTML
        details["dashboard"]={"ok":dashboard_ok,"total":vm.get("total"),"health":vm.get("health"),"groups":[g["name"] for g in vm.get("groups",[])]}
    except Exception as e:
        dashboard_ok=False; details["dashboard"]={"ok":False,"error":str(e)}
    try:
        import seed_avatar2_v129 as a
        st=a.status()
        avatar_ok=st.get("ok") is True and "Seed Avatar" in a.HTML and "health" in st.get("state",{})
        details["avatar"]={"ok":avatar_ok,"state":st.get("state",{})}
    except Exception as e:
        avatar_ok=False; details["avatar"]={"ok":False,"error":str(e)}
    r={"created_at":now(),"version":"v130.1-ui","ready":modules_ok and dashboard_ok and avatar_ok,"modules_ok":modules_ok,"dashboard_ok":dashboard_ok,"avatar_ok":avatar_ok,"checks":checks,"details":details}
    Path("seed_v1301_ui_gate_report.json").write_text(json.dumps(r,indent=4,ensure_ascii=False)); return r
def show():
    r=run_gate()
    print("\n=== SEED v130.1 UI/UX GATE ===")
    print(f"Ready: {r['ready']}")
    print(f"Modules OK: {r['modules_ok']}")
    print(f"Dashboard OK: {r['dashboard_ok']}")
    print(f"Avatar OK: {r['avatar_ok']}")
    print(f"Details: {r['details']}")
if __name__=="__main__": show()
