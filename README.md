# Page Change Tracker

Telegram keyword monitoring bot for Hacker News and BBC RSS feeds with AI-powered news summarization.

The bot can check preset sources by keywords, save reusable keywords, monitor Hacker News and BBC News in the background, show active monitors, stop monitors, and summarize news using AI — all through Telegram inline buttons.

## What it does

- Checks preset sources by keywords
- Supports Hacker News and BBC RSS feeds
- Tracks Hacker News in the background
- Tracks BBC News RSS feeds in the background
- Sends Telegram alerts for new matching monitor items
- AI-powered news summarization via OpenRouter (Gemini 2.0 Flash)
- Saves reusable keyword lists
- Shows active monitors with `/watchlist`
- Stops active monitors with `/untrack`
- Button-based source checks, monitor setup, monitor stopping, and keyword management
- Interval selection: 1 min, 5 min, 15 min, or custom
- Confirmation steps before creating monitors, stopping monitors, and clearing keywords
- Automatic keyword cleanup and normalization
- SQLite database for persistent storage

## Project structure

```text
page-change-tracker/
├── bot/
│   ├── __init__.py
│   ├── main.py
│   ├── handlers.py
│   └── ui.py
├── core/
│   ├── __init__.py
│   ├── checker.py
│   ├── db.py
│   └── ai.py
├── data/
│   └── bot.db
├── .env
├── .gitignore
├── requirements.txt
├── run.py
└── README.md
```

## Quick start

```bash
git clone https://github.com/mayfairx/page-change-tracker.git
cd page-change-tracker
pip install -r requirements.txt
```

Create `.env`:

```env
BOT_TOKEN=your_telegram_bot_token
OPENROUTER_API_KEY=sk-or-v1-your-openrouter-key
```

Run the bot:

```bash
python run.py
```

## Commands

| Command | Description |
|---|---|
| `/start` | Open the main inline menu |
| `/help` | Show available commands and examples |
| `/check_source <source> <keywords>` | Check a source immediately |
| `/set_keywords <keywords>` | Save keywords for later use |
| `/show_keywords` | Display your saved keywords |
| `/track <source> [keywords]` | Start background monitoring |
| `/untrack <source>` | Stop monitoring a source |
| `/watchlist` | Show all active monitors |

## Button UI

Main menu:

```
[🔎 Check now]  [📡 Start monitoring]
[📋 Watchlist]  [🔑 Saved keywords]
```

**Check now flow:** Check now → Hacker News or BBC News → Enter keywords or Use saved keywords → Results with AI summaries.

**Start monitoring flow:** Start monitoring → Hacker News or BBC News → Enter keywords or Use saved keywords → Choose interval (1/5/15/Custom min) → Confirm → Start.

**Watchlist flow:** Watchlist → Stop Hacker News / Stop BBC News → Confirm → Monitor removed.

**Saved keywords flow:** Saved keywords → Show / Set / Clear.

If you choose "Use saved keywords" but none are saved, the bot asks you to enter them now and saves automatically.

## Supported sources

| Source | Keys | Adapter | Check | Monitor | AI Summary |
|---|---|---|---|---|---|
| Hacker News | `hn`, `hacker_news` | Structured Link Feed | ✅ | ✅ | ✅ |
| BBC News | `bbc`, `bbc_all` | RSS Feed | ✅ | ✅ | ✅ |

## AI Summarization

The bot uses OpenRouter API with Google Gemini 2.0 Flash to generate one-sentence summaries. For BBC News, the AI receives both the title and the article text for better accuracy. For Hacker News, it summarizes based on the title.

**Example — raw title vs AI summary:**

```text
Why Spotify has no button to filter out AI music
Summary: Spotify doesn't offer a button to filter AI music because they haven't addressed the issue yet.
```

## Requirements

- Python 3.10+
- `python-telegram-bot`
- `python-dotenv`
- `requests`
- `beautifulsoup4`
- `feedparser`
- `openai`

## Tech stack

- **Database:** SQLite
- **AI:** OpenRouter → Google Gemini 2.0 Flash
- **Navigation:** Custom MenuStack (stack-based screen history)
- **Architecture:** `bot/` for Telegram layer, `core/` for business logic, `data/` for storage

## License

MIT
```