import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"

SYSTEM_PROMPT = """
You are a helpful AI assistant that translates natural language requests into safe, minimal Linux shell commands. Only output the command, nothing else.
"""

def get_command_from_llm(query, model):
    payload = {
        "model": model,
        "prompt": f"{SYSTEM_PROMPT}\nUser: {query}\nCommand:",
        "stream": False
    }
    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        # Ollama returns { 'response': '...' }
        return data.get("response", "").strip().split("\n")[0]
    except Exception as e:
        return f"echo 'Ollama error: {e}'" 