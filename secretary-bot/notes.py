import os
from datetime import datetime
from zoneinfo import ZoneInfo

TIMEZONE = os.environ.get("TIMEZONE", "Asia/Taipei")

# In-memory — resets on redeploy, fine for a prototype
_notes: list[dict] = []


def save_note(text: str) -> None:
    tz = ZoneInfo(TIMEZONE)
    _notes.append({
        "text": text.strip(),
        "time": datetime.now(tz).strftime("%b %d, %I:%M %p"),
    })


def get_notes() -> list[dict]:
    return _notes.copy()


def clear_notes() -> None:
    _notes.clear()
