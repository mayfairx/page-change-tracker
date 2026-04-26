# Page Change Tracker

A Telegram bot built with Python that monitors webpages, tracks page changes, parses listings from supported pages, and checks pages for specific keywords.

## Features

- `/check <url>` — manually check if a page changed
- `/track <url> <minutes>` — track a page automatically
- `/untrack <url>` — stop tracking a page
- `/show` — show tracked pages
- `/reset` — clear tracked data

- `/listings <url>` — show parsed listings from a supported page
- `/new_listings <url>` — detect new listings based on saved links

- `/check_keyword <url> <keyword>` — check one keyword on a page
- `/check_keywords <url> <keyword1> <keyword2>` — check multiple keywords on a page
- `/set_keywords <keyword1> <keyword2>` — save keywords
- `/show_keywords` — show saved keywords

- `/start` — quick start guide
- `/help` — show commands

## How It Works

The bot can work in several modes.

First, it can monitor full webpage changes. It downloads the page HTML, creates a SHA-256 hash of the content, saves it, and compares it with future checks. If the hash changes, the bot sends a Telegram notification.

Second, it can parse structured listing cards from supported pages. It extracts listing title, price, and link, then saves seen links. If a new link appears later, the bot can detect it as a new listing.

Third, it can check webpages for specific keywords. This can be used to monitor words like `discount`, `promo`, `sale`, `-50%`, or any custom keyword list saved by the user.

## Project Structure

- `bot.py` — Telegram bot commands and scheduled checks
- `page_checker.py` — page requests, hashing, listings parsing, keyword logic and state logic
- `state.json` — saved tracked pages, listing links and keywords (ignored)
- `requirements.txt` — dependencies
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

Track page changes:

```text
/track https://example.com 5
```

Check one keyword:

```text
/check_keyword https://example.com example
```

Check multiple keywords:

```text
/check_keywords https://example.com example domain sale
```

Save keywords:

```text
/set_keywords discount promo sale -50
```

Show saved keywords:

```text
/show_keywords
```

Show listings from a supported page:

```text
/listings https://books.toscrape.com/
```

Check new listings:

```text
/new_listings https://books.toscrape.com/
```

## Notes

- Uses `requests` to load webpages
- Uses `BeautifulSoup` to parse HTML
- Uses SHA-256 hashes to detect full page changes
- Uses saved listing links to detect new listings
- Supports single keyword checks
- Supports multiple keyword checks
- Can save user-specific keywords in `state.json`
- Keyword matching is case-insensitive
- Stores state in `state.json`
- Supports scheduled checks with `python-telegram-bot[job-queue]`
- Current listing parser is site-specific and may need to be adapted for each website
- The bot can detect page changes and new listings, but does not yet show detailed differences for every website