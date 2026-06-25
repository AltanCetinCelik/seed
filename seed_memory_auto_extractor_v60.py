import json
import re
import uuid
from datetime import datetime
from pathlib import Path


CANDIDATE_FILE = Path("seed_memory_candidates_v60.json")


KEYWORDS = [
    "altan wants",
    "user wants",
    "seed should",
    "seed must",
    "working",
    "works",
    "confirmed",
    "preference",
    "goal",
    "decision",
    "do not",
    "from now on",
    "no more",
    "natural",
    "control plane",
    "terminal",
    "model",
    "repo",
    "hermes",
    "moltbot",
]


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def sentence_split(text):
    parts = re.split(r"(?<=[.!?])\s+|\n+", str(text))
    return [p.strip() for p in parts if len(p.strip()) > 30]


def score_sentence(sentence):
    low = sentence.lower()
    score = 0
    for k in KEYWORDS:
        if k in low:
            score += 2

    if "seed" in low:
        score += 1
    if "altan" in low:
        score += 1
    if len(sentence) > 220:
        score -= 1

    return score


def collect_sources():
    sources = []

    for path in [
        "Seed_Core.md",
        "seed_v50_full_update_ledger.json",
        "seed_v45_total_systems_state.json",
        "seed_v30_agent_hq_v30.json",
    ]:
        p = Path(path)
        if p.exists():
            sources.append((path, p.read_text(errors="ignore")[:25000]))

    log_dir = Path("seed_logs")
    if log_dir.exists():
        for log in sorted(log_dir.glob("chat_*.txt"))[-5:]:
            sources.append((str(log), log.read_text(errors="ignore")[-16000:]))

    return sources


def extract_candidates(limit=80):
    candidates = []

    for source, text in collect_sources():
        for sentence in sentence_split(text):
            score = score_sentence(sentence)
            if score >= 2:
                candidates.append({
                    "id": uuid.uuid4().hex[:10],
                    "created_at": now_timestamp(),
                    "version": "v60.0.0",
                    "source": source,
                    "score": score,
                    "content": sentence[:500],
                    "status": "candidate",
                    "suggested_layer": "project" if "seed" in sentence.lower() else "profile",
                })

    candidates = sorted(candidates, key=lambda x: x["score"], reverse=True)[:limit]

    data = {
        "created_at": now_timestamp(),
        "version": "v60.0.0",
        "ok": True,
        "count": len(candidates),
        "candidates": candidates,
    }

    CANDIDATE_FILE.write_text(json.dumps(data, indent=4))
    return data


def promote_top_candidates(limit=12):
    data = extract_candidates()
    added = []

    try:
        from seed_memory_brain_max_v32 import add_memory
    except Exception as error:
        return {"ok": False, "error": str(error)}

    existing = ""
    memory_file = Path("seed_memory_brain_v32.json")
    if memory_file.exists():
        existing = memory_file.read_text(errors="ignore")

    for item in data.get("candidates", [])[:limit]:
        if item["content"] in existing:
            continue

        added.append(add_memory(
            content=item["content"],
            layer=item["suggested_layer"],
            source=f"auto_extractor:{item['source']}",
            confidence=min(0.95, 0.55 + item["score"] * 0.05),
            tags=["auto_extracted", "v60"],
        ))

    return {
        "created_at": now_timestamp(),
        "version": "v60.0.0",
        "ok": True,
        "candidates": data.get("count"),
        "promoted": len(added),
        "items": added,
    }


def show_memory_auto_extract():
    print("\n=== SEED MEMORY AUTO EXTRACTOR v60 ===")
    print(json.dumps(extract_candidates(), indent=4))


def show_memory_auto_promote():
    print("\n=== SEED MEMORY AUTO PROMOTE v60 ===")
    print(json.dumps(promote_top_candidates(), indent=4))


if __name__ == "__main__":
    show_memory_auto_extract()
