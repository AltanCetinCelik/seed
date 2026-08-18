import json, shutil, subprocess, time
from pathlib import Path
from datetime import datetime

STATE_FILE=Path("seed_model_real_mode_v61.json"); BENCH_FILE=Path("seed_model_real_benchmark_v61.json"); ROLE_FILE=Path("seed_model_real_roles_v61.json")
STARTER_MODELS=["llama3.1:8b","qwen3:8b","deepseek-r1:8b","qwen2.5-coder:7b","gemma3:4b"]

def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")

BIGGER_MAC_MODELS=["qwen3:14b","qwen2.5-coder:14b"]
ROLE_CANDIDATES={"fast_chat":["llama3.1:8b","qwen3:8b","gemma3:4b"],"turkish":["qwen3:8b","llama3.1:8b"],"coding":["qwen2.5-coder:7b","qwen2.5-coder:14b","qwen3:8b"],"reasoning":["deepseek-r1:8b","qwen3:8b"],"patch_planning":["qwen2.5-coder:7b","qwen3:8b"],"memory_extraction":["llama3.1:8b","qwen3:8b","gemma3:4b"]}
BENCH_PROMPTS={"fast_chat":"Answer in one short paragraph: what should Seed improve next?","turkish":"Türkçe doğal cevap ver: Seed bugün neye odaklanmalı?","coding":"Give a concise patch plan to improve a Python CLI UX. Include files and tests.","reasoning":"Give 3 tradeoffs for local-first AI companions. Be precise.","patch_planning":"Plan a safe patch for improving a dashboard UI. Include rollback and test steps.","memory_extraction":"Extract durable memories from: User wants Seed natural, not slash-command heavy."}

def now(): return datetime.now().isoformat(timespec="seconds")
def ollama(): return shutil.which("ollama")
def run(cmd, timeout=60):
    try:
        p=subprocess.run(cmd,capture_output=True,text=True,timeout=timeout); return {"ok":p.returncode==0,"stdout":p.stdout,"stderr":p.stderr,"returncode":p.returncode}
    except Exception as e: return {"ok":False,"error":str(e)}
def list_models():
    if not ollama(): return {"created_at":now(),"version":"v70.0.0","ok":False,"error":"Ollama not found.","models":[]}
    r=run([ollama(),"list"],30); models=[]
    if r.get("ok"):
        for line in r.get("stdout","").splitlines()[1:]:
            parts=line.split();
            if parts: models.append(parts[0])
    return {"created_at":now(),"version":"v70.0.0","ok":r.get("ok"),"models":models,"raw":r}
def install_plan():
    installed=set(list_models().get("models",[])); missing=[m for m in STARTER_MODELS if m not in installed]; bigger=[m for m in BIGGER_MAC_MODELS if m not in installed]
    data={"created_at":now(),"version":"v70.0.0","ok":True,"ollama_found":bool(ollama()),"installed":sorted(installed),"starter_models":STARTER_MODELS,"bigger_mac_models":BIGGER_MAC_MODELS,"missing_starter":missing,"missing_bigger_mac":bigger,"starter_pull_commands":[f"ollama pull {m}" for m in missing],"bigger_pull_commands":[f"ollama pull {m}" for m in bigger],"note":"Run starter pulls first. Benchmark before 14B models."}
    STATE_FILE.write_text(json.dumps(data, indent=4)); return data
def pull_missing_starter_models():
    plan=install_plan()
    if not plan.get("ollama_found"): return {"ok":False,"error":"Ollama not found."}
    results=[{"model":m,"result":run(["ollama","pull",m],1800)} for m in plan["missing_starter"]]
    return {"created_at":now(),"version":"v70.0.0","ok":all(x["result"].get("ok") for x in results),"results":results}

def benchmark_model(model, role, timeout=90):
    import urllib.request
    import urllib.error

    prompt = BENCH_PROMPTS[role]
    start = time.time()

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "num_predict": 96,
            "temperature": 0.2,
            "num_ctx": 2048
        }
    }

    try:
        req = urllib.request.Request(
            "http://127.0.0.1:11434/api/generate",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8", errors="ignore"))

        ms = int((time.time() - start) * 1000)
        reply = data.get("response", "").strip()

        quality = 2 if reply else 0

        if role == "coding" and any(w in reply.lower() for w in ["file", "test", "patch", "function"]):
            quality += 2

        if role == "turkish" and any(ch in reply.lower() for ch in "çğıöşü"):
            quality += 2

        if role == "reasoning" and any(w in reply.lower() for w in ["tradeoff", "risk", "because", "reason"]):
            quality += 2

        if role == "patch_planning" and any(w in reply.lower() for w in ["rollback", "test", "file", "step"]):
            quality += 2

        if role == "memory_extraction" and any(w in reply.lower() for w in ["user", "seed", "wants", "memory"]):
            quality += 2

        speed_score = max(0, 8 - int(ms / 6000))

        return {
            "model": model,
            "role": role,
            "ok": bool(reply),
            "ms": ms,
            "quality_score": quality,
            "speed_score": speed_score,
            "combined_score": quality + speed_score,
            "reply_tail": reply[-900:],
            "api": "ollama_generate"
        }

    except Exception as error:
        return {
            "model": model,
            "role": role,
            "ok": False,
            "error": str(error),
            "combined_score": 0,
            "api": "ollama_generate"
        }


def run_arena():
    installed = list_models().get("models", [])

    role_tests = {
        "fast_chat": ["qwen3:8b", "llama3.1:8b", "gemma3:4b"],
        "turkish": ["qwen3:8b", "llama3.1:8b"],
        "coding": ["qwen2.5-coder:7b", "qwen3:8b"],
        "reasoning": ["deepseek-r1:8b", "qwen3:8b", "llama3.1:8b"],
        "patch_planning": ["qwen2.5-coder:7b", "qwen3:8b"],
        "memory_extraction": ["qwen3:8b", "llama3.1:8b", "gemma3:4b"],
    }

    results = []
    best = {}

    print("Seed model arena started.")
    print(f"Installed models: {installed}")

    for role, candidates in role_tests.items():
        print(f"\n=== Testing role: {role} ===")
        role_results = []

        for model in candidates:
            if model not in installed:
                print(f"skip {model}: not installed")
                continue

            print(f"testing {model} for {role} ...", flush=True)
            result = benchmark_model(model, role, timeout=90)
            print(
                f"done {model}: ok={result.get('ok')} "
                f"ms={result.get('ms')} score={result.get('combined_score')}",
                flush=True
            )

            if result.get("error"):
                print(f"error: {result.get('error')[:200]}", flush=True)

            role_results.append(result)
            results.append(result)

        valid = [r for r in role_results if r.get("ok")]
        if valid:
            best[role] = sorted(valid, key=lambda x: x.get("combined_score", 0), reverse=True)[0]["model"]
        else:
            # Safe fallback if all candidates failed.
            if role in {"coding", "patch_planning"} and "qwen2.5-coder:7b" in installed:
                best[role] = "qwen2.5-coder:7b"
            elif "qwen3:8b" in installed:
                best[role] = "qwen3:8b"
            elif "llama3.1:8b" in installed:
                best[role] = "llama3.1:8b"
            else:
                best[role] = installed[0] if installed else None

    report = {
        "created_at": now_timestamp(),
        "version": "v70.0.0",
        "ok": True,
        "models_tested": sorted(set(r["model"] for r in results)),
        "results": results,
        "best_role_map": best,
        "mode": "ollama_api_fast_benchmark",
    }

    BENCH_FILE.write_text(json.dumps(report, indent=4))
    ROLE_FILE.write_text(json.dumps({
        "created_at": now_timestamp(),
        "version": "v70.0.0",
        "ok": True,
        "role_map": best,
        "source": str(BENCH_FILE),
        "mode": "ollama_api_fast_benchmark",
    }, indent=4))

    return report

def load_role_map():
    if ROLE_FILE.exists():
        try: return json.loads(ROLE_FILE.read_text(errors="ignore"))
        except Exception: pass
    installed=set(list_models().get("models",[])); role_map={role:next((m for m in cands if m in installed),None) for role,cands in ROLE_CANDIDATES.items()}; return {"created_at":now(),"version":"v70.0.0","ok":True,"role_map":role_map,"source":"heuristic"}
def route(text):
    low=str(text).lower()
    if any(w in low for w in ["code","patch","bug","file","aider","python","cli"]): role="coding"
    elif any(w in low for w in ["türkçe","turkish","turkce"]): role="turkish"
    elif any(w in low for w in ["reason","think","tradeoff","decide"]): role="reasoning"
    elif any(w in low for w in ["memory","remember","extract"]): role="memory_extraction"
    elif any(w in low for w in ["plan","improve","control plane","dashboard"]): role="patch_planning"
    else: role="fast_chat"
    return {"created_at":now(),"version":"v70.0.0","ok":True,"role":role,"model":load_role_map().get("role_map",{}).get(role),"text":text}
def show_model_real(): print("\n=== SEED MODEL MANAGER REAL MODE v61 ==="); print(json.dumps(install_plan(),indent=4))
def show_model_pull_starter(): print("\n=== SEED MODEL PULL STARTER ==="); print(json.dumps(pull_missing_starter_models(),indent=4))
def show_model_arena(): print("\n=== SEED MODEL BENCHMARK ARENA ==="); print(json.dumps(run_arena(),indent=4))
def show_model_route(): print(json.dumps(route(input("Task: ").strip()),indent=4))
if __name__ == "__main__": show_model_real()
