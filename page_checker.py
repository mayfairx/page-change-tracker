import requests
import hashlib
import json

STATE_FILE = "state.json"

def read_state():
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def write_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as file:
        json.dump(state, file)

def get_page_content(url):
    try:
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return None
        
        return response.text
    
    except requests.RequestException:
        return None

def get_page_hash(content):
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

def check_page_change(url):
    content = get_page_content(url)

    if content is None:
        return "Could not get page."
    
    current_hash = get_page_hash(content)

    state = read_state()
    last_hash = state.get(url, "")
    
    if not last_hash:
        state[url] = current_hash
        write_state(state)
        return "Page saved for tracking."
    
    if current_hash != last_hash:
        state[url] = current_hash
        write_state(state)
        return "Page changed."
    
    return "No changes."

def show_tracked_pages():
    state = read_state()

    if not state:
        return "No tracked pages."
    
    message = "Tracked pages:\n\n"

    for url in state:
        message += f"{url}\n"

    return message

def reset_tracked_pages():
    write_state({})
    return "Tracked pages reset."