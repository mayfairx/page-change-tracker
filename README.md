```markdown
# Page Change Tracker

A Telegram bot that monitors Hacker News and BBC News for keywords you care about. Check sources manually, save reusable keywords, run background monitors with configurable intervals, get alerts when new matches appear, and receive AI-powered summaries of news — all through an inline button interface.

**Features:** Manual source check for Hacker News and BBC News. Background monitoring at 1/5/15 minute intervals or custom. Saved keywords reusable across checks and monitors. Watchlist with dynamic stop buttons for active monitors. Confirmation flows before creating monitors, stopping monitors, and clearing keywords. Smart navigation via MenuStack — Back always returns to the previous screen. Keyword auto-save when none are saved yet. Formatted UI with bold headers, emoji icons, and clean message structure. AI-powered news summarization via OpenRouter (Gemini 2.0 Flash). SQLite database for persistent storage.

## Project structure

```
page-change-tracker/
├── bot/                    # Telegram layer
│   ├── __init__.py
│   ├── main.py             # Entry point, Application setup
│   ├── handlers.py         # All async handlers and commands
│   └── ui.py               # Keyboards, texts, MenuStack, helpers
├── core/                   # Business logic
│   ├── __init__.py
│   ├── checker.py          # Page loading, parsing, matching, monitors
│   ├── db.py               # SQLite database operations
│   ├── ai.py               # AI summarization via OpenRouter
│   └── state.py            # Legacy JSON state (deprecated)
├── data/                   # Persistent storage
│   └── bot.db              # SQLite database
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

Create a `.env` file:

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
| `/check_source <source> <keywords>` | Check a source immediately (e.g. `/check_source hn ai python`) |
| `/set_keywords <keywords>` | Save keywords for later use |
| `/show_keywords` | Display your saved keywords |
| `/track <source> [keywords]` | Start background monitoring. Uses saved keywords if none provided. |
| `/untrack <source>` | Stop monitoring a source |
| `/watchlist` | Show all active monitors |

## Button UI

Launch the bot with `/start` to open the main menu:

```
[🔎 Check now]  [📡 Start monitoring]
[📋 Watchlist]  [🔑 Saved keywords]
```

**Check now flow:** Check now → Hacker News or BBC News → Enter keywords or Use saved keywords → Results appear immediately with AI summaries.

**Start monitoring flow:** Start monitoring → Hacker News or BBC News → Enter keywords or Use saved keywords → Choose interval (1 min / 5 min / 15 min / Custom) → Confirm screen shows source, keywords, and interval → Press Start to create the monitor.

**Watchlist flow:** Watchlist shows all active monitors with their details. Dynamic stop buttons appear for each active source. Pressing one shows a confirmation screen. After confirming, the monitor is removed and the updated watchlist is shown.

**Saved keywords flow:** Saved keywords → Show keywords displays your list. Set / Replace asks you to send new keywords. Clear keywords shows a confirmation before deleting.

**Keyword auto-save:** If you choose "Use saved keywords" but none are saved, the bot asks you to enter keywords now and saves them automatically.

## Supported sources

| Source | Keys | Adapter | Check | Monitor | AI Summary |
|---|---|---|---|---|---|
| Hacker News | `hn`, `hacker_news` | Structured Link Feed | ✅ | ✅ | ✅ |
| BBC News | `bbc`, `bbc_all` | RSS Feed | ✅ | ✅ | ✅ |

## AI Summarization

The bot uses OpenRouter API with Google Gemini 2.0 Flash to generate one-sentence summaries of news articles. For BBC News, the AI receives both the title and the article summary for better accuracy. For Hacker News, it summarizes based on the title. Summaries are included in both manual checks and background monitor alerts.

## Requirements

- Python 3.10+
- `python-telegram-bot` — Telegram Bot API framework
- `python-dotenv` — Environment variable loading
- `requests` — HTTP requests
- `beautifulsoup4` — HTML parsing
- `feedparser` — RSS feed parsing
- `openai` — OpenRouter API client (OpenAI-compatible)

## Tech stack

- **Database:** SQLite via `sqlite3`
- **AI:** OpenRouter → Google Gemini 2.0 Flash
- **Navigation:** Custom MenuStack (stack-based screen history)
- **Architecture:** Modular — `bot/` for Telegram layer, `core/` for business logic, `data/` for storage

## License

MIT
```