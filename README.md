# Page Change Tracker

A Telegram bot built with Python for monitoring webpages, checking keywords, parsing RSS feeds, and tracking live sources like Hacker News.

## Features

### Page tracking

- `/check <url>` — manually check if a webpage changed
- `/track <url> <minutes>` — automatically track webpage changes
- `/untrack <url>` — stop tracking a webpage
- `/show` — show tracked webpages
- `/reset` — clear tracked data

### Listings

- `/listings <url>` — show parsed listings from a supported page
- `/new_listings <url>` — check for new listings based on saved links

### Keywords

- `/check_keyword <url> <keyword>` — check if a page contains one keyword
- `/check_keywords <url> <keyword1> <keyword2>` — check if a page contains multiple keywords
- `/set_keywords <keyword1> <keyword2>` — save a custom keyword list
- `/show_keywords` — show saved keywords
- `/check_saved_keywords <url>` — check a page using saved keywords

### Hacker News

- `/check_hn <url> <keyword1> <keyword2>` — manually check Hacker News topics by keywords
- `/track_hn <url> <minutes> <keyword1> <keyword2>` — track new Hacker News topics in the background
- `/track_hn <url> <minutes>` — track Hacker News using saved keywords

### Source presets

- `/check_source bbc_all <keyword1> <keyword2>` — check multiple BBC RSS feeds at once
- `/check_source hacker_news <keyword1> <keyword2>` — check Hacker News without manually entering the URL
- `/check_source bbc <keyword1> <keyword2>` — shortcut for BBC All
- `/check_source hn <keyword1> <keyword2>` — shortcut for Hacker News

### General

- `/start` — show the quick start guide
- `/help` — show available commands

## How It Works

The bot supports several monitoring and parsing modes.

First, it can detect full webpage changes. It downloads the page HTML, creates a SHA-256 hash of the content, saves it, and compares it with future checks. If the hash changes, the bot sends a Telegram notification.

Second, it can parse structured listing cards from supported pages. It extracts listing titles, prices, and links, then saves already-seen links. If a new link appears later, the bot can detect it as a new listing.

Third, it can check webpages for custom keywords. Users can check keywords directly in a command or save a keyword list and reuse it later.

Fourth, it can parse Hacker News topic titles and return matching topics with their links and post age. This is more precise than checking the full page HTML because it searches inside topic titles and returns the related links.

Fifth, it can track Hacker News in the background. When tracking is enabled, the bot saves current matching topics as already seen. After that, it checks the page on a schedule and sends Telegram alerts only for new matching topics.

Finally, it supports source presets. Instead of manually entering technical feed URLs, the user can choose a simple source key like `bbc_all` or `hacker_news`. The bot then uses the correct internal URL and adapter logic.

## Source Presets

Source presets hide technical URLs from the user.

Instead of writing:

```text
/check_rss https://feeds.bbci.co.uk/news/rss.xml?edition=uk government police
```

the user can write:

```text
/check_source bbc_all government police
```

Instead of writing:

```text
/check_hn https://news.ycombinator.com/newest ai python
```

the user can write:

```text
/check_source hacker_news ai python
```

Available source presets:

| Source key | Adapter | Profile | Description |
|---|---|---|---|
| `bbc_all` | RSS Feed | BBC News | Checks several BBC RSS feeds at once |
| `bbc` | RSS Feed | BBC News | Shortcut for `bbc_all` |
| `hacker_news` | Structured Link Feed | Hacker News | Checks Hacker News newest page |
| `hn` | Structured Link Feed | Hacker News | Shortcut for `hacker_news` |

## Adapter Logic

The project is moving toward an adapter-based structure.

Current adapters:

- **Structured Link Feed** — used for Hacker News-style structured link pages
- **RSS Feed** — used for RSS feeds such as BBC News

Current profiles:

- **Hacker News** — parses Hacker News topics, links, and post age
- **BBC News** — parses BBC RSS feeds and checks multiple categories through `bbc_all`

The goal is to keep the user-facing commands simple while keeping parsing logic flexible internally.

## Hacker News Tracking Logic

`/check_hn` is used for manual checks. It shows matching topics that are currently visible on the Hacker News page.

`/track_hn` starts background tracking. On the first run, it saves current matching topic links into `seen_links`, so old topics are not sent as new alerts. After that, the bot checks Hacker News repeatedly and sends only newly detected matching topics.

For Hacker News topic matching, keywords are matched as full words using regular expressions. This helps avoid false matches where a short keyword appears inside another word.

## Project Structure

- `bot.py` — Telegram bot commands, handlers, and scheduled background checks
- `page_checker.py` — page requests, hashing, listing parsing, RSS parsing, keyword logic, Hacker News parsing, source presets, and state handling
- `state.json` — saved tracked pages, listing links, keywords, and HN tracking data
- `requirements.txt` — project dependencies
- `.env` — bot token
- `.gitignore` — ignored files

## Installation

```bash
pip install -r requirements.txt
```

## Setup & Run

Create a `.env` file:

```env
BOT_TOKEN=your_telegram_bot_token
```

Run the bot:

```bash
python bot.py
```

## Example Commands

Track a webpage:

```text
/track https://example.com 5
```

Manually check a webpage:

```text
/check https://example.com
```

Show tracked webpages:

```text
/show
```

Check one keyword:

```text
/check_keyword https://example.com example
```

Check multiple keywords:

```text
/check_keywords https://example.com example domain
```

Save keywords:

```text
/set_keywords example domain update
```

Show saved keywords:

```text
/show_keywords
```

Check Hacker News manually:

```text
/check_hn https://news.ycombinator.com/newest ai bot python
```

Track Hacker News topics:

```text
/track_hn https://news.ycombinator.com/newest 1 ai bot python
```

Check BBC All through source presets:

```text
/check_source bbc_all government minister police trump
```

Check Hacker News through source presets:

```text
/check_source hacker_news ai python bot
```

Use shortcuts:

```text
/check_source bbc ai trump
/check_source hn ai python
```

## Notes

- Uses `requests` to load webpages
- Uses `BeautifulSoup` to parse supported HTML pages
- Uses `feedparser` to parse RSS feeds
- Uses SHA-256 hashes to detect full page changes
- Uses saved listing links to detect new listings
- Supports single and multiple keyword checks
- Supports user-specific saved keywords
- Can parse Hacker News topic titles, links, and post age
- Can track new Hacker News topics in the background
- Uses `seen_links` to avoid duplicate HN alerts
- Uses regular expressions for more accurate keyword matching
- Supports source presets such as `bbc_all` and `hacker_news`
- Stores data in `state.json`
- Supports scheduled checks with `python-telegram-bot[job-queue]`
- Listing parsing, Hacker News parsing, and RSS parsing are source-specific
- The bot does not yet support universal parsing for every website