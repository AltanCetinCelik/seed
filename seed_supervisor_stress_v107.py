import json
import time
from datetime import datetime
from pathlib import Path

REPORT = Path("seed_supervisor_stress_v107_report.json")

def now():
    return datetime.now().isoformat(timespec="seconds")

def run(cycles=2, sleep_seconds=1.0):
    import seed_supervisor_v92 as sup
    events = []
    ok = True
    for i in range(int(cycles)):
        started = sup.start()
        events.append({"cycle": i + 1, "event": "start", "ok": started.get("ok"), "data": started})
        if not started.get("ok"):
            ok = False
        time.sleep(float(sleep_seconds))
        status = sup.supervisor_status()
        events.append({"cycle": i + 1, "event": "status", "ok": status.get("ok"), "mode": status.get("mode"), "ok_count": status.get("ok_count"), "total": status.get("total")})
        if not status.get("required_ok", status.get("ok")):
            ok = False
        stopped = sup.stop()
        events.append({"cycle": i + 1, "event": "stop", "ok": stopped.get("ok"), "data": stopped})
        if not stopped.get("ok"):
            ok = False
        time.sleep(float(sleep_seconds))
    report = {"created_at": now(), "version": "v107.3.0", "ok": ok, "cycles": cycles, "events": events}
    REPORT.write_text(json.dumps(report, indent=4, ensure_ascii=False))
    return report

def dry():
    try:
        import seed_supervisor_v92 as sup
        status = sup.supervisor_status()
        return {"created_at": now(), "version": "v107.3.0", "ok": bool(status.get("required_ok", status.get("ok"))), "mode": "dry", "status": {"ok": status.get("ok"), "mode": status.get("mode"), "ok_count": status.get("ok_count"), "total": status.get("total")}}
    except Exception as e:
        return {"created_at": now(), "version": "v107.3.0", "ok": False, "mode": "dry", "error": str(e)}

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "run":
        cycles = int(sys.argv[2]) if len(sys.argv) > 2 else 2
        print(json.dumps(run(cycles), indent=4, ensure_ascii=False))
    else:
        print(json.dumps(dry(), indent=4, ensure_ascii=False))
