import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

MODULES = [
    "seed_doctor_v105.py",
    "seed_safety_ledger_v94.py",
    "seed_tool_bridge_v97.py",
    "seed_vision_v98.py",
    "seed_rag_v104.py",
    "seed_tasks_v99.py",
    "seed_supervisor_v92.py",
    "seed_v1062_clean_status_gate.py",
]

def now():
    return datetime.now().isoformat(timespec="seconds")

def comp(module):
    proc = subprocess.run([sys.executable, "-m", "py_compile", module], capture_output=True, text=True, timeout=30)
    return {"module": module, "ok": proc.returncode == 0, "stderr": proc.stderr[-1000:]}

def run_gate():
    checks = [comp(m) for m in MODULES]
    modules_ok = all(c["ok"] for c in checks)
    details = {}

    try:
        import seed_doctor_v105 as doctor
        d = doctor.diagnose()
        doctor_ok = d.get("required_ok") is True and d.get("ok") is True
        details["doctor"] = {"ok": d.get("ok"), "optional_down": d.get("optional_down", [])}
    except Exception as e:
        doctor_ok = False
        details["doctor_error"] = str(e)

    try:
        import seed_safety_ledger_v94 as safety
        obs_ok = safety.decision("tool git.status").get("allowed") is True
        pwd_ok = safety.decision("tool shell.pwd").get("allowed") is True
        danger_ok = safety.classify("shell", "rm -rf /").get("risk") == "dangerous"
        details["safety"] = {"observe_git_allowed": obs_ok, "observe_pwd_allowed": pwd_ok, "dangerous_blocked": danger_ok}
    except Exception as e:
        obs_ok = pwd_ok = danger_ok = False
        details["safety_error"] = str(e)

    try:
        import seed_tool_bridge_v97 as tools
        git = tools.call("git.status")
        pwd = tools.call("shell.pwd")
        tools_ok = git.get("ok") is True and pwd.get("ok") is True
        details["tools"] = {"git_ok": git.get("ok"), "pwd_ok": pwd.get("ok")}
    except Exception as e:
        tools_ok = False
        details["tools_error"] = str(e)

    try:
        import seed_rag_v104 as rag
        st = rag.status()
        excludes = set(st.get("settings", {}).get("exclude_dirs", []))
        rag_ok = {"third_party_repos", "seed_checkpoints"}.issubset(excludes)
        details["rag"] = {"indexed": st.get("indexed"), "has_focused_excludes": rag_ok}
    except Exception as e:
        rag_ok = False
        details["rag_error"] = str(e)

    try:
        import seed_vision_v98 as vision
        clean = vision.cleanup_existing()
        vision_ok = clean.get("ok") is True
        details["vision"] = clean
    except Exception as e:
        vision_ok = False
        details["vision_error"] = str(e)

    try:
        import seed_supervisor_v92 as sup
        st = sup.supervisor_status()
        supervisor_ok = st.get("required_ok") is True and st.get("mode") == "mostly_green"
        details["supervisor"] = {"required_ok": st.get("required_ok"), "mode": st.get("mode"), "ok_count": st.get("ok_count"), "total": st.get("total")}
    except Exception as e:
        supervisor_ok = False
        details["supervisor_error"] = str(e)

    report = {
        "created_at": now(),
        "version": "v106.2.0",
        "ready": modules_ok and doctor_ok and obs_ok and pwd_ok and danger_ok and tools_ok and rag_ok and vision_ok and supervisor_ok,
        "modules_ok": modules_ok,
        "doctor_ok": doctor_ok,
        "observe_tools_ok": obs_ok and pwd_ok and tools_ok,
        "dangerous_block_ok": danger_ok,
        "rag_focus_ok": rag_ok,
        "vision_cleanup_ok": vision_ok,
        "supervisor_ok": supervisor_ok,
        "checks": checks,
        "details": details,
    }
    Path("seed_v1062_clean_status_gate_report.json").write_text(json.dumps(report, indent=4, ensure_ascii=False))
    return report

def show():
    r = run_gate()
    print("\n=== SEED v106.2 CLEAN STATUS POLISH GATE ===")
    print(f"Ready: {r['ready']}")
    print(f"Modules OK: {r['modules_ok']}")
    print(f"Doctor OK: {r['doctor_ok']}")
    print(f"Observe Tools OK: {r['observe_tools_ok']}")
    print(f"Dangerous Block OK: {r['dangerous_block_ok']}")
    print(f"RAG Focus OK: {r['rag_focus_ok']}")
    print(f"Vision Cleanup OK: {r['vision_cleanup_ok']}")
    print(f"Supervisor OK: {r['supervisor_ok']}")
    print(f"Details: {r['details']}")

if __name__ == "__main__":
    show()
