import json
import subprocess
from datetime import datetime


MODULES = [
    "seed_context_accelerator.py",
    "seed_performance_kernel.py",
    "seed_quick_gate_runner.py",
    "seed_companion_os_context.py",
    "seed_control_plane_ui.py",
    "seed_arsenal_commands.py",
]


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def compile_module(module):
    proc = subprocess.run(["python", "-m", "py_compile", module], capture_output=True, text=True)
    return {
        "module": module,
        "ok": proc.returncode == 0,
        "stderr": proc.stderr[-2000:]
    }


def run_v51_gate():
    checks = [compile_module(m) for m in MODULES]
    modules_ok = all(x["ok"] for x in checks)

    details = {}

    try:
        from seed_context_accelerator import get_fast_companion_context
        import time
        start = time.time()
        ctx = get_fast_companion_context("hello")
        context_ms = int((time.time() - start) * 1000)
        context_ok = len(ctx) < 12000 and context_ms < 800
        details["context_chars"] = len(ctx)
        details["context_ms"] = context_ms
    except Exception as error:
        context_ok = False
        details["context_error"] = str(error)

    try:
        from seed_performance_kernel import performance_status
        perf = performance_status()
        performance_ok = perf.get("ok") is True
        details["performance"] = perf
    except Exception as error:
        performance_ok = False
        details["performance_error"] = str(error)

    try:
        from seed_quick_gate_runner import run_quick_gates
        quick = run_quick_gates()
        quick_ok = quick.get("ok") is True
        details["quick_gates"] = {"ok": quick.get("ok"), "passed": quick.get("passed"), "count": quick.get("count")}
    except Exception as error:
        quick_ok = False
        details["quick_error"] = str(error)

    ready = all([modules_ok, context_ok, performance_ok, quick_ok])

    report = {
        "created_at": now_timestamp(),
        "release": "Seed v5.1.0 — Performance Kernel",
        "ready": ready,
        "modules_ok": modules_ok,
        "context_ok": context_ok,
        "performance_ok": performance_ok,
        "quick_gates_ok": quick_ok,
        "module_checks": checks,
        "details": details
    }

    with open("seed_v51_performance_gate.json", "w") as file:
        json.dump(report, file, indent=4)

    return report


def show_v51_gate():
    report = run_v51_gate()
    print("\n=== SEED v5.1.0 PERFORMANCE KERNEL GATE ===")
    print(f"Ready: {report['ready']}")
    print(f"Modules OK: {report['modules_ok']}")
    print(f"Context OK: {report['context_ok']}")
    print(f"Performance OK: {report['performance_ok']}")
    print(f"Quick Gates OK: {report['quick_gates_ok']}")
    print("\nDetails:")
    for k, v in report["details"].items():
        print(f"- {k}: {v}")


if __name__ == "__main__":
    show_v51_gate()
