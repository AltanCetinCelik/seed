import json, subprocess, sys, time
from pathlib import Path
from datetime import datetime

MODULES=["seed_voice_runtime_v136.py","seed_voice_runtime_ui_v136.py","seed_v136_runtime_gate.py"]

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
        import seed_voice_runtime_v136 as rt
        test=rt.test()
        details["runtime_test"]=test
        runtime_ok=test.get("ok") is True
    except Exception as e:
        runtime_ok=False
        details["runtime_test"]={"ok":False,"error":str(e)}
    try:
        import seed_voice_runtime_v136 as rt
        started=rt.start(speak=False)
        time.sleep(0.8)
        status=rt.runtime_status()
        stopped=rt.stop()
        details["start_stop"]={"started":started,"status":status,"stopped":stopped}
        start_stop_ok=started.get("ok") is True and stopped.get("ok") is True
    except Exception as e:
        start_stop_ok=False
        details["start_stop"]={"ok":False,"error":str(e)}
    try:
        import seed_voice_runtime_ui_v136 as ui
        ui_status=ui.status()
        details["ui"]=ui_status
        ui_ok=ui_status.get("ok") is True
    except Exception as e:
        ui_ok=False
        details["ui"]={"ok":False,"error":str(e)}
    report={
        "created_at":now(),
        "version":"v136.0.0",
        "ready":modules_ok and runtime_ok and start_stop_ok and ui_ok,
        "modules_ok":modules_ok,
        "runtime_ok":runtime_ok,
        "start_stop_ok":start_stop_ok,
        "ui_ok":ui_ok,
        "checks":checks,
        "details":details
    }
    Path("seed_v136_runtime_gate_report.json").write_text(json.dumps(report,indent=4,ensure_ascii=False))
    return report

def show():
    r=run_gate()
    print("\n=== SEED v136 VOICE RUNTIME GATE ===")
    print(f"Ready: {r['ready']}")
    print(f"Modules OK: {r['modules_ok']}")
    print(f"Runtime OK: {r['runtime_ok']}")
    print(f"Start/Stop OK: {r['start_stop_ok']}")
    print(f"UI OK: {r['ui_ok']}")
    try:
        print("Runtime answer:", r["details"]["runtime_test"]["direct_text"]["result"]["session"]["answer"])
    except Exception:
        pass

if __name__=="__main__":
    show()
