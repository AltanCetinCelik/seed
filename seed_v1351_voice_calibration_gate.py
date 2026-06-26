import json, subprocess, sys
from pathlib import Path
from datetime import datetime
MODULES=["seed_voice_calibration_v1351.py","seed_voice_input_v131.py","seed_voice_conversation_v133.py","seed_v1351_voice_calibration_gate.py"]
def now(): return datetime.now().isoformat(timespec="seconds")
def comp(m):
    p=subprocess.run([sys.executable,"-m","py_compile",m],capture_output=True,text=True,timeout=30)
    return {"module":m,"ok":p.returncode==0,"stderr":p.stderr[-1000:]}
def run_gate():
    checks=[comp(m) for m in MODULES]; modules_ok=all(c["ok"] for c in checks); details={}
    try:
        import seed_voice_calibration_v1351 as cal
        details["validation"]={"you":cal.validate_transcript("You"),"good":cal.validate_transcript("Seed status how many systems are green")}
        validation_ok=details["validation"]["you"]["ok"] is False and details["validation"]["good"]["ok"] is True
        details["devices"]=cal.list_devices()
    except Exception as e:
        validation_ok=False; details["validation"]={"error":str(e)}
    try:
        import seed_voice_input_v131 as vi
        vi_test=vi.test(); details["voice_input"]=vi_test
        voice_ok=vi_test.get("ok") is True and vi_test.get("validation",{}).get("you",{}).get("ok") is False
    except Exception as e:
        voice_ok=False; details["voice_input"]={"error":str(e)}
    try:
        import seed_voice_conversation_v133 as vc
        ctest=vc.test(); details["conversation"]=ctest
        conv_ok=ctest.get("ok") is True
    except Exception as e:
        conv_ok=False; details["conversation"]={"error":str(e)}
    report={"created_at":now(),"version":"v135.1.0","ready":modules_ok and validation_ok and voice_ok and conv_ok,"modules_ok":modules_ok,"validation_ok":validation_ok,"voice_ok":voice_ok,"conversation_ok":conv_ok,"checks":checks,"details":details}
    Path("seed_v1351_voice_calibration_gate_report.json").write_text(json.dumps(report,indent=4,ensure_ascii=False))
    return report
def show():
    r=run_gate()
    print("\n=== SEED v135.1 VOICE CALIBRATION GATE ===")
    print(f"Ready: {r['ready']}")
    print(f"Modules OK: {r['modules_ok']}")
    print(f"Validation OK: {r['validation_ok']}")
    print(f"Voice OK: {r['voice_ok']}")
    print(f"Conversation OK: {r['conversation_ok']}")
    print(f"Device count: {len(r['details'].get('devices',{}).get('audio_devices',[]))}")
if __name__=="__main__": show()
