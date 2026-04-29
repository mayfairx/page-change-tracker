# Page Change Tracker

Telegram keyword monitoring bot for structured sources like Hacker News and BBC RSS feeds.

The bot can check preset sources by keywords, save keyword lists, monitor Hacker News in the background, and show active monitors in a Telegram watchlist.

## What it does

- Checks preset sources by keywords
- Supports Hacker News and BBC RSS feeds
- Tracks Hacker News in the background
- Sends Telegram alerts for new matching Hacker News topics
- Saves reusable keyword lists
- Shows active monitors with `/watchlist`
- Cleans keyword input automatically, so `ai, python, bot` becomes `ai`, `python`, `bot`
- Stores active background monitors in a universal `monitors` state structure

## Demo

### Check Hacker News

```text
/check_source hn ai, python, bot
```

Example response:

```text
Adapter: Structured Link Feed
Detected profile: Hacker News
Source: Hacker News

Matching items:

Evaluating CUDA Tile for AI Workloads on Hopper and Blackwell GPUs
Time: 0 minutes ago
Keywords: ai
https://...
```

### Start background monitoring

```text
/track hn ai, python, bot
```

Example response:

```text
Monitor enabled.

Source: Hacker News
Adapter: Structured Link Feed
Profile: Hacker News
URL: https://news.ycombinator.com/newest
Interval: 1 min
Keywords: ai, python, bot
Current matching topics saved: 4
```

### Use saved keywords

```text
/set_keywords ai python api prompt
/track hn
```

Example response:

```text
Monitor enabled.

Source: Hacker News
Adapter: Structured Link Feed
Profile: Hacker News
URL: https://news.ycombinator.com/newest
Interval: 1 min
Keywords: ai, python, api, prompt
Current matching topics saved: 5
```

### Show active monitors

```text
/watchlist
```

Example response:

```text
Watchlist

Active monitors:
– Hacker News
  Source: hacker_news
  Adapter: structured_link_feed
  URL: https://news.ycombinator.com/newest
  Every: 1 min
  Keywords: ai, python, api, prompt
  Seen links: 5

Saved keywords:
ai, python, api, prompt
```

## Supported sources

| Source | Key | Adapter | Status |
|---|---|---|---|
| Hacker News | `hn` | Structured Link Feed | Check + background monitoring |
| BBC News | `bbc` | RSS Feed | Check only |

## Main commands

### Start / help

```text
/start
/help
```

### Check a source now

```text
/check_source <source> <keywords>
```

Examples:

```text
/check_source hn ai python bot
/check_source bbc government police trump
```

Comma-separated input also works:

```text
/check_source hn ai, python, bot
```

### Save keywords

```text
/set_keywords ai python bot
```

or:

```text
/set_keywords ai, python, bot
```

Both formats are saved as clean keywords.

### Show saved keywords

```text
/show_keywords
```

### Start background monitoring

Use keywords directly:

```text
/track hn ai python bot
```

or with commas:

```text
/track hn ai, python, bot
```

or use saved keywords:

```text
/set_keywords ai python bot
/track hn
```

Current default monitoring interval:

```text
1 minute
```

Interval selection will be added later through the button UI.

### Show active monitors

```text
/watchlist
```

## Current command interface

Current user-facing commands:

```text
/start
/help
/check_source
/set_keywords
/show_keywords
/track
/watchlist
```

Legacy development commands were removed from the Telegram interface to keep the bot focused on source monitoring.

## Current architecture

The project currently has several main parts:

```text
bot.py
```

Handles Telegram commands, user input, and scheduled background jobs.

```text
page_checker.py
```

Handles page loading, keyword logic, RSS parsing, Hacker News parsing, source presets, monitor creation, state handling, and watchlist output.

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

Manual checks do not create monitors and do not save tracking data.

### Hacker News background monitoring

```text
/track hn ai python
```

Flow:

```text
Start monitoring
→ resolve source key
→ use Hacker News profile
→ get current matching topics
→ save current matching links as seen_links
→ store monitor in state.json
→ background checker reads monitors
→ send alert only for new matching links
```

This prevents old posts from being sent as new alerts.

### Saved keyword flow

```text
/set_keywords ai python bot
/track hn
```

Flow:

```text
Save keywords
→ start monitoring source
→ no keywords provided in /track
→ bot uses saved keywords
→ monitor is created
```

## Monitors state

Background monitoring is stored in a universal `monitors` structure.

Example:

```json
{
  "chat_id": {
    "keywords": ["ai", "python", "bot"],
    "monitors": {
      "https://news.ycombinator.com/newest": {
        "source": "hacker_news",
        "adapter": "structured_link_feed",
        "profile": "Hacker News",
        "url": "https://news.ycombinator.com/newest",
        "interval": 1,
        "last_check": 0,
        "keywords": ["ai", "python", "bot"],
        "seen_links": []
      }
    }
  }
}
```

## Source presets

Source presets hide technical URLs from the user.

Instead of writing a Hacker News URL manually, the user can write:

```text
/check_source hn ai python
```

or:

```text
/track hn ai python
```

Instead of writing a BBC RSS URL manually, the user can write:

```text
/check_source bbc trump police
```

BBC background monitoring is not available yet, so this currently works only for manual checks.

## Adapter idea

The project is moving toward an adapter-based monitoring system.

Current adapters:

- **Structured Link Feed** — used for Hacker News-style structured link pages
- **RSS Feed** — used for BBC RSS feeds

Current profiles:

- **Hacker News**
- **BBC News**

The goal is to keep user-facing commands simple while keeping parsing logic flexible internally.

## Keyword normalization

The bot normalizes user input before saving, checking, or tracking keywords.

Example input:

```text
ai, python, bot
```

becomes:

```text
ai
python
bot
```

This makes the bot more tolerant of normal human input.

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

- Clean Telegram command interface
- Hacker News parsing
- BBC RSS parsing
- Source presets
- Keyword normalization
- Saved keywords
- Hacker News background monitoring
- Universal `monitors` state for active monitors
- Watchlist view
- Duplicate protection with `seen_links`

Known limitations:

- BBC source currently supports manual checking, not background monitoring
- Background monitoring is currently implemented for Hacker News only
- Monitoring interval is currently fixed at 1 minute
- Storage currently uses `state.json`
- No database yet
- No Telegram button UI yet
- The main logic file should be split into modules later

## Roadmap

Planned improvements:

- Add BBC background monitoring
- Add interval selection
- Add universal `/untrack`
- Add Telegram button UI
- Add user-created keyword templates
- Split the large logic file into modules
- Add SQLite storage
- Add custom RSS URLs
- Add deployment guide
- Add screenshots and demo GIFs

## Future button flow

Planned UI direction:

```text
/start
→ Choose action
→ Choose source
→ Enter keywords or use saved keywords
→ Choose interval
→ Confirm monitor
```

The command interface is kept simple now so the same logic can later be reused by buttons.

## Example use cases

- Track Hacker News for AI, Python, startup, API, or product keywords
- Check BBC news feeds for politics, business, technology, or world events
- Save a keyword list and reuse it later
- Get Telegram alerts when new matching Hacker News topics appear

## License

MIT