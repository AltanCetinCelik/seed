import json
import math
import re
import uuid
from collections import Counter
from datetime import datetime
from pathlib import Path


MEMORY_FILE = Path("seed_memory_brain_v32.json")


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def tokenize(text):
    return re.findall(r"[a-zA-Z0-9_çğıöşüÇĞİÖŞÜ]+", str(text).lower())


def _load():
    if MEMORY_FILE.exists():
        try:
            return json.loads(MEMORY_FILE.read_text(errors="ignore"))
        except Exception:
            pass
    return {"version": "v45.0.0", "memories": []}


def _save(data):
    MEMORY_FILE.write_text(json.dumps(data, indent=4))
    return data


def add_memory(content, layer="project", source="manual", confidence=0.7, tags=None):
    data = _load()
    item = {
        "id": uuid.uuid4().hex[:10],
        "created_at": now_timestamp(),
        "version": "v45.0.0",
        "layer": layer,
        "source": source,
        "confidence": float(confidence),
        "tags": tags or [],
        "content": str(content).strip(),
        "tokens": tokenize(content),
        "status": "active"
    }
    data.setdefault("memories", []).append(item)
    _save(data)
    return item


def index_runtime_memories():
    candidates = []

    for path in ["Seed_Core.md", "seed_v20_sovereign_state.json", "seed_v30_agent_hq_v30.json", "seed_v30_agent_hq_state.json"]:
        p = Path(path)
        if p.exists():
            candidates.append((path, p.read_text(errors="ignore")[:6000]))

    try:
        from seed_event_bus import read_events
        events = read_events(limit=30)
        candidates.append(("event_bus", json.dumps(events)[-8000:]))
    except Exception:
        pass

    added = []
    for source, text in candidates:
        if text.strip():
            added.append(add_memory(
                content=text[:3000],
                layer="runtime",
                source=source,
                confidence=0.55,
                tags=["auto_indexed"]
            ))

    return {"ok": True, "added": len(added), "items": added}


def similarity(query, memory):
    q = Counter(tokenize(query))
    m = Counter(memory.get("tokens") or tokenize(memory.get("content", "")))

    if not q or not m:
        return 0.0

    common = set(q) & set(m)
    dot = sum(q[t] * m[t] for t in common)
    q_norm = math.sqrt(sum(v * v for v in q.values()))
    m_norm = math.sqrt(sum(v * v for v in m.values()))

    if not q_norm or not m_norm:
        return 0.0

    return dot / (q_norm * m_norm)


def search_memory(query, limit=8):
    data = _load()
    results = []

    for memory in data.get("memories", []):
        if memory.get("status") != "active":
            continue
        score = similarity(query, memory) * float(memory.get("confidence", 0.5))
        if score > 0:
            results.append({**memory, "score": score})

    return sorted(results, key=lambda x: x["score"], reverse=True)[:limit]


def memory_stats():
    data = _load()
    layers = Counter(m.get("layer") for m in data.get("memories", []))
    return {
        "created_at": now_timestamp(),
        "version": "v45.0.0",
        "ok": True,
        "count": len(data.get("memories", [])),
        "layers": dict(layers),
        "file": str(MEMORY_FILE)
    }


def show_memory_brain():
    print("\n=== SEED MEMORY BRAIN MAX v32 ===")
    print(json.dumps(memory_stats(), indent=4))


def show_memory_index_runtime():
    print(json.dumps(index_runtime_memories(), indent=4))


def show_memory_search():
    query = input("Memory search query: ").strip()
    results = search_memory(query)
    print("\n=== MEMORY SEARCH RESULTS ===")
    for item in results:
        print(f"- score={item['score']:.3f} layer={item['layer']} source={item['source']}: {item['content'][:220].replace(chr(10), ' ')}")


if __name__ == "__main__":
    show_memory_brain()
