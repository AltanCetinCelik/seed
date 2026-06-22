import requests

from seed_config import (
    OLLAMA_BASE_URL,
    OLLAMA_GENERATE_URL,
    OLLAMA_TAGS_URL,
    DEFAULT_CHAT_MODEL,
    LLM_TIMEOUT_SECONDS,
    LLM_HEALTH_TIMEOUT_SECONDS,
    LLM_NUM_CTX,
    LLM_TASK_CONFIG,
    OLLAMA_EMBED_URL,
    EMBEDDING_MODEL
)

def normalize_task_type(task_type):
    if task_type is None:
        return "chat"

    task_type = task_type.strip().lower()

    if task_type in LLM_TASK_CONFIG:
        return task_type

    return "chat"


def get_available_task_types():
    return list(LLM_TASK_CONFIG.keys())


def get_task_config(task_type):
    task_type = normalize_task_type(task_type)
    return LLM_TASK_CONFIG[task_type]


def get_default_model_for_task(task_type):
    config = get_task_config(task_type)
    return config["model"]


def get_temperature_for_task(task_type):
    config = get_task_config(task_type)
    return config["temperature"]


def ensure_task_model_state(runtime_context):
    if runtime_context is None:
        return {}

    if "task_models" not in runtime_context:
        runtime_context["task_models"] = {}

    return runtime_context["task_models"]


def get_active_model(task_type="chat", runtime_context=None):
    task_type = normalize_task_type(task_type)

    if runtime_context is not None:
        task_models = ensure_task_model_state(runtime_context)

        if task_type in task_models:
            return task_models[task_type]

        if task_type == "chat":
            active_model = runtime_context.get("active_model")

            if active_model:
                return active_model

    return get_default_model_for_task(task_type)


def update_last_llm_call(runtime_context, task_type, model_name, temperature):
    if runtime_context is None:
        return

    runtime_context["last_llm_task"] = task_type
    runtime_context["last_llm_model"] = model_name
    runtime_context["last_llm_temperature"] = temperature


def check_ollama_health():
    try:
        response = requests.get(
            OLLAMA_TAGS_URL,
            timeout=LLM_HEALTH_TIMEOUT_SECONDS
        )

        if response.status_code == 200:
            return {
                "ok": True,
                "message": "Ollama is reachable."
            }

        return {
            "ok": False,
            "message": f"Ollama responded with status code {response.status_code}."
        }

    except requests.exceptions.ConnectionError:
        return {
            "ok": False,
            "message": "Ollama is not reachable. Open the Ollama app/server."
        }

    except requests.exceptions.Timeout:
        return {
            "ok": False,
            "message": "Ollama health check timed out."
        }

    except requests.exceptions.RequestException as error:
        return {
            "ok": False,
            "message": f"Ollama health check error: {error}"
        }


def get_local_models():
    try:
        response = requests.get(
            OLLAMA_TAGS_URL,
            timeout=LLM_HEALTH_TIMEOUT_SECONDS
        )

        response.raise_for_status()
        data = response.json()

        model_names = []

        for model in data.get("models", []):
            name = model.get("name")

            if name:
                model_names.append(name)

        model_names.sort()
        return model_names

    except requests.exceptions.RequestException:
        return []


def model_exists_locally(model_name):
    models = get_local_models()
    return model_name in models


def ask_llm(prompt, task_type="chat", runtime_context=None):
    task_type = normalize_task_type(task_type)

    model_name = get_active_model(task_type, runtime_context)
    temperature = get_temperature_for_task(task_type)

    update_last_llm_call(
        runtime_context,
        task_type,
        model_name,
        temperature
    )

    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_ctx": LLM_NUM_CTX
        }
    }

    try:
        response = requests.post(
            OLLAMA_GENERATE_URL,
            json=payload,
            timeout=LLM_TIMEOUT_SECONDS
        )

        response.raise_for_status()
        data = response.json()

        return data.get("response", "")

    except requests.exceptions.ConnectionError:
        return (
            "Seed could not connect to Ollama. "
            "Make sure Ollama is running."
        )

    except requests.exceptions.Timeout:
        return (
            "Seed's LLM request timed out. "
            "The model may be too slow or overloaded."
        )

    except requests.exceptions.RequestException as error:
        return f"Seed LLM request error: {error}"


def show_llm_status(chat_state=None):
    if chat_state is None:
        chat_state = {}

    health = check_ollama_health()
    active_chat_model = get_active_model("chat", chat_state)

    print("\n=== LLM ENGINE STATUS ===")
    print(f"Ollama base URL: {OLLAMA_BASE_URL}")
    print(f"Health: {health['message']}")
    print(f"Active chat model: {active_chat_model}")
    print(f"Last LLM task: {chat_state.get('last_llm_task', 'none')}")
    print(f"Last LLM model: {chat_state.get('last_llm_model', 'none')}")
    print(f"Last temperature: {chat_state.get('last_llm_temperature', 'none')}")

    print("\n=== TASK ROUTING ===")

    task_models = chat_state.get("task_models", {})

    for task_type in get_available_task_types():
        config = get_task_config(task_type)
        active_model = get_active_model(task_type, chat_state)

        if task_type in task_models:
            source = "runtime override"
        else:
            source = "default"

        print(
            f"{task_type}: model={active_model} "
            f"temperature={config['temperature']} "
            f"source={source}"
        )


def show_local_models():
    print("\n=== LOCAL OLLAMA MODELS ===")

    models = get_local_models()

    if not models:
        print("No local models found or Ollama is not reachable.")
        return

    for number, model_name in enumerate(models, start=1):
        print(f"{number}. {model_name}")


def show_task_models(chat_state=None):
    if chat_state is None:
        chat_state = {}

    print("\n=== LLM TASK MODELS ===")

    for task_type in get_available_task_types():
        config = get_task_config(task_type)
        active_model = get_active_model(task_type, chat_state)

        print(f"\nTask: {task_type}")
        print(f"  Active model: {active_model}")
        print(f"  Default model: {config['model']}")
        print(f"  Temperature: {config['temperature']}")
        print(f"  Purpose: {config['description']}")


def set_active_chat_model(chat_state, requested_model=None):
    print("\n=== SET ACTIVE CHAT MODEL ===")

    models = get_local_models()

    if models:
        print("Available local models:")

        for number, model_name in enumerate(models, start=1):
            print(f"{number}. {model_name}")

    if requested_model is None:
        requested_model = input("Model name: ")

    requested_model = requested_model.strip()

    if requested_model == "":
        print("Model name cannot be empty.")
        return False

    if models and requested_model not in models:
        print("That model was not found in local Ollama models.")
        print("Use `ollama pull model_name` first if you want to use it.")
        return False

    chat_state["active_model"] = requested_model
    print(f"Active chat model changed to: {requested_model}")
    return True


def set_task_model(chat_state):
    print("\n=== SET TASK MODEL ===")

    show_task_models(chat_state)

    task_type = input("\nTask type: ")
    task_type = normalize_task_type(task_type)

    models = get_local_models()

    if models:
        print("\nAvailable local models:")

        for number, model_name in enumerate(models, start=1):
            print(f"{number}. {model_name}")

    requested_model = input("Model name: ").strip()

    if requested_model == "":
        print("Model name cannot be empty.")
        return False

    if models and requested_model not in models:
        print("That model was not found in local Ollama models.")
        print("Use `ollama pull model_name` first if you want to use it.")
        return False

    task_models = ensure_task_model_state(chat_state)
    task_models[task_type] = requested_model

    if task_type == "chat":
        chat_state["active_model"] = requested_model

    print(f"Task model changed: {task_type} -> {requested_model}")
    return True

def get_embedding(text, model_name=None):
    if model_name is None:
        model_name = EMBEDDING_MODEL

    payload = {
        "model": model_name,
        "input": text
    }

    try:
        response = requests.post(
            OLLAMA_EMBED_URL,
            json=payload,
            timeout=LLM_TIMEOUT_SECONDS
        )

        response.raise_for_status()
        data = response.json()

        embeddings = data.get("embeddings", [])

        if not embeddings:
            return None, "No embeddings returned."

        return embeddings[0], None

    except requests.exceptions.ConnectionError:
        return None, "Could not connect to Ollama for embeddings."

    except requests.exceptions.Timeout:
        return None, "Embedding request timed out."

    except requests.exceptions.RequestException as error:
        return None, f"Embedding request error: {error}"


def test_embedding():
    print("\n=== EMBEDDING TEST ===")

    embedding, error = get_embedding("Seed semantic memory test.")

    if error is not None:
        print(error)
        return False

    print(f"Embedding model: {EMBEDDING_MODEL}")
    print(f"Embedding dimensions: {len(embedding)}")
    print("Embedding engine is working.")
    return True

def test_llm(chat_state=None):
    print("\n=== LLM TEST ===")

    task_type = input("Task type (chat/summary/memory/debug/code): ").strip()

    if task_type == "":
        task_type = "debug"

    task_type = normalize_task_type(task_type)

    prompt = (
        "Reply in one short sentence. "
        f"Say that Seed's {task_type} LLM route is working."
    )

    response = ask_llm(
        prompt,
        task_type=task_type,
        runtime_context=chat_state
    )

    print(response)


def get_llm_hud_lines(chat_state=None):
    if chat_state is None:
        chat_state = {}

    health = check_ollama_health()
    active_model = get_active_model("chat", chat_state)

    if health["ok"]:
        health_text = "online"
    else:
        health_text = "offline"

    return [
        ("LLM health", health_text),
        ("Active chat", active_model),
        ("Last task", chat_state.get("last_llm_task", "none")),
        ("Last model", chat_state.get("last_llm_model", "none")),
        ("Summary model", get_active_model("summary", chat_state)),
        ("Memory model", get_active_model("memory", chat_state)),
        ("Debug model", get_active_model("debug", chat_state)),
        ("Code model", get_active_model("code", chat_state))
    ]