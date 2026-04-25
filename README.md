# Page Change Tracker

A Telegram bot built with Python that monitors webpages, tracks page changes, and can parse product/listing cards from supported pages.

## Features

- `/check <url>` — manually check if a page changed
- `/track <url> <minutes>` — track a page automatically
- `/untrack <url>` — stop tracking a page
- `/show` — show tracked pages
- `/reset` — clear tracked pages
- `/listings <url>` — show parsed listings from a supported page
- `/new_listings <url>` — detect new listings based on saved links
- `/start` — quick start guide
- `/help` — show commands

## How It Works

The bot can work in two modes.

First, it can monitor a full webpage by downloading its HTML, creating a SHA-256 hash of the content, and comparing it with the previously saved hash.

Second, it can parse structured listing cards from supported pages and save seen listing links. If a new link appears later, the bot can detect it as a new listing.

## Project Structure

- `bot.py` — Telegram bot commands and scheduled checks
- `page_checker.py` — page requests, hashing, listings parsing and state logic
- `state.json` — saved tracked pages and listing links (ignored)
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

## Notes

- Uses `requests` to load webpages
- Uses `BeautifulSoup` to parse HTML
- Uses SHA-256 hashes to detect full page changes
- Uses saved listing links to detect new listings
- Stores state in `state.json`
- Supports scheduled checks with `python-telegram-bot[job-queue]`
- Current listing parser is site-specific and may need to be adapted for each website
- The bot currently detects that something changed, but does not yet show detailed differences for every website