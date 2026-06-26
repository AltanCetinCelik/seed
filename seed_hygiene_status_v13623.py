import json, sys
from datetime import datetime

VERSION="v136.2.3"

def now():
    return datetime.now().isoformat(timespec="seconds")

def base_scan():
    try:
        import seed_hygiene_center_v1362 as h
        return h.scan()
    except Exception as e:
        return {"ok":False,"error":str(e)}

def scan():
    b = base_scan()
    try:
        import seed_approval_resolver_v13623 as resolver
        eff = resolver.effective_status()
        b["approval_v13623"] = eff
        # Override visible pending count with effective pending count.
        if isinstance(b.get("approval"), dict):
            b["approval"]["raw_pending_count"] = b["approval"].get("pending_count")
            b["approval"]["pending_count"] = eff.get("effective_pending_count")
            b["approval"]["pending_effective"] = eff.get("effective_pending")
            b["approval"]["filtered"] = eff.get("filtered")
        # Re-score with fixed approval count.
        reasons = []
        score = 100
        if not b.get("runtime",{}).get("alive"):
            score -= 10; reasons.append("voice_runtime_not_alive")
        pc = eff.get("effective_pending_count") or 0
        if pc:
            score -= min(25, pc*15); reasons.append(f"{pc}_pending_approval")
        tc = b.get("tasks",{}).get("test_task_count") or 0
        if tc:
            score -= min(20, tc*15); reasons.append(f"{tc}_test_task")
        dc = b.get("memory",{}).get("duplicate_count") or 0
        if dc:
            score -= min(20, dc*4); reasons.append(f"{dc}_duplicate_memory_entries")
        if b.get("logs",{}).get("large_logs"):
            score -= 5; reasons.append("large_logs")
        b["hygiene_v13623"] = {"score": max(0, score), "reasons": reasons, "grade": "clean" if score>=90 else "needs_review" if score>=70 else "dirty"}
    except Exception as e:
        b["approval_v13623_error"] = str(e)
    b["created_at_v13623"] = now()
    b["version_v13623"] = VERSION
    return b

def text():
    d=scan()
    h=d.get("hygiene_v13623") or d.get("hygiene",{})
    lines=[
        "Seed v136.2.3 Effective Hygiene Status",
        f"Hygiene score: {h.get('score')}/100 ({h.get('grade')})",
        f"Reasons: {', '.join(h.get('reasons',[])) or 'none'}",
        f"Voice runtime: {'alive' if d.get('runtime',{}).get('alive') else 'stopped'} pid={d.get('runtime',{}).get('pid')}",
        f"Approvals pending effective: {d.get('approval_v13623',{}).get('effective_pending_count')}",
        f"Approvals pending raw: {d.get('approval_v13623',{}).get('raw_pending_count')}",
        f"Open tasks: {d.get('tasks',{}).get('open_count')} / test tasks: {d.get('tasks',{}).get('test_task_count')}",
        f"Memory count: {d.get('memory',{}).get('memory_count')} / duplicate entries: {d.get('memory',{}).get('duplicate_count')}",
        f"Last answer: {d.get('runtime',{}).get('last_answer')}",
    ]
    return "\n".join(lines)

if __name__=="__main__":
    if "--json" in sys.argv:
        print(json.dumps(scan(), indent=4, ensure_ascii=False))
    else:
        print(text())
