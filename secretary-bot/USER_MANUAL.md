# Secretary Bot — User Manual

Personal Telegram bot for Chung. Sends a morning briefing at 6:30 AM and handles schedule, events, notes, and reminders via natural language.

---

## Daily Usage

### Checking Your Schedule

| What you say | What you get |
|---|---|
| "What's my schedule today?" | Today's events |
| "What's my week look like?" | Next 7 days |
| "Anything important coming up?" | Next 14 days |

---

### Adding Events

Start your message with a create keyword, or phrase it naturally:

**Keyword triggers:** `add`, `create`, `schedule`, `book`, `set up`, `put`, `new event`, `make an appointment`

**Conversational triggers:** `I'll have`, `I'm having`, `I've got`, `I'm meeting`, `I'll be`

**Examples:**
```
Add dinner with Darren tomorrow at 7pm at Bing An Tang for 2 hours
Create a study session on Friday from 2-4pm
I'll have dinner with Darren tomorrow from 7-9pm, location TBD
I'm meeting Dr. Chen on Monday at 10am
Schedule my dentist appointment next Thursday at 3pm for 1 hour
```

> If the bot says "Could not parse that as an event", try rephrasing with "Add [event] on [date] at [time]".

---

### Editing Events

Start with: `change`, `edit`, `update`, `move`, `reschedule`, `rename`

**Examples:**
```
Change dinner to 8pm
Change the dinner end time to 10pm
Move dinner to Saturday                  ← keeps same time, new date
Reschedule dentist to next Friday at 2pm
Rename "Study session" to "Anatomy review"
Change dinner location to Shin Yeh
```

**How time updates work:**
- "Change dinner to 8pm" → moves start to 8pm, end shifts to preserve original duration
- "Change dinner end time to 10pm" → only end time changes
- "Change dinner to 8pm-10pm" → both start and end updated explicitly
- "Move dinner to Saturday" → same time, new date

> The bot can find events up to 60 days out.

---

### Deleting Events

Start with: `delete`, `cancel`, `remove`, `drop`

**Examples:**
```
Delete my dinner with Darren
Cancel the dentist appointment
Remove study session on Friday
```

The bot will ask you to confirm before deleting. Reply `yes` or `no`.

---

### Reminders

```
Remind me in 30 minutes to take my medication
Remind me in 2 hours to call the hospital
Set a reminder for 45 minutes to check email
Reminder for 1 hour to leave for the airport
```

Reminders are in-memory — they are lost if the bot restarts.

---

### Notes

**Saving notes:**
```
note: Darren is vegetarian
/note Call Mom about flight details
Remember that the MSU orientation is business casual
Don't forget parking is paid at the hospital
Note that Dr. Chen prefers email over phone
Keep in mind the library closes at 9pm on weekends
Just so you know the exam is open book
```

**Viewing and clearing notes:**
```
/notes        — view all saved notes
/clearnotes   — clear all notes
```

> Notes reset when the bot redeploys on Railway. They are for short-term reminders, not permanent storage.

---

### General Questions

You can ask the bot anything conversational — it has context of today's schedule and upcoming exams:

```
Am I free this afternoon?
Do I have anything before 3pm?
What time is my exam?
How many days until med school starts?
```

> The bot cannot add, edit, or delete events through general conversation. Use the explicit commands above for calendar changes.

---

## Commands

| Command | What it does |
|---|---|
| `/start` | Show this help summary |
| `/notes` | View saved notes |
| `/clearnotes` | Clear all notes |
| `/timezone Asia/Taipei` | Switch timezone |
| `/timezone America/Chicago` | Switch to US Central (MSU) |

---

## Travel Mode

When you travel, update the timezone so times display correctly:

```
/timezone Asia/Taipei        ← Taiwan
/timezone America/Chicago    ← Michigan (MSU/East Lansing)
/timezone America/New_York   ← New York
/timezone America/Los_Angeles ← California
/timezone Australia/Sydney   ← Sydney
```

The morning briefing always fires at 6:30 AM in whatever timezone is set.

---

## Morning Briefing

Sent automatically at **6:30 AM** in your current timezone. Includes:
- Today's weather (temperature, feels like, high/low)
- Today's full schedule
- Upcoming exam alerts (next 14 days)
- Countdown to med school start date
- One motivational line

---

## Exam & Alert Keywords

The bot automatically flags events as "upcoming exams/alerts" if the title contains any of these words:

`exam`, `test`, `nbme`, `usmle`, `quiz`, `assessment`, `final`, `midterm`, `osce`, `interview`, `appointment`, `deadline`, `due`, `presentation`, `orientation`

---

## Troubleshooting

**Bot not responding:**
- Wait 30 seconds — Railway may be restarting the container
- Check if a previous message got a response; if yes, the bot is alive

**Event not showing up after adding:**
- Refresh your Google Calendar app
- Check that you're looking at the correct calendar (the one shared with the service account)

**"No events found" when editing/deleting:**
- The bot searches up to 60 days ahead
- Try using a more specific search term (e.g., "dinner with Darren" instead of "dinner")

**"Could not parse" on event creation:**
- Rephrase as: `Add [title] on [date] at [time]`
- Include a specific date and time

**Wrong time on events after moving:**
- Make sure to specify the time explicitly if you want it to change: "Move dinner to Saturday at 8pm"

**Morning briefing not arriving:**
- Verify the timezone is set correctly with `/timezone`
- The bot uses APScheduler — if Railway restarted after 6:30 AM, the briefing for that day is missed

---

## Infrastructure

| Component | Details |
|---|---|
| Hosting | Railway (cloud, always-on) |
| AI model | Claude Haiku (`claude-haiku-4-5-20251001`) |
| Calendar read | Google Calendar private ICS URL |
| Calendar write | Google Service Account API |
| Weather | Open-Meteo (free, no API key) |
| Telegram | python-telegram-bot 21.5, polling mode |

---

## Known Limitations

- Notes are in-memory — reset on every Railway redeploy
- Cannot handle recurring event edits (edits only affect the specific instance found by search)
- Reminders are lost on restart
- General conversation ("Am I free?") cannot modify the calendar — use explicit commands
