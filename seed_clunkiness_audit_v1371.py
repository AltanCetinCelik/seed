import json, subprocess, sys, time, glob
from pathlib import Path
from datetime import datetime

VERSION="v137.1.0"
REPORT=Path("seed_clunkiness_audit_v1371_report.json")

def now():
    return datetime.now().isoformat(timespec="seconds")

def run(cmd, timeout=120):
    start=time.time()
    try:
        p=subprocess.run(cmd,capture_output=True,text=True,timeout=timeout)
        return {"cmd":cmd,"ok":p.returncode==0,"returncode":p.returncode,"latency_seconds":round(time.time()-start,3),"stdout_bytes":len(p.stdout or ""),"stderr_bytes":len(p.stderr or ""),"stdout_tail":(p.stdout or "")[-1200:],"stderr_tail":(p.stderr or "")[-800:]}
    except Exception as e:
        return {"cmd":cmd,"ok":False,"error":str(e),"latency_seconds":round(time.time()-start,3)}

def audit():
    checks=[]
    for cmd in [
        [sys.executable,"seed_hygiene_status_v13623.py"],
        [sys.executable,"seed_service_supervisor_v1371.py","status"],
        [sys.executable,"seed_runtime_proxy_v1371.py","wake-text","status"],
        [sys.executable,"seed_log_optimizer_v1371.py","status"],
    ]:
        if Path(cmd[1]).exists():
            checks.append(run(cmd))
    files=[]
    for pat in ["*events.jsonl","*.log","seed_full_outputs_v1371/*.json"]:
        for p in glob.glob(pat):
            path=Path(p)
            if path.is_file():
                files.append({"path":str(path),"bytes":path.stat().st_size})
    files=sorted(files,key=lambda x:x["bytes"],reverse=True)[:20]
    problems=[]
    for c in checks:
        if not c.get("ok"):
            problems.append({"type":"command_failed","cmd":c.get("cmd"),"error":c.get("error") or c.get("stderr_tail")})
        if c.get("latency_seconds",0)>8:
            problems.append({"type":"slow_command","cmd":c.get("cmd"),"latency_seconds":c.get("latency_seconds")})
        if c.get("stdout_bytes",0)>20000:
            problems.append({"type":"huge_stdout","cmd":c.get("cmd"),"stdout_bytes":c.get("stdout_bytes")})
    for f in files:
        if f["bytes"]>750000:
            problems.append({"type":"large_log","path":f["path"],"bytes":f["bytes"]})
    score=max(0,100-len(problems)*8)
    report={"created_at":now(),"version":VERSION,"ok":True,"clunkiness_score":score,"problem_count":len(problems),"problems":problems,"checks":checks,"largest_files":files}
    REPORT.write_text(json.dumps(report,indent=4,ensure_ascii=False))
    return report

def text(r):
    lines=[f"Seed v137.1 Clunkiness Audit",f"Score: {r['clunkiness_score']}/100",f"Problems: {r['problem_count']}"]
    for p in r["problems"][:10]:
        lines.append("- "+json.dumps(p,ensure_ascii=False))
    return "\n".join(lines)

if __name__=="__main__":
    r=audit()
    if "--json" in sys.argv:
        print(json.dumps(r,indent=4,ensure_ascii=False))
    else:
        print(text(r))
