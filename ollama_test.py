import requests


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.1:8b"


def ask_ollama(prompt):
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(OLLAMA_URL, json=payload)
    data = response.json()

    return data["response"]


user_prompt = input("Ask Ollama: ")
answer = ask_ollama(user_prompt)

print("\n=== OLLAMA RESPONSE ===")
print(answer)