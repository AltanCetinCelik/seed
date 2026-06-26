import json,subprocess,sys
from pathlib import Path
from datetime import datetime
MODULES=["seed_deep_research_v123.py","seed_knowledge_graph_v124.py","seed_device_router_v125.py","seed_pi_satellite_v126.py","seed_windows_worker_v127.py","seed_menu_bar_v128.py","seed_avatar2_v129.py","seed_release_packaging_v130.py","seed_v123_130_systems.py","seed_v123_130_mega.py","seed_v123_130_gate.py"]
def now(): return datetime.now().isoformat(timespec="seconds")
def comp(m):
    p=subprocess.run([sys.executable,"-m","py_compile",m],capture_output=True,text=True,timeout=30); return {"module":m,"ok":p.returncode==0,"stderr":p.stderr[-1000:]}
def run_gate():
    checks=[comp(m) for m in MODULES]; modules_ok=all(c["ok"] for c in checks); details={}; tests=[]
    def safe(name,fn):
        try:
            d=fn(); details[name]=d; tests.append(bool(d.get("ok",True)))
        except Exception as e: details[name]={"ok":False,"error":str(e)}; tests.append(False)
    safe("research",lambda: __import__("seed_deep_research_v123",fromlist=["create"]).create("Seed v130 gate test"))
    safe("kg",lambda: __import__("seed_knowledge_graph_v124",fromlist=["status"]).status())
    safe("route",lambda: __import__("seed_device_router_v125",fromlist=["route"]).route("heavy gpu vision task"))
    safe("pi",lambda: __import__("seed_pi_satellite_v126",fromlist=["status"]).status())
    safe("windows",lambda: __import__("seed_windows_worker_v127",fromlist=["status"]).status())
    safe("menu",lambda: __import__("seed_menu_bar_v128",fromlist=["status"]).status())
    safe("avatar",lambda: __import__("seed_avatar2_v129",fromlist=["status"]).status())
    safe("packaging",lambda: __import__("seed_release_packaging_v130",fromlist=["status"]).status())
    safe("systems",lambda: __import__("seed_v123_130_systems",fromlist=["status"]).status())
    r={"created_at":now(),"version":"v123-v130.0.0","ready":modules_ok and all(tests),"modules_ok":modules_ok,"tests_ok":all(tests),"checks":checks,"details":details}
    Path("seed_v123_130_gate_report.json").write_text(json.dumps(r,indent=4,ensure_ascii=False)); return r
def show():
    r=run_gate(); print("\n=== SEED v123-v130 BIG PATCH GATE ==="); print(f"Ready: {r['ready']}"); print(f"Modules OK: {r['modules_ok']}"); print(f"Tests OK: {r['tests_ok']}"); print(f"Systems: {r['details'].get('systems',{}).get('ok_count')}/{r['details'].get('systems',{}).get('total')}")
if __name__=="__main__": show()
