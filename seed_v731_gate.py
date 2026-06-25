import json
import subprocess
from datetime import datetime

MODULES = [
    "seed_live_voice_v731.py",
    "seed_v731_gate.py",
]

def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")

def compile_module(module):
    proc = subprocess.run(["python", "-m", "py_compile", module], capture_output=True, text=True, timeout=30)
    return {"module": module, "ok": proc.returncode == 0, "stderr": proc.stderr[-1200:]}

def run_v731_gate():
    checks = [compile_module(m) for m in MODULES]
    modules_ok = all(c["ok"] for c in checks)
    details = {}

    try:
        from seed_live_voice_v731 import voice_status
        status = voice_status()
        voice_ok = bool(status.get("tools", {}).get("ffmpeg")) and bool(status.get("tools", {}).get("macos_say"))
        details["voice"] = status
    except Exception as error:
        voice_ok = False
        details["voice_error"] = str(error)

    try:
        from seed_v73_gate import run_v73_gate
        v73 = run_v73_gate()
        v73_ok = v73.get("ready") is True
        details["v73"] = {"ready": v73.get("ready")}
    except Exception as error:
        v73_ok = False
        details["v73_error"] = str(error)

    report = {
        "created_at": now_timestamp(),
        "version": "v73.1.0",
        "ready": modules_ok and voice_ok and v73_ok,
        "modules_ok": modules_ok,
        "voice_ok": voice_ok,
        "v73_ok": v73_ok,
        "module_checks": checks,
        "details": details,
    }

    with open("seed_v731_gate_report.json", "w") as f:
        json.dump(report, f, indent=4)

    return report

def show_v731_gate():
    report = run_v731_gate()
    print("\n=== SEED v73.1 VOICE ROUTER GATE ===")
    print(f"Ready: {report['ready']}")
    print(f"Modules OK: {report['modules_ok']}")
    print(f"Voice OK: {report['voice_ok']}")
    print(f"v73 OK: {report['v73_ok']}")
    print("Details:")
    print(json.dumps(report["details"], indent=4, ensure_ascii=False))

if __name__ == "__main__":
    show_v731_gate()
