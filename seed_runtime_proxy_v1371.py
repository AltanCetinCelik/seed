import json, subprocess, sys, shlex, time
from pathlib import Path
from datetime import datetime
import seed_output_compactor_v1371 as compactor

VERSION = "v137.1.1"
EVENTS = Path("seed_runtime_proxy_v1371_events.jsonl")

KNOWN_FLAGS = {
    "--json", "--speak", "--no-speak", "--verbose", "--quiet",
    "--compact", "--full", "--raw"
}

def now():
    return datetime.now().isoformat(timespec="seconds")

def event(row):
    row.setdefault("created_at", now())
    row.setdefault("version", VERSION)
    with EVENTS.open("a") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row

def clean_args(args):
    flags = set()
    words = []
    for a in args:
        if a in KNOWN_FLAGS:
            flags.add(a)
        else:
            words.append(a)
    return words, flags

def sanitize_message(text):
    text = text or ""
    # remove accidentally leaked CLI flags from natural-language wake text
    parts = []
    for p in shlex.split(text) if (" " in text or "\t" in text) else text.split():
        if p not in KNOWN_FLAGS:
            parts.append(p)
    cleaned = " ".join(parts).strip()
    cleaned = cleaned.replace(" --json", "").replace("--json", "").strip()
    cleaned = cleaned.replace(" --no-speak", "").replace("--no-speak", "").strip()
    cleaned = cleaned.replace(" --speak", "").replace("--speak", "").strip()
    return cleaned or "status"

def run(cmd, timeout=180):
    start = time.time()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        latency = round(time.time() - start, 3)
        c = compactor.compact(p.stdout, p.stderr, p.returncode, {"cmd": cmd, "latency_seconds": latency, "proxy_version": VERSION})
        c["latency_seconds"] = latency
        c["cmd"] = cmd
        c["proxy_version"] = VERSION
        event({"event": "run", "cmd": cmd, "ok": c.get("ok"), "latency_seconds": latency, "answer_preview": (c.get("answer") or "")[:160]})
        return c
    except subprocess.TimeoutExpired:
        out = {"ok": False, "error": "timeout", "cmd": cmd, "timeout": timeout, "proxy_version": VERSION}
        event({"event": "timeout", "cmd": cmd, "timeout": timeout})
        return out
    except Exception as e:
        out = {"ok": False, "error": str(e), "cmd": cmd, "proxy_version": VERSION}
        event({"event": "error", "cmd": cmd, "error": str(e)})
        return out

def py(script, *args):
    return [sys.executable, script, *args]

def wake_text(text, speak=False):
    if not Path("seed_voice_runtime_v136.py").exists():
        return {"ok": False, "error": "seed_voice_runtime_v136.py missing", "proxy_version": VERSION}
    clean = sanitize_message(text)
    phrase = clean if clean.lower().startswith(("wake up", "hey seed", "seed ")) else "wake up " + clean
    args = ["wake-text", phrase]
    if not speak:
        args.append("--no-speak")
    return run(py("seed_voice_runtime_v136.py", *args), timeout=240)

def voice_once(speak=False):
    if not Path("seed_voice_runtime_v136.py").exists():
        return {"ok": False, "error": "seed_voice_runtime_v136.py missing", "proxy_version": VERSION}
    args = ["voice-once"]
    if not speak:
        args.append("--no-speak")
    return run(py("seed_voice_runtime_v136.py", *args), timeout=240)

def status():
    if Path("seed_voice_runtime_v136.py").exists():
        return run(py("seed_voice_runtime_v136.py", "status"), timeout=60)
    return {"ok": False, "error": "seed_voice_runtime_v136.py missing", "proxy_version": VERSION}

def text(obj):
    lines = ["Seed Runtime Proxy v137.1.1"]
    lines.append(f"OK: {obj.get('ok')}")
    if obj.get("latency_seconds") is not None:
        lines.append(f"Latency: {obj.get('latency_seconds')}s")
    if obj.get("intent"):
        lines.append(f"Intent: {obj.get('intent')}")
    if obj.get("transcript"):
        lines.append(f"Input: {obj.get('transcript')}")
    if obj.get("answer"):
        lines.append(f"Answer: {obj.get('answer')}")
    if obj.get("full_output_file"):
        lines.append(f"Full output: {obj.get('full_output_file')}")
    if obj.get("error"):
        lines.append(f"Error: {obj.get('error')}")
    return "\n".join(lines)

if __name__ == "__main__":
    raw_args = sys.argv[1:]
    cmd = raw_args[0] if raw_args else "status"
    words, flags = clean_args(raw_args[1:])
    speak = "--speak" in flags
    output_json = "--json" in flags
    if cmd in {"wake-text", "ask", "text"}:
        msg = " ".join(words) or "status"
        res = wake_text(msg, speak=speak)
    elif cmd in {"voice-once", "listen"}:
        res = voice_once(speak=speak)
    else:
        res = status()
    if output_json:
        print(json.dumps(res, indent=4, ensure_ascii=False))
    else:
        print(text(res))
