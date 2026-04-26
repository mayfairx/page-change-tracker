# Page Change Tracker

A Telegram bot built with Python for monitoring webpages, detecting changes, parsing supported listing pages, and checking custom keywords.

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

- `/start` — show the quick start guide
- `/help` — show available commands

## How It Works

The bot supports three basic monitoring modes.

First, it can detect full webpage changes. It downloads the page HTML, creates a SHA-256 hash of the content, saves it, and compares it with future checks. If the hash changes, the bot sends a Telegram notification.

Second, it can parse structured listing cards from supported pages. It extracts listing titles, prices, and links, then saves already-seen links. If a new link appears later, the bot can detect it as a new listing.

Third, it can check webpages for custom keywords. This allows users to monitor specific terms or updates without manually reviewing the page.

## Project Structure

- `bot.py` — Telegram bot commands and scheduled checks
- `page_checker.py` — page requests, hashing, listing parsing, keyword logic, and state handling
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

Show listings from a supported page:

```text
/listings https://books.toscrape.com/
```

Check for new listings:

```text
/new_listings https://books.toscrape.com/
```

## Notes

- Uses `requests` to load webpages
- Uses `BeautifulSoup` to parse supported HTML pages
- Uses SHA-256 hashes to detect full page changes
- Uses saved listing links to detect new listings
- Supports single and multiple keyword checks
- Supports user-specific saved keywords
- Stores data in `state.json`
- Supports scheduled checks with `python-telegram-bot[job-queue]`
- Listing parsing is currently site-specific and may need to be adapted for each website
- The bot detects changes and new items, but does not yet show detailed visual differences between page versions