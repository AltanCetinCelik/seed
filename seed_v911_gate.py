import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

MODULES = ["seed_contextual_chat_v91.py", "seed_v911_gate.py"]

def now():
    return datetime.now().isoformat(timespec="seconds")

def comp(module):
    proc = subprocess.run([sys.executable, "-m", "py_compile", module], capture_output=True, text=True, timeout=30)
    return {"module": module, "ok": proc.returncode == 0, "stderr": proc.stderr[-1000:]}

def run_v911_gate():
    checks = [comp(m) for m in MODULES]
    modules_ok = all(c["ok"] for c in checks)

    try:
        import seed_contextual_chat_v91 as chat
        prompt = chat.build_prompt("what do you remember about yourself right now?")
        prompt_ok = (
            "Answer from the context, concretely" in prompt
            and "Do not become poetic or vague" in prompt
            and "green baseline" in prompt
            and "v88" in prompt
            and "v90" in prompt
        )
        fallback = chat.fallback_memory_reply()
        fallback_ok = "v88" in fallback and "v89" in fallback and "v90" in fallback and "v91" in fallback
        status = chat.status()
        status_ok = status.get("ok") is True
        details = {
            "prompt_preview": prompt[:700],
            "fallback": fallback,
            "status": status
        }
    except Exception as e:
        prompt_ok = False
        fallback_ok = False
        status_ok = False
        details = {"error": str(e)}

    report = {
        "created_at": now(),
        "version": "v91.1.0",
        "ready": modules_ok and prompt_ok and fallback_ok and status_ok,
        "modules_ok": modules_ok,
        "prompt_ok": prompt_ok,
        "fallback_ok": fallback_ok,
        "status_ok": status_ok,
        "module_checks": checks,
        "details": details
    }
    Path("seed_v911_gate_report.json").write_text(json.dumps(report, indent=4, ensure_ascii=False))
    return report

def show_v911_gate():
    r = run_v911_gate()
    print("\n=== SEED v91.1 CONTEXTUAL RECALL GATE ===")
    print(f"Ready: {r['ready']}")
    print(f"Modules OK: {r['modules_ok']}")
    print(f"Prompt OK: {r['prompt_ok']}")
    print(f"Fallback OK: {r['fallback_ok']}")
    print(f"Status OK: {r['status_ok']}")
    print(f"Details: {r['details']}")

if __name__ == "__main__":
    show_v911_gate()
