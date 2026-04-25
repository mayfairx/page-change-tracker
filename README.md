# Page Change Tracker

A Telegram bot built with Python that monitors webpages and notifies users when tracked pages change.

## Features

- `/track <url> <minutes>` — start tracking a page
- `/untrack <url>` — stop tracking a page
- `/show` — show tracked pages
- `/check <url>` — manually check a page
- `/reset` — clear tracked pages
- `/start` — quick start guide
- `/help` — show commands

## How It Works

The bot downloads a webpage, creates a hash of its content, saves it to `state.json`, and compares it with future checks.

If the hash changes, the bot sends a Telegram notification.

## Project Structure

- `bot.py` — Telegram bot logic
- `page_checker.py` — page request, hash and state logic
- `state.json` — tracked pages and saved hashes (ignored)
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
- Uses SHA-256 hashes to detect page changes
- Supports multiple tracked pages
- Stores tracked pages in `state.json`
- Runs automatic checks with `python-telegram-bot[job-queue]`
- The bot detects that a page changed, but does not yet show exactly what changed