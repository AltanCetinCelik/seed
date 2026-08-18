import json, re, sys
from pathlib import Path
from datetime import datetime

LOG=Path("seed_voice_intent_normalizer_v1352.jsonl")

SEED_MISHEARS=[
    "see it","see its","seet","seat","sheet","set","seed's","seeds","ceed","cede","sit","site","sid","sede"
]
STATUS_HINTS=[
    "status","state","systems are green","system green","how many systems","how many system","green systems","are green","health"
]
APPROVAL_HINTS=[
    "approval","approvals","pending approval","pending approvals","approve","approved","permission"
]
MEMORY_HINTS=[
    "memory","remember","what do you remember","stored"
]
WAKE_HINTS=[
    "wake","make up","wake up","hey seed","ok seed","okay seed"
]

def now():
    return datetime.now().isoformat(timespec="seconds")

def norm(s):
    s=str(s or "").lower().strip()
    s=re.sub(r"[^a-z0-9çğıöşüİı\s?]", " ", s)
    s=re.sub(r"\s+"," ",s).strip()
    return s

def contains_any(text, arr):
    return any(x in text for x in arr)

def normalize_seed_word(text):
    n=norm(text)
    changed=False
    for w in SEED_MISHEARS:
        if re.search(rf"\b{re.escape(w)}\b", n):
            n=re.sub(rf"\b{re.escape(w)}\b", "seed", n)
            changed=True
    return n, changed

def classify(text):
    raw=str(text or "").strip()
    n, seed_fixed = normalize_seed_word(raw)
    intent="general"
    confidence=0.2
    reason=[]

    if contains_any(n, STATUS_HINTS):
        intent="seed_status"
        confidence=0.86
        reason.append("status_hint")
    if contains_any(n, APPROVAL_HINTS):
        intent="approval_status"
        confidence=0.9
        reason.append("approval_hint")
    if contains_any(n, MEMORY_HINTS):
        intent="memory_recall"
        confidence=max(confidence,0.78)
        reason.append("memory_hint")
    if contains_any(n, WAKE_HINTS):
        reason.append("wake_hint")
        confidence=max(confidence,0.62)

    if seed_fixed:
        reason.append("seed_mishear_fixed")
        confidence=min(0.98, confidence+0.08)

    # Very common Whisper output from User's mic tests.
    if "seet status" in norm(raw) or "see its status" in norm(raw):
        intent="seed_status"
        confidence=0.95
        reason.append("known_seed_status_mishear")

    normalized_text=n
    if intent=="seed_status":
        normalized_text="Seed status. How many systems are green?"
    elif intent=="approval_status":
        normalized_text="How many approvals are pending?"
    elif intent=="memory_recall":
        normalized_text="What do you remember about Seed?"

    return {
        "ok": True,
        "raw_text": raw,
        "normalized_text": normalized_text,
        "intent": intent,
        "confidence": round(confidence,2),
        "reason": reason or ["fallback_general"]
    }

def normalize(text):
    row=classify(text)
    row["created_at"]=now()
    row["version"]="v135.2.0"
    try:
        with LOG.open("a") as f:
            f.write(json.dumps(row,ensure_ascii=False)+"\n")
    except Exception:
        pass
    return row

def test():
    cases={
        "Seet status, how many systems are green?":"seed_status",
        "See its status, how many systems are green?":"seed_status",
        "Seat status how many systems are green":"seed_status",
        "How many approvals are pending?":"approval_status",
        "What do you remember about Seed?":"memory_recall",
        "hello there":"general"
    }
    results={}
    ok=True
    for text, expected in cases.items():
        got=classify(text)
        results[text]={"expected":expected,"got":got["intent"],"normalized_text":got["normalized_text"],"confidence":got["confidence"],"reason":got["reason"]}
        ok = ok and got["intent"]==expected
    return {"created_at":now(),"version":"v135.2.0","ok":ok,"results":results}

def status():
    return {"created_at":now(),"version":"v135.2.0","ok":True,"tests":test()}

if __name__=="__main__":
    a=sys.argv[1] if len(sys.argv)>1 else "status"
    if a=="normalize":
        print(json.dumps(normalize(" ".join(sys.argv[2:])),indent=4,ensure_ascii=False))
    elif a=="test":
        print(json.dumps(test(),indent=4,ensure_ascii=False))
    else:
        print(json.dumps(status(),indent=4,ensure_ascii=False))
