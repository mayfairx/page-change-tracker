import requests
import json
import re
import feedparser

from bs4 import BeautifulSoup
from urllib.parse import urljoin


def get_page_content(url):
    try:
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return None

        response.encoding = "utf-8"
        return response.text

    except requests.RequestException:
        return None


def set_keywords(chat_id, keywords):
    from core.db import save_keywords

    save_keywords(chat_id, keywords)
    return "Keywords saved."


def show_keywords(chat_id):
    from core.db import load_keywords

    keywords = load_keywords(chat_id)
    if not keywords:
        return "No keywords saved."
    message = "Saved keywords:\n\n"
    for keyword in keywords:
        message += f"{keyword}\n"
    return message


def clear_keywords(chat_id):
    from core.db import load_keywords, save_keywords

    keywords = load_keywords(chat_id)
    if not keywords:
        return "No keywords saved."
    save_keywords(chat_id, [])
    return "Saved keywords cleared."


def normalize_keywords(keywords):
    clean_keywords = []

    for keyword in keywords:
        parts = keyword.split(",")

        for part in parts:
            clean_keyword = part.strip().lower()

            if clean_keyword:
                clean_keywords.append(clean_keyword)

    return clean_keywords


def get_hn_topics(url):
    content = get_page_content(url)

    if content is None:
        return None

    soup = BeautifulSoup(content, "html.parser")

    topics = []
    rows = soup.find_all("tr", class_="athing")

    for row in rows:
        title_line = row.find("span", class_="titleline")

        if title_line is None:
            continue

        link_tag = title_line.find("a")

        if link_tag is None:
            continue

        title = link_tag.text
        link = link_tag["href"]
        full_link = urljoin(url, link)

        age = "Unknown time"

        subtext_row = row.find_next_sibling("tr")

        if subtext_row is not None:
            age_tag = subtext_row.find("span", class_="age")

            if age_tag is not None:
                age = age_tag.text

        topics.append({"title": title, "link": full_link, "age": age})

    return topics


def get_hn_matches(url, keywords):
    topics = get_hn_topics(url)

    if topics is None:
        return None

    matches = []

    for topic in topics:
        title_lower = topic["title"].lower()
        matched_keywords = []

        for keyword in keywords:
            keyword_lower = keyword.lower()

            pattern = r"\b" + re.escape(keyword_lower) + r"\b"

            if re.search(pattern, title_lower):
                matched_keywords.append(keyword_lower)

        if matched_keywords:
            matches.append(
                {
                    "title": topic["title"],
                    "link": topic["link"],
                    "age": topic["age"],
                    "keywords": matched_keywords,
                }
            )

    return matches


def track_hn_page(chat_id, url, interval, keywords):
    from core.db import save_monitor

    matches = get_hn_matches(url, keywords)
    if matches is None:
        return "Could not get HN topics."
    seen_links = [item["link"] for item in matches]
    monitor_data = {
        "source": "hacker_news",
        "url": url,
        "interval": interval,
        "keywords": keywords,
        "last_check": 0,
        "seen_links": seen_links,
    }
    save_monitor(chat_id, monitor_data)
    return (
        "Monitor enabled.\n\n"
        "Source: Hacker News\n"
        f"URL: {url}\n"
        f"Interval: {interval} min\n"
        f"Keywords: {', '.join(keywords)}\n"
        f"Current matching topics saved: {len(seen_links)}"
    )


def get_rss_items(url):
    feed = feedparser.parse(url)

    if not feed.entries:
        return None

    items = []

    for entry in feed.entries:
        title = entry.get("title", "No title")
        link = entry.get("link", url)
        published = entry.get("published", entry.get("updated", "Unknown time"))
        summary = entry.get("summary", "")

        items.append(
            {"title": title, "link": link, "published": published, "summary": summary}
        )

    return items


def track_bbc_all_monitor(chat_id, interval, keywords):
    from core.db import save_monitor

    matches = get_bbc_all_matches(keywords)
    if matches is None:
        return "Could not get BBC RSS feed."
    seen_links = [item["link"] for item in matches]
    monitor_data = {
        "source": "bbc_all",
        "url": "bbc_all",
        "interval": interval,
        "keywords": keywords,
        "last_check": 0,
        "seen_links": seen_links,
    }
    save_monitor(chat_id, monitor_data)
    return (
        "Monitor enabled.\n\n"
        "Source: BBC News\n"
        f"Interval: {interval} min\n"
        f"Keywords: {', '.join(keywords)}\n"
        f"Current matching items saved: {len(seen_links)}"
    )


HACKER_NEWS_URL = "https://news.ycombinator.com/newest"

BBC_ALL_FEEDS = [
    {
        "name": "BBC Top Stories",
        "url": "https://feeds.bbci.co.uk/news/rss.xml?edition=uk",
    },
    {"name": "BBC World", "url": "https://feeds.bbci.co.uk/news/world/rss.xml"},
    {"name": "BBC UK", "url": "https://feeds.bbci.co.uk/news/uk/rss.xml"},
    {"name": "BBC Business", "url": "https://feeds.bbci.co.uk/news/business/rss.xml"},
    {
        "name": "BBC Technology",
        "url": "https://feeds.bbci.co.uk/news/technology/rss.xml",
    },
    {
        "name": "BBC Science",
        "url": "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml",
    },
    {
        "name": "BBC Entertainment",
        "url": "https://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml",
    },
]


def get_bbc_all_matches(keywords):
    matches = []
    seen_links = set()
    feeds_checked = 0

    for feed_info in BBC_ALL_FEEDS:
        feed_name = feed_info["name"]
        feed_url = feed_info["url"]

        items = get_rss_items(feed_url)

        if items is None:
            continue

        feeds_checked += 1

        for item in items:
            text = f"{item['title']} {item['summary']}".lower()
            matched_keywords = []

            for keyword in keywords:
                keyword_lower = keyword.lower()
                pattern = r"\b" + re.escape(keyword_lower) + r"\b"

                if re.search(pattern, text):
                    matched_keywords.append(keyword_lower)

            if matched_keywords:
                if item["link"] in seen_links:
                    continue

                seen_links.add(item["link"])

                matches.append(
                    {
                        "source": feed_name,
                        "title": item["title"],
                        "link": item["link"],
                        "published": item["published"],
                        "keywords": matched_keywords,
                    }
                )

    if feeds_checked == 0:
        return None

    return matches


def check_hacker_news_source(keywords):
    matches = get_hn_matches(HACKER_NEWS_URL, keywords)

    if matches is None:
        return "Could not get Hacker News topics."

    if not matches:
        return "No matching Hacker News topics found."

    message = (
        "Adapter: Structured Link Feed\n"
        "Detected profile: Hacker News\n"
        "Source: Hacker News\n\n"
        "Matching items:\n\n"
    )

    for item in matches[:10]:
        keywords_text = ", ".join(item["keywords"])

        message += (
            f"{item['title']}\n"
            f"Time: {item['age']}\n"
            f"Keywords: {keywords_text}\n"
            f"{item['link']}\n\n"
        )

    return message


def check_bbc_all_source(keywords):
    matches = get_bbc_all_matches(keywords)

    if matches is None:
        return "Could not get BBC RSS feeds."

    if not matches:
        return "No matching BBC items found."

    message = (
        "Adapter: RSS Feed\n"
        "Detected profile: BBC News\n"
        "Source: BBC All\n\n"
        "Matching items:\n\n"
    )

    for item in matches[:10]:
        keywords_text = ", ".join(item["keywords"])

        message += (
            f"{item['title']}\n"
            f"Feed: {item['source']}\n"
            f"Published: {item['published']}\n"
            f"Keywords: {keywords_text}\n"
            f"{item['link']}\n\n"
        )

    return message


def check_source_preset(source_key, keywords):
    source_key = source_key.strip().lower()

    if source_key in ["hacker_news", "hn"]:
        return check_hacker_news_source(keywords)

    if source_key in ["bbc_all", "bbc"]:
        return check_bbc_all_source(keywords)

    return (
        "Unknown source.\n\n"
        "Available sources:\n"
        "bbc_all\n"
        "hacker_news\n"
        "hn\n"
        "bbc"
    )


def track_source_monitor(chat_id, source_key, interval, keywords):
    source_key = source_key.strip().lower()

    if source_key in ["hn", "hacker_news"]:
        return track_hn_page(chat_id, HACKER_NEWS_URL, interval, keywords)

    if source_key in ["bbc", "bbc_all"]:
        return track_bbc_all_monitor(chat_id, interval, keywords)

    return "Unknown source.\n\n" "Available sources:\n" "hn\n" "bbc"


def untrack_source_monitor(chat_id, source_key):
    from core.db import load_monitors, delete_monitor

    source_key = source_key.strip().lower()
    if source_key in ["hn", "hacker_news"]:
        source_name = "hacker_news"
        display_name = "Hacker News"
    elif source_key in ["bbc", "bbc_all"]:
        source_name = "bbc_all"
        display_name = "BBC News"
    else:
        return "Unknown source.\n\nAvailable sources:\nhn\nbbc"

    monitors = load_monitors(chat_id)
    removed = 0
    for url, data in list(monitors.items()):
        if data["source"] == source_name:
            delete_monitor(chat_id, url)
            removed += 1

    if removed == 0:
        return f"No active {display_name} monitor found."
    return (
        "Monitor disabled.\n\n"
        f"Source: {display_name}\n"
        f"Removed monitors: {removed}"
    )


def show_watchlist(chat_id):
    from core.db import load_monitors

    monitors = load_monitors(chat_id)
    if not monitors:
        return "<b>📋 Watchlist</b>\n\nNo active monitors."
    message = "<b>📋 Watchlist</b>\n\nActive monitors:\n"
    lines = []
    for url, data in monitors.items():
        lines.append(
            f"– {data['source']}\n"
            f"  URL: {url}\n"
            f"  Every: {data['interval']} min\n"
            f"  Keywords: {', '.join(data['keywords'])}\n"
            f"  Seen links: {len(data.get('seen_links', []))}"
        )
    message += "\n\n".join(lines)
    return message
