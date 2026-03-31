---
name: syllabus-to-calendar
description: Use this skill when the user wants to parse a course syllabus (PDF, image, or pasted text) and bulk-create Google Calendar events from it. Extracts lectures, labs, exams, deadlines, and orientations, shows a preview, then creates all events after confirmation.
version: 1.0.0
---

# Syllabus to Calendar

Parse a syllabus and bulk-create Google Calendar events. One command turns an entire semester schedule into calendar events.

## When This Skill Applies

Activate when the user says any of:
- `/syllabus`
- `parse my syllabus`
- `import syllabus to calendar`
- `add syllabus to calendar`
- Provides a syllabus file with intent to populate their calendar

Accepts any of:
- A **PDF file path** (e.g. `syllabus: /path/to/syllabus.pdf`)
- An **image/screenshot path** (PNG, JPG, etc.)
- **Pasted text** — raw syllabus schedule copied from a website or document

---

## Step 1: Get the Syllabus

If the user provided a file path, read it:

```
Read the file at the provided path.
```

- **PDF**: Use the Read tool — Claude can read PDFs directly with vision.
- **Image**: Use the Read tool — Claude can see images.
- **Pasted text**: Process it directly.

If no input is provided, ask:
> "Please provide the syllabus — paste the text, or give me the file path (PDF or image)."

---

## Step 2: Extract All Events

Analyze the syllabus content and extract every schedulable item. For each event, extract:

| Field | Description |
|-------|-------------|
| `date` | YYYY-MM-DD |
| `start_time` | HH:MM in 24h, or `all_day` if no time given |
| `end_time` | HH:MM in 24h, or `all_day` |
| `title` | Full event title |
| `type` | One of: Lecture, Lab, Exam, Deadline, Orientation, Holiday, Other |
| `location` | Room/building if mentioned, else empty |
| `description` | Any notes (topics covered, instructions) |

**Extraction rules:**
- Date ranges like "Aug 17–21" should create one event per day only if there are distinct events each day — otherwise create one event on the start date.
- Recurring items (e.g. "Anatomy lecture every Mon/Wed 8am") → create individual events for every occurrence across the semester.
- Deadlines with no time → mark as `all_day`.
- Exams: capture start time AND end time if given; otherwise default 2-hour duration.
- Skip administrative items with no calendar date (e.g. office hours listed without specific dates).

---

## Step 3: Show Preview Table

Present the extracted events as a compact table before creating anything:

```
Found 47 events. Preview (first 10):

| Date       | Time          | Title                          | Type        |
|------------|---------------|--------------------------------|-------------|
| 2026-08-17 | All day       | Orientation Day                | Orientation |
| 2026-08-18 | 08:00–09:00   | Anatomy Lecture 1 — Intro      | Lecture     |
| 2026-08-20 | 08:00–09:00   | Anatomy Lecture 2 — Upper Limb | Lecture     |
| 2026-09-05 | 09:00–12:00   | Foundations Block Exam         | Exam        |
| ...        |               | (37 more events)               |             |

Create all 47 events? (yes / no, or: yes but skip lectures / exams only)
```

Wait for user confirmation before proceeding.

**Filter shortcuts the user may say:**
- `exams only` → create only Exam-type events
- `skip lectures` → create everything except Lecture events
- `just exams and deadlines` → filter accordingly
- `yes` → create all

---

## Step 4: Create Calendar Events

After confirmation, first get the user's calendar list to confirm which calendar to use:

1. Call `mcp__claude_ai_Google_Calendar__gcal_list_calendars` to see available calendars.
2. Use the primary calendar unless the user specifies otherwise (e.g. "use my school calendar").

Then create each event. For **timed events**:
```
mcp__claude_ai_Google_Calendar__gcal_create_event with:
  calendarId: <primary or specified>
  summary: <title>
  start: { dateTime: "YYYY-MM-DDTHH:MM:SS", timeZone: <user's timezone> }
  end: { dateTime: "YYYY-MM-DDTHH:MM:SS", timeZone: <user's timezone> }
  description: <type + any notes>
  location: <if present>
```

For **all-day events** (no time given):
```
  start: { date: "YYYY-MM-DD" }
  end: { date: "YYYY-MM-DD" }
```

Create events sequentially. If a batch fails, note which ones failed and continue.

**Default timezone**: Check the user's local timezone from context. If unknown, ask before creating events.

---

## Step 5: Report Results

After all events are created:

```
Done. Created 47/47 events on your primary calendar.

Summary:
- 32 Lectures
- 8 Labs
- 5 Exams
- 2 Deadlines
```

If any failed:
```
Created 45/47 events. 2 failed:
- 2026-09-05 Foundations Block Exam (date parse error)
- 2026-11-24 Thanksgiving (holiday already exists?)

Retry these? (yes / no)
```

---

## Notes

- **Recurring lectures**: If a syllabus says "lecture every Mon/Wed 8–9am for 16 weeks", calculate and create each individual event — do not rely on calendar recurrence rules, as schedule irregularities (holidays, etc.) are easier to handle as individual events.
- **Duplicate detection**: If the user runs the skill twice, duplicate events will be created. Warn the user if they mention re-running it.
- **Large syllabi**: For 100+ events, warn the user this may take a moment.
- **Ambiguous dates**: If a date is ambiguous (e.g. "9/5" — September or May?), use the academic year context to resolve (Aug start = fall semester = Sep).
