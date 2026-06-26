import json, sys
from pathlib import Path
from datetime import datetime
REPORT=Path('seed_runtime_polish_v1361_report.json')
def now(): return datetime.now().isoformat(timespec='seconds')
def safe(mod,fn='status'):
    try:
        m=__import__(mod,fromlist=[fn])
        return {'ok':True,'data':getattr(m,fn)()}
    except Exception as e: return {'ok':False,'error':str(e)}
def voice_runtime():
    try:
        import seed_voice_runtime_v136 as rt
        st=rt.runtime_status(); ev=(st.get('recent_events') or [])[-1] if st.get('recent_events') else st.get('state',{}).get('last_event')
        ans=intent=trans=None
        if isinstance(ev,dict):
            res=ev.get('result') or ev.get('runtime',{}).get('result') or {}; sess=res.get('session') or {}
            ans=sess.get('answer'); intent=sess.get('intent',{}).get('intent') or ev.get('intent',{}).get('intent'); trans=sess.get('input') or res.get('listen',{}).get('transcript',{}).get('text')
        return {'ok':True,'alive':st.get('alive'),'pid':st.get('pid'),'mode':st.get('settings',{}).get('mode'),'last_intent':intent,'last_transcript':trans,'last_answer':ans,'raw':st}
    except Exception as e: return {'ok':False,'error':str(e)}
def approvals():
    try:
        import seed_action_approval_v107 as a
        st=a.status(); return {'ok':True,'pending_count':st.get('pending_count',0),'status':st}
    except Exception as e: return {'ok':False,'pending_count':None,'error':str(e)}
def tasks():
    try:
        import seed_tasks_v99 as t
        st=t.status(); op=st.get('open',st.get('tasks',[])); tests=[x for x in op if 'test' in (x.get('title','')+' '+x.get('description','')).lower()]
        return {'ok':True,'open_count':len(op),'test_task_count':len(tests),'test_tasks':tests,'status':st}
    except Exception as e: return {'ok':False,'open_count':None,'test_task_count':None,'error':str(e)}
def memory():
    try:
        import seed_memory_garden3_v112 as m
        st=m.status(); return {'ok':True,'count':st.get('count'),'by_type':st.get('by_type',{}),'latest':st.get('latest',[])[:3]}
    except Exception as e: return {'ok':False,'error':str(e)}
def compact_status():
    rt=voice_runtime(); ap=approvals(); tk=tasks(); mem=memory()
    try:
        import seed_v131_135_systems as s
        ss=s.status(); sys_green=f"{ss.get('ok_count')}/{ss.get('total')}"
    except Exception: sys_green='unknown'
    out={'created_at':now(),'version':'v136.1.0','ok':True,'voice_runtime':{'alive':rt.get('alive'),'pid':rt.get('pid'),'mode':rt.get('mode'),'last_intent':rt.get('last_intent'),'last_transcript':rt.get('last_transcript'),'last_answer':rt.get('last_answer')},'systems_v131_135':sys_green,'approval_pending':ap.get('pending_count'),'open_tasks':tk.get('open_count'),'test_tasks':tk.get('test_task_count'),'memory_count':mem.get('count'),'memory_by_type':mem.get('by_type'),'raw':{'runtime':rt,'approval':ap,'tasks':tk,'memory':mem}}
    REPORT.write_text(json.dumps(out,indent=4,ensure_ascii=False)); return out
def suggestions():
    st=compact_status(); out=[]
    if st.get('test_tasks',0): out.append({'type':'old_test_task','message':'Old test task is still open; review before closing.'})
    if st.get('approval_pending',0): out.append({'type':'pending_approval','message':'Pending approval exists; review before more autonomy.'})
    return {'created_at':now(),'version':'v136.1.0','ok':True,'suggestions':out,'status':st}
def clean_logs(max_events=300):
    p=Path('seed_voice_runtime_v136_events.jsonl')
    if not p.exists(): return {'ok':True,'changed':False,'reason':'no log'}
    lines=p.read_text(errors='ignore').splitlines()
    if len(lines)<=max_events: return {'ok':True,'changed':False,'line_count':len(lines)}
    b=Path(f'seed_voice_runtime_v136_events_backup_{int(datetime.now().timestamp())}.jsonl'); b.write_text('\n'.join(lines)+'\n'); p.write_text('\n'.join(lines[-max_events:])+'\n')
    return {'ok':True,'changed':True,'before':len(lines),'after':max_events,'backup':str(b)}
def text_status():
    st=compact_status(); return '\n'.join([f"Seed v136.1 Runtime Polish",f"Voice runtime: {'alive' if st['voice_runtime'].get('alive') else 'stopped'} pid={st['voice_runtime'].get('pid')}",f"Last intent: {st['voice_runtime'].get('last_intent')}",f"Last answer: {st['voice_runtime'].get('last_answer')}",f"v131-v135 systems: {st.get('systems_v131_135')}",f"Approvals pending: {st.get('approval_pending')}",f"Open tasks: {st.get('open_tasks')} / test tasks: {st.get('test_tasks')}",f"Memory count: {st.get('memory_count')} {st.get('memory_by_type')}"])
def test():
    st=compact_status(); sg=suggestions(); return {'created_at':now(),'version':'v136.1.0','ok':'voice_runtime' in st and sg.get('ok') is True,'status':st,'suggestions':sg}
if __name__=='__main__':
    a=sys.argv[1] if len(sys.argv)>1 else 'status'
    if a=='suggest': print(json.dumps(suggestions(),indent=4,ensure_ascii=False))
    elif a=='clean-logs': print(json.dumps(clean_logs(int(sys.argv[2]) if len(sys.argv)>2 and sys.argv[2].isdigit() else 300),indent=4,ensure_ascii=False))
    elif a=='tasks': print(json.dumps(tasks(),indent=4,ensure_ascii=False))
    elif a=='approvals': print(json.dumps(approvals(),indent=4,ensure_ascii=False))
    elif a=='text': print(text_status())
    elif a=='test': print(json.dumps(test(),indent=4,ensure_ascii=False))
    else: print(json.dumps(compact_status(),indent=4,ensure_ascii=False))
