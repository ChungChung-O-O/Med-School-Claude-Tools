# Morning Briefing Skill

**Version:** 1.0.0
**Trigger phrases:** "morning briefing", "run morning briefing", "market update", "play my briefing"

---

## What This Skill Does

Fetches the last 12 hours of US market news (stock-specific + macro), uses Claude to rank and write a podcast-style broadcast script, converts it to audio via edge-tts, auto-plays it, and saves the MP3 to `~/Desktop/MorningBriefing/YYYY-MM-DD.mp3`.

**Tracked stocks:** NVDA, MU, VST, FIG, IBIT
**Voice:** Ava (en-US-AvaNeural, US female)
**Schedule:** 8am Taiwan time via launchd (automatic)

---

## When Triggered Manually

Run the script immediately:

```bash
python3 ~/.claude/skills/morning-briefing/morning_briefing.py
```

---

## Configuration Updates

### Update stock watchlist
Edit `STOCKS` and `STOCK_CONTEXT` in:
```
~/.claude/skills/morning-briefing/morning_briefing.py
```

### Change the lookback window
Edit `HOURS_BACK` (default: `12`) in `morning_briefing.py`.

### Change the voice
Edit `VOICE` in `morning_briefing.py`. Browse available voices:
```bash
python3 -c "import asyncio, edge_tts; asyncio.run(edge_tts.list_voices())" | grep en-US
```

### Change the schedule time
Edit `Hour` and `Minute` in:
```
~/Library/LaunchAgents/com.user.morningbriefing.plist
```
Then reload:
```bash
launchctl unload ~/Library/LaunchAgents/com.user.morningbriefing.plist
launchctl load ~/Library/LaunchAgents/com.user.morningbriefing.plist
```

---

## One-Time Setup

### 1. Install Python dependencies
```bash
pip3 install yfinance feedparser edge-tts
```

### 2. Register launchd scheduler
```bash
cp ~/.claude/skills/morning-briefing/com.user.morningbriefing.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.user.morningbriefing.plist
```

### 3. Verify it's registered
```bash
launchctl list | grep morningbriefing
```

### 4. Test it manually before relying on the schedule
```bash
python3 ~/.claude/skills/morning-briefing/morning_briefing.py
```

---

## Troubleshooting

- **No audio plays:** Check edge-tts install (`pip3 install edge-tts`). Fallback: script prints to terminal.
- **Claude not found:** Ensure `claude` is in PATH. Check with `which claude`.
- **No news fetched:** Check internet connection. RSS feeds may occasionally be unreachable.
- **Logs:** launchd output goes to `/tmp/morning_briefing.log` and `/tmp/morning_briefing_error.log`

---

## Files

| File | Purpose |
|------|---------|
| `morning_briefing.py` | Main script — edit config here |
| `com.user.morningbriefing.plist` | launchd schedule definition |
| `SKILL.md` | This file |
