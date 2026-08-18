import json
from datetime import datetime
from pathlib import Path

STATE = Path("seed_supervisor_v92_state.json")

OPTIONAL_TITLES = {"Doctor", "Dashboard"}

def now():
    return datetime.now().isoformat(timespec="seconds")

def safe(name, fn):
    try:
        return {"name": name, "ok": True, "result": fn()}
    except Exception as e:
        try:
            from seed_trace_v95 import error
            error(name, e)
        except Exception:
            pass
        return {"name": name, "ok": False, "error": str(e)}

def start():
    results = [
        safe("avatar", lambda: __import__("seed_avatar_v89", fromlist=["start_server"]).start_server()),
        safe("organism", lambda: __import__("seed_organism_v89", fromlist=["start_organism"]).start_organism()),
        safe("wake_engine", lambda: __import__("seed_wake_engine_v93", fromlist=["start"]).start()),
        safe("dashboard", lambda: __import__("seed_dashboard_v106", fromlist=["start"]).start()),
    ]
    data = {"created_at": now(), "version": "v92.1.0", "ok": all(r["ok"] for r in results), "mode": "started", "results": results}
    STATE.write_text(json.dumps(data, indent=4, ensure_ascii=False))
    return data

def stop():
    results = [
        safe("wake_engine", lambda: __import__("seed_wake_engine_v93", fromlist=["stop"]).stop()),
        safe("organism", lambda: __import__("seed_organism_v89", fromlist=["stop_organism"]).stop_organism()),
        safe("dashboard", lambda: __import__("seed_dashboard_v106", fromlist=["stop"]).stop()),
    ]
    data = {"created_at": now(), "version": "v92.1.0", "ok": all(r["ok"] for r in results), "mode": "stopped", "results": results}
    STATE.write_text(json.dumps(data, indent=4, ensure_ascii=False))
    return data

def module_card(title, module, fn):
    try:
        m = __import__(module, fromlist=[fn])
        data = getattr(m, fn)()
        return {"title": title, "ok": bool(data.get("ok", True)), "optional": title in OPTIONAL_TITLES, "data": data}
    except Exception as e:
        return {"title": title, "ok": False, "optional": title in OPTIONAL_TITLES, "error": str(e)}

def supervisor_status():
    items = [
        ("Context", "seed_companion_context_v91", "status"),
        ("Wake", "seed_wake_engine_v93", "status"),
        ("Safety", "seed_safety_ledger_v94", "status"),
        ("Trace", "seed_trace_v95", "status"),
        ("Memory2", "seed_memory_garden2_v96", "status"),
        ("Tools", "seed_tool_bridge_v97", "status"),
        ("Vision", "seed_vision_v98", "status"),
        ("Tasks", "seed_tasks_v99", "status"),
        ("Operator", "seed_operator_v100", "status"),
        ("Coder", "seed_coder_v101", "status"),
        ("Voice", "seed_voice_v102", "status"),
        ("Devices", "seed_device_body_v103", "status"),
        ("RAG", "seed_rag_v104", "status"),
        ("Doctor", "seed_doctor_v105", "diagnose"),
        ("Dashboard", "seed_dashboard_v106", "status"),
    ]
    cards = [module_card(*x) for x in items]
    required_ok = all(c["ok"] for c in cards if not c.get("optional"))
    ok_count = sum(1 for c in cards if c["ok"])
    data = {
        "created_at": now(),
        "version": "v92.1.0",
        "ok": required_ok,
        "required_ok": required_ok,
        "ok_count": ok_count,
        "total": len(cards),
        "mode": "mostly_green" if required_ok else "needs_attention",
        "cards": cards,
    }
    STATE.write_text(json.dumps(data, indent=4, ensure_ascii=False))
    return data

def doctor():
    return __import__("seed_doctor_v105", fromlist=["diagnose"]).diagnose()

if __name__ == "__main__":
    import sys
    arg = sys.argv[1] if len(sys.argv) > 1 else "status"
    if arg == "start":
        print(json.dumps(start(), indent=4, ensure_ascii=False))
    elif arg == "stop":
        print(json.dumps(stop(), indent=4, ensure_ascii=False))
    elif arg == "doctor":
        print(json.dumps(doctor(), indent=4, ensure_ascii=False))
    else:
        print(json.dumps(supervisor_status(), indent=4, ensure_ascii=False))
