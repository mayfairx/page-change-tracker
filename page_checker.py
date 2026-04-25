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
  page_data = state.get(url)

  if not page_data:
      state[url] = {
          "hash": current_hash,
          "interval": 5,
          "last_check": 0
      }
      write_state(state)
      return "Page saved for tracking."
  
  last_hash = page_data["hash"]

  if current_hash != last_hash:
      state[url]["hash"] = current_hash
      write_state(state)
      return "Page changed."
  
  return "No changes."  


def show_tracked_pages(chat_id):
    state = read_state()

    if chat_id not in state or not state[chat_id]:
        return "No tracked pages."
    
    message = "Tracked pages:\n\n"

    for url, data in state[chat_id].items():
        interval = data["interval"]
        message += f"{url} — every {interval} min\n"

    return message

def reset_tracked_pages():
    write_state({})
    return "Tracked pages reset."

def track_page(chat_id, url, interval):
    content = get_page_content(url)

    if content is None:
        return "Could not get page."
    
    current_hash = get_page_hash(content)

    state = read_state()

    if chat_id not in state:
        state[chat_id] = {}

    state[chat_id][url] = {
        "hash": current_hash,
        "interval": interval,
        "last_check": 0
    }

    write_state(state)

    return "Page tracking enabled."

def untrack_page(chat_id, url):
    state = read_state()

    if chat_id not in state or url not in state[chat_id]:
        return "Page is not being tracked."
    
    del state[chat_id][url]

    if not state[chat_id]:
        del state[chat_id]

    write_state(state)

    return "Page tracking disabled."