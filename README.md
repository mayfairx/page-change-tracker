# Page Change Tracker

A Telegram bot built with Python for monitoring webpages, detecting changes, parsing supported listing pages, checking custom keywords, and matching Hacker News topics by keywords.

## Features

- `/check <url>` — manually check if a webpage changed
- `/track <url> <minutes>` — automatically track webpage changes
- `/untrack <url>` — stop tracking a webpage
- `/show` — show tracked webpages
- `/reset` — clear tracked data

- `/listings <url>` — show parsed listings from a supported page
- `/new_listings <url>` — check for new listings based on saved links

- `/check_keyword <url> <keyword>` — check if a page contains a specific keyword
- `/check_keywords <url> <keyword1> <keyword2>` — check if a page contains multiple keywords
- `/set_keywords <keyword1> <keyword2>` — save a custom keyword list
- `/show_keywords` — show saved keywords
- `/check_saved_keywords <url>` — check a page using saved keywords

- `/check_hn <url> <keyword1> <keyword2>` — find Hacker News topics matching keywords

- `/start` — show the quick start guide
- `/help` — show available commands

## How It Works

The bot supports several monitoring modes.

First, it can detect full webpage changes. It downloads the page HTML, creates a SHA-256 hash of the content, saves it, and compares it with future checks. If the hash changes, the bot sends a Telegram notification.

Second, it can parse structured listing cards from supported pages. It extracts listing titles, prices, and links, then saves already-seen links. If a new link appears later, the bot can detect it as a new listing.

Third, it can check webpages for custom keywords. Users can check keywords directly in a command or save a keyword list and reuse it across different pages.

Fourth, it can parse Hacker News topic titles and return matching topics with their links. This is more precise than checking the full page HTML because it searches inside topic titles and returns the related links.

## Project Structure

- `bot.py` — Telegram bot commands and scheduled checks
- `page_checker.py` — page requests, hashing, listing parsing, keyword logic, Hacker News topic matching, and state handling
- `state.json` — saved tracked pages, listing links, and keywords (ignored)
- `requirements.txt` — project dependencies
- `.env` — bot token (not uploaded)
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

Show listings from a supported page:

```text
/listings https://books.toscrape.com/
```

Check for new listings:

```text
/new_listings https://books.toscrape.com/
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

Check a page using saved keywords:

```text
/check_saved_keywords https://example.com
```

Check Hacker News topics by keywords:

```text
/check_hn https://news.ycombinator.com/newest ai bot python
```

## Notes

- Uses `requests` to load webpages
- Uses `BeautifulSoup` to parse supported HTML pages
- Uses SHA-256 hashes to detect full page changes
- Uses saved listing links to detect new listings
- Supports single and multiple keyword checks
- Supports user-specific saved keywords
- Can parse Hacker News topic titles and return matching links
- Stores data in `state.json`
- Supports scheduled checks with `python-telegram-bot[job-queue]`
- Listing parsing and Hacker News parsing are site-specific and may need adapters for other websites
- The bot detects page changes, new items, and matching topics, but does not yet show detailed visual differences between page versions