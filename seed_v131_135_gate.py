import json, subprocess, sys
from pathlib import Path
from datetime import datetime
MODULES=["seed_voice_input_v131.py","seed_real_wake_v132.py","seed_voice_conversation_v133.py","seed_proactive_presence_v134.py","seed_repo_assimilation_v135.py","seed_v131_135_systems.py","seed_v131_135_mega.py","seed_v131_135_gate.py"]
def now(): return datetime.now().isoformat(timespec="seconds")
def comp(m):
    p=subprocess.run([sys.executable,"-m","py_compile",m],capture_output=True,text=True,timeout=30); return {"module":m,"ok":p.returncode==0,"stderr":p.stderr[-1000:]}
def run_gate():
    checks=[comp(m) for m in MODULES]; modules_ok=all(c["ok"] for c in checks); details={}; tests=[]
    def safe(name,fn):
        try:
            d=fn(); details[name]=d; tests.append(bool(d.get("ok",True)))
        except Exception as e: details[name]={"ok":False,"error":str(e)}; tests.append(False)
    safe("voice_input",lambda: __import__("seed_voice_input_v131",fromlist=["test"]).test())
    safe("wake",lambda: __import__("seed_real_wake_v132",fromlist=["test"]).test())
    safe("conversation",lambda: __import__("seed_voice_conversation_v133",fromlist=["test"]).test())
    safe("proactive_presence",lambda: __import__("seed_proactive_presence_v134",fromlist=["suggestion"]).suggestion())
    safe("repo_assimilation",lambda: __import__("seed_repo_assimilation_v135",fromlist=["status"]).status())
    safe("systems",lambda: __import__("seed_v131_135_systems",fromlist=["status"]).status())
    r={"created_at":now(),"version":"v131-v135.0.0","ready":modules_ok and all(tests),"modules_ok":modules_ok,"tests_ok":all(tests),"checks":checks,"details":details}
    Path("seed_v131_135_gate_report.json").write_text(json.dumps(r,indent=4,ensure_ascii=False)); return r
def show():
    r=run_gate(); print("\n=== SEED v131-v135 NO-UPDATE-BEHIND GATE ==="); print(f"Ready: {r['ready']}"); print(f"Modules OK: {r['modules_ok']}"); print(f"Tests OK: {r['tests_ok']}"); print(f"Systems: {r['details'].get('systems',{}).get('ok_count')}/{r['details'].get('systems',{}).get('total')}"); print(f"Voice readiness: {r['details'].get('voice_input',{}).get('readiness')}"); print(f"Wake engine: {r['details'].get('wake',{}).get('engine')}")
if __name__=="__main__": show()
