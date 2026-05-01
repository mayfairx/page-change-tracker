# Page Change Tracker

Telegram keyword monitoring bot for structured sources like Hacker News and BBC RSS feeds.

The bot can check preset sources by keywords, save reusable keywords, monitor Hacker News and BBC News in the background, show active monitors, stop monitors, and manage the main user flow through Telegram buttons.

## What it does

- Checks preset sources by keywords
- Supports Hacker News and BBC RSS feeds
- Tracks Hacker News in the background
- Tracks BBC News RSS feeds in the background
- Sends Telegram alerts for new matching monitor items
- Saves reusable keyword lists
- Shows active monitors with `/watchlist`
- Stops active monitors with `/untrack`
- Supports button-based source checks
- Supports button-based monitor setup
- Supports button-based monitor stopping
- Supports button-based saved keyword management
- Supports manual keyword input through buttons
- Supports saved keywords through buttons
- Supports interval selection: 1 min, 5 min, 15 min, or custom
- Shows a confirmation step before creating a monitor
- Shows a confirmation step before stopping a monitor
- Shows a confirmation step before clearing saved keywords
- Cleans keyword input automatically, so `ai, python, bot` becomes `ai`, `python`, `bot`
- Stores active background monitors in a universal `monitors` state structure

## Demo

### Start menu

```text
/start
```

Button menu:

```text
[Check now] [Start monitoring]
[Watchlist] [Saved keywords]
```

---

## Main user flows

### Check now with buttons

Flow:

```text
/start
→ Check now
→ Hacker News / BBC News
→ Enter keywords / Use saved keywords
→ Show results
```

Example:

```text
/start
→ Check now
→ Hacker News
→ Enter keywords
→ ai python bot
```

The bot immediately checks Hacker News and returns matching items.

Saved keywords flow:

```text
/start
→ Check now
→ BBC News
→ Use saved keywords
```

The bot uses the currently saved keyword list and returns matching BBC items.

---

### Start monitoring with buttons

Flow:

```text
/start
→ Start monitoring
→ Hacker News / BBC News
→ Enter keywords / Use saved keywords
→ 1 min / 5 min / 15 min / Custom
→ Confirm monitor
→ Start / Cancel
```

Example:

```text
/start
→ Start monitoring
→ Hacker News
→ Enter keywords
→ ai python bot
→ 5 min
→ Start
```

This creates a Hacker News monitor with:

```text
Source: Hacker News
Keywords: ai, python, bot
Interval: 5 min
```

### Custom interval

The user can choose `Custom` and send any interval in minutes.

Example:

```text
10
```

This creates a monitor that checks every 10 minutes.

---

### Watchlist and stop monitoring with buttons

Flow:

```text
/start
→ Watchlist
→ Stop Hacker News / Stop BBC News
→ Confirm stop
→ Stop / Cancel
```

Example:

```text
/start
→ Watchlist
→ Stop BBC News
→ Stop
```

Expected result:

```text
Monitor disabled.

Source: BBC News
Removed monitors: 1
```

After stopping a monitor, the bot shows the updated watchlist.

---

### Manage saved keywords with buttons

Flow:

```text
/start
→ Saved keywords
→ Show keywords / Set / Replace / Clear keywords
```

Set or replace saved keywords:

```text
/start
→ Saved keywords
→ Set / Replace
→ ai python api prompt
```

Show saved keywords:

```text
/start
→ Saved keywords
→ Show keywords
```

Clear saved keywords:

```text
/start
→ Saved keywords
→ Clear keywords
→ Clear / Cancel
```

Saved keywords can then be reused in both check and monitoring flows.

---

## Command examples

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

Example Hacker News topic
Time: 3 minutes ago
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

### Start monitoring with command

```text
/track hn ai, python, bot
/track bbc trump police government
```

Command mode currently uses the default monitoring interval:

```text
1 minute
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

### Use saved keywords with command

Save keywords first:

```text
/set_keywords ai python api prompt
```

Then use:

```text
/track hn
```

or:

```text
/track bbc
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
  Every: 10 min
  Keywords: trump, police, government
  Seen links: 26

– Hacker News
  Source: hacker_news
  Adapter: structured_link_feed
  URL: https://news.ycombinator.com/newest
  Every: 5 min
  Keywords: ai, python, bot
  Seen links: 8
```

### Stop monitoring with command

```text
/untrack hn
/untrack bbc
```

Example response:

```text
Monitor disabled.

Source: BBC News
Removed monitors: 1
```

---

## Supported sources

| Source | Key | Adapter | Status |
|---|---|---|---|
| Hacker News | `hn` | Structured Link Feed | Check + background monitoring |
| BBC News | `bbc` | RSS Feed | Check + background monitoring |

---

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
/check_source bbc trump, police, government
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

or use saved keywords:

```text
/set_keywords ai python bot
/track hn
```

### Show active monitors

```text
/watchlist
```

### Stop monitoring

```text
/untrack <source>
```

Examples:

```text
/untrack hn
/untrack bbc
```

---

## Button UI

The bot has a Telegram button interface.

Open the main menu:

```text
/start
```

Main menu:

```text
[Check now] [Start monitoring]
[Watchlist] [Saved keywords]
```

### Check now flow

```text
/start
→ Check now
→ Choose source
→ Choose keywords option
→ Show results
```

Current check flow:

```text
Check now
→ Hacker News / BBC News
→ Enter keywords / Use saved keywords
→ Result message
```

### Start monitoring flow

```text
/start
→ Start monitoring
→ Choose source
→ Choose keywords option
→ Choose interval
→ Confirm monitor
```

Current monitoring flow:

```text
Start monitoring
→ Hacker News / BBC News
→ Enter keywords / Use saved keywords
→ 1 min / 5 min / 15 min / Custom
→ Confirm monitor
→ Start / Cancel
```

### Saved keywords flow

```text
/start
→ Saved keywords
→ Show keywords / Set / Replace / Clear keywords
```

Current saved keywords menu:

```text
[Show keywords] [Set / Replace]
[Clear keywords]
[Back]
```

### Keyword options

The user can choose:

```text
Enter keywords
```

and then send:

```text
ai python bot
```

or choose:

```text
Use saved keywords
```

after saving keywords with:

```text
/set_keywords ai python api prompt
```

or through the button UI:

```text
/start
→ Saved keywords
→ Set / Replace
```

### Interval options

The user can choose:

```text
1 min
5 min
15 min
Custom
```

If `Custom` is selected, the bot asks for a custom interval in minutes.

Example:

```text
10
```

### Monitor confirmation

Before creating a monitor, the bot shows a confirmation screen:

```text
Confirm monitor

Source: Hacker News
Keywords: ai, python, bot
Interval: 5 min

Start monitoring?
```

Buttons:

```text
[Start] [Cancel]
```

The monitor is only created after pressing `Start`.

### Watchlist buttons

The Watchlist button shows active monitors and dynamic stop buttons.

If both sources are active:

```text
[Stop Hacker News] [Stop BBC News]
[Back]
```

If only BBC is active:

```text
[Stop BBC News]
[Back]
```

If there are no active monitors:

```text
[Back]
```

### Stop confirmation

Before stopping a monitor, the bot shows a confirmation screen:

```text
Confirm stop

Source: BBC News

Stop this monitor?
```

Buttons:

```text
[Stop] [Cancel]
```

The monitor is removed only after pressing `Stop`.

### Clear keywords confirmation

Before clearing saved keywords, the bot shows a confirmation screen:

```text
Clear saved keywords?

This will remove your saved keyword list.
```

Buttons:

```text
[Clear] [Cancel]
```

The saved keyword list is removed only after pressing `Clear`.

---

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

---

## Current architecture

The project currently has several main parts:

```text
bot.py
```

Handles Telegram commands, button UI, user input, temporary button-flow state, and scheduled background jobs.

```text
page_checker.py
```

Handles page loading, keyword logic, RSS parsing, Hacker News parsing, BBC matching, source presets, monitor creation, monitor removal, saved keyword logic, state handling, and watchlist output.

```text
state.json
```

Stores saved keywords, active monitors, seen links, intervals, and last check time.

---

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

### Button-based source check

```text
/start
→ Check now
→ source selected
→ keywords selected or entered
→ result shown
```

Temporary data is stored in `context.user_data` during the flow:

```python
context.user_data["pending_action"] = "check"
context.user_data["pending_source"] = "hn"
context.user_data["pending_step"] = "keywords"
```

After the result is shown, temporary setup data is cleared.

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

### Button-based monitor setup

Flow:

```text
/start
→ Start monitoring
→ source selected
→ keywords selected or entered
→ interval selected
→ confirmation shown
→ monitor created only after Start
```

Temporary data is stored in `context.user_data` during setup.

Example temporary values:

```python
context.user_data["pending_action"] = "track"
context.user_data["pending_source"] = "hn"
context.user_data["pending_keywords"] = ["ai", "python", "bot"]
context.user_data["pending_interval"] = 5
context.user_data["pending_step"] = "confirm"
```

After monitor creation or cancel/back action, the temporary setup data is cleared.

### Button-based monitor stopping

Flow:

```text
/start
→ Watchlist
→ source stop button selected
→ confirmation shown
→ monitor removed only after Stop
```

Temporary stop data is stored in:

```python
context.user_data["pending_untrack_source"] = "hn"
```

or:

```python
context.user_data["pending_untrack_source"] = "bbc"
```

After stopping or cancelling, the temporary stop data is cleared.

### Button-based saved keywords management

Flow:

```text
/start
→ Saved keywords
→ Set / Replace
→ user sends keywords
→ keywords saved
```

Temporary data:

```python
context.user_data["pending_action"] = "set_keywords"
context.user_data["pending_step"] = "saved_keywords"
```

After saving, temporary data is cleared.

### Saved keyword reuse

Command flow:

```text
/set_keywords ai python bot
/track hn
```

Button check flow:

```text
/start
→ Check now
→ Hacker News
→ Use saved keywords
```

Button monitoring flow:

```text
/start
→ Start monitoring
→ Hacker News
→ Use saved keywords
→ Choose interval
→ Start
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

---

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
        "interval": 5,
        "last_check": 0,
        "keywords": ["ai", "python", "bot"],
        "seen_links": []
      },
      "bbc_all": {
        "source": "bbc_all",
        "adapter": "rss_feed",
        "profile": "BBC News",
        "url": "bbc_all",
        "interval": 10,
        "last_check": 0,
        "keywords": ["trump", "police", "government"],
        "seen_links": []
      }
    }
  }
}
```

---

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

---

## Adapter idea

The project is moving toward an adapter-based monitoring system.

Current adapters:

- **Structured Link Feed** — used for Hacker News-style structured link pages
- **RSS Feed** — used for BBC RSS feeds

Current profiles:

- **Hacker News**
- **BBC News**

The goal is to keep user-facing commands simple while keeping parsing logic flexible internally.

---

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

---

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

---

## Requirements

Main libraries:

- `python-telegram-bot`
- `python-dotenv`
- `requests`
- `beautifulsoup4`
- `feedparser`

---

## Project status

This is a working learning project that is evolving into a small Telegram monitoring tool.

Current stable features:

- Clean Telegram command interface
- Basic Telegram button UI
- Hacker News parsing
- BBC RSS parsing
- Source presets
- Keyword normalization
- Saved keywords
- Button-based saved keyword management
- Button-based source checks
- Hacker News background monitoring
- BBC background monitoring
- Button-based monitor setup
- Button-based monitor stopping
- Manual keyword input through buttons
- Saved keyword usage through buttons
- Interval selection with 1 / 5 / 15 min options
- Custom interval input
- Confirmation step before monitor creation
- Confirmation step before monitor stopping
- Confirmation step before clearing saved keywords
- Dynamic watchlist stop buttons based on active monitors
- Universal `monitors` state for active monitors
- Watchlist view
- Source untracking
- Duplicate protection with `seen_links`

Known limitations:

- Storage currently uses `state.json`
- No database yet
- Button UI works, but visual polish is still minimal
- No named keyword templates yet
- No deployment guide yet
- The main logic file should be split into modules later
- No screenshots or demo GIF yet

---

## Roadmap

Planned improvements:

- Improve button labels and message text
- Add UI polish with clearer button names and emojis
- Add named user keyword templates
- Split the large logic file into modules
- Add SQLite storage
- Add custom RSS URLs
- Add deployment guide
- Add screenshots and demo GIFs

---

## Next UI direction

The next project step is UI polish.

Possible improved menu:

```text
[🔎 Check now] [📡 Start monitor]
[📋 Watchlist] [🔑 Keywords]
```

Possible improved flow names:

```text
Start monitoring → Start monitor
Saved keywords → Keywords
Set / Replace → Set keywords
Clear keywords → Delete keywords
```

The main logic already works. The next step is making the bot feel cleaner and more user-friendly.

---

## Example use cases

- Track Hacker News for AI, Python, startup, API, or product keywords
- Track BBC news feeds for politics, business, technology, or world events
- Save a keyword list and reuse it later
- Get Telegram alerts when new matching Hacker News or BBC items appear
- Stop active monitoring when a source is no longer needed
- Quickly check a source without creating a background monitor

---

## Learning focus

This project was built to practice:

- Telegram bot commands
- Telegram inline buttons
- Callback query handling
- Temporary user state with `context.user_data`
- HTML parsing with BeautifulSoup
- RSS parsing with feedparser
- Keyword matching
- Background jobs
- JSON state management
- Basic monitor architecture
- Git commits and project cleanup
- Button-based UX flows

## License

MIT