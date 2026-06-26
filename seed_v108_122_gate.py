import json,subprocess,sys
from pathlib import Path
from datetime import datetime
MODULES=["seed_proactive_rhythm_v108.py","seed_native_wake_v109.py","seed_stt_v110.py","seed_tts_v111.py","seed_memory_garden3_v112.py","seed_memory_gate_v113.py","seed_project_memory_v114.py","seed_operator2_v115.py","seed_screen_understanding_v116.py","seed_approval_ui2_v117.py","seed_skill_registry2_v118.py","seed_mcp_bridge_v119.py","seed_odysseus_audit_v120.py","seed_repo_audit_v121.py","seed_private_rag2_v122.py","seed_v108_122_systems.py","seed_v108_122_mega.py","seed_v108_122_gate.py"]
def now(): return datetime.now().isoformat(timespec='seconds')
def comp(m):
    p=subprocess.run([sys.executable,"-m","py_compile",m],capture_output=True,text=True,timeout=30); return {"module":m,"ok":p.returncode==0,"stderr":p.stderr[-1000:]}
def run_gate():
    checks=[comp(m) for m in MODULES]; modules_ok=all(c["ok"] for c in checks); details={}
    def get(name,mod,fn):
        try:
            d=getattr(__import__(mod,fromlist=[fn]),fn)(); details[name]=d; return bool(d.get("ok",True))
        except Exception as e: details[name]={"ok":False,"error":str(e)}; return False
    tests=[get("proactive","seed_proactive_rhythm_v108","test"),get("wake","seed_native_wake_v109","test"),get("stt","seed_stt_v110","test"),get("tts","seed_tts_v111","status"),get("memory3","seed_memory_garden3_v112","status"),get("memory_gate","seed_memory_gate_v113","test"),get("project","seed_project_memory_v114","test"),get("operator2","seed_operator2_v115","status"),get("screen2","seed_screen_understanding_v116","status"),get("approval2","seed_approval_ui2_v117","status"),get("skills2","seed_skill_registry2_v118","discover"),get("mcp","seed_mcp_bridge_v119","status"),get("odysseus","seed_odysseus_audit_v120","status"),get("repo","seed_repo_audit_v121","status"),get("rag2","seed_private_rag2_v122","status"),get("systems","seed_v108_122_systems","status")]
    r={"created_at":now(),"version":"v108-v122.0.0","ready":modules_ok and all(tests),"modules_ok":modules_ok,"tests_ok":all(tests),"details":details,"checks":checks}
    Path("seed_v108_122_gate_report.json").write_text(json.dumps(r,indent=4,ensure_ascii=False)); return r
def show():
    r=run_gate(); print("\n=== SEED v108-v122 MEGA EVOLUTION GATE ==="); print(f"Ready: {r['ready']}"); print(f"Modules OK: {r['modules_ok']}"); print(f"Tests OK: {r['tests_ok']}"); print(f"Systems: {r['details'].get('systems',{}).get('ok_count')}/{r['details'].get('systems',{}).get('total')}")
if __name__=="__main__": show()
