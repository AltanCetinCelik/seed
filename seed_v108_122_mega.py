import json,sys
def main():
    a=sys.argv[1] if len(sys.argv)>1 else "status"; rest=sys.argv[2:]
    if a=="status":
        import seed_v108_122_systems as s; print(json.dumps(s.status(),indent=4,ensure_ascii=False))
    elif a=="gate":
        import seed_v108_122_gate as g; g.show()
    elif a=="proactive":
        import seed_proactive_rhythm_v108 as p; sub=rest[0] if rest else "status"; print(json.dumps(p.start("--speak" in rest) if sub=="start" else p.stop() if sub=="stop" else p.tick("--speak" in rest) if sub=="tick" else p.status(),indent=4,ensure_ascii=False))
    elif a=="rag2":
        import seed_rag2_v122 as r; sub=rest[0] if rest else "status"; print(json.dumps(r.index(rest[1] if len(rest)>1 else "seed") if sub=="index" else r.search(" ".join(rest[1:])) if sub=="search" else r.status(),indent=4,ensure_ascii=False))
    else: print("Commands: status | gate | proactive start/stop/tick/status | rag2 index/search/status")
if __name__=="__main__": main()
