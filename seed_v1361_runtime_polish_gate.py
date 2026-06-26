import json, subprocess, sys
from pathlib import Path
from datetime import datetime
MODULES=['seed_runtime_polish_v1361.py','seed_start.py','seed_v1361_runtime_polish_gate.py']
def now(): return datetime.now().isoformat(timespec='seconds')
def comp(m):
    p=subprocess.run([sys.executable,'-m','py_compile',m],capture_output=True,text=True,timeout=30); return {'module':m,'ok':p.returncode==0,'stderr':p.stderr[-1000:]}
def run_gate():
    checks=[comp(m) for m in MODULES]; modules_ok=all(c['ok'] for c in checks); details={}
    try:
        import seed_runtime_polish_v1361 as p; pt=p.test(); details['polish']=pt; polish_ok=pt.get('ok') is True
    except Exception as e: polish_ok=False; details['polish']={'ok':False,'error':str(e)}
    try:
        import seed_start; st=seed_start.test(); details['seed_start']=st; start_ok=st.get('ok') is True
    except Exception as e: start_ok=False; details['seed_start']={'ok':False,'error':str(e)}
    report={'created_at':now(),'version':'v136.1.0','ready':modules_ok and polish_ok and start_ok,'modules_ok':modules_ok,'polish_ok':polish_ok,'seed_start_ok':start_ok,'checks':checks,'details':details}
    Path('seed_v1361_runtime_polish_gate_report.json').write_text(json.dumps(report,indent=4,ensure_ascii=False)); return report
def show():
    r=run_gate(); print('\n=== SEED v136.1 RUNTIME POLISH GATE ==='); print(f"Ready: {r['ready']}"); print(f"Modules OK: {r['modules_ok']}"); print(f"Polish OK: {r['polish_ok']}"); print(f"Seed Start OK: {r['seed_start_ok']}")
    try:
        st=r['details']['polish']['status']; print(f"Approvals pending: {st.get('approval_pending')}"); print(f"Open tasks: {st.get('open_tasks')} / test tasks: {st.get('test_tasks')}")
    except Exception: pass
if __name__=='__main__': show()
