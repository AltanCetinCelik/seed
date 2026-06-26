import json,importlib.util,sys
from datetime import datetime
from pathlib import Path
SETTINGS=Path("seed_native_wake_v109_settings.json")
DEFAULT={"version":"v109.1.0","preferred":"openwakeword","fallback":"v107_matcher","store_raw_audio":False,"custom_model_path":"","install_hint":"python -m pip install openwakeword"}
def now(): return datetime.now().isoformat(timespec="seconds")
def settings():
    if SETTINGS.exists():
        try:
            d=DEFAULT.copy(); d.update(json.loads(SETTINGS.read_text(errors="ignore"))); d["version"]="v109.1.0"; return d
        except Exception: pass
    SETTINGS.write_text(json.dumps(DEFAULT,indent=4)); return DEFAULT.copy()
def detect(): return {"openwakeword":importlib.util.find_spec("openwakeword") is not None,"porcupine":importlib.util.find_spec("pvporcupine") is not None,"fallback_v107":Path("seed_wake_reliability_v107.py").exists(),"custom_model_exists":bool(settings().get("custom_model_path") and Path(settings().get("custom_model_path")).exists())}
def route():
    d=detect()
    if d["openwakeword"]: return "openwakeword"
    if d["porcupine"]: return "porcupine"
    return "v107_matcher" if d["fallback_v107"] else "none"
def match(text):
    try:
        from seed_wake_reliability_v107 import match_wake_reliable
        return {"ok":True,"engine":route(),"match":match_wake_reliable(text)}
    except Exception as e:return {"ok":False,"engine":route(),"error":str(e)}
def recommendations():
    d=detect(); rec=[]
    if not d["openwakeword"]: rec.append("Install openWakeWord later for real native wake. Current v107 matcher fallback is safe.")
    if not d["custom_model_exists"]: rec.append("Train/configure a custom Seed wake model only after baseline mic tests are stable.")
    return rec
def test():
    cases={"make up status":True,"wake app status":True,"pumpkin seed recipe":False,"hello there":False}; res={}; ok=True
    for t,e in cases.items():
        g=match(t).get("match",(False,None,""))[0]; res[t]={"expected":e,"got":g}; ok=ok and (g==e)
    return {"created_at":now(),"version":"v109.1.0","ok":ok,"route":route(),"detect":detect(),"results":res,"recommendations":recommendations()}
def status(): return {"created_at":now(),"version":"v109.1.0","ok":True,"route":route(),"detect":detect(),"settings":settings(),"configured":detect()["openwakeword"] or detect()["porcupine"],"recommendations":recommendations()}
if __name__=="__main__":
    a=sys.argv[1] if len(sys.argv)>1 else "status"
    print(json.dumps(match(" ".join(sys.argv[2:])) if a=="match" else test() if a=="test" else status(),indent=4,ensure_ascii=False))
