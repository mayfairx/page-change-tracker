# Page Change Tracker

Telegram keyword monitoring bot for structured sources like Hacker News and BBC RSS feeds.

The bot can check sources by keywords, save keyword lists, monitor Hacker News in the background, and show active monitors in a Telegram watchlist.

## What it does

- Checks preset sources by keywords
- Supports Hacker News and BBC RSS feeds
- Tracks Hacker News in the background
- Sends Telegram alerts for new matching HN topics
- Saves user keywords
- Shows active monitors with `/watchlist`
- Cleans keyword input automatically, so `ai, python, bot` becomes `ai`, `python`, `bot`

## Demo

```text
/check_source hn ai, python, bot
```

```text
Adapter: Structured Link Feed
Detected profile: Hacker News
Source: Hacker News

Matching items:

From spaghetti to main bus: refactoring an AI agent orchestrator with Elm
Time: 3 minutes ago
Keywords: ai
https://...
```

```text
/watchlist
```

```text
Watchlist

Hacker News monitors:
– https://news.ycombinator.com/newest
  Every: 1 min
  Keywords: ai, python, bot
  Seen links: 2

Saved keywords:
ai, python, bot, problem, api, prompt, trump
```

## Supported sources

| Source | Key | Adapter | Status |
|---|---|---|---|
| Hacker News | `hacker_news` / `hn` | Structured Link Feed | Check + background tracking |
| BBC News | `bbc_all` / `bbc` | RSS Feed | Check only |

## Main commands

### Check a source now

```text
/check_source <source> <keywords>
```

Examples:

```text
/check_source hn ai python bot
/check_source bbc_all government police trump
```

### Save keywords

```text
/set_keywords ai python bot
```

You can also use commas:

```text
/set_keywords ai, python, bot
```

The bot will normalize the input into clean keywords.

### Show saved keywords

```text
/show_keywords
```

### Track Hacker News in the background

```text
/track_hn https://news.ycombinator.com/newest 1 ai python bot
```

Or use saved keywords:

```text
/set_keywords ai python bot
/track_hn https://news.ycombinator.com/newest 1
```

### Show active monitors

```text
/watchlist
```

## Current architecture

The project currently has several parts:

```text
bot.py
```

Handles Telegram commands, user input, and scheduled background checks.

```text
page_checker.py
```

Handles page loading, keyword logic, RSS parsing, Hacker News parsing, source presets, state handling, and watchlist output.

```text
state.json
```

Stores saved keywords, active monitors, seen links, intervals, and last check time.

## How the bot works

### Manual source check

```text
/check_source hn ai python
```

Flow:

```text
Telegram command
→ source key
→ source preset
→ adapter logic
→ keyword matching
→ formatted Telegram response
```

### Hacker News background tracking

```text
/track_hn https://news.ycombinator.com/newest 1 ai python
```

Flow:

```text
Start tracking
→ get current matching topics
→ save current links as seen_links
→ check again every interval
→ send alert only for new matching links
```

This prevents old posts from being sent as new alerts.

## Source presets

Source presets hide technical URLs from the user.

Instead of writing:

```text
/check_hn https://news.ycombinator.com/newest ai python
```

the user can write:

```text
/check_source hn ai python
```

Instead of writing:

```text
/check_rss https://feeds.bbci.co.uk/news/rss.xml?edition=uk trump police
```

the user can write:

```text
/check_source bbc_all trump police
```

## Adapter idea

The project is moving toward an adapter-based system.

Current adapters:

- **Structured Link Feed** — used for Hacker News-style structured link pages
- **RSS Feed** — used for BBC RSS feeds

Current profiles:

- **Hacker News**
- **BBC News**

The goal is to keep user-facing commands simple while keeping parsing logic flexible internally.

## Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/page-change-tracker.git
cd page-change-tracker
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create `.env`:

```env
BOT_TOKEN=your_telegram_bot_token
```

Run the bot:

```bash
python bot.py
```

## Requirements

Main libraries:

- `python-telegram-bot`
- `python-dotenv`
- `requests`
- `beautifulsoup4`
- `feedparser`

## Project status

This is a working learning project that is evolving into a small Telegram monitoring tool.

Current stable features:

- Telegram bot commands
- Hacker News parsing
- BBC RSS parsing
- Source presets
- Keyword normalization
- Saved keywords
- Hacker News background tracking
- Watchlist view

Known limitations:

- BBC source currently supports manual checking, not background tracking
- Hacker News tracking still uses a temporary internal structure
- Old development commands still exist in code
- Storage currently uses `state.json`
- No database yet
- No button UI yet

## Roadmap

Planned improvements:

- Replace `hn_tracks` with universal `monitors`
- Add `/track` support for source presets
- Add BBC background monitoring
- Add universal `/untrack`
- Add Telegram button UI
- Split the large logic file into modules
- Add SQLite storage
- Add custom RSS URLs
- Add deployment guide

## Example use cases

- Track Hacker News for AI, Python, startup, API, or product keywords
- Check BBC news feeds for politics, business, technology, or world events
- Save a keyword list and reuse it later
- Get Telegram alerts when new matching HN topics appear

## License

MIT