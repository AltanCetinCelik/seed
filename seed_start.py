import json, subprocess, sys, time
from pathlib import Path
from datetime import datetime
STATE=Path('seed_start_state_v1361.json')
SERVICES=[
 {'name':'dashboard','start':[sys.executable,'seed_dashboard_v106.py','start'],'stop':[sys.executable,'seed_dashboard_v106.py','stop'],'module':'seed_dashboard_v106'},
 {'name':'avatar','start':[sys.executable,'seed_avatar2_v129.py','start'],'stop':[sys.executable,'seed_avatar2_v129.py','stop'],'module':'seed_avatar2_v129'},
 {'name':'proactive_rhythm','start':[sys.executable,'seed_proactive_rhythm_v108.py','start'],'stop':[sys.executable,'seed_proactive_rhythm_v108.py','stop'],'module':'seed_proactive_rhythm_v108'},
 {'name':'voice_runtime','start':[sys.executable,'seed_voice_runtime_v136.py','start','--no-speak'],'stop':[sys.executable,'seed_voice_runtime_v136.py','stop'],'module':'seed_voice_runtime_v136'},
 {'name':'voice_runtime_ui','start':[sys.executable,'seed_voice_runtime_ui_v136.py','start'],'stop':[sys.executable,'seed_voice_runtime_ui_v136.py','stop'],'module':'seed_voice_runtime_ui_v136','optional':True},
]
def now(): return datetime.now().isoformat(timespec='seconds')
def run(cmd,timeout=45):
    try:
        p=subprocess.run(cmd,capture_output=True,text=True,timeout=timeout); txt=(p.stdout or '').strip(); data=None
        if txt:
            try: data=json.loads(txt)
            except Exception: data={'raw':txt}
        return {'ok':p.returncode==0,'returncode':p.returncode,'cmd':cmd,'stdout':txt[-2500:],'stderr':(p.stderr or '')[-1200:],'data':data}
    except Exception as e: return {'ok':False,'cmd':cmd,'error':str(e)}
def svc_status(module):
    try:
        m=__import__(module,fromlist=['status'])
        if hasattr(m,'runtime_status'): return m.runtime_status()
        if hasattr(m,'status'): return m.status()
        return {'ok':False,'error':'no status'}
    except Exception as e: return {'ok':False,'error':str(e)}
def select(include_ui=False): return [s for s in SERVICES if include_ui or not s.get('optional')]
def save(obj): obj['updated_at']=now(); obj['version']='v136.1.0'; STATE.write_text(json.dumps(obj,indent=4,ensure_ascii=False)); return obj
def start(include_ui=False,dry_run=False):
    rows=[]
    for s in select(include_ui): rows.append({'name':s['name'],'result':{'ok':True,'dry_run':True,'cmd':s['start']} if dry_run else run(s['start'])})
    return {'ok':all(r['result'].get('ok') for r in rows),'state':save({'action':'start','include_ui':include_ui,'dry_run':dry_run,'results':rows}),'results':rows}
def stop(include_ui=True,dry_run=False):
    rows=[]
    for s in reversed(select(include_ui)): rows.append({'name':s['name'],'result':{'ok':True,'dry_run':True,'cmd':s['stop']} if dry_run else run(s['stop'])})
    return {'ok':all(r['result'].get('ok') for r in rows),'state':save({'action':'stop','include_ui':include_ui,'dry_run':dry_run,'results':rows}),'results':rows}
def status():
    rows=[{'name':s['name'],'status':svc_status(s['module'])} for s in SERVICES]
    try:
        import seed_runtime_polish_v1361 as p; compact=p.compact_status()
    except Exception as e: compact={'ok':False,'error':str(e)}
    return {'created_at':now(),'version':'v136.1.0','ok':True,'services':rows,'compact':compact}
def restart(include_ui=False,dry_run=False):
    a=stop(True,dry_run); time.sleep(.5); b=start(include_ui,dry_run); return {'ok':a.get('ok') and b.get('ok'),'stop':a,'start':b}
def test(): return {'created_at':now(),'version':'v136.1.0','ok':start(True,True).get('ok') and status().get('ok') and stop(True,True).get('ok')}
if __name__=='__main__':
    args=sys.argv[1:]; cmd=args[0] if args else 'status'; ui='--ui' in args; dry='--dry-run' in args
    if cmd=='start': print(json.dumps(start(ui,dry),indent=4,ensure_ascii=False))
    elif cmd=='stop': print(json.dumps(stop(True,dry),indent=4,ensure_ascii=False))
    elif cmd=='restart': print(json.dumps(restart(ui,dry),indent=4,ensure_ascii=False))
    elif cmd=='test': print(json.dumps(test(),indent=4,ensure_ascii=False))
    else: print(json.dumps(status(),indent=4,ensure_ascii=False))
