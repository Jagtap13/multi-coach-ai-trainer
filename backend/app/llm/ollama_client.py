import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3"

def generate_response(prompt, model=MODEL_NAME):
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(OLLAMA_URL, json=payload)

    if response.status_code != 200:
        print("Ollama error response:", response.text)

    response.raise_for_status()

    data = response.json()
    return data["response"]

if __name__ == "__main__":
    test_prompt = "In one sentence, what is progressive overload in fitness training?"
    print("Sending prompt to Llama 3...")
    answer = generate_response(test_prompt)
    print("\n--- Response ---")
    print(answer)