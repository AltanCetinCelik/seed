import json, sys
def main():
    a=sys.argv[1] if len(sys.argv)>1 else "status"; rest=sys.argv[2:]
    if a=="status":
        import seed_v131_135_systems as s; print(json.dumps(s.status(),indent=4,ensure_ascii=False))
    elif a=="gate":
        import seed_v131_135_gate as g; g.show()
    elif a=="listen":
        import seed_voice_input_v131 as vi; print(json.dumps(vi.listen_once(int(rest[0]) if rest and rest[0].isdigit() else None),indent=4,ensure_ascii=False))
    elif a=="voice":
        import seed_voice_conversation_v133 as vc
        if rest and rest[0]=="text": print(json.dumps(vc.converse_text(" ".join(x for x in rest[1:] if x!="--no-speak"),"--no-speak" not in rest),indent=4,ensure_ascii=False))
        else: print(json.dumps(vc.listen_and_answer(None,"--no-speak" not in rest),indent=4,ensure_ascii=False))
    elif a=="wake":
        import seed_real_wake_v132 as w; sub=rest[0] if rest else "status"
        if sub=="start": print(json.dumps(w.start(),indent=4,ensure_ascii=False))
        elif sub=="stop": print(json.dumps(w.stop(),indent=4,ensure_ascii=False))
        elif sub=="match": print(json.dumps(w.match_text(" ".join(rest[1:])),indent=4,ensure_ascii=False))
        else: print(json.dumps(w.status(),indent=4,ensure_ascii=False))
    elif a=="presence":
        import seed_proactive_presence_v134 as p; sub=rest[0] if rest else "status"
        print(json.dumps(p.suggestion() if sub=="suggest" else p.reflection() if sub=="reflect" else p.status(),indent=4,ensure_ascii=False))
    elif a=="assimilate":
        import seed_repo_assimilation_v135 as ra; sub=rest[0] if rest else "status"
        print(json.dumps(ra.audit() if sub=="audit" else ra.promote() if sub=="promote" else ra.status(),indent=4,ensure_ascii=False))
    else: print("Commands: status | gate | listen | voice text/listen | wake start/stop/match/status | presence suggest/reflect/status | assimilate audit/promote/status")
if __name__=="__main__": main()
