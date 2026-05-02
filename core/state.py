import json
import os

STATE_FILE = os.path.join("data", "state.json")


def read_state():
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}


def write_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as file:
        json.dump(state, file, indent=2, ensure_ascii=False)
