import json, sys
from pathlib import Path
from datetime import datetime

SESS=Path("seed_voice_conversation_v133_sessions.jsonl")

def now():
    return datetime.now().isoformat(timespec="seconds")

def write(row):
    row.setdefault("created_at",now())
    row.setdefault("version","v133.2.0")
    with SESS.open("a") as f:
        f.write(json.dumps(row,ensure_ascii=False)+"\n")
    return row

def history(limit=20):
    if not SESS.exists():
        return []
    out=[]
    for l in SESS.read_text(errors="ignore").splitlines()[-limit:]:
        try: out.append(json.loads(l))
        except Exception: pass
    return out

def validate(text):
    try:
        import seed_voice_calibration_v1351 as cal
        return cal.validate_transcript(text)
    except Exception:
        t=str(text or "").strip()
        return {"ok":bool(t and t.lower()!="you" and len(t)>=8),"text":t}

def normalize_intent(text):
    try:
        import seed_voice_intent_normalizer_v1352 as n
        return n.normalize(text)
    except Exception as e:
        return {"ok":False,"raw_text":text,"normalized_text":text,"intent":"general","confidence":0.2,"error":str(e)}

def context(text):
    c={"memory":[],"rag":[]}
    try:
        import seed_memory_gate_v113 as mg
        c["memory"]=mg.retrieve(text,limit=5)
    except Exception as e:
        c["memory_error"]=str(e)
    try:
        import seed_private_rag2_v122 as rag
        c["rag"]=rag.search(text,limit=5)
    except Exception as e:
        c["rag_error"]=str(e)
    return c

def answer(text, intent_info=None):
    intent_info = intent_info or normalize_intent(text)
    intent=intent_info.get("intent","general")
    normalized_text=intent_info.get("normalized_text",text)
    c=context(normalized_text)

    if intent=="seed_status":
        try:
            import seed_v123_130_systems as s
            st=s.status()
            ans=f"Seed status: {st.get('ok_count')}/{st.get('total')} systems green."
        except Exception:
            ans="Seed status check failed."
    elif intent=="approval_status":
        try:
            import seed_action_approval_v107 as a
            ans=f"There are {a.status().get('pending_count',0)} pending approvals."
        except Exception:
            ans="Approval center check failed."
    elif intent=="memory_recall":
        if c.get("memory"):
            ans="Relevant memory: "+c["memory"][0]["memory"].get("summary","")
        elif c.get("rag"):
            ans="Top local context source: "+c["rag"][0].get("source","unknown")
        else:
            ans="I do not have a strong relevant memory yet."
    else:
        low=normalized_text.lower()
        if "status" in low:
            try:
                import seed_v123_130_systems as s
                st=s.status()
                ans=f"Seed status: {st.get('ok_count')}/{st.get('total')} systems green."
            except Exception:
                ans="Seed status check failed."
        elif "approval" in low:
            try:
                import seed_action_approval_v107 as a
                ans=f"There are {a.status().get('pending_count',0)} pending approvals."
            except Exception:
                ans="Approval center check failed."
        elif c.get("memory"):
            ans="Relevant memory: "+c["memory"][0]["memory"].get("summary","")
        elif c.get("rag"):
            ans="Top local context source: "+c["rag"][0].get("source","unknown")
        else:
            ans="I heard you. I can route this through memory, RAG, tools, or a local model next."

    return ans,c,intent_info

def speak(text):
    try:
        import seed_tts_v111 as t
        return t.say(text)
    except Exception as e:
        return {"ok":False,"error":str(e)}

def converse_text(text,speak_enabled=True,allow_bad_text=False):
    val=validate(text)
    if not val.get("ok") and not allow_bad_text:
        row=write({"input":text,"ok":False,"stage":"bad_transcript","validation":val,"answer":"I could not hear clearly. Please repeat."})
        return {"ok":False,"stage":"bad_transcript","session":row}
    intent_info=normalize_intent(text)
    ans,c,intent_info=answer(text,intent_info)
    row=write({"input":text,"ok":True,"intent":intent_info,"answer":ans,"context":c,"tts":speak(ans) if speak_enabled else {"ok":True,"skipped":True}})
    return {"ok":True,"session":row}

def listen_and_answer(seconds=None,speak_enabled=True):
    import seed_voice_input_v131 as vi
    listened=vi.listen_once(seconds)
    if not listened.get("ok"):
        row=write({"ok":False,"stage":"listen_failed","listen":listened,"answer":"I could not hear clearly. Please repeat."})
        return {"ok":False,"stage":"listen_failed","listen":listened,"session":row}
    text=listened.get("transcript",{}).get("text") or listened.get("transcript",{}).get("raw_text","")
    val=validate(text)
    if not val.get("ok"):
        row=write({"ok":False,"stage":"bad_transcript","listen":listened,"validation":val,"answer":"I could not hear clearly. Please repeat."})
        return {"ok":False,"stage":"bad_transcript","listen":listened,"session":row}
    out=converse_text(text,speak_enabled,allow_bad_text=True)
    out["listen"]=listened
    return out

def test():
    a=converse_text("Seed status",False)
    b=converse_text("You",False)
    c=converse_text("Seet status, how many systems are green?",False)
    d=converse_text("See its status, how many systems are green?",False)
    return {
        "ok": a.get("ok") is True and b.get("ok") is False and c.get("ok") is True and d.get("ok") is True and c.get("session",{}).get("intent",{}).get("intent")=="seed_status",
        "good":a,
        "bad":b,
        "seet":c,
        "see_its":d
    }

def status():
    return {"created_at":now(),"version":"v133.2.0","ok":True,"history":history(10)}

if __name__=="__main__":
    a=sys.argv[1] if len(sys.argv)>1 else "status"
    if a=="text":
        msg=" ".join(x for x in sys.argv[2:] if x!="--no-speak")
        print(json.dumps(converse_text(msg,"--no-speak" not in sys.argv),indent=4,ensure_ascii=False))
    elif a=="listen":
        print(json.dumps(listen_and_answer(None,"--no-speak" not in sys.argv),indent=4,ensure_ascii=False))
    elif a=="test":
        print(json.dumps(test(),indent=4,ensure_ascii=False))
    else:
        print(json.dumps(status(),indent=4,ensure_ascii=False))
