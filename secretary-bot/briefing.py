import json as _json
import os
import anthropic
from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo

from weather import get_weather
from notes import get_notes

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
MED_SCHOOL_START = os.environ.get("MED_SCHOOL_START", "")


def _tz_str() -> str:
    return os.environ.get("TIMEZONE", "Asia/Taipei")

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_CONTEXT = """You are a concise personal secretary for a medical student named Chung.
Rules:
- Keep responses brief and well-formatted for Telegram
- Use Telegram markdown: *bold* for emphasis, bullet points with -
- Professional but warm tone, no excessive emojis (1-2 max)
- For morning briefings: greeting, weather, schedule, exam alerts, countdown, one motivational line
- For queries: answer directly and reference the schedule when relevant
- CRITICAL: You cannot add, edit, or delete calendar events yourself. Never confirm or pretend to have done so. If the user mentions a future event they want added, tell them: 'To add it, say: Add [event] on [date] at [time]'"""


def _call_claude(prompt: str) -> str:
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def _countdown_text() -> str:
    if not MED_SCHOOL_START:
        return ""
    try:
        start = date.fromisoformat(MED_SCHOOL_START)
        tz = ZoneInfo(_tz_str())
        today = datetime.now(tz).date()
        days = (start - today).days
        if days > 0:
            return f"\nMed school starts in *{days} days* ({start.strftime('%B %d, %Y')})"
        elif days == 0:
            return "\n*Med school starts TODAY!*"
    except ValueError:
        pass
    return ""


def format_events(events: list[dict]) -> str:
    if not events:
        return "No events scheduled."

    lines = []
    for event in events:
        if event["all_day"] or event["start"] is None:
            time_str = "All day"
        else:
            time_str = event["start"].strftime("%-I:%M %p")
            if event["end"]:
                time_str += f" - {event['end'].strftime('%-I:%M %p')}"

        line = f"- {time_str}: {event['title']}"
        if event.get("location"):
            line += f" @ {event['location']}"
        if event.get("description"):
            desc = event["description"][:120].strip()
            line += f"\n  _{desc}_"
        lines.append(line)

    return "\n".join(lines)


def format_week(week: dict) -> str:
    if not week:
        return "Nothing on the calendar this week."
    lines = []
    for day, events in sorted(week.items()):
        day_str = day.strftime("%A, %b %d")
        lines.append(f"*{day_str}*")
        lines.append(format_events(events))
    return "\n".join(lines)


def generate_morning_briefing(events: list[dict], upcoming_exams: list[dict]) -> str:
    tz = ZoneInfo(_tz_str())
    date_str = datetime.now(tz).strftime("%A, %B %d, %Y")
    weather = get_weather()
    events_text = format_events(events)
    countdown = _countdown_text()

    exam_section = ""
    if upcoming_exams:
        exam_lines = []
        for exam in upcoming_exams:
            d = exam["days_until"]
            label = "tomorrow" if d == 1 else f"in {d} days"
            exam_lines.append(f"- *{exam['title']}* — {label}")
        exam_section = "\n\nUpcoming exams:\n" + "\n".join(exam_lines)

    prompt = (
        f"{SYSTEM_CONTEXT}\n\n"
        f"Today is {date_str}.\n"
        f"Weather: {weather}\n\n"
        f"Today's schedule:\n{events_text}"
        f"{exam_section}"
        f"{countdown}\n\n"
        "Write a morning briefing. Start with 'Good morning, Chung.' "
        "Include the weather, schedule, exam alerts if any, countdown if present, "
        "and end with one short motivational line. Keep it under 200 words."
    )

    return _call_claude(prompt)


def generate_week_response(week: dict, upcoming_exams: list[dict]) -> str:
    week_text = format_week(week)
    countdown = _countdown_text()

    exam_section = ""
    if upcoming_exams:
        exam_lines = [f"- {e['title']} in {e['days_until']} day(s)" for e in upcoming_exams]
        exam_section = "\nUpcoming exams:\n" + "\n".join(exam_lines)

    prompt = (
        f"{SYSTEM_CONTEXT}\n\n"
        f"Week schedule:\n{week_text}"
        f"{exam_section}"
        f"{countdown}\n\n"
        "Give a brief weekly overview. Highlight busy days, exam alerts, and the countdown if present."
    )

    return _call_claude(prompt)


def generate_response(
    user_message: str,
    events: list[dict],
    upcoming_exams: list[dict],
    history: list[dict],
) -> str:
    tz = ZoneInfo(_tz_str())
    date_str = datetime.now(tz).strftime("%A, %B %d, %Y")
    events_text = format_events(events)
    countdown = _countdown_text()

    exam_section = ""
    if upcoming_exams:
        exam_lines = [f"- {e['title']} in {e['days_until']} day(s)" for e in upcoming_exams]
        exam_section = "\nUpcoming exams (next 7 days):\n" + "\n".join(exam_lines)

    notes = get_notes()
    notes_section = ""
    if notes:
        note_lines = [f"- [{n['time']}] {n['text']}" for n in notes]
        notes_section = "\nSaved notes:\n" + "\n".join(note_lines)

    calendar_context = (
        f"Today is {date_str}.\n\n"
        f"Today's schedule:\n{events_text}"
        f"{exam_section}"
        f"{countdown}"
        f"{notes_section}"
    )

    history_text = ""
    for msg in history[-10:]:
        role = "You" if msg["role"] == "model" else "Chung"
        history_text += f"{role}: {msg['content']}\n"

    prompt = (
        f"{SYSTEM_CONTEXT}\n\n"
        f"Context:\n{calendar_context}\n\n"
        f"{history_text}"
        f"Chung: {user_message}\nYou:"
    )

    return _call_claude(prompt)


def parse_event_from_message(user_message: str) -> dict | None:
    """Extract structured event data from natural language. Returns dict or None."""
    tz = ZoneInfo(_tz_str())
    now = datetime.now(tz)

    prompt = (
        f"Today is {now.strftime('%A, %B %d, %Y')} and the time is {now.strftime('%I:%M %p')} ({_tz_str()}).\n\n"
        f"Extract calendar event details from this message: \"{user_message}\"\n\n"
        "Reply with JSON only, no markdown:\n"
        '{"title":"...","date":"YYYY-MM-DD","start_time":"HH:MM","end_time":"HH:MM","location":"","description":""}\n\n'
        "Rules:\n"
        "- Use 24-hour HH:MM format for times (e.g. 19:00 for 7pm, 22:00 for 10pm)\n"
        "- If no end time, add 1 hour to start time\n"
        "- Resolve 'tomorrow', 'next Monday', etc. to actual dates\n"
        "- If this is NOT a request to create/add/schedule an event, reply with: {\"error\":\"not an event\"}"
    )

    try:
        text = _call_claude(prompt).strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0]
        data = _json.loads(text)
        if "error" in data:
            return None
        return data
    except Exception:
        return None


def parse_delete_request(user_message: str) -> dict | None:
    """Extract event search query from a delete request. Returns dict or None."""
    prompt = (
        f"Extract the event to delete from: \"{user_message}\"\n"
        "Reply with JSON only: {\"query\": \"search term for the event\"}\n"
        "If not a delete request, reply: {\"error\": \"not a delete\"}"
    )
    try:
        text = _call_claude(prompt).strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0]
        data = _json.loads(text)
        return None if "error" in data else data
    except Exception:
        return None


def parse_edit_request(user_message: str) -> dict | None:
    """Extract event edit details from natural language. Returns dict or None."""
    tz = ZoneInfo(_tz_str())
    now = datetime.now(tz)
    prompt = (
        f"Today is {now.strftime('%A, %B %d, %Y')} ({_tz_str()}).\n"
        f"Extract edit details from: \"{user_message}\"\n"
        "Reply with JSON only:\n"
        "{\"query\":\"search term\",\"new_title\":\"\",\"new_date\":\"\",\"new_start_time\":\"\",\"new_end_time\":\"\",\"new_location\":\"\"}\n"
        "Use 24-hour HH:MM format for times (e.g. 22:00 for 10pm). Use YYYY-MM-DD for dates. Leave fields empty if not changing them.\n"
        "If not an edit request, reply: {\"error\": \"not an edit\"}"
    )
    try:
        text = _call_claude(prompt).strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0]
        data = _json.loads(text)
        return None if "error" in data else data
    except Exception:
        return None


def parse_reminder(user_message: str) -> dict | None:
    """Extract reminder time and message. Returns {minutes: int, message: str} or None."""
    tz = ZoneInfo(_tz_str())
    now = datetime.now(tz)
    prompt = (
        f"Current time is {now.strftime('%I:%M %p')} ({_tz_str()}).\n"
        f"Extract reminder from: \"{user_message}\"\n"
        "Reply with JSON only: {\"minutes\": 60, \"message\": \"what to remind\"}\n"
        "Convert 'in X hours' to minutes. For 'at 3pm', calculate minutes from now.\n"
        "If not a reminder request, reply: {\"error\": \"not a reminder\"}"
    )
    try:
        text = _call_claude(prompt).strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0]
        data = _json.loads(text)
        return None if "error" in data else data
    except Exception:
        return None
