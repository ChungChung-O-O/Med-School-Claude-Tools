import os
import requests
import recurring_ical_events
from datetime import datetime, date, timedelta
from icalendar import Calendar
from zoneinfo import ZoneInfo

CALENDAR_ICS_URL = os.environ["CALENDAR_ICS_URL"]


def _tz_str() -> str:
    return os.environ.get("TIMEZONE", "Asia/Taipei")


def fetch_calendar() -> Calendar:
    response = requests.get(CALENDAR_ICS_URL, timeout=10)
    response.raise_for_status()
    return Calendar.from_ical(response.content)


def get_events_for_date(target_date: date) -> list[dict]:
    cal = fetch_calendar()
    tz = ZoneInfo(_tz_str())
    raw_events = recurring_ical_events.of(cal).at(target_date)

    events = []
    for component in raw_events:
        dtstart = component.get("DTSTART")
        if dtstart is None:
            continue

        start = dtstart.dt
        is_all_day = not isinstance(start, datetime)

        start_local = start.astimezone(tz) if isinstance(start, datetime) else None

        dtend = component.get("DTEND")
        end_local = None
        if dtend:
            end_dt = dtend.dt
            if isinstance(end_dt, datetime):
                end_local = end_dt.astimezone(tz)

        location = str(component.get("LOCATION", ""))
        description = str(component.get("DESCRIPTION", ""))
        events.append({
            "title": str(component.get("SUMMARY", "Untitled")),
            "start": start_local,
            "end": end_local,
            "location": location if location != "None" else "",
            "description": description if description != "None" else "",
            "all_day": is_all_day,
        })

    def sort_key(e):
        if e["all_day"] or e["start"] is None:
            return datetime.min.replace(tzinfo=tz)
        return e["start"]

    events.sort(key=sort_key)
    return events


def get_week_events(days: int = 7) -> dict:
    """Returns {date: [events]} for the next N days (skips empty days)."""
    tz = ZoneInfo(_tz_str())
    today = datetime.now(tz).date()
    week = {}
    for i in range(days):
        target = today + timedelta(days=i)
        events = get_events_for_date(target)
        if events:
            week[target] = events
    return week


def get_today_events() -> list[dict]:
    tz = ZoneInfo(_tz_str())
    today = datetime.now(tz).date()
    return get_events_for_date(today)


def get_upcoming_exams(days: int = 3) -> list[dict]:
    tz = ZoneInfo(_tz_str())
    today = datetime.now(tz).date()
    exam_keywords = [
        "exam", "test", "nbme", "usmle", "quiz", "assessment", "final", "midterm", "osce",
        "interview", "appointment", "deadline", "due", "presentation", "orientation",
    ]

    upcoming = []
    for i in range(1, days + 1):
        target_date = today + timedelta(days=i)
        for event in get_events_for_date(target_date):
            if any(kw in event["title"].lower() for kw in exam_keywords):
                upcoming.append({**event, "days_until": i})

    return upcoming
