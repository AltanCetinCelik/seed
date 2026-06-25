import json
import shutil
import subprocess
import time
from datetime import datetime
from pathlib import Path


STATE_FILE = Path("seed_model_manager_v60.json")
BENCH_FILE = Path("seed_model_benchmark_v60.json")
ROLE_MAP_FILE = Path("seed_model_role_map_v60.json")


MODEL_ROLE_MAP = {
    "fast_chat": ["llama3.1:8b", "qwen3:8b", "gemma3:4b"],
    "coding": ["qwen2.5-coder:7b", "qwen2.5-coder:14b"],
    "reasoning": ["deepseek-r1:8b", "qwen3:8b"],
    "turkish": ["qwen3:8b", "llama3.1:8b"],
    "memory_extraction": ["llama3.1:8b", "qwen3:8b"],
    "repo_planning": ["qwen2.5-coder:7b", "qwen3:8b"],
}


BENCH_PROMPTS = {
    "fast_chat": "Answer briefly: what should Seed improve next?",
    "coding": "Give a concise patch plan to improve a Python CLI UX.",
    "reasoning": "Think carefully and give 3 tradeoffs of local-first AI assistants.",
    "turkish": "Türkçe doğal ve kısa cevap ver: Seed bugün neye odaklanmalı?",
    "memory_extraction": "Extract one durable memory from: Altan wants Seed to be natural and not command-heavy.",
}


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def ollama_available():
    return shutil.which("ollama") is not None


def run_command(command, timeout=60):
    try:
        proc = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
        return {
            "ok": proc.returncode == 0,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "returncode": proc.returncode,
        }
    except Exception as error:
        return {"ok": False, "error": str(error)}


def list_ollama_models():
    if not ollama_available():
        return {"ok": False, "error": "Ollama not found on PATH.", "models": []}

    result = run_command(["ollama", "list"], timeout=30)

    models = []
    if result.get("ok"):
        lines = result.get("stdout", "").splitlines()[1:]
        for line in lines:
            parts = line.split()
            if parts:
                models.append(parts[0])

    return {
        "created_at": now_timestamp(),
        "ok": result.get("ok"),
        "raw": result,
        "models": models,
    }


def build_pull_plan():
    installed = set(list_ollama_models().get("models", []))
    wanted = []
    for models in MODEL_ROLE_MAP.values():
        for model in models:
            if model not in wanted:
                wanted.append(model)

    missing = [m for m in wanted if m not in installed]

    plan = {
        "created_at": now_timestamp(),
        "version": "v60.0.0",
        "ok": True,
        "installed": sorted(installed),
        "wanted": wanted,
        "missing": missing,
        "commands": [f"ollama pull {m}" for m in missing],
        "note": "Seed does not auto-download models. You approve and run the pull commands.",
    }

    STATE_FILE.write_text(json.dumps(plan, indent=4))
    return plan


def choose_model_for_role(role):
    installed = set(list_ollama_models().get("models", []))
    for model in MODEL_ROLE_MAP.get(role, []):
        if model in installed:
            return model

    for model in installed:
        return model

    return None


def route_task(task_text):
    text = str(task_text).lower()

    if any(w in text for w in ["code", "patch", "bug", "file", "aider", "python", "repo"]):
        role = "coding"
    elif any(w in text for w in ["think", "reason", "tradeoff", "decide", "plan"]):
        role = "reasoning"
    elif any(w in text for w in ["türkçe", "turkish", "tr "]):
        role = "turkish"
    elif any(w in text for w in ["remember", "memory", "extract"]):
        role = "memory_extraction"
    elif any(w in text for w in ["repo", "hermes", "moltbot", "openclaw"]):
        role = "repo_planning"
    else:
        role = "fast_chat"

    return {
        "created_at": now_timestamp(),
        "version": "v60.0.0",
        "ok": True,
        "task": task_text,
        "role": role,
        "model": choose_model_for_role(role),
    }


def benchmark_model(model, prompt, timeout=90):
    start = time.time()
    try:
        proc = subprocess.run(
            ["ollama", "run", model, prompt],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        ms = int((time.time() - start) * 1000)
        return {
            "model": model,
            "ok": proc.returncode == 0,
            "ms": ms,
            "reply_tail": proc.stdout[-1200:],
            "stderr_tail": proc.stderr[-1200:],
        }
    except Exception as error:
        return {"model": model, "ok": False, "error": str(error)}


def run_model_benchmark(max_models=5):
    available = list_ollama_models()
    models = available.get("models", [])[:max_models]

    results = []
    for model in models:
        model_results = {}
        for role, prompt in BENCH_PROMPTS.items():
            model_results[role] = benchmark_model(model, prompt)
        results.append({"model": model, "roles": model_results})

    report = {
        "created_at": now_timestamp(),
        "version": "v60.0.0",
        "ok": True,
        "ollama_available": ollama_available(),
        "models_tested": models,
        "results": results,
    }

    BENCH_FILE.write_text(json.dumps(report, indent=4))
    return report


def build_role_map_from_benchmark():
    installed = list_ollama_models().get("models", [])
    role_map = {}

    for role in MODEL_ROLE_MAP:
        role_map[role] = choose_model_for_role(role)

    data = {
        "created_at": now_timestamp(),
        "version": "v60.0.0",
        "ok": True,
        "installed": installed,
        "role_map": role_map,
        "routing_rules": MODEL_ROLE_MAP,
    }

    ROLE_MAP_FILE.write_text(json.dumps(data, indent=4))
    return data


def show_model_manager():
    print("\n=== SEED MODEL MANAGER v60 ===")
    print(json.dumps(build_pull_plan(), indent=4))


def show_model_router():
    task = input("Describe the task: ").strip()
    print(json.dumps(route_task(task), indent=4))


def show_model_benchmark():
    print("\nRunning local model benchmark. This may take a while.")
    print(json.dumps(run_model_benchmark(), indent=4))


def show_model_role_map():
    print(json.dumps(build_role_map_from_benchmark(), indent=4))


if __name__ == "__main__":
    show_model_manager()
