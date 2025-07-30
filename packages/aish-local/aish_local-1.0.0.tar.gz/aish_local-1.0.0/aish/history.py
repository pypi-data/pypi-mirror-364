import os
import json

HIST_FILE = os.path.expanduser("~/.config/aish/history.json")

def save_history(query, command, risk):
    os.makedirs(os.path.dirname(HIST_FILE), exist_ok=True)
    hist = load_history()
    hist.append({"query": query, "command": command, "risk": risk})
    with open(HIST_FILE, "w") as f:
        json.dump(hist, f)

def load_history():
    if not os.path.exists(HIST_FILE):
        return []
    with open(HIST_FILE) as f:
        return json.load(f) 