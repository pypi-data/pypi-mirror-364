import os
import json

TOKEN_PATH = os.path.expanduser("~/.scripbox_token")

def save_token(data):
    with open(TOKEN_PATH, "w") as f:
        json.dump(data, f)

def load_token():
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, "r") as f:
            return json.load(f)
    return None

def delete_token():
    if os.path.exists(TOKEN_PATH):
        os.remove(TOKEN_PATH)
        return True
    return False
