import json
import logging
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from google.oauth2 import service_account
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)

CALENDAR_ID = os.environ["CALENDAR_ID"]


def _get_service():
    info = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
    creds = service_account.Credentials.from_service_account_info(
        info,
        scopes=["https://www.googleapis.com/auth/calendar"],
    )
    return build("calendar", "v3", credentials=creds)


def _tz():
    return os.environ.get("TIMEZONE", "Asia/Taipei")


def create_event(
    title: str,
    start: datetime,
    end: datetime,
    location: str = "",
    description: str = "",
) -> str:
    service = _get_service()
    tz = _tz()
    event = {
        "summary": title,
        "location": location,
        "description": description,
        "start": {"dateTime": start.isoformat(), "timeZone": tz},
        "end": {"dateTime": end.isoformat(), "timeZone": tz},
    }
    logger.info(f"Creating event on calendar: {CALENDAR_ID}")
    result = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
    logger.info(f"Created event ID: {result.get('id')}")
    return result.get("htmlLink", "")


def search_events(query: str, days: int = 60) -> list[dict]:
    """Search for events matching query within next N days."""
    service = _get_service()
    tz = ZoneInfo(_tz())
    now = datetime.now(tz)
    time_max = now + timedelta(days=days)

    result = service.events().list(
        calendarId=CALENDAR_ID,
        q=query,
        timeMin=now.isoformat(),
        timeMax=time_max.isoformat(),
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    events = []
    for item in result.get("items", []):
        start_raw = item["start"].get("dateTime", item["start"].get("date", ""))
        events.append({
            "id": item["id"],
            "title": item.get("summary", "Untitled"),
            "start_raw": start_raw,
        })
    return events


def delete_event(event_id: str) -> None:
    service = _get_service()
    service.events().delete(calendarId=CALENDAR_ID, eventId=event_id).execute()
    logger.info(f"Deleted event ID: {event_id}")


def update_event(
    event_id: str,
    title: str = None,
    start: datetime = None,
    end: datetime = None,
    location: str = None,
) -> None:
    service = _get_service()
    tz = _tz()
    event = service.events().get(calendarId=CALENDAR_ID, eventId=event_id).execute()

    if title:
        event["summary"] = title
    if start and not end:
        # Preserve original duration when only start changes
        orig_start_str = event["start"].get("dateTime")
        orig_end_str = event["end"].get("dateTime")
        if orig_start_str and orig_end_str:
            orig_start = datetime.fromisoformat(orig_start_str)
            orig_end = datetime.fromisoformat(orig_end_str)
            duration = orig_end - orig_start
            event["start"] = {"dateTime": start.isoformat(), "timeZone": tz}
            event["end"] = {"dateTime": (start + duration).isoformat(), "timeZone": tz}
        else:
            event["start"] = {"dateTime": start.isoformat(), "timeZone": tz}
    elif start:
        event["start"] = {"dateTime": start.isoformat(), "timeZone": tz}
    if end:
        event["end"] = {"dateTime": end.isoformat(), "timeZone": tz}
    if location is not None:
        event["location"] = location

    service.events().update(calendarId=CALENDAR_ID, eventId=event_id, body=event).execute()
    logger.info(f"Updated event ID: {event_id}")
