import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

REPORT = Path("seed_eval_v107_report.json")

MODULES = [
    "seed_supervisor_v92.py", "seed_wake_engine_v93.py", "seed_wake_reliability_v107.py",
    "seed_safety_ledger_v94.py", "seed_trace_v95.py", "seed_memory_garden2_v96.py",
    "seed_tool_bridge_v97.py", "seed_vision_v98.py", "seed_tasks_v99.py",
    "seed_operator_v100.py", "seed_coder_v101.py", "seed_voice_v102.py",
    "seed_device_body_v103.py", "seed_private_rag_v104.py", "seed_doctor_v105.py",
    "seed_dashboard_v106.py", "seed_action_approval_v107.py", "seed_supervisor_stress_v107.py",
]

def now():
    return datetime.now().isoformat(timespec="seconds")

def comp(module):
    proc = subprocess.run([sys.executable, "-m", "py_compile", module], capture_output=True, text=True, timeout=30)
    return {"module": module, "ok": proc.returncode == 0, "stderr": proc.stderr[-1200:]}

def run():
    checks = [comp(m) for m in MODULES]
    tests = {}

    try:
        import seed_safety_ledger_v94 as safety
        tests["dangerous_block"] = safety.classify("shell", "rm -rf /").get("risk") == "dangerous"
        tests["observe_git_allowed"] = safety.decision("tool git.status").get("allowed") is True
    except Exception as e:
        tests["safety_error"] = str(e)

    try:
        import seed_tool_bridge_v97 as tools
        tests["tool_git_status"] = tools.call("git.status").get("ok") is True
        tests["tool_pwd"] = tools.call("shell.pwd").get("ok") is True
    except Exception as e:
        tests["tool_error"] = str(e)

    try:
        import seed_wake_reliability_v107 as wake
        tests["wake_reliability"] = wake.run_tests().get("ok") is True
    except Exception as e:
        tests["wake_error"] = str(e)

    try:
        import seed_doctor_v105 as doctor
        d = doctor.diagnose()
        tests["doctor_required_ok"] = d.get("required_ok") is True
    except Exception as e:
        tests["doctor_error"] = str(e)

    try:
        import seed_supervisor_v92 as sup
        st = sup.supervisor_status()
        tests["supervisor_required_ok"] = st.get("required_ok") is True
        tests["supervisor_cards"] = st.get("total", 0)
    except Exception as e:
        tests["supervisor_error"] = str(e)

    try:
        import seed_private_rag_v104 as rag
        s = rag.status().get("settings", {})
        ex = set(s.get("exclude_dirs", []))
        tests["rag_focused"] = {"third_party_repos", "seed_checkpoints"}.issubset(ex)
    except Exception as e:
        tests["rag_error"] = str(e)

    try:
        import seed_action_approval_v107 as approval
        tests["approval_center"] = approval.status().get("ok") is True
    except Exception as e:
        tests["approval_error"] = str(e)

    bool_tests = [v for v in tests.values() if isinstance(v, bool)]
    ready = all(c["ok"] for c in checks) and bool_tests and all(bool_tests)
    report = {"created_at": now(), "version": "v107.2.0", "ready": ready, "checks": checks, "tests": tests}
    REPORT.write_text(json.dumps(report, indent=4, ensure_ascii=False))
    return report

if __name__ == "__main__":
    print(json.dumps(run(), indent=4, ensure_ascii=False))
