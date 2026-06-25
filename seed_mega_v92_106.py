import json, sys
def main():
    a=sys.argv[1] if len(sys.argv)>1 else "status"
    if a in ["start","stop","doctor","status"]:
        import seed_supervisor_v92 as s
        print(json.dumps(s.start() if a=="start" else s.stop() if a=="stop" else s.doctor() if a=="doctor" else s.supervisor_status(),indent=4,ensure_ascii=False))
    elif a=="dashboard":
        import seed_dashboard_v106 as d; print(json.dumps(d.start(),indent=4))
    elif a=="eval":
        import seed_eval_v107 as e; print(json.dumps(e.run(),indent=4,ensure_ascii=False))
if __name__=="__main__": main()
