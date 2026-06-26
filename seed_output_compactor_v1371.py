import json, re, sys
from pathlib import Path
from datetime import datetime

VERSION = "v137.1.0"
EVENTS = Path("seed_output_compactor_v1371_events.jsonl")
FULL_OUTPUT_DIR = Path("seed_full_outputs_v1371")
FULL_OUTPUT_DIR.mkdir(exist_ok=True)

def now():
    return datetime.now().isoformat(timespec="seconds")

def event(row):
    row.setdefault("created_at", now())
    row.setdefault("version", VERSION)
    with EVENTS.open("a") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row

def _loads_maybe(text):
    if not isinstance(text, str):
        return text
    t = text.strip()
    if not t:
        return None
    # Try whole JSON first.
    try:
        return json.loads(t)
    except Exception:
        pass
    # Try finding first object.
    start = t.find("{")
    end = t.rfind("}")
    if start >= 0 and end > start:
        try:
            return json.loads(t[start:end+1])
        except Exception:
            return None
    return None

def _walk(obj):
    if isinstance(obj, dict):
        yield obj
        for v in obj.values():
            yield from _walk(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _walk(v)

def _first_str(obj, keys):
    for d in _walk(obj):
        for k in keys:
            v = d.get(k) if isinstance(d, dict) else None
            if isinstance(v, str) and v.strip():
                return v.strip()
    return None

def _first_obj(obj, keys):
    for d in _walk(obj):
        for k in keys:
            v = d.get(k) if isinstance(d, dict) else None
            if isinstance(v, (dict, list)):
                return v
    return None

def _regex_first(text, patterns):
    for pat in patterns:
        m = re.search(pat, text, flags=re.S)
        if m:
            val = m.group(1)
            try:
                return json.loads('"' + val.replace('"', '\\"') + '"')
            except Exception:
                return val.replace("\\n", "\n").replace('\\"', '"').strip()
    return None

def save_full_output(stdout="", stderr="", meta=None):
    meta = meta or {}
    name = datetime.now().strftime("full_output_%Y%m%d_%H%M%S_%f.json")
    path = FULL_OUTPUT_DIR / name
    path.write_text(json.dumps({
        "created_at": now(),
        "version": VERSION,
        "meta": meta,
        "stdout": stdout,
        "stderr": stderr,
    }, indent=4, ensure_ascii=False))
    return str(path)

def compact(stdout="", stderr="", returncode=0, meta=None, max_chars=1800):
    meta = meta or {}
    full_path = save_full_output(stdout, stderr, meta)
    data = _loads_maybe(stdout)
    answer = None
    intent = None
    transcript = None
    ok = returncode == 0
    wake = None
    if data is not None:
        answer = _first_str(data, ["answer", "final_answer", "response", "message"])
        intent = _first_str(data, ["intent", "intent_name"])
        transcript = _first_str(data, ["transcript", "raw_text", "input"])
        wake = _first_obj(data, ["wake"])
        # Avoid treating long RAG previews as answer.
        if answer and ("seed_control_plane" in answer or "?? seed_" in answer):
            answer = None
        for d in _walk(data):
            if isinstance(d, dict) and d.get("ok") is False:
                ok = False
                break
    if answer is None and stdout:
        answer = _regex_first(stdout, [
            r'"answer"\s*:\s*"([^"]{1,2000})"',
            r"'answer'\s*:\s*'([^']{1,2000})'",
            r"Seed status:\s*([^\n\r]{1,500})",
        ])
        if answer and not str(answer).startswith("Seed status:") and "8/8" in str(answer):
            answer = "Seed status: " + str(answer).strip()
    if intent is None and stdout:
        intent = _regex_first(stdout, [r'"intent"\s*:\s*"([^"]{1,200})"', r"'intent'\s*:\s*'([^']{1,200})'"])
    if transcript is None and stdout:
        transcript = _regex_first(stdout, [r'"raw_text"\s*:\s*"([^"]{1,500})"', r'"input"\s*:\s*"([^"]{1,500})"'])
    if answer is None:
        # Last resort: meaningful tail without huge JSON.
        cleaned = re.sub(r"\s+", " ", stdout or "").strip()
        answer = cleaned[:max_chars] if cleaned else ""
    if len(answer) > max_chars:
        answer = answer[:max_chars] + "…"
    out = {
        "ok": ok,
        "answer": answer,
        "intent": intent,
        "transcript": transcript,
        "returncode": returncode,
        "full_output_file": full_path,
    }
    if stderr and returncode != 0:
        out["stderr_tail"] = stderr[-800:]
    if wake is not None:
        out["wake"] = wake
    event({"event": "compact", "ok": ok, "intent": intent, "answer_preview": answer[:160], "full_output_file": full_path})
    return out

def text_summary(obj):
    lines = []
    lines.append("Seed Compact Runtime Output")
    lines.append(f"OK: {obj.get('ok')}")
    if obj.get("intent"):
        lines.append(f"Intent: {obj.get('intent')}")
    if obj.get("transcript"):
        lines.append(f"Input: {obj.get('transcript')}")
    lines.append(f"Answer: {obj.get('answer')}")
    lines.append(f"Full output: {obj.get('full_output_file')}")
    return "\n".join(lines)

if __name__ == "__main__":
    raw = sys.stdin.read()
    c = compact(raw, "", 0, {"source": "stdin"})
    if "--json" in sys.argv:
        print(json.dumps(c, indent=4, ensure_ascii=False))
    else:
        print(text_summary(c))
