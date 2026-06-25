import json
from datetime import datetime
from pathlib import Path
ADVICE_FILE = Path("seed_friend_advice_v72.json")
CATS = {
 "voice":["voice","speech","mic","whisper","tts","wake"], "avatar":["avatar","face","visual","character","mood"],
 "curiosity":["curious","ask","proactive","notice","suggest"], "memory":["memory","remember","recall","continuity"],
 "agent":["agent","tools","execute","workflow","aider"], "ui":["ui","ux","dashboard","terminal","menu"],
 "safety":["safe","permission","approval","risk"], "model":["model","ollama","llm","qwen","llama","gemma","deepseek"],
 "repo_pattern":["repo","hermes","moltbot","openclaw","github"], "life":["habit","life","routine","sleep","study","work","social","health"]
}
def now(): return datetime.now().isoformat(timespec="seconds")
def load():
    if ADVICE_FILE.exists():
        try: return json.loads(ADVICE_FILE.read_text(errors="ignore"))
        except Exception: pass
    return {"created_at":now(),"version":"v72.0.0","items":[]}
def classify(text):
    low=str(text).lower(); out=[c for c,ws in CATS.items() if any(w in low for w in ws)]
    return out or ["general"]
def add_advice(text, source="friend", priority="normal"):
    data=load(); item={"id":f"advice_{len(data['items'])+1:04d}","created_at":now(),"source":source,"priority":priority,"content":str(text).strip(),"categories":classify(text),"status":"new"}
    data["items"].append(item); data["updated_at"]=now(); ADVICE_FILE.write_text(json.dumps(data,indent=4,ensure_ascii=False)); return item
def build_advice_backlog():
    tasks=[]; data=load()
    for item in data["items"]:
        for cat in item["categories"]:
            tasks.append({"source_advice_id":item["id"],"category":cat,"title":f"Improve Seed {cat}","reason":item["content"],"status":"candidate"})
    return {"created_at":now(),"version":"v72.0.0","ok":True,"task_count":len(tasks),"tasks":tasks}
def show_add_advice():
    print(json.dumps(add_advice(input("Advice: ").strip()), indent=4, ensure_ascii=False))
def show_advice():
    data=load(); print("\n=== SEED FRIEND ADVICE v72 ==="); print("Advice items:",len(data["items"]))
    for item in data["items"][-30:]: print(f"- {item['id']} {item['categories']} {item['content'][:180]}")
def show_advice_backlog(): print(json.dumps(build_advice_backlog(), indent=4, ensure_ascii=False))
if __name__ == "__main__": show_advice()
