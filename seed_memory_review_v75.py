import json, hashlib
from datetime import datetime
from pathlib import Path

MEMORY_FILE=Path("seed_long_term_memory_v75.json")
DECISIONS_FILE=Path("seed_memory_decisions_v75.jsonl")
CACHE_FILE=Path("seed_memory_candidates_cache_v75.json")

def now(): return datetime.now().isoformat(timespec="seconds")
def h(text): return hashlib.sha256(str(text).strip().lower().encode()).hexdigest()[:16]

def text_of(item):
    if isinstance(item,str): return item.strip()
    if isinstance(item,dict):
        for k in ["content","text","memory","candidate","summary","body","message","reason"]:
            if item.get(k): return str(item[k]).strip()
        return json.dumps(item,ensure_ascii=False)[:900]
    return str(item).strip()

def load_memory():
    if MEMORY_FILE.exists():
        try: return json.loads(MEMORY_FILE.read_text(errors="ignore"))
        except Exception: pass
    return {"created_at":now(),"version":"v75.0.0","memories":[]}

def save_memory_file(data):
    data["updated_at"]=now(); MEMORY_FILE.write_text(json.dumps(data,indent=4,ensure_ascii=False)); return data

def decision_rows(limit=None):
    if not DECISIONS_FILE.exists(): return []
    lines=DECISIONS_FILE.read_text(errors="ignore").splitlines()
    if limit: lines=lines[-limit:]
    out=[]
    for line in lines:
        try: out.append(json.loads(line))
        except Exception: pass
    return out

def write_decision(row):
    with DECISIONS_FILE.open("a") as f: f.write(json.dumps(row,ensure_ascii=False)+"\n")

def score(text, source=""):
    low=str(text).lower(); s=50
    if "seed" in low: s+=15
    if "user" in low: s+=15
    if any(w in low for w in ["wants","prefers","doesn't want","needs","goal"]): s+=15
    if any(w in low for w in ["v74","v75","voice","avatar","memory","panel","ollama"]): s+=10
    if "friend" in low or "friend" in str(source).lower(): s+=8
    if len(str(text))<20: s-=15
    return max(0,min(100,s))

def why(text, source=""):
    low=str(text).lower(); r=[]
    if "seed" in low: r.append("It affects Seed continuity or architecture.")
    if "user" in low: r.append("It is about User specifically.")
    if "friend" in low or "friend" in str(source).lower(): r.append("It came from friend/external advice.")
    if any(w in low for w in ["voice","avatar","memory","panel","curiosity"]): r.append("It matches active v1 feature work.")
    return " ".join(r) or "It may be useful context, but should be reviewed."

def raw_candidates(limit=120):
    found=[]
    try:
        from seed_memory_review_inbox_v64 import build_inbox
        inbox=build_inbox()
        for k in ["candidates","pending_items","items","memories"]:
            if isinstance(inbox.get(k),list):
                for it in inbox[k]:
                    txt=text_of(it)
                    if txt: found.append({"source":"seed_memory_review_inbox_v64","text":txt,"raw":it if isinstance(it,dict) else {"value":it}})
                break
        if not found and isinstance(inbox.get("pending"),int) and inbox["pending"]>0:
            found.append({"source":"v64_count","text":f"Seed has {inbox['pending']} memory candidates pending; reviewing them improves continuity.","raw":inbox})
    except Exception: pass

    try:
        from seed_friend_advice_ingestor_v72 import load as load_advice
        for it in load_advice().get("items",[]):
            if it.get("content"): found.append({"source":"friend_advice_v72","text":f"Friend advice: {it['content']}","raw":it})
    except Exception: pass

    for txt in [
        "Seed v75.0.0 combines self-state truth fix and real memory review.",
        "Seed v74.0.0 Embodied Companion panel works locally.",
        "Seed v73.1.1 voice recording and transcription route into Seed local chat successfully.",
        "Seed v72 Presence Max allows simulated emotional expression and relevant life advice.",
        "User wants Seed to be bigger, more present, voice-enabled, avatar-enabled, curious, and personally relevant."
    ]:
        found.append({"source":"v75_milestone_seed","text":txt,"raw":{"type":"milestone"}})

    seen=set(); out=[]
    for it in found:
        txt=text_of(it["text"]); hh=h(txt)
        if not txt or hh in seen: continue
        seen.add(hh)
        out.append({"id":f"mem_{len(out)+1:04d}","hash":hh,"text":txt,"source":it.get("source","unknown"),"raw":it.get("raw",{}),"confidence":score(txt,it.get("source","")),"why":why(txt,it.get("source",""))})
        if len(out)>=limit: break
    CACHE_FILE.write_text(json.dumps({"created_at":now(),"version":"v75.0.0","candidates":out},indent=4,ensure_ascii=False))
    return out

def accepted_hashes(): return {m.get("hash") for m in load_memory().get("memories",[])}
def decision_map():
    d={}
    for row in decision_rows():
        hh=row.get("hash") or row.get("candidate_hash")
        if hh: d[hh]=row
    return d

def candidates(limit=20, include_decided=False):
    accepted=accepted_hashes(); decisions=decision_map(); out=[]
    for c in raw_candidates():
        decided=c["hash"] in accepted or c["hash"] in decisions
        if decided and not include_decided: continue
        c["decision"]=decisions.get(c["hash"]); c["accepted"]=c["hash"] in accepted
        out.append(c)
        if len(out)>=limit: break
    return out

def save_candidate(candidate_id_or_hash, note="", edited_text=None):
    target=None
    for c in raw_candidates(200):
        if c["id"]==candidate_id_or_hash or c["hash"]==candidate_id_or_hash: target=c; break
    if not target:
        target={"id":candidate_id_or_hash,"hash":h(edited_text or candidate_id_or_hash),"text":edited_text or candidate_id_or_hash,"source":"manual","confidence":60,"why":"Manual memory save."}
    txt=(edited_text or target["text"]).strip(); hh=h(txt)
    data=load_memory()
    for m in data.get("memories",[]):
        if m.get("hash")==hh:
            row={"created_at":now(),"version":"v75.0.0","action":"save_duplicate","candidate_id":target.get("id"),"hash":hh,"text":txt,"note":note}
            write_decision(row); return {"ok":True,"duplicate":True,"memory":m,"decision":row}
    item={"id":f"memory_{len(data.get('memories',[]))+1:04d}","created_at":now(),"hash":hh,"text":txt,"source":target.get("source","unknown"),"confidence":target.get("confidence",score(txt)),"why":target.get("why",why(txt)),"note":note,"status":"active"}
    data.setdefault("memories",[]).append(item); save_memory_file(data)
    row={"created_at":now(),"version":"v75.0.0","action":"save","candidate_id":target.get("id"),"hash":hh,"text":txt,"note":note}
    write_decision(row); return {"ok":True,"duplicate":False,"memory":item,"decision":row}

def decide_memory(candidate_id_or_hash, action="later", note=""):
    action=str(action).lower().strip()
    if action in {"accept"}: action="save"
    if action in {"skip"}: action="ignore"
    if action=="save": return save_candidate(candidate_id_or_hash,note=note)
    target=None
    for c in raw_candidates(200):
        if c["id"]==candidate_id_or_hash or c["hash"]==candidate_id_or_hash: target=c; break
    if not target: target={"id":candidate_id_or_hash,"hash":h(candidate_id_or_hash),"text":candidate_id_or_hash}
    row={"created_at":now(),"version":"v75.0.0","action":action if action in {"ignore","later","edit"} else "later","candidate_id":target.get("id"),"hash":target.get("hash"),"text":target.get("text"),"note":note}
    write_decision(row); return {"ok":True,"decision":row}

def memory_summary():
    return {"created_at":now(),"version":"v75.0.0","ok":True,"pending_count":len(candidates(200)),"accepted_count":len(load_memory().get("memories",[])),"decision_count":len(decision_rows()),"top_pending":candidates(5),"memory_file":str(MEMORY_FILE),"decisions_file":str(DECISIONS_FILE)}

def show_memory_review(limit=10):
    s=memory_summary(); print("\n=== SEED v75 REAL MEMORY REVIEW ===")
    print(f"Accepted: {s['accepted_count']} | Pending: {s['pending_count']} | Decisions: {s['decision_count']}")
    for c in candidates(limit):
        print(f"- {c['id']} score={c['confidence']} source={c['source']}\n  {c['text'][:260]}\n  why: {c['why']}")
    print("\nUse: save memory mem_0001 | ignore memory mem_0001 | later memory mem_0001 | show accepted memories")

def show_accepted_memories(limit=30):
    print("\n=== SEED v75 ACCEPTED MEMORIES ===")
    mem=load_memory().get("memories",[])[-limit:]
    if not mem: print("No accepted v75 memories yet.")
    for m in mem: print(f"- {m['id']} score={m.get('confidence')} source={m.get('source')}\n  {m['text'][:260]}")

if __name__=="__main__": show_memory_review()
