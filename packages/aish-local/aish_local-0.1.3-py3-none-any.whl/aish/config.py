import os
import json

CONFIG_DIR = os.path.expanduser("~/.config/aish")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

def get_model():
    if not os.path.exists(CONFIG_FILE):
        return None
    with open(CONFIG_FILE) as f:
        data = json.load(f)
    return data.get("model")

def set_model(model):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    data = {"model": model}
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f) 