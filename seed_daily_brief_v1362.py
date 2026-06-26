import json, sys
from datetime import datetime
def now(): return datetime.now().isoformat(timespec="seconds")
def brief():
    try:
        import seed_hygiene_center_v1362 as h
        scan=h.scan()
    except Exception as e: return {"created_at":now(),"version":"v136.2.0","ok":False,"error":str(e)}
    lines=["Seed Daily Brief v136.2",f"Hygiene: {scan['hygiene']['score']}/100 ({scan['hygiene']['grade']})",f"Runtime: {'alive' if scan['runtime'].get('alive') else 'stopped'}",f"Last answer: {scan['runtime'].get('last_answer')}",f"Pending approvals: {scan['approval'].get('pending_count')}",f"Open tasks: {scan['tasks'].get('open_count')} / test tasks: {scan['tasks'].get('test_task_count')}",f"Duplicate memory entries: {scan['memory'].get('duplicate_count')}"]
    if scan.get("suggestions"):
        lines.append("Suggested next actions:")
        [lines.append(f"- {s['message']}") for s in scan["suggestions"]]
    return {"created_at":now(),"version":"v136.2.0","ok":True,"text":"\n".join(lines),"scan":scan}
if __name__=="__main__":
    o=brief()
    print(json.dumps(o,indent=4,ensure_ascii=False) if "--json" in sys.argv else o.get("text",json.dumps(o,indent=4,ensure_ascii=False)))
