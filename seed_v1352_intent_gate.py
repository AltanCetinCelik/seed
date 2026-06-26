import json, subprocess, sys
from pathlib import Path
from datetime import datetime

MODULES=["seed_voice_intent_normalizer_v1352.py","seed_voice_conversation_v133.py","seed_v1352_intent_gate.py"]

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
        import seed_voice_intent_normalizer_v1352 as n
        nt=n.test()
        details["normalizer"]=nt
        normalizer_ok=nt.get("ok") is True
    except Exception as e:
        normalizer_ok=False
        details["normalizer"]={"ok":False,"error":str(e)}
    try:
        import seed_voice_conversation_v133 as c
        ct=c.test()
        details["conversation"]=ct
        conversation_ok=ct.get("ok") is True
    except Exception as e:
        conversation_ok=False
        details["conversation"]={"ok":False,"error":str(e)}
    report={
        "created_at":now(),
        "version":"v135.2.0",
        "ready":modules_ok and normalizer_ok and conversation_ok,
        "modules_ok":modules_ok,
        "normalizer_ok":normalizer_ok,
        "conversation_ok":conversation_ok,
        "checks":checks,
        "details":details
    }
    Path("seed_v1352_intent_gate_report.json").write_text(json.dumps(report,indent=4,ensure_ascii=False))
    return report

def show():
    r=run_gate()
    print("\n=== SEED v135.2 VOICE INTENT NORMALIZER GATE ===")
    print(f"Ready: {r['ready']}")
    print(f"Modules OK: {r['modules_ok']}")
    print(f"Normalizer OK: {r['normalizer_ok']}")
    print(f"Conversation OK: {r['conversation_ok']}")
    print("Intent cases:")
    for k,v in r.get("details",{}).get("normalizer",{}).get("results",{}).items():
        print(f"- {k} -> {v.get('got')} / {v.get('normalized_text')}")

if __name__=="__main__":
    show()
