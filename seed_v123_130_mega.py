import json,sys
def main():
    a=sys.argv[1] if len(sys.argv)>1 else "status"; rest=sys.argv[2:]
    if a=="status":
        import seed_v123_130_systems as s; print(json.dumps(s.status(),indent=4,ensure_ascii=False))
    elif a=="gate":
        import seed_v123_130_gate as g; g.show()
    elif a=="research":
        import seed_deep_research_v123 as r; sub=rest[0] if rest else "status"
        if sub=="create": print(json.dumps(r.create(" ".join(rest[1:])),indent=4,ensure_ascii=False))
        elif sub=="local-rag": print(json.dumps(r.local_rag(rest[1]," ".join(rest[2:])),indent=4,ensure_ascii=False))
        elif sub=="extract": print(json.dumps(r.extract(rest[1]),indent=4,ensure_ascii=False))
        elif sub=="brief": print(r.brief(rest[1]))
        else: print(json.dumps(r.status(),indent=4,ensure_ascii=False))
    elif a=="kg":
        import seed_knowledge_graph_v124 as kg; print(json.dumps(kg.status(),indent=4,ensure_ascii=False))
    elif a=="route":
        import seed_device_router_v125 as dr; print(json.dumps(dr.route(" ".join(rest)),indent=4,ensure_ascii=False))
    elif a=="avatar":
        import seed_avatar2_v129 as av; sub=rest[0] if rest else "status"; print(json.dumps(av.start() if sub=="start" else av.stop() if sub=="stop" else av.status(),indent=4,ensure_ascii=False))
    else: print("Commands: status | gate | research create/local-rag/extract/brief | kg | route | avatar start/stop/status")
if __name__=="__main__": main()
