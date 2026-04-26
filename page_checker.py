import requests
import hashlib
import json

from bs4 import BeautifulSoup
from urllib.parse import urljoin

STATE_FILE = "state.json"

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
        json.dump(state, file)

def get_page_content(url):
    try:
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return None
        
        response.encoding = "utf-8"
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

def get_listings(url):
    content = get_page_content(url)

    if content is None:
        return None
    
    soup = BeautifulSoup(content, "html.parser")

    listings = []

    cards = soup.find_all("article", class_="product_pod")

    for card in cards:
        title = card.find("h3").find("a")["title"]
        price = card.find("p", class_="price_color").text
        relative_link = card.find("h3").find("a")["href"]
        link = urljoin(url, relative_link)

        listings.append({
            "title": title,
            "price": price,
            "link": link
        })

    return listings

def check_new_listings(chat_id, url):
    listings = get_listings(url)

    if listings is None:
        return "Could not get listings."

    state = read_state()

    if chat_id not in state:
        state[chat_id] = {}

    if url not in state[chat_id]:
        seen_links = []

        for item in listings:
            seen_links.append(item["link"])

        state[chat_id][url] = {
            "seen_links": seen_links,
            "interval": 5,
            "last_check": 0
        }

        write_state(state)

        return "Listings saved for tracking."

    seen_links = state[chat_id][url].get("seen_links", [])

    new_items = []

    for item in listings:
        if item["link"] not in seen_links:
            new_items.append(item)
            seen_links.append(item["link"])

    state[chat_id][url]["seen_links"] = seen_links
    write_state(state)

    if not new_items:
        return "No new listings."

    message = "New listings:\n\n"

    for item in new_items[:5]:
        message += (
            f"{item['title']}\n"
            f"{item['price']}\n"
            f"{item['link']}\n\n"
        )

    return message

def check_keyword(url, keyword):
    content = get_page_content(url)

    if content is None:
        return "Could not get page."
    
    content = content.lower()
    keyword = keyword.lower()

    if keyword in content:
        return "Keyword found."
    
    return "Keyword not found."

def check_keywords(url, keywords):
    content = get_page_content(url)

    if content is None:
        return "Could not get page."
    
    content = content.lower()

    found_keywords = []

    for keyword in keywords:
        keyword = keyword.lower()

        if keyword in content:
            found_keywords.append(keyword)

    if not found_keywords:
        return "No keywords found."
    
    message = "Found keywords:\n\n"

    for keyword in found_keywords:
        message += f"{keyword}\n"

    return message

def set_keywords(chat_id, keywords):
    state = read_state()

    if chat_id not in state:
        state[chat_id] = {}

    state[chat_id]["keywords"] = keywords

    write_state(state)

    return "Keywords saved."

def show_keywords(chat_id):
    state = read_state()

    if chat_id not in state or "keywords" not in state[chat_id]:
        return "No keywords saved."
    
    keywords = state[chat_id]["keywords"]

    if not keywords:
        return "No keywords saved."
    
    message = "Saved keywords:\n\n"

    for keyword in keywords:
        message += f"{keyword}\n"

    return message