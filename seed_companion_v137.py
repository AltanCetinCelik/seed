import json, os, signal, subprocess, sys, time, shlex
from pathlib import Path
from datetime import datetime

VERSION = "v137.0.0"
PID = Path("seed_companion_v137.pid")
STATE = Path("seed_companion_v137_state.json")
EVENTS = Path("seed_companion_v137_events.jsonl")
INBOX = Path("seed_companion_v137_inbox.jsonl")
LOG = Path("seed_companion_v137.log")
SETTINGS = Path("seed_companion_v137_settings.json")

DEFAULT_SETTINGS = {
    "version": VERSION,
    "mode": "safe_presence",
    "loop_interval_seconds": 2,
    "cooldown_seconds": 8,
    "auto_start_services": True,
    "start_ui": False,
    "start_autopilot": True,
    "start_voice_runtime": True,
    "start_proactive": True,
    "start_dashboard_avatar": True,
    "audio_wake_enabled": False,
    "audio_probe_seconds": 3,
    "wake_phrases": ["wake up", "hey seed", "seed"],
    "ignore_phrases": ["pumpkin seed", "seed recipe"],
    "speak_default": False,
    "max_events": 1200,
    "note": "v137 defaults to safe presence. Audio wake can be enabled after explicit testing."
}

def now():
    return datetime.now().isoformat(timespec="seconds")

def load_json(path, default):
    if Path(path).exists():
        try:
            obj = json.loads(Path(path).read_text(errors="ignore"))
            if isinstance(obj, dict):
                base = default.copy()
                base.update(obj)
                base["version"] = VERSION
                return base
        except Exception:
            pass
    Path(path).write_text(json.dumps(default, indent=4, ensure_ascii=False))
    return default.copy()

def settings():
    return load_json(SETTINGS, DEFAULT_SETTINGS)

def save_settings(s):
    s["version"] = VERSION
    SETTINGS.write_text(json.dumps(s, indent=4, ensure_ascii=False))
    return s

def write_state(obj):
    obj["updated_at"] = now()
    obj["version"] = VERSION
    STATE.write_text(json.dumps(obj, indent=4, ensure_ascii=False))
    return obj

def event(row):
    row.setdefault("created_at", now())
    row.setdefault("version", VERSION)
    with EVENTS.open("a") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    trim_events()
    return row

def trim_events():
    if not EVENTS.exists():
        return
    try:
        s = settings()
        max_events = int(s.get("max_events", 1200))
        lines = EVENTS.read_text(errors="ignore").splitlines()
        if len(lines) > max_events:
            EVENTS.write_text("\n".join(lines[-max_events:]) + "\n")
    except Exception:
        pass

def alive(pid):
    try:
        os.kill(int(pid), 0)
        return True
    except Exception:
        return False

def run(cmd, timeout=90):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        out = (p.stdout or "").strip()
        data = None
        if out:
            try:
                data = json.loads(out)
            except Exception:
                data = {"raw": out}
        return {"ok": p.returncode == 0, "returncode": p.returncode, "cmd": cmd, "stdout": out[-4000:], "stderr": (p.stderr or "")[-2000:], "data": data}
    except subprocess.TimeoutExpired:
        return {"ok": False, "cmd": cmd, "error": "timeout"}
    except Exception as e:
        return {"ok": False, "cmd": cmd, "error": str(e)}

def py(script, *args):
    return [sys.executable, script, *args]

def service_status():
    rows = {}
    commands = {
        "voice_runtime": py("seed_voice_runtime_v136.py", "status"),
        "approval_autopilot": py("seed_approval_autopilot_v13623.py", "status"),
        "effective_hygiene": py("seed_hygiene_status_v13623.py", "--json"),
        "dashboard": py("seed_dashboard_v106.py", "status"),
        "avatar": py("seed_avatar2_v129.py", "status"),
        "proactive": py("seed_proactive_rhythm_v108.py", "status"),
    }
    for name, cmd in commands.items():
        if Path(cmd[1]).exists():
            rows[name] = run(cmd, timeout=30)
        else:
            rows[name] = {"ok": False, "missing": cmd[1]}
    return rows

def start_services():
    s = settings()
    actions = []
    if not s.get("auto_start_services", True):
        return {"ok": True, "skipped": True, "actions": actions}
    if s.get("start_dashboard_avatar", True):
        if Path("seed_dashboard_v106.py").exists():
            actions.append({"service": "dashboard", "result": run(py("seed_dashboard_v106.py", "start"))})
        if Path("seed_avatar2_v129.py").exists():
            actions.append({"service": "avatar", "result": run(py("seed_avatar2_v129.py", "start"))})
    if s.get("start_proactive", True) and Path("seed_proactive_rhythm_v108.py").exists():
        actions.append({"service": "proactive", "result": run(py("seed_proactive_rhythm_v108.py", "start"))})
    if s.get("start_voice_runtime", True) and Path("seed_voice_runtime_v136.py").exists():
        actions.append({"service": "voice_runtime", "result": run(py("seed_voice_runtime_v136.py", "start", "--no-speak"))})
    if s.get("start_autopilot", True) and Path("seed_approval_autopilot_v13623.py").exists():
        actions.append({"service": "approval_autopilot", "result": run(py("seed_approval_autopilot_v13623.py", "start"))})
    event({"event": "start_services", "actions": actions})
    return {"ok": True, "actions": actions}

def stop_services():
    actions = []
    # Stop companion-adjacent services, but keep dashboard/avatar unless user uses stop-all.
    if Path("seed_approval_autopilot_v13623.py").exists():
        actions.append({"service": "approval_autopilot", "result": run(py("seed_approval_autopilot_v13623.py", "stop"))})
    if Path("seed_voice_runtime_v136.py").exists():
        actions.append({"service": "voice_runtime", "result": run(py("seed_voice_runtime_v136.py", "stop"))})
    event({"event": "stop_services", "actions": actions})
    return {"ok": True, "actions": actions}

def stop_all_services():
    actions = []
    for script, name in [
        ("seed_approval_autopilot_v13623.py", "approval_autopilot"),
        ("seed_voice_runtime_v136.py", "voice_runtime"),
        ("seed_proactive_rhythm_v108.py", "proactive"),
        ("seed_avatar2_v129.py", "avatar"),
        ("seed_dashboard_v106.py", "dashboard")
    ]:
        if Path(script).exists():
            actions.append({"service": name, "result": run(py(script, "stop"))})
    event({"event": "stop_all_services", "actions": actions})
    return {"ok": True, "actions": actions}

def enqueue(text, source="manual"):
    row = {"created_at": now(), "version": VERSION, "source": source, "text": text, "processed": False}
    with INBOX.open("a") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    event({"event": "enqueue", "text": text, "source": source})
    return {"ok": True, "queued": row}

def read_inbox():
    rows = []
    if not INBOX.exists():
        return rows
    for line in INBOX.read_text(errors="ignore").splitlines():
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except Exception:
            rows.append({"created_at": now(), "text": line, "processed": False, "unparsed": True})
    return rows

def write_inbox(rows):
    INBOX.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + ("\n" if rows else ""))

def wake_match(text):
    s = settings()
    t = (text or "").lower().strip()
    for bad in s.get("ignore_phrases", []):
        if bad in t:
            return {"ok": True, "matched": False, "reason": "ignore_phrase", "phrase": bad, "rest": ""}
    for phrase in s.get("wake_phrases", []):
        p = phrase.lower()
        if t == p:
            return {"ok": True, "matched": True, "phrase": phrase, "rest": ""}
        if t.startswith(p + " "):
            return {"ok": True, "matched": True, "phrase": phrase, "rest": text[len(phrase):].strip()}
    # If v132 matcher exists, use it as a second opinion.
    try:
        import seed_real_wake_v132 as wake
        if hasattr(wake, "text_match"):
            m = wake.text_match(text)
            if isinstance(m, dict) and m.get("matched"):
                return {"ok": True, "matched": True, "phrase": m.get("phrase"), "rest": m.get("rest",""), "engine": "seed_real_wake_v132"}
    except Exception:
        pass
    return {"ok": True, "matched": False, "reason": "no_match", "rest": ""}

def run_text_runtime(text):
    args = ["wake-text", "wake up " + text if not text.lower().startswith(("wake up", "hey seed", "seed")) else text]
    if not settings().get("speak_default", False):
        args.append("--no-speak")
    if Path("seed_voice_runtime_v136.py").exists():
        return run(py("seed_voice_runtime_v136.py", *args), timeout=180)
    return {"ok": False, "error": "seed_voice_runtime_v136.py missing"}

def run_voice_once():
    # Tries the v136 voice runtime CLI first; fallback to v133 listen.
    if Path("seed_voice_runtime_v136.py").exists():
        r = run(py("seed_voice_runtime_v136.py", "voice-once", "--no-speak"), timeout=180)
        if r.get("ok"):
            return r
    if Path("seed_voice_conversation_v133.py").exists():
        return run(py("seed_voice_conversation_v133.py", "listen", "--no-speak"), timeout=180)
    return {"ok": False, "error": "no voice once command available"}

def extract_transcript(result):
    data = result.get("data") if isinstance(result, dict) else result
    if not isinstance(data, dict):
        return None
    # Common shapes from previous modules.
    paths = [
        ["transcript"],
        ["text"],
        ["listen", "transcript", "text"],
        ["result", "listen", "transcript", "text"],
        ["session", "input"],
        ["result", "session", "input"],
        ["event", "result", "session", "input"],
    ]
    for path in paths:
        cur = data
        for k in path:
            if isinstance(cur, dict) and k in cur:
                cur = cur[k]
            else:
                cur = None; break
        if isinstance(cur, str) and cur.strip():
            return cur.strip()
    # Search recursively.
    return find_textish(data)

def find_textish(obj):
    if isinstance(obj, dict):
        for key in ["transcript", "text", "input", "normalized_text"]:
            v = obj.get(key)
            if isinstance(v, str) and len(v.strip()) >= 2:
                return v.strip()
        for v in obj.values():
            r = find_textish(v)
            if r:
                return r
    elif isinstance(obj, list):
        for x in obj:
            r = find_textish(x)
            if r:
                return r
    return None

def process_text(text, source="inbox"):
    wm = wake_match(text)
    row = {"event": "text_received", "source": source, "text": text, "wake": wm}
    if not wm.get("matched"):
        row["handled"] = False
        event(row)
        return {"ok": True, "handled": False, "wake": wm}
    rest = wm.get("rest") or "status"
    runtime = run_text_runtime(rest)
    row["handled"] = True
    row["runtime"] = runtime
    event(row)
    return {"ok": True, "handled": True, "wake": wm, "runtime": runtime}

def process_inbox():
    rows = read_inbox()
    changed = False
    results = []
    for r in rows:
        if r.get("processed"):
            continue
        res = process_text(r.get("text",""), source=r.get("source","inbox"))
        r["processed"] = True
        r["processed_at"] = now()
        r["result"] = res
        changed = True
        results.append(res)
    if changed:
        write_inbox(rows)
    return {"ok": True, "processed": len(results), "results": results}

def audio_probe():
    s = settings()
    if not s.get("audio_wake_enabled", False):
        return {"ok": True, "skipped": True, "reason": "audio_wake_disabled"}
    # Conservative: listen short snippet and only run full voice once if wake word detected.
    if Path("seed_voice_input_v131.py").exists():
        r = run(py("seed_voice_input_v131.py", "listen-once", str(s.get("audio_probe_seconds", 3))), timeout=180)
    elif Path("seed_voice_conversation_v133.py").exists():
        r = run(py("seed_voice_conversation_v133.py", "listen", "--no-speak"), timeout=180)
    else:
        return {"ok": False, "error": "no audio input module"}
    transcript = extract_transcript(r)
    wm = wake_match(transcript or "")
    out = {"ok": True, "probe": r, "transcript": transcript, "wake": wm, "handled": False}
    if transcript and wm.get("matched"):
        rest = wm.get("rest")
        if rest:
            out["runtime"] = run_text_runtime(rest)
        else:
            out["runtime"] = run_voice_once()
        out["handled"] = True
    event({"event": "audio_probe", "transcript": transcript, "wake": wm, "handled": out.get("handled")})
    return out

def loop_tick():
    results = {"created_at": now(), "version": VERSION, "inbox": process_inbox(), "audio": audio_probe()}
    return results

def daemon():
    s = settings()
    start_services()
    write_state({"alive": True, "pid": os.getpid(), "mode": s.get("mode"), "started_at": now(), "last_tick": None})
    event({"event": "daemon_started", "pid": os.getpid(), "settings": s})
    last_handled = 0
    while True:
        s = settings()
        try:
            tick = loop_tick()
            write_state({"alive": True, "pid": os.getpid(), "mode": s.get("mode"), "last_tick": tick, "heartbeat_at": now()})
        except Exception as e:
            event({"event": "daemon_error", "error": str(e)})
            write_state({"alive": True, "pid": os.getpid(), "mode": s.get("mode"), "error": str(e), "heartbeat_at": now()})
        time.sleep(float(s.get("loop_interval_seconds", 2)))

def start(audio=False, ui=False):
    s = settings()
    if audio:
        s["audio_wake_enabled"] = True
    if ui:
        s["start_ui"] = True
    save_settings(s)
    if PID.exists():
        try:
            pid = int(PID.read_text().strip())
            if alive(pid):
                return {"ok": True, "already_running": True, "pid": pid, "settings": s}
        except Exception:
            pass
    p = subprocess.Popen([sys.executable, "seed_companion_v137.py", "daemon"], stdout=LOG.open("a"), stderr=LOG.open("a"))
    PID.write_text(str(p.pid))
    time.sleep(0.7)
    return {"ok": True, "pid": p.pid, "settings": s}

def stop(stop_services_flag=False):
    pid = None; stopped = False
    if PID.exists():
        try:
            pid = int(PID.read_text().strip())
            if alive(pid):
                os.kill(pid, signal.SIGTERM)
                stopped = True
            PID.unlink(missing_ok=True)
        except Exception:
            pass
    write_state({"alive": False, "pid": None, "stopped_at": now()})
    event({"event": "daemon_stopped", "pid": pid, "stopped": stopped})
    service_result = None
    if stop_services_flag:
        service_result = stop_services()
    return {"ok": True, "stopped": stopped, "pid": pid, "services": service_result}

def status():
    pid = None; al = False
    if PID.exists():
        try:
            pid = int(PID.read_text().strip())
            al = alive(pid)
        except Exception:
            pass
    state = {}
    if STATE.exists():
        try:
            state = json.loads(STATE.read_text(errors="ignore"))
        except Exception:
            state = {}
    recent = []
    if EVENTS.exists():
        for line in EVENTS.read_text(errors="ignore").splitlines()[-20:]:
            try:
                recent.append(json.loads(line))
            except Exception:
                pass
    return {
        "created_at": now(),
        "version": VERSION,
        "ok": True,
        "alive": al,
        "pid": pid,
        "settings": settings(),
        "state": state,
        "services": service_status(),
        "inbox_pending": len([r for r in read_inbox() if not r.get("processed")]),
        "recent_events": recent
    }

def configure(key, value):
    s = settings()
    if value.lower() in {"true","yes","1","on"}:
        v = True
    elif value.lower() in {"false","no","0","off"}:
        v = False
    else:
        try:
            v = int(value)
        except Exception:
            v = value
    s[key] = v
    save_settings(s)
    return {"ok": True, "settings": s}

def test():
    start_res = start_services()
    q = enqueue("wake up status", source="v137_test")
    proc = process_inbox()
    wm_good = wake_match("wake up status")
    wm_bad = wake_match("pumpkin seed recipe")
    return {"ok": True, "start_services": start_res, "enqueue": q, "process": proc, "wake_good": wm_good, "wake_bad": wm_bad, "status": status()}

if __name__ == "__main__":
    args = sys.argv[1:]
    cmd = args[0] if args else "status"
    if cmd == "daemon":
        daemon()
    elif cmd == "start":
        print(json.dumps(start(audio="--audio" in args, ui="--ui" in args), indent=4, ensure_ascii=False))
    elif cmd == "stop":
        print(json.dumps(stop(stop_services_flag="--services" in args or "--all" in args), indent=4, ensure_ascii=False))
    elif cmd == "stop-all":
        print(json.dumps({"companion": stop(False), "services": stop_all_services()}, indent=4, ensure_ascii=False))
    elif cmd == "enqueue":
        print(json.dumps(enqueue(" ".join(args[1:]) or "wake up status"), indent=4, ensure_ascii=False))
    elif cmd == "process":
        print(json.dumps(process_inbox(), indent=4, ensure_ascii=False))
    elif cmd == "tick":
        print(json.dumps(loop_tick(), indent=4, ensure_ascii=False))
    elif cmd == "audio-on":
        print(json.dumps(configure("audio_wake_enabled", "true"), indent=4, ensure_ascii=False))
    elif cmd == "audio-off":
        print(json.dumps(configure("audio_wake_enabled", "false"), indent=4, ensure_ascii=False))
    elif cmd == "set" and len(args) >= 3:
        print(json.dumps(configure(args[1], args[2]), indent=4, ensure_ascii=False))
    elif cmd == "test":
        print(json.dumps(test(), indent=4, ensure_ascii=False))
    else:
        print(json.dumps(status(), indent=4, ensure_ascii=False))
