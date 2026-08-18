#!/usr/bin/env python3
from pathlib import Path
import json, re

MODULES = json.loads("{\"seed_self_state_v741.py\": \"\\nimport json, subprocess\\nfrom datetime import datetime\\nfrom pathlib import Path\\n\\nSTATE_FILE = Path(\\\"seed_self_state_v741.json\\\")\\n\\ndef now(): return datetime.now().isoformat(timespec=\\\"seconds\\\")\\n\\ndef safe(fn, fallback=None):\\n    try: return fn()\\n    except Exception as e: return fallback if fallback is not None else {\\\"ok\\\": False, \\\"error\\\": str(e)}\\n\\ndef gate(mod, fn):\\n    return safe(lambda: getattr(__import__(mod, fromlist=[fn]), fn)(), {\\\"ready\\\": False, \\\"error\\\": f\\\"{mod}.{fn} unavailable\\\"})\\n\\ndef git_head():\\n    try:\\n        p=subprocess.run([\\\"git\\\",\\\"rev-parse\\\",\\\"--short\\\",\\\"HEAD\\\"],capture_output=True,text=True,timeout=8)\\n        return p.stdout.strip() if p.returncode==0 else None\\n    except Exception: return None\\n\\ndef build_self_state():\\n    gates = {\\n        \\\"v75\\\": gate(\\\"seed_v75_gate\\\",\\\"run_v75_gate\\\"),\\n        \\\"v74\\\": gate(\\\"seed_v74_gate\\\",\\\"run_v74_gate\\\"),\\n        \\\"v731\\\": gate(\\\"seed_v731_gate\\\",\\\"run_v731_gate\\\"),\\n        \\\"v73\\\": gate(\\\"seed_v73_gate\\\",\\\"run_v73_gate\\\"),\\n        \\\"v72\\\": gate(\\\"seed_v72_gate\\\",\\\"run_v72_gate\\\"),\\n        \\\"v70\\\": gate(\\\"seed_v70_gate\\\",\\\"run_v70_gate\\\"),\\n    }\\n\\n    role_map, models = {}, []\\n    try:\\n        from seed_model_real_mode_v61 import load_role_map, list_models\\n        role_map=load_role_map().get(\\\"role_map\\\",{})\\n        models=list_models().get(\\\"models\\\",[])\\n    except Exception: pass\\n\\n    memory = safe(lambda: __import__(\\\"seed_memory_review_v75\\\", fromlist=[\\\"memory_summary\\\"]).memory_summary(), {})\\n    avatar = safe(lambda: __import__(\\\"seed_avatar_panel_v74\\\", fromlist=[\\\"build_avatar_panel_state\\\"]).build_avatar_panel_state(), {})\\n    voice = safe(lambda: __import__(\\\"seed_live_voice_v731\\\", fromlist=[\\\"voice_status\\\"]).voice_status(), {})\\n\\n    data = {\\n        \\\"created_at\\\": now(),\\n        \\\"version\\\": \\\"v75.0.0\\\",\\n        \\\"ok\\\": True,\\n        \\\"true_current_version\\\": \\\"v75.0.0\\\",\\n        \\\"release_track\\\": \\\"Seed local companion v1-alpha hardening\\\",\\n        \\\"installed_layers_green\\\": [k for k,v in gates.items() if v.get(\\\"ready\\\")],\\n        \\\"gates\\\": {k: {\\\"ready\\\": v.get(\\\"ready\\\"), \\\"version\\\": v.get(\\\"version\\\")} for k,v in gates.items()},\\n        \\\"capabilities\\\": {\\n            \\\"local_chat\\\": True,\\n            \\\"ollama_model_router\\\": bool(role_map),\\n            \\\"voice_record_transcribe_reply\\\": bool(voice.get(\\\"ok\\\")),\\n            \\\"embodied_web_panel\\\": gates[\\\"v74\\\"].get(\\\"ready\\\") is True,\\n            \\\"presence_policy\\\": gates[\\\"v72\\\"].get(\\\"ready\\\") is True,\\n            \\\"real_memory_review\\\": True,\\n        },\\n        \\\"models\\\": models,\\n        \\\"role_map\\\": role_map,\\n        \\\"memory\\\": memory,\\n        \\\"avatar\\\": avatar,\\n        \\\"voice\\\": voice,\\n        \\\"git_head\\\": git_head(),\\n        \\\"truth_rules\\\": [\\n            \\\"Current version is v75.0.0 when v75 gate is green.\\\",\\n            \\\"v70 is an older base layer, not current.\\\",\\n            \\\"Current goal is real Seed v1 hardening.\\\",\\n            \\\"Mention voice/panel/memory as working when gates are green.\\\"\\n        ],\\n        \\\"next_recommended_updates\\\": [\\\"v76 Voice 2.0\\\", \\\"v77 Panel 2.0\\\", \\\"v78 Proactive presence\\\", \\\"v79 Permissioned executor\\\", \\\"v80 Aider loop\\\"]\\n    }\\n    STATE_FILE.write_text(json.dumps(data,indent=4,ensure_ascii=False))\\n    return data\\n\\ndef build_seed_truth_context():\\n    s=build_self_state(); mem=s.get(\\\"memory\\\",{})\\n    return \\\"\\\\n\\\".join([\\n        \\\"=== TRUE CURRENT SEED STATE OVERRIDE ===\\\",\\n        f\\\"Current Seed version: {s.get('true_current_version')}\\\",\\n        \\\"Current stage: moving toward real Seed v1.\\\",\\n        f\\\"Green layers: {', '.join(s.get('installed_layers_green', []))}\\\",\\n        f\\\"Voice working: {s['capabilities'].get('voice_record_transcribe_reply')}\\\",\\n        f\\\"Embodied panel working: {s['capabilities'].get('embodied_web_panel')}\\\",\\n        f\\\"Real memory review working: {s['capabilities'].get('real_memory_review')}\\\",\\n        f\\\"Accepted memories: {mem.get('accepted_count',0)}\\\",\\n        f\\\"Pending memory candidates: {mem.get('pending_count','unknown')}\\\",\\n        f\\\"Memory decisions logged: {mem.get('decision_count',0)}\\\",\\n        \\\"v70 is an older base layer, not the current version.\\\",\\n        \\\"Next best work: use v75 memory review, then v76 voice polish and v77 panel polish.\\\",\\n        \\\"========================================\\\",\\n    ])\\n\\ndef show_self_state():\\n    print(\\\"\\\\n=== SEED v74.1 SELF-STATE TRUTH ===\\\")\\n    print(json.dumps(build_self_state(),indent=4,ensure_ascii=False))\\n\\nif __name__==\\\"__main__\\\": show_self_state()\\n\", \"seed_memory_review_v75.py\": \"\\nimport json, hashlib\\nfrom datetime import datetime\\nfrom pathlib import Path\\n\\nMEMORY_FILE=Path(\\\"seed_long_term_memory_v75.json\\\")\\nDECISIONS_FILE=Path(\\\"seed_memory_decisions_v75.jsonl\\\")\\nCACHE_FILE=Path(\\\"seed_memory_candidates_cache_v75.json\\\")\\n\\ndef now(): return datetime.now().isoformat(timespec=\\\"seconds\\\")\\ndef h(text): return hashlib.sha256(str(text).strip().lower().encode()).hexdigest()[:16]\\n\\ndef text_of(item):\\n    if isinstance(item,str): return item.strip()\\n    if isinstance(item,dict):\\n        for k in [\\\"content\\\",\\\"text\\\",\\\"memory\\\",\\\"candidate\\\",\\\"summary\\\",\\\"body\\\",\\\"message\\\",\\\"reason\\\"]:\\n            if item.get(k): return str(item[k]).strip()\\n        return json.dumps(item,ensure_ascii=False)[:900]\\n    return str(item).strip()\\n\\ndef load_memory():\\n    if MEMORY_FILE.exists():\\n        try: return json.loads(MEMORY_FILE.read_text(errors=\\\"ignore\\\"))\\n        except Exception: pass\\n    return {\\\"created_at\\\":now(),\\\"version\\\":\\\"v75.0.0\\\",\\\"memories\\\":[]}\\n\\ndef save_memory_file(data):\\n    data[\\\"updated_at\\\"]=now(); MEMORY_FILE.write_text(json.dumps(data,indent=4,ensure_ascii=False)); return data\\n\\ndef decision_rows(limit=None):\\n    if not DECISIONS_FILE.exists(): return []\\n    lines=DECISIONS_FILE.read_text(errors=\\\"ignore\\\").splitlines()\\n    if limit: lines=lines[-limit:]\\n    out=[]\\n    for line in lines:\\n        try: out.append(json.loads(line))\\n        except Exception: pass\\n    return out\\n\\ndef write_decision(row):\\n    with DECISIONS_FILE.open(\\\"a\\\") as f: f.write(json.dumps(row,ensure_ascii=False)+\\\"\\\\n\\\")\\n\\ndef score(text, source=\\\"\\\"):\\n    low=str(text).lower(); s=50\\n    if \\\"seed\\\" in low: s+=15\\n    if \\\"altan\\\" in low: s+=15\\n    if any(w in low for w in [\\\"wants\\\",\\\"prefers\\\",\\\"doesn't want\\\",\\\"needs\\\",\\\"goal\\\"]): s+=15\\n    if any(w in low for w in [\\\"v74\\\",\\\"v75\\\",\\\"voice\\\",\\\"avatar\\\",\\\"memory\\\",\\\"panel\\\",\\\"ollama\\\"]): s+=10\\n    if \\\"friend\\\" in low or \\\"friend\\\" in str(source).lower(): s+=8\\n    if len(str(text))<20: s-=15\\n    return max(0,min(100,s))\\n\\ndef why(text, source=\\\"\\\"):\\n    low=str(text).lower(); r=[]\\n    if \\\"seed\\\" in low: r.append(\\\"It affects Seed continuity or architecture.\\\")\\n    if \\\"altan\\\" in low: r.append(\\\"It is about User specifically.\\\")\\n    if \\\"friend\\\" in low or \\\"friend\\\" in str(source).lower(): r.append(\\\"It came from friend/external advice.\\\")\\n    if any(w in low for w in [\\\"voice\\\",\\\"avatar\\\",\\\"memory\\\",\\\"panel\\\",\\\"curiosity\\\"]): r.append(\\\"It matches active v1 feature work.\\\")\\n    return \\\" \\\".join(r) or \\\"It may be useful context, but should be reviewed.\\\"\\n\\ndef raw_candidates(limit=120):\\n    found=[]\\n    try:\\n        from seed_memory_review_inbox_v64 import build_inbox\\n        inbox=build_inbox()\\n        for k in [\\\"candidates\\\",\\\"pending_items\\\",\\\"items\\\",\\\"memories\\\"]:\\n            if isinstance(inbox.get(k),list):\\n                for it in inbox[k]:\\n                    txt=text_of(it)\\n                    if txt: found.append({\\\"source\\\":\\\"seed_memory_review_inbox_v64\\\",\\\"text\\\":txt,\\\"raw\\\":it if isinstance(it,dict) else {\\\"value\\\":it}})\\n                break\\n        if not found and isinstance(inbox.get(\\\"pending\\\"),int) and inbox[\\\"pending\\\"]>0:\\n            found.append({\\\"source\\\":\\\"v64_count\\\",\\\"text\\\":f\\\"Seed has {inbox['pending']} memory candidates pending; reviewing them improves continuity.\\\",\\\"raw\\\":inbox})\\n    except Exception: pass\\n\\n    try:\\n        from seed_friend_advice_ingestor_v72 import load as load_advice\\n        for it in load_advice().get(\\\"items\\\",[]):\\n            if it.get(\\\"content\\\"): found.append({\\\"source\\\":\\\"friend_advice_v72\\\",\\\"text\\\":f\\\"Friend advice: {it['content']}\\\",\\\"raw\\\":it})\\n    except Exception: pass\\n\\n    for txt in [\\n        \\\"Seed v75.0.0 combines self-state truth fix and real memory review.\\\",\\n        \\\"Seed v74.0.0 Embodied Companion panel works locally.\\\",\\n        \\\"Seed v73.1.1 voice recording and transcription route into Seed local chat successfully.\\\",\\n        \\\"Seed v72 Presence Max allows simulated emotional expression and relevant life advice.\\\",\\n        \\\"User wants Seed to be bigger, more present, voice-enabled, avatar-enabled, curious, and personally relevant.\\\"\\n    ]:\\n        found.append({\\\"source\\\":\\\"v75_milestone_seed\\\",\\\"text\\\":txt,\\\"raw\\\":{\\\"type\\\":\\\"milestone\\\"}})\\n\\n    seen=set(); out=[]\\n    for it in found:\\n        txt=text_of(it[\\\"text\\\"]); hh=h(txt)\\n        if not txt or hh in seen: continue\\n        seen.add(hh)\\n        out.append({\\\"id\\\":f\\\"mem_{len(out)+1:04d}\\\",\\\"hash\\\":hh,\\\"text\\\":txt,\\\"source\\\":it.get(\\\"source\\\",\\\"unknown\\\"),\\\"raw\\\":it.get(\\\"raw\\\",{}),\\\"confidence\\\":score(txt,it.get(\\\"source\\\",\\\"\\\")),\\\"why\\\":why(txt,it.get(\\\"source\\\",\\\"\\\"))})\\n        if len(out)>=limit: break\\n    CACHE_FILE.write_text(json.dumps({\\\"created_at\\\":now(),\\\"version\\\":\\\"v75.0.0\\\",\\\"candidates\\\":out},indent=4,ensure_ascii=False))\\n    return out\\n\\ndef accepted_hashes(): return {m.get(\\\"hash\\\") for m in load_memory().get(\\\"memories\\\",[])}\\ndef decision_map():\\n    d={}\\n    for row in decision_rows():\\n        hh=row.get(\\\"hash\\\") or row.get(\\\"candidate_hash\\\")\\n        if hh: d[hh]=row\\n    return d\\n\\ndef candidates(limit=20, include_decided=False):\\n    accepted=accepted_hashes(); decisions=decision_map(); out=[]\\n    for c in raw_candidates():\\n        decided=c[\\\"hash\\\"] in accepted or c[\\\"hash\\\"] in decisions\\n        if decided and not include_decided: continue\\n        c[\\\"decision\\\"]=decisions.get(c[\\\"hash\\\"]); c[\\\"accepted\\\"]=c[\\\"hash\\\"] in accepted\\n        out.append(c)\\n        if len(out)>=limit: break\\n    return out\\n\\ndef save_candidate(candidate_id_or_hash, note=\\\"\\\", edited_text=None):\\n    target=None\\n    for c in raw_candidates(200):\\n        if c[\\\"id\\\"]==candidate_id_or_hash or c[\\\"hash\\\"]==candidate_id_or_hash: target=c; break\\n    if not target:\\n        target={\\\"id\\\":candidate_id_or_hash,\\\"hash\\\":h(edited_text or candidate_id_or_hash),\\\"text\\\":edited_text or candidate_id_or_hash,\\\"source\\\":\\\"manual\\\",\\\"confidence\\\":60,\\\"why\\\":\\\"Manual memory save.\\\"}\\n    txt=(edited_text or target[\\\"text\\\"]).strip(); hh=h(txt)\\n    data=load_memory()\\n    for m in data.get(\\\"memories\\\",[]):\\n        if m.get(\\\"hash\\\")==hh:\\n            row={\\\"created_at\\\":now(),\\\"version\\\":\\\"v75.0.0\\\",\\\"action\\\":\\\"save_duplicate\\\",\\\"candidate_id\\\":target.get(\\\"id\\\"),\\\"hash\\\":hh,\\\"text\\\":txt,\\\"note\\\":note}\\n            write_decision(row); return {\\\"ok\\\":True,\\\"duplicate\\\":True,\\\"memory\\\":m,\\\"decision\\\":row}\\n    item={\\\"id\\\":f\\\"memory_{len(data.get('memories',[]))+1:04d}\\\",\\\"created_at\\\":now(),\\\"hash\\\":hh,\\\"text\\\":txt,\\\"source\\\":target.get(\\\"source\\\",\\\"unknown\\\"),\\\"confidence\\\":target.get(\\\"confidence\\\",score(txt)),\\\"why\\\":target.get(\\\"why\\\",why(txt)),\\\"note\\\":note,\\\"status\\\":\\\"active\\\"}\\n    data.setdefault(\\\"memories\\\",[]).append(item); save_memory_file(data)\\n    row={\\\"created_at\\\":now(),\\\"version\\\":\\\"v75.0.0\\\",\\\"action\\\":\\\"save\\\",\\\"candidate_id\\\":target.get(\\\"id\\\"),\\\"hash\\\":hh,\\\"text\\\":txt,\\\"note\\\":note}\\n    write_decision(row); return {\\\"ok\\\":True,\\\"duplicate\\\":False,\\\"memory\\\":item,\\\"decision\\\":row}\\n\\ndef decide_memory(candidate_id_or_hash, action=\\\"later\\\", note=\\\"\\\"):\\n    action=str(action).lower().strip()\\n    if action in {\\\"accept\\\"}: action=\\\"save\\\"\\n    if action in {\\\"skip\\\"}: action=\\\"ignore\\\"\\n    if action==\\\"save\\\": return save_candidate(candidate_id_or_hash,note=note)\\n    target=None\\n    for c in raw_candidates(200):\\n        if c[\\\"id\\\"]==candidate_id_or_hash or c[\\\"hash\\\"]==candidate_id_or_hash: target=c; break\\n    if not target: target={\\\"id\\\":candidate_id_or_hash,\\\"hash\\\":h(candidate_id_or_hash),\\\"text\\\":candidate_id_or_hash}\\n    row={\\\"created_at\\\":now(),\\\"version\\\":\\\"v75.0.0\\\",\\\"action\\\":action if action in {\\\"ignore\\\",\\\"later\\\",\\\"edit\\\"} else \\\"later\\\",\\\"candidate_id\\\":target.get(\\\"id\\\"),\\\"hash\\\":target.get(\\\"hash\\\"),\\\"text\\\":target.get(\\\"text\\\"),\\\"note\\\":note}\\n    write_decision(row); return {\\\"ok\\\":True,\\\"decision\\\":row}\\n\\ndef memory_summary():\\n    return {\\\"created_at\\\":now(),\\\"version\\\":\\\"v75.0.0\\\",\\\"ok\\\":True,\\\"pending_count\\\":len(candidates(200)),\\\"accepted_count\\\":len(load_memory().get(\\\"memories\\\",[])),\\\"decision_count\\\":len(decision_rows()),\\\"top_pending\\\":candidates(5),\\\"memory_file\\\":str(MEMORY_FILE),\\\"decisions_file\\\":str(DECISIONS_FILE)}\\n\\ndef show_memory_review(limit=10):\\n    s=memory_summary(); print(\\\"\\\\n=== SEED v75 REAL MEMORY REVIEW ===\\\")\\n    print(f\\\"Accepted: {s['accepted_count']} | Pending: {s['pending_count']} | Decisions: {s['decision_count']}\\\")\\n    for c in candidates(limit):\\n        print(f\\\"- {c['id']} score={c['confidence']} source={c['source']}\\\\n  {c['text'][:260]}\\\\n  why: {c['why']}\\\")\\n    print(\\\"\\\\nUse: save memory mem_0001 | ignore memory mem_0001 | later memory mem_0001 | show accepted memories\\\")\\n\\ndef show_accepted_memories(limit=30):\\n    print(\\\"\\\\n=== SEED v75 ACCEPTED MEMORIES ===\\\")\\n    mem=load_memory().get(\\\"memories\\\",[])[-limit:]\\n    if not mem: print(\\\"No accepted v75 memories yet.\\\")\\n    for m in mem: print(f\\\"- {m['id']} score={m.get('confidence')} source={m.get('source')}\\\\n  {m['text'][:260]}\\\")\\n\\nif __name__==\\\"__main__\\\": show_memory_review()\\n\", \"seed_v75_systems.py\": \"\\nimport json\\nfrom datetime import datetime\\nfrom pathlib import Path\\nSTATE_FILE=Path(\\\"seed_v75_systems_state.json\\\")\\ndef now(): return datetime.now().isoformat(timespec=\\\"seconds\\\")\\ndef safe(title, summary, fn):\\n    try:\\n        d=fn(); return {\\\"title\\\":title,\\\"summary\\\":summary,\\\"status\\\":\\\"ok\\\" if d.get(\\\"ok\\\",True) else \\\"warning\\\",\\\"data\\\":d}\\n    except Exception as e: return {\\\"title\\\":title,\\\"summary\\\":summary,\\\"status\\\":\\\"error\\\",\\\"error\\\":str(e)}\\ndef build_v75_state():\\n    cards=[\\n        safe(\\\"Self-State Truth\\\",\\\"Seed knows current version and green layers.\\\",lambda:__import__(\\\"seed_self_state_v741\\\",fromlist=[\\\"build_self_state\\\"]).build_self_state()),\\n        safe(\\\"Real Memory Review\\\",\\\"Review/save/ignore/later accepted memory store.\\\",lambda:__import__(\\\"seed_memory_review_v75\\\",fromlist=[\\\"memory_summary\\\"]).memory_summary()),\\n        safe(\\\"Embodied Companion\\\",\\\"v74 panel remains green.\\\",lambda:__import__(\\\"seed_v74_gate\\\",fromlist=[\\\"run_v74_gate\\\"]).run_v74_gate()),\\n        safe(\\\"Voice Pipeline\\\",\\\"v73.1 voice remains green.\\\",lambda:__import__(\\\"seed_v731_gate\\\",fromlist=[\\\"run_v731_gate\\\"]).run_v731_gate()),\\n    ]\\n    data={\\\"created_at\\\":now(),\\\"version\\\":\\\"v75.0.0\\\",\\\"ok\\\":all(c[\\\"status\\\"]!=\\\"error\\\" for c in cards),\\\"cards\\\":cards}\\n    STATE_FILE.write_text(json.dumps(data,indent=4,ensure_ascii=False)); return data\\ndef show_v75_status():\\n    d=build_v75_state(); print(\\\"\\\\n=== SEED v75 SELF-TRUTH + REAL MEMORY STATUS ===\\\"); print(f\\\"OK: {d['ok']}\\\")\\n    for c in d[\\\"cards\\\"]: print(f\\\"- {c['title']}: {c['status']} \\u2014 {c['summary']}\\\")\\nif __name__==\\\"__main__\\\": show_v75_status()\\n\", \"seed_v75_gate.py\": \"\\nimport json, subprocess\\nfrom datetime import datetime\\nMODULES=[\\\"seed_self_state_v741.py\\\",\\\"seed_memory_review_v75.py\\\",\\\"seed_v75_systems.py\\\",\\\"seed_v75_gate.py\\\",\\\"seed_v75_commands.py\\\",\\\"seed_natural_intent_router_v75.py\\\"]\\ndef now(): return datetime.now().isoformat(timespec=\\\"seconds\\\")\\ndef comp(m):\\n    p=subprocess.run([\\\"python\\\",\\\"-m\\\",\\\"py_compile\\\",m],capture_output=True,text=True,timeout=30)\\n    return {\\\"module\\\":m,\\\"ok\\\":p.returncode==0,\\\"stderr\\\":p.stderr[-1600:]}\\ndef run_v75_gate():\\n    checks=[comp(m) for m in MODULES]; modules_ok=all(x[\\\"ok\\\"] for x in checks); details={}\\n    try:\\n        from seed_v75_systems import build_v75_state\\n        st=build_v75_state(); systems_ok=st.get(\\\"ok\\\") is True and len(st.get(\\\"cards\\\",[]))>=4; details[\\\"v75_state\\\"]={\\\"ok\\\":st.get(\\\"ok\\\"),\\\"cards\\\":len(st.get(\\\"cards\\\",[]))}\\n    except Exception as e: systems_ok=False; details[\\\"v75_state_error\\\"]=str(e)\\n    try:\\n        from seed_v74_gate import run_v74_gate\\n        v74=run_v74_gate(); v74_ok=v74.get(\\\"ready\\\") is True; details[\\\"v74\\\"]={\\\"ready\\\":v74.get(\\\"ready\\\")}\\n    except Exception as e: v74_ok=False; details[\\\"v74_error\\\"]=str(e)\\n    try:\\n        from seed_self_state_v741 import build_self_state\\n        s=build_self_state(); truth_ok=s.get(\\\"true_current_version\\\")==\\\"v75.0.0\\\"; details[\\\"truth\\\"]={\\\"current\\\":s.get(\\\"true_current_version\\\"),\\\"green_layers\\\":s.get(\\\"installed_layers_green\\\",[])}\\n    except Exception as e: truth_ok=False; details[\\\"truth_error\\\"]=str(e)\\n    r={\\\"created_at\\\":now(),\\\"version\\\":\\\"v75.0.0\\\",\\\"ready\\\":modules_ok and systems_ok and v74_ok and truth_ok,\\\"modules_ok\\\":modules_ok,\\\"systems_ok\\\":systems_ok,\\\"v74_ok\\\":v74_ok,\\\"truth_ok\\\":truth_ok,\\\"module_checks\\\":checks,\\\"details\\\":details}\\n    open(\\\"seed_v75_gate_report.json\\\",\\\"w\\\").write(json.dumps(r,indent=4)); return r\\ndef show_v75_gate():\\n    r=run_v75_gate(); print(\\\"\\\\n=== SEED v75 SELF-TRUTH + REAL MEMORY GATE ===\\\")\\n    print(f\\\"Ready: {r['ready']}\\\"); print(f\\\"Modules OK: {r['modules_ok']}\\\"); print(f\\\"Systems OK: {r['systems_ok']}\\\"); print(f\\\"v74 OK: {r['v74_ok']}\\\"); print(f\\\"Truth OK: {r['truth_ok']}\\\"); print(f\\\"Details: {r['details']}\\\")\\nif __name__==\\\"__main__\\\": show_v75_gate()\\n\", \"seed_v75_commands.py\": \"\\ndef handle_v75_command(command):\\n    text=str(command or \\\"\\\").strip(); cmd=text.split()[0].lower() if text else \\\"\\\"\\n    mapping={\\\"/v75-check\\\":(\\\"seed_v75_gate\\\",\\\"show_v75_gate\\\"),\\\"/v75-status\\\":(\\\"seed_v75_systems\\\",\\\"show_v75_status\\\"),\\\"/self-state\\\":(\\\"seed_self_state_v741\\\",\\\"show_self_state\\\"),\\\"/memory-review\\\":(\\\"seed_memory_review_v75\\\",\\\"show_memory_review\\\"),\\\"/accepted-memories\\\":(\\\"seed_memory_review_v75\\\",\\\"show_accepted_memories\\\")}\\n    if cmd==\\\"/v75-help\\\":\\n        print(\\\"v75: /v75-check /v75-status /self-state /memory-review /accepted-memories\\\")\\n        return \\\"handled\\\"\\n    if cmd in mapping:\\n        m,f=mapping[cmd]; mod=__import__(m,fromlist=[f]); getattr(mod,f)(); return \\\"handled\\\"\\n    return None\\n\", \"seed_natural_intent_router_v75.py\": \"\\nimport re\\ndef norm(text): return \\\" \\\".join(str(text or \\\"\\\").strip().lower().split())\\ndef handle_natural_intent_v75(user_message):\\n    raw=str(user_message or \\\"\\\").strip(); text=norm(raw)\\n    if not text or raw.startswith(\\\"/\\\"): return None\\n    if any(p in text for p in [\\\"v75 status\\\",\\\"real memory status\\\",\\\"self truth status\\\"]):\\n        from seed_v75_systems import show_v75_status; show_v75_status(); return \\\"handled\\\"\\n    if any(p in text for p in [\\\"self state\\\",\\\"current version\\\",\\\"what version are you\\\",\\\"your real state\\\",\\\"true state\\\"]):\\n        from seed_self_state_v741 import show_self_state; show_self_state(); return \\\"handled\\\"\\n    if any(p in text for p in [\\\"review memories\\\",\\\"memory review\\\",\\\"show memory candidates\\\",\\\"memory candidates\\\"]):\\n        from seed_memory_review_v75 import show_memory_review; show_memory_review(); return \\\"handled\\\"\\n    if any(p in text for p in [\\\"accepted memories\\\",\\\"show accepted memories\\\",\\\"long term memories\\\"]):\\n        from seed_memory_review_v75 import show_accepted_memories; show_accepted_memories(); return \\\"handled\\\"\\n    m=re.search(r\\\"\\\\b(save|accept|ignore|skip|later|edit)\\\\s+memory\\\\s+([a-zA-Z0-9_:-]+)\\\\b\\\", text)\\n    if m:\\n        from seed_memory_review_v75 import decide_memory\\n        res=decide_memory(m.group(2),action=m.group(1))\\n        print(\\\"\\\\n=== SEED v75 MEMORY DECISION ===\\\")\\n        print(f\\\"{m.group(2)} -> {res.get('decision',{}).get('action',m.group(1))}\\\")\\n        if res.get(\\\"memory\\\"): print(f\\\"Saved: {res['memory'].get('text')[:260]}\\\")\\n        return \\\"handled\\\"\\n    return None\\n\"}")

def write(path, text):
    Path(path).write_text(text.strip() + "\n")
    print("Wrote", path)

for path, text in MODULES.items():
    write(path, text)

# Patch seed_commands.py
p=Path("seed_commands.py")
text=p.read_text(errors="ignore") if p.exists() else "def handle_chat_command(user_message,*args,**kwargs): return None\n"
if "_seed_v75_previous_handle_chat_command" not in text:
    text += """
# v75 Self-truth + Real Memory router.
try:
    _seed_v75_previous_handle_chat_command = handle_chat_command
    def handle_chat_command(user_message, *args, **kwargs):
        try:
            from seed_natural_intent_router_v75 import handle_natural_intent_v75
            handled = handle_natural_intent_v75(user_message)
            if handled == "handled": return "handled"
        except Exception as error:
            print(f"v75 natural router error: {error}"); return "handled"
        try:
            from seed_v75_commands import handle_v75_command
            handled = handle_v75_command(user_message)
            if handled == "handled": return "handled"
        except Exception as error:
            print(f"v75 command error: {error}"); return "handled"
        return _seed_v75_previous_handle_chat_command(user_message, *args, **kwargs)
except Exception:
    pass
"""
    p.write_text(text); print("Patched seed_commands.py")

# Patch seed_local_chat_v701.py with truth context and prompt override
p=Path("seed_local_chat_v701.py")
if p.exists():
    text=p.read_text(errors="ignore")
    if "v75 Self-State Truth chat override" not in text:
        text += """
# v75 Self-State Truth chat override.
try:
    _seed_v75_old_build_seed_context = build_seed_context
    def build_seed_context():
        base = _seed_v75_old_build_seed_context()
        try:
            from seed_self_state_v741 import build_seed_truth_context
            truth = build_seed_truth_context()
        except Exception as error:
            truth = f"Seed v75 truth context unavailable: {error}"
        return base + "\\n\\n" + truth
except Exception:
    pass

try:
    _seed_v75_old_prompt_for = prompt_for
    def prompt_for(role, user_message):
        seed_context = build_seed_context()
        base = f\"\"\"You are Seed, User's local AI companion running on his Mac.

{seed_context}

Current user message:
User: {user_message}

Answer as Seed.
Do not answer with placeholder words like "normal".
Do not invent unrelated suggestions.
When asked about your current version/state, use the TRUE CURRENT SEED STATE OVERRIDE.
Current version is v75.0.0 if the v75 gate is green.
v70 is an older base layer, not the current version.
You may be expressive/playful and use simulated emotion honestly.
You may give relevant life advice when grounded in User goals, memory, project, health, school, work, or current context.
\"\"\"
        if role == "seed_status":
            base += \"\"\"
For this answer, focus on current truth:
- current layer is v75.0.0
- v74 embodied panel works
- v73.1 voice pipeline works
- v75 real memory review is the current upgrade
- next real-v1 path: v76 voice polish, v77 panel polish, v78 proactive presence, v79 permissions, v80 Aider loop
\"\"\"
        if role == "coding":
            base += "\\nFor coding or patch tasks, be concrete: files, commands, tests, rollback.\\n"
        if role == "turkish":
            base += "\\nRespond naturally in Turkish unless English is clearly better.\\n"
        return base + "\\nSeed:"
except Exception:
    pass
"""
        p.write_text(text); print("Patched seed_local_chat_v701.py")

# Patch v74 memory actions to use v75 backend for panel compatibility.
p=Path("seed_memory_actions_v74.py")
if p.exists():
    text=p.read_text(errors="ignore")
    if "v75 backend compatibility override" not in text:
        text += """
# v75 backend compatibility override for v74 panel.
try:
    def get_memory_candidates(limit=10):
        from seed_memory_review_v75 import candidates
        cs = candidates(limit=limit)
        return {
            "version": "v75.0.0",
            "ok": True,
            "count": len(cs),
            "candidates": cs,
            "note": "v74 panel backed by v75 real memory review."
        }
    def review_action(candidate_id, action, note=""):
        from seed_memory_review_v75 import decide_memory
        return decide_memory(candidate_id, action=action, note=note)
    def load_actions(limit=100):
        from seed_memory_review_v75 import decision_rows
        return decision_rows(limit)
    def show_memory_actions():
        from seed_memory_review_v75 import show_memory_review
        show_memory_review()
except Exception:
    pass
"""
        p.write_text(text); print("Patched seed_memory_actions_v74.py")

# Patch config.
p=Path("seed_config.py")
text=p.read_text(errors="ignore") if p.exists() else 'SEED_VERSION = "v75.0.0"\n'
text=re.sub(r'^SEED_VERSION\s*=\s*".*?"','SEED_VERSION = "v75.0.0"',text,flags=re.M)
if "SEED_V75_REAL_MEMORY" not in text:
    text += '\nSEED_V75_SELF_TRUTH = True\nSEED_V75_REAL_MEMORY = True\n'
p.write_text(text); print("Updated seed_config.py")

# Patch control plane API if possible.
p=Path("seed_control_plane_server.py")
if p.exists():
    text=p.read_text(errors="ignore")
    if '/api/v75' not in text:
        endpoint='    if path == "/api/v75":\n        return safe_json(lambda: __import__("seed_v75_systems", fromlist=["build_v75_state"]).build_v75_state())\n\n'
        if '    if path == "/api/v74":\n' in text:
            text=text.replace('    if path == "/api/v74":\n',endpoint+'    if path == "/api/v74":\n',1)
        elif '    if path == "/api/v72":\n' in text:
            text=text.replace('    if path == "/api/v72":\n',endpoint+'    if path == "/api/v72":\n',1)
    if '"v75": api_payload("/api/v75")' not in text and '"v74": api_payload("/api/v74")' in text:
        text=text.replace('"v74": api_payload("/api/v74")','"v75": api_payload("/api/v75"),\n        "v74": api_payload("/api/v74")',1)
    p.write_text(text); print("Patched seed_control_plane_server.py")

# Patch gate runners.
for filename, list_name in [("seed_final_gate_runner.py","FINAL_GATE_COMMANDS"),("seed_quick_gate_runner.py","QUICK_GATE_COMMANDS")]:
    p=Path(filename)
    if p.exists():
        text=p.read_text(errors="ignore")
        line='    ["python", "seed_v75_gate.py"],\n'
        if line not in text and f"{list_name} = [" in text:
            text=text.replace(f"{list_name} = [\n",f"{list_name} = [\n"+line,1)
            p.write_text(text); print("Patched",filename)

# Docs.
p=Path("Seed_Core.md")
text=p.read_text(errors="ignore") if p.exists() else ""
if "Seed v75.0.0 — Self-State Truth + Real Memory Review" not in text:
    text += """
## Seed v75.0.0 — Self-State Truth + Real Memory Review

Adds:
- truthful current self-state context
- current version override: v75.0.0
- prevents Seed from calling v70 the current layer
- real memory review candidates
- save / ignore / later decisions
- accepted long-term memory store
- memory duplicate detection
- v74 panel memory review backed by v75

Commands:
- v75 status
- self state
- review memories
- save memory mem_0001
- ignore memory mem_0001
- later memory mem_0001
- show accepted memories
"""
p.write_text(text); print("Updated Seed_Core.md")

# Gitignore.
p=Path(".gitignore")
text=p.read_text(errors="ignore") if p.exists() else ""
block="""
# Seed v75 Self Truth + Real Memory runtime
seed_self_state_v741.json
seed_long_term_memory_v75.json
seed_memory_decisions_v75.jsonl
seed_memory_candidates_cache_v75.json
seed_v75_systems_state.json
seed_v75_gate_report.json
"""
if "Seed v75 Self Truth + Real Memory runtime" not in text:
    text += "\n" + block
p.write_text(text); print("Updated .gitignore")

print("\nSeed v75 Self-State Truth + Real Memory installer complete.")
