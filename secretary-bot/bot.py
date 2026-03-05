import logging
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from briefing import (
    generate_morning_briefing, generate_response, generate_week_response,
    parse_event_from_message, parse_delete_request, parse_edit_request, parse_reminder,
)
from calendar_utils import get_today_events, get_upcoming_exams, get_week_events
from calendar_write import create_event, search_events, delete_event, update_event
from notes import save_note, get_notes, clear_notes

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
AUTHORIZED_USER_ID = int(os.environ["AUTHORIZED_USER_ID"])

WEEK_KEYWORDS = ["this week", "next 7 days", "week look", "weekly", "what's my week", "whats my week", "one week"]
TWO_WEEK_KEYWORDS = ["two weeks", "2 weeks", "next two", "14 days", "upcoming", "anything important"]
NOTE_PREFIXES = ("note:", "/note ")
CONV_NOTE_TRIGGERS = ("remember that ", "don't forget ", "dont forget ", "note that ", "keep in mind ", "just so you know ")
CREATE_KEYWORDS = ("add ", "create ", "schedule ", "book ", "set up ", "put ", "new event", "add event", "make an appointment", "add appointment")
CONV_CREATE_KEYWORDS = ("i'll have ", "i'm having ", "i've got ", "i'm meeting ", "i'll be ")
DELETE_KEYWORDS = ("delete ", "cancel ", "remove ", "drop ")
EDIT_KEYWORDS = ("change ", "edit ", "update ", "move ", "reschedule ", "rename ")
REMINDER_KEYWORDS = ("remind me", "set a reminder", "reminder for")

CITY_TZ_MAP = {
    "taiwan": "Asia/Taipei", "taipei": "Asia/Taipei",
    "michigan": "America/Chicago", "east lansing": "America/Chicago",
    "msu": "America/Chicago", "us": "America/Chicago", "states": "America/Chicago",
    "new york": "America/New_York", "california": "America/Los_Angeles",
    "sydney": "Australia/Sydney", "australia": "Australia/Sydney",
}

# Pending delete confirmations: {user_id: {"event_id": ..., "title": ...}}
pending_deletions: dict = {}


async def send_morning_briefing(application: Application) -> None:
    try:
        events = get_today_events()
        upcoming_exams = get_upcoming_exams(days=14)
        briefing = generate_morning_briefing(events, upcoming_exams)
        try:
            await application.bot.send_message(
                chat_id=AUTHORIZED_USER_ID, text=briefing, parse_mode="Markdown",
            )
        except Exception:
            await application.bot.send_message(chat_id=AUTHORIZED_USER_ID, text=briefing)
        logger.info("Morning briefing sent")
    except Exception as e:
        logger.error(f"Morning briefing failed: {e}")
        try:
            await application.bot.send_message(chat_id=AUTHORIZED_USER_ID, text=f"Morning briefing failed: {e}")
        except Exception:
            pass


async def send_reminder(application: Application, message: str) -> None:
    try:
        await application.bot.send_message(chat_id=AUTHORIZED_USER_ID, text=f"Reminder: {message}")
    except Exception as e:
        logger.error(f"Reminder failed: {e}")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != AUTHORIZED_USER_ID:
        return

    user_message = update.message.text
    msg_lower = user_message.lower().strip()

    # ── Delete confirmation ──────────────────────────────────────────────────
    if AUTHORIZED_USER_ID in pending_deletions:
        pending = pending_deletions.pop(AUTHORIZED_USER_ID)
        if msg_lower in ("yes", "y", "confirm", "delete", "ok"):
            try:
                delete_event(pending["event_id"])
                await update.message.reply_text(f"Deleted: {pending['title']}")
            except Exception as e:
                await update.message.reply_text(f"Could not delete: {e}")
        else:
            await update.message.reply_text("Cancelled.")
        return

    # ── Note saving (prefix) ─────────────────────────────────────────────────
    for prefix in NOTE_PREFIXES:
        if msg_lower.startswith(prefix):
            text = user_message[len(prefix):].strip()
            if text:
                save_note(text)
                await update.message.reply_text("Noted.")
            return

    # ── Conversational note saving ───────────────────────────────────────────
    for trigger in CONV_NOTE_TRIGGERS:
        if msg_lower.startswith(trigger):
            text = user_message[len(trigger):].strip()
            if text:
                save_note(text)
                await update.message.reply_text("Got it, noted.")
            return

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    # ── Event creation ───────────────────────────────────────────────────────
    if any(msg_lower.startswith(kw) for kw in CREATE_KEYWORDS) or any(msg_lower.startswith(kw) for kw in CONV_CREATE_KEYWORDS):
        event_data = parse_event_from_message(user_message)
        if not event_data:
            await update.message.reply_text(
                "Could not parse that as an event. Try:\n"
                "'Add [title] on [date] at [time] for [duration] at [location]'"
            )
            return
        try:
            tz = ZoneInfo(os.environ.get("TIMEZONE", "Asia/Taipei"))
            start_dt = datetime.strptime(
                f"{event_data['date']} {event_data['start_time']}", "%Y-%m-%d %H:%M"
            ).replace(tzinfo=tz)
            end_dt = datetime.strptime(
                f"{event_data['date']} {event_data['end_time']}", "%Y-%m-%d %H:%M"
            ).replace(tzinfo=tz)
            create_event(
                title=event_data["title"], start=start_dt, end=end_dt,
                location=event_data.get("location", ""),
                description=event_data.get("description", ""),
            )
            reply = (
                f"Created: *{event_data['title']}*\n"
                f"{start_dt.strftime('%A, %b %d')} · "
                f"{start_dt.strftime('%-I:%M %p')} – {end_dt.strftime('%-I:%M %p')}"
            )
            if event_data.get("location"):
                reply += f"\n@ {event_data['location']}"
        except Exception as e:
            reply = f"Could not create event: {e}"
        try:
            await update.message.reply_text(reply, parse_mode="Markdown")
        except Exception:
            await update.message.reply_text(reply)
        return

    # ── Event deletion ───────────────────────────────────────────────────────
    if any(msg_lower.startswith(kw) for kw in DELETE_KEYWORDS):
        parsed = parse_delete_request(user_message)
        if not parsed:
            await update.message.reply_text("Could not identify which event to delete.")
            return
        results = search_events(parsed["query"])
        if not results:
            await update.message.reply_text(f"No events found matching '{parsed['query']}'.")
            return
        event = results[0]
        pending_deletions[AUTHORIZED_USER_ID] = {"event_id": event["id"], "title": event["title"]}
        await update.message.reply_text(
            f"Found: *{event['title']}* ({event['start_raw']})\nDelete this? (yes/no)",
            parse_mode="Markdown",
        )
        return

    # ── Event editing ────────────────────────────────────────────────────────
    if any(msg_lower.startswith(kw) for kw in EDIT_KEYWORDS):
        parsed = parse_edit_request(user_message)
        if not parsed:
            await update.message.reply_text("Could not understand the edit. Try: 'Change dinner with Darren to 8pm'")
            return
        results = search_events(parsed.get("query", ""))
        if not results:
            await update.message.reply_text(f"No events found matching '{parsed.get('query', '')}'.")
            return
        event = results[0]
        try:
            tz = ZoneInfo(os.environ.get("TIMEZONE", "Asia/Taipei"))
            new_start = None
            new_end = None
            date_str = parsed.get("new_date") or event["start_raw"][:10]
            if parsed.get("new_start_time"):
                new_start = datetime.strptime(
                    f"{date_str} {parsed['new_start_time']}", "%Y-%m-%d %H:%M"
                ).replace(tzinfo=tz)
            elif parsed.get("new_date") and "T" in event["start_raw"]:
                # Date changed but no new time — keep original time on new date
                orig_dt = datetime.fromisoformat(event["start_raw"]).astimezone(tz)
                orig_time = orig_dt.strftime("%H:%M")
                new_start = datetime.strptime(
                    f"{date_str} {orig_time}", "%Y-%m-%d %H:%M"
                ).replace(tzinfo=tz)
            if parsed.get("new_end_time"):
                new_end = datetime.strptime(
                    f"{date_str} {parsed['new_end_time']}", "%Y-%m-%d %H:%M"
                ).replace(tzinfo=tz)
            update_event(
                event_id=event["id"],
                title=parsed.get("new_title") or None,
                start=new_start,
                end=new_end,
                location=parsed.get("new_location") or None,
            )
            await update.message.reply_text(f"Updated: *{event['title']}*", parse_mode="Markdown")
        except Exception as e:
            await update.message.reply_text(f"Could not update event: {e}")
        return

    # ── Reminders ────────────────────────────────────────────────────────────
    if any(kw in msg_lower for kw in REMINDER_KEYWORDS):
        parsed = parse_reminder(user_message)
        if parsed and "minutes" in parsed:
            minutes = int(parsed["minutes"])
            message = parsed.get("message", "reminder")
            tz = ZoneInfo(os.environ.get("TIMEZONE", "Asia/Taipei"))
            run_at = datetime.now(tz) + timedelta(minutes=minutes)
            scheduler = context.application.bot_data.get("scheduler")
            if scheduler:
                scheduler.add_job(
                    send_reminder, "date", run_date=run_at,
                    args=[context.application, message],
                )
                await update.message.reply_text(
                    f"Reminder set for {run_at.strftime('%-I:%M %p')}: {message}"
                )
            else:
                await update.message.reply_text("Scheduler not available.")
            return

    # ── Two-week view ────────────────────────────────────────────────────────
    if any(kw in msg_lower for kw in TWO_WEEK_KEYWORDS):
        week = get_week_events(days=14)
        upcoming_exams = get_upcoming_exams(days=14)
        response = generate_week_response(week, upcoming_exams)

    # ── One-week view ────────────────────────────────────────────────────────
    elif any(kw in msg_lower for kw in WEEK_KEYWORDS):
        week = get_week_events(days=7)
        upcoming_exams = get_upcoming_exams(days=7)
        response = generate_week_response(week, upcoming_exams)

    # ── Normal response ──────────────────────────────────────────────────────
    else:
        conversation_history = context.application.bot_data.setdefault("history", [])
        conversation_history.append({"role": "user", "content": user_message})
        if len(conversation_history) > 20:
            conversation_history.pop(0)
        events = get_today_events()
        upcoming_exams = get_upcoming_exams(days=7)
        response = generate_response(
            user_message, events, upcoming_exams, conversation_history[:-1]
        )
        conversation_history.append({"role": "model", "content": response})

    try:
        await update.message.reply_text(response, parse_mode="Markdown")
    except Exception:
        await update.message.reply_text(response)


async def notes_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != AUTHORIZED_USER_ID:
        return
    notes = get_notes()
    if not notes:
        await update.message.reply_text("No notes saved.")
        return
    lines = [f"- [{n['time']}] {n['text']}" for n in notes]
    try:
        await update.message.reply_text("*Your notes:*\n" + "\n".join(lines), parse_mode="Markdown")
    except Exception:
        await update.message.reply_text("Your notes:\n" + "\n".join(lines))


async def clear_notes_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != AUTHORIZED_USER_ID:
        return
    clear_notes()
    await update.message.reply_text("Notes cleared.")


async def timezone_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != AUTHORIZED_USER_ID:
        return
    if not context.args:
        current = os.environ.get("TIMEZONE", "Asia/Taipei")
        await update.message.reply_text(f"Current timezone: {current}\nUsage: /timezone Asia/Taipei")
        return
    new_tz = context.args[0]
    try:
        ZoneInfo(new_tz)  # validate
        os.environ["TIMEZONE"] = new_tz
        scheduler = context.application.bot_data.get("scheduler")
        if scheduler:
            scheduler.reschedule_job("morning_briefing", trigger="cron", hour=6, minute=30)
        await update.message.reply_text(f"Timezone updated to {new_tz}")
    except Exception:
        await update.message.reply_text(
            f"Invalid timezone '{new_tz}'. Use IANA format e.g. Asia/Taipei, America/Chicago"
        )


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != AUTHORIZED_USER_ID:
        return
    await update.message.reply_text(
        "*Secretary bot is active.*\n\n"
        "Morning briefing: 6:30 AM daily\n\n"
        "*Schedule:*\n"
        "- 'What's my schedule today?'\n"
        "- 'What's my week look like?'\n"
        "- 'Anything important coming up?'\n\n"
        "*Events:*\n"
        "- 'Add [event] on [date] at [time]'\n"
        "- 'Delete my dinner tonight'\n"
        "- 'Change dinner to 8pm'\n\n"
        "*Reminders:*\n"
        "- 'Remind me in 2 hours to call the hospital'\n\n"
        "*Notes:*\n"
        "- 'note: [text]' or 'remember that [text]'\n"
        "- /notes — view notes\n"
        "- /clearnotes — clear notes\n\n"
        "*Travel:*\n"
        "- /timezone Asia/Taipei\n"
        "- /timezone America/Chicago",
        parse_mode="Markdown",
    )


async def post_init(application: Application) -> None:
    tz = os.environ.get("TIMEZONE", "Asia/Taipei")
    scheduler = AsyncIOScheduler(timezone=tz)
    scheduler.add_job(
        send_morning_briefing, "cron",
        hour=6, minute=30,
        id="morning_briefing",
        args=[application],
    )
    scheduler.start()
    application.bot_data["scheduler"] = scheduler
    logger.info(f"Scheduler started — briefing at 6:30 AM {tz}")


def main() -> None:
    application = (
        Application.builder()
        .token(TELEGRAM_TOKEN)
        .post_init(post_init)
        .build()
    )

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("notes", notes_command))
    application.add_handler(CommandHandler("clearnotes", clear_notes_command))
    application.add_handler(CommandHandler("timezone", timezone_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot polling started")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
