import json
import re
from datetime import datetime
from pathlib import Path

REPORT = Path("seed_wake_reliability_v107_report.json")

WAKE_PHRASES = [
    "wake up seed", "wake up", "hey seed", "ok seed", "okay seed", "seed",
    "yo seed", "hello seed", "seed wake",
]

MISHEARS = [
    "make up", "makeup", "weight up", "wait up", "wake app", "wakeup",
    "break up", "pick up", "bake up", "week up", "weak up", "way cup",
]

FALSE_POSITIVE_BLOCKS = [
    "makeup tutorial", "make up homework", "breakup", "seedling", "seeds",
    "pumpkin seed", "sunflower seed",
]

def now():
    return datetime.now().isoformat(timespec="seconds")

def norm(text):
    text = str(text or "").lower()
    text = text.replace("wake-up", "wake up")
    text = re.sub(r"[^a-z0-9çğıöşü\s]", " ", text)
    return " ".join(text.split())

def match_wake_reliable(text):
    n = norm(text)
    if not n:
        return (False, None, "")

    for bad in FALSE_POSITIVE_BLOCKS:
        if bad in n:
            return (False, None, "")

    phrases = sorted(WAKE_PHRASES + MISHEARS, key=len, reverse=True)
    mis = {norm(x) for x in MISHEARS}

    for phrase in phrases:
        p = norm(phrase)
        if not p:
            continue
        if n == p:
            real = "wake up" if p in mis else phrase
            return (True, real, "")
        if n.startswith(p + " "):
            inline = n[len(p):].strip()
            # bare "seed" can wake only when it is near the beginning and not part of a long unrelated sentence
            if p == "seed" and len(n.split()) > 8:
                continue
            real = "wake up" if p in mis else phrase
            return (True, real, inline)
        if p != "seed" and p in n:
            before, after = n.split(p, 1)
            if len(before.split()) <= 4:
                real = "wake up" if p in mis else phrase
                return (True, real, after.strip())

    # pattern: "seed, can you..." should wake
    if n.startswith("seed ") and len(n.split()) <= 12:
        return (True, "seed", n[5:].strip())

    return (False, None, "")

def run_tests():
    good = {
        "wake up what do you remember": True,
        "make up what do you remember": True,
        "weight up what do you remember": True,
        "hey seed status": True,
        "ok seed are you alive": True,
        "seed what is your status": True,
        "wake app what do you remember": True,
    }
    bad = {
        "makeup tutorial": False,
        "pumpkin seed recipe": False,
        "hello there": False,
        "this is a random sentence": False,
        "sunflower seed oil": False,
    }
    results = {}
    ok = True
    for text, expected in {**good, **bad}.items():
        got = match_wake_reliable(text)[0]
        results[text] = {"expected": expected, "got": got, "match": match_wake_reliable(text)}
        if got != expected:
            ok = False
    report = {"created_at": now(), "version": "v107.4.0", "ok": ok, "results": results}
    REPORT.write_text(json.dumps(report, indent=4, ensure_ascii=False))
    return report

def status():
    return {"created_at": now(), "version": "v107.4.0", "ok": True, "wake_phrases": WAKE_PHRASES, "mishears": MISHEARS}

if __name__ == "__main__":
    import sys
    arg = sys.argv[1] if len(sys.argv) > 1 else "test"
    if arg == "match":
        print(json.dumps({"text": " ".join(sys.argv[2:]), "match": match_wake_reliable(" ".join(sys.argv[2:]))}, indent=4, ensure_ascii=False))
    elif arg == "status":
        print(json.dumps(status(), indent=4, ensure_ascii=False))
    else:
        print(json.dumps(run_tests(), indent=4, ensure_ascii=False))
