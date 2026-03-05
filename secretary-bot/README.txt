==============================================================
  SECRETARY BOT - README
==============================================================

REPOSITORY
  GitHub: https://github.com/ChungChung-O-O/Secretary-Bot
  Hosted on: Railway (auto-deploys on GitHub push)
  Local code: /Users/austin_cheng/Desktop/Medical School/Claude/secretary-bot/
  User manual: secretary-bot/USER_MANUAL.md
  Skill file:  skills/daily-secretary/SKILL.md

--------------------------------------------------------------
STACK
--------------------------------------------------------------
  - Python + python-telegram-bot 21.5 (polling mode)
  - Claude Haiku (claude-haiku-4-5-20251001) via Anthropic SDK
  - Google Calendar: read via private ICS URL, write via Service Account
  - APScheduler: 6:30 AM daily morning briefing
  - Open-Meteo: weather data (free, no API key needed)

--------------------------------------------------------------
ENVIRONMENT VARIABLES (set on Railway)
--------------------------------------------------------------
  TELEGRAM_TOKEN
  AUTHORIZED_USER_ID
  ANTHROPIC_API_KEY
  CALENDAR_ICS_URL
  CALENDAR_ID
  GOOGLE_SERVICE_ACCOUNT_JSON
  TIMEZONE
  MED_SCHOOL_START
  WEATHER_LAT
  WEATHER_LON

--------------------------------------------------------------
ARCHITECTURE NOTES
--------------------------------------------------------------
  - calendar_utils.py  : reads calendar via ICS (read-only)
  - calendar_write.py  : writes events via Google Service Account
  - TIMEZONE           : read dynamically via _tz_str() in
                         briefing.py and calendar_utils.py
  - search_events()    : searches 60 days ahead
  - pending_deletions  : in-memory dict for delete confirmations

--------------------------------------------------------------
BUGS FIXED (Sessions 1-2)
--------------------------------------------------------------
  1. Claude faking calendar actions
       Fix: Added CRITICAL rule to SYSTEM_CONTEXT
  2. Conversational event creation not triggering
       Fix: Added CONV_CREATE_KEYWORDS list
  3. timeRangeEmpty error on event edit
       Fix: update_event preserves duration when only start changes
  4. Edit time parsed as "10pm" instead of "22:00"
       Fix: Added HH:MM format instruction to prompts
  5. Date-only moves ("move to Saturday") silently failing
       Fix: Extract original time via fromisoformat().astimezone()
  6. TIMEZONE module-level caching causing stale reads
       Fix: Replaced with _tz_str() dynamic reads
  7. search_events() had 14-day limit
       Fix: Extended to 60 days
  8. "i have a" false positive in CONV_CREATE_KEYWORDS
       Fix: Removed that trigger phrase

--------------------------------------------------------------
PHASE 2 ROADMAP (future, Windows desktop)
--------------------------------------------------------------
  - Replace Anthropic API with `claude -p` subprocess
  - Add Anki SQLite integration
      Path: %APPDATA%\Anki2\<profile>\collection.anki2
  - Switch calendar to MSU Outlook 365 ICS
  - Use Windows Task Scheduler instead of APScheduler

==============================================================
