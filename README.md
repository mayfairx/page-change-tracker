# Page Change Tracker

Telegram keyword monitoring bot for structured sources like Hacker News and BBC RSS feeds.

The bot can check preset sources by keywords, save keyword lists, monitor Hacker News and BBC News in the background, show active monitors, and disable monitors from Telegram.

## What it does

- Checks preset sources by keywords
- Supports Hacker News and BBC RSS feeds
- Tracks Hacker News in the background
- Tracks BBC News RSS feeds in the background
- Sends Telegram alerts for new matching monitor items
- Saves reusable keyword lists
- Shows active monitors with `/watchlist`
- Disables active monitors with `/untrack`
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

### Check BBC News

```text
/check_source bbc trump police government
```

Example response:

```text
Adapter: RSS Feed
Detected profile: BBC News
Source: BBC All

Matching items:

Example BBC article title
Feed: BBC Top Stories
Published: Tue, 28 Apr 2026 18:48:48 GMT
Keywords: government
https://...
```

### Start Hacker News monitoring

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

### Start BBC monitoring

```text
/track bbc trump police government
```

Example response:

```text
Monitor enabled.

Source: BBC News
Adapter: RSS Feed
Profile: BBC News
Interval: 1 min
Keywords: trump, police, government
Current matching items saved: 26
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
– BBC News
  Source: bbc_all
  Adapter: rss_feed
  URL: bbc_all
  Every: 1 min
  Keywords: trump, police, government
  Seen links: 26

– Hacker News
  Source: hacker_news
  Adapter: structured_link_feed
  URL: https://news.ycombinator.com/newest
  Every: 1 min
  Keywords: ai, python, bot
  Seen links: 8

Saved keywords:
ai, python, api, prompt
```

### Disable monitoring

```text
/untrack hn
```

or:

```text
/untrack bbc
```

Example response:

```text
Monitor disabled.

Source: BBC News
Removed monitors: 1
```

## Supported sources

| Source | Key | Adapter | Status |
|---|---|---|---|
| Hacker News | `hn` | Structured Link Feed | Check + background monitoring |
| BBC News | `bbc` | RSS Feed | Check + background monitoring |

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
/track bbc trump police government
```

or with commas:

```text
/track hn ai, python, bot
/track bbc trump, police, government
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

### Disable monitoring

```text
/untrack <source>
```

Examples:

```text
/untrack hn
/untrack bbc
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
/untrack
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

Handles page loading, keyword logic, RSS parsing, Hacker News parsing, BBC matching, source presets, monitor creation, monitor removal, state handling, and watchlist output.

```text
state.json
```

Stores saved keywords, active monitors, seen links, intervals, and last check time.

## How the bot works

### Manual source check

```text
/check_source hn ai python
/check_source bbc trump police
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

### Background monitoring

```text
/track hn ai python
/track bbc trump police
```

Flow:

```text
Start monitoring
→ resolve source key
→ use source profile
→ get current matching items
→ save current matching links as seen_links
→ store monitor in state.json
→ background checker reads monitors
→ send alert only for new matching links
```

This prevents old items from being sent as new alerts.

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

### Untrack flow

```text
/untrack bbc
```

Flow:

```text
Telegram command
→ source key
→ find matching monitors in state.json
→ remove monitors for that source
→ save updated state
→ confirm removal
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
      },
      "bbc_all": {
        "source": "bbc_all",
        "adapter": "rss_feed",
        "profile": "BBC News",
        "url": "bbc_all",
        "interval": 1,
        "last_check": 0,
        "keywords": ["trump", "police", "government"],
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
/track hn ai python
```

Instead of writing BBC RSS feed URLs manually, the user can write:

```text
/check_source bbc trump police
/track bbc trump police
```

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
- BBC background monitoring
- Universal `monitors` state for active monitors
- Watchlist view
- Source untracking
- Duplicate protection with `seen_links`

Known limitations:

- Monitoring interval is currently fixed at 1 minute
- Storage currently uses `state.json`
- No database yet
- No Telegram button UI yet
- The main logic file should be split into modules later

## Roadmap

Planned improvements:

- Add interval selection
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
- Track BBC news feeds for politics, business, technology, or world events
- Save a keyword list and reuse it later
- Get Telegram alerts when new matching Hacker News or BBC items appear
- Disable active monitoring when a source is no longer needed

## License

MIT