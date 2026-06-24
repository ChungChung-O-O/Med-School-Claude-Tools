---
name: daily-secretary
description: Use this skill when the user wants to set up, deploy, update, or troubleshoot their personal Telegram secretary bot. This bot sends a morning briefing at 6:30 AM and responds to schedule queries via Telegram. Handles both cloud deployment (Railway) and future local Windows deployment.
version: 1.0.0
---

# Daily Secretary Bot

A personal Telegram bot that acts as a secretary for a medical student. Sends a morning briefing at 6:30 AM and responds to schedule questions throughout the day. Powered by Gemini 2.0 Flash and Google Calendar.

## Architecture

```
secretary-bot/
  bot.py              — Telegram bot, scheduler, message handler
  briefing.py         — Gemini API calls for briefing and responses
  calendar_utils.py   — ICS fetch, event parsing, exam detection
  requirements.txt
  Procfile            — Railway deployment
  railway.json        — Railway config
  .env.example        — Credential template
```

## Phase 1: Cloud (Railway) — Current Setup

### Environment Variables
| Variable | Value |
|---|---|
| `TELEGRAM_TOKEN` | Bot token from @BotFather |
| `AUTHORIZED_USER_ID` | `6749308184` |
| `GEMINI_API_KEY` | Google AI Studio API key |
| `CALENDAR_ICS_URL` | Google Calendar public ICS URL |
| `TIMEZONE` | e.g. `Asia/Taipei`, `America/Chicago` |

### First-Time Deployment on Railway

Guide the user through these steps:

1. **Create a Railway account** at railway.app (free tier, no credit card)

2. **Push the bot code to GitHub**
   - Create a new GitHub repo (can be private)
   - Push only the `secretary-bot/` folder contents (not the whole Claude repo)
   - Make sure `.env` is NOT committed (it's in .gitignore)

3. **Create a new Railway project**
   - New Project → Deploy from GitHub repo → select the secretary-bot repo
   - Railway auto-detects Python via NIXPACKS

4. **Add environment variables in Railway dashboard**
   - Go to your service → Variables tab
   - Add all five variables from the table above
   - Do NOT use a `.env` file on Railway — use the Variables tab

5. **Verify the Procfile** — Railway uses `worker: python bot.py` (not a web server)
   - In Railway: Settings → ensure it picks up the Procfile

6. **Test the bot**
   - Open Telegram → find your bot → send `/start`
   - It should reply confirming it's active
   - To test the morning briefing immediately, temporarily change the cron time in `bot.py` to 2 minutes from now, redeploy, then revert

### Updating the Bot

When the user wants to change behavior (timezone, exam keywords, briefing style):
1. Edit the relevant file in `secretary-bot/`
2. Push to GitHub — Railway auto-redeploys

## Phase 2: Local Windows Desktop (Future)

When the user is back in the US with their desktop, migrate to local:

### Key differences from cloud version
- Replace Gemini API with `claude -p` subprocess (uses Claude Code subscription)
- Add Anki SQLite integration: `%APPDATA%\Anki2\<profile>\collection.anki2`
- Use Windows Task Scheduler instead of APScheduler for the 6:30 AM trigger
- Run bot as a startup script via Task Scheduler ("At startup" trigger)

### Anki integration (Phase 2 only)
Read the Anki database with Python sqlite3:
```python
import sqlite3, os
db_path = os.path.expandvars(r"%APPDATA%\Anki2\<ProfileName>\collection.anki2")
# Query due cards per deck — Anki must be closed when reading
```
Anki must be closed when the script reads the DB (database lock).

### Switching from Gemini to claude CLI
Replace `briefing.py` Gemini calls with:
```python
import subprocess
result = subprocess.run(
    ["claude", "-p", prompt],
    capture_output=True, text=True, timeout=30
)
return result.stdout.strip()
```

## Troubleshooting

**Bot not responding:**
- Check Railway logs for errors
- Verify `TELEGRAM_TOKEN` and `AUTHORIZED_USER_ID` env vars are set correctly
- Ensure the Procfile says `worker:` not `web:`

**Calendar showing no events:**
- If using the public ICS URL, only events with "Public" visibility appear
- Private ICS URL (shows all events): use the `private-[key]/basic.ics` format
- Current private URL is stored in Railway environment variables as `CALENDAR_ICS_URL`

**Morning briefing not arriving:**
- Verify `TIMEZONE` env var matches your current timezone
- Railway runs in UTC — the APScheduler timezone conversion handles local time
- Check Railway logs around 6:30 AM local time for scheduler output

**Exam alerts not triggering:**
- Exam detection uses keywords: exam, test, nbme, usmle, quiz, assessment, final, midterm, osce
- Make sure calendar event titles contain one of these keywords
