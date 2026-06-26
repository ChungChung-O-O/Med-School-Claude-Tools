---
name: course-prep
description: Use this skill when Austin points at a folder of course materials (slides/docs/PDFs) plus an objectives or "FACts"/learning-goals list and wants it turned into a complete study pack — an objective-by-objective study guide, an Anki deck, scheduled spaced reviews, and an active-recall quiz. Trigger when he says "course prep:", "prep this folder", "prep this course", "make a study pack from this folder", "FACts prep", drops a course folder path, or asks to "get me ready for the <X> quiz/exam" given a materials folder. This is the orchestrator that chains lecture-to-notebooklm, notebooklm-to-anki, clinical-vignette-coach, and spaced-review scheduling.
version: 1.0.0
---

# Course Prep — Folder → Study Pack

One command turns a folder of course materials into everything needed to learn it: an objective-by-objective study guide, an Anki deck, spaced reviews on the calendar, and an active-recall quiz.

This skill is an **orchestrator**. It does not re-implement the component skills — it sequences them and adds a coverage-and-quality gate so nothing is missed.

## Execution model — Opus brain, Sonnet hand

Austin's standing preference (logic over filler, minimize wasted tokens): the orchestrating model (Opus) does the **thinking and checking**; Sonnet subagents do the **bulk drafting**. Apply this on every run:

1. **Opus writes the blueprint** — a numbered checklist of every objective, term, and concept that must be covered. This is cheap (a spec, not prose) and it doubles as the QA gate.
2. **Sonnet drafts** the study guide and Anki cards *against that blueprint* — Sonnet never decides *what* to cover, only fills in what Opus enumerated. This is what prevents "Sonnet missed a detail."
3. **Opus verifies** every artifact against the blueprint before declaring it done, and spot-checks accuracy of anything not directly in the source.
4. **Opus runs the live quiz directly** — grading the user's answers and catching subtle gaps is judgment work and low-volume per turn, so it is worth Opus.

Spawn Sonnet via the Agent tool with `model: sonnet`. Give it the blueprint, exact output paths, and the relevant component-skill rules.

## When This Skill Applies

Activate when Austin provides (or points at) a course folder containing:
- An **objectives / FACts / learning-goals** document (the source of truth for what to cover), AND
- One or more **source materials**: `.pptx`, `.docx`, `.pdf` slides/readings.

If the objectives file is ambiguous (multiple candidate docs), ask which one lists the learning objectives before proceeding. Everything else flows from it.

---

## Phase 0 — Intake (Opus)

This skill expects a **canonical course-folder layout** so it never re-processes old files or eats its own output. Each course folder is organized as:

```
<Course>/
  _inbox/        ← new source materials to process. The skill reads ONLY this.
  _processed/    ← files already carded (moved here after a successful run). This IS the "done" record.
  _outputs/      ← generated study guides + .apkg copies. NEVER read as a source.
  objectives/    ← the FACts / objectives / learning-goals docs (the source of truth for what to cover).
```

1. **Check the layout.** If `_inbox/`, `_processed/`, `_outputs/`, and `objectives/` don't all exist, create them. On a first run against a flat folder, move loose source materials into `_inbox/` and the FACts/objectives doc into `objectives/` — but confirm which file is the objectives doc with Austin before moving it.
2. **The input set for this run = the contents of `_inbox/` only.** Never scan `_processed/` or `_outputs/`. If `_inbox/` is empty, tell Austin there's nothing new to process and stop.
3. **Identify the objectives file** from `objectives/` (name signals: "FACts", "objectives", "learning goals", "quiz assignments"). If multiple candidates, ask which one.
4. Confirm in one line what you detected: objectives file + N new source files in `_inbox/` + the target quiz/exam date if known. If the exam date is unknown, ask once (it drives the spaced-review cadence).

## Phase 1 — Blueprint (Opus brain)

Read the objectives file in full. Produce a numbered coverage checklist, grouped by activity/section, listing **every** learning objective and **every** named term/concept the objectives demand (e.g. each directional pair, each plane, each node group). Keep it; you will hand it to Sonnet and check against it later. Do not skip enumerating list-type objectives — those are where details get dropped.

## Phase 2 — Study guide (Sonnet hand)

Spawn a Sonnet subagent to:
1. Extract text from every source file. For `.docx`/`.pptx`, extract paragraph/slide text (unzip XML if no library is available); for `.pdf` use the Read tool or `pypdf`.
2. Write an **objective-by-objective study guide** to `<course-folder>/_outputs/<CourseTag>_Study_Guide.md` (in `_outputs/`, never the folder root, so it is never picked up as a source on a later run):
   - One `##` section per activity, in the objectives' order.
   - Restate each objective as a **bold prompt**, then a tight, high-yield answer. **Bold every key term on first use.**
   - Stay at the level the objectives ask for (recognition + basic understanding unless they demand more). Depth over padding, but cover every blueprint item.
   - End with a `## Term Glossary` listing every named term with a one-line definition (for self-quiz).
   - Ground answers in the sources. Where a source is thin, fill from well-established standard knowledge and mark it **(supp)** so the verifier can spot-check. Never fabricate specifics.
3. (Optional) For slide-heavy decks that need deeper structuring, route them through **lecture-to-notebooklm** first and use that output as a source.

## Phase 3 — Verify the guide (Opus brain)

Read the guide. Confirm every blueprint item is covered (walk the checklist). Spot-check accuracy of every **(supp)** item. If anything is missing or wrong, fix it directly or send Sonnet back with the specific gaps. Only then proceed.

## Phase 4 — Anki deck (Opus blueprint + Sonnet hand)

1. Opus writes a **card coverage blueprint**: which terms/concepts become cards, which are Q&A vs cloze (cloze for sequences/mechanisms; Q&A for term→definition).
2. Spawn Sonnet to draft the cards and build the `.apkg` following the **notebooklm-to-anki** skill's rules (card quality, 6-axis tag schema, bundled `generate_apkg.py` script). Output to `~/Desktop/Claude Code/Claude_For_School/Anki/Anki_<CourseTag>_<YYYY-MM-DD>.apkg`.

   **Canonical organization (non-negotiable):**
   - All cards go into the **`MedSchool`** home deck. Never create per-lecture or per-date subdecks. Never touch `Undergrad MCAT (Austin)`.
   - Tags use the 6-axis schema: `Course::<code>`, `System::<system>`, `Source::<material>`, `Yield::High|Mid|Low`, `Boards::<section>`, and optionally `Exam::<id>`.
   - Auto-import via AnkiConnect (localhost:8765) is the default. If Anki is closed, fall back to .apkg with deck name `MedSchool`.

3. Opus verifies: file exists, non-zero, card count sane, blueprint covered, no old-style `Claude::` deck names or `FirstAid::` tags present.

## Phase 4b — Mark sources processed (Opus)

**Only after Phase 3 (guide verified) and Phase 4 (deck verified) both succeed:** move every source file processed this run from `_inbox/` to `_processed/`. This is the mechanism that prevents re-processing on the next run, so it must happen on every successful run.

- Never move a file that failed to process. If a run is partial, leave the unprocessed files in `_inbox/` and tell Austin exactly which ones remain.
- Do not move the objectives file — it stays in `objectives/`.
- After moving, report the new `_inbox/` (should be empty) and `_processed/` counts in the final summary.

On the **Medical School** Google Calendar:
- Add the quiz/exam as an event on its date.
- Seed spaced reviews of the material. Default cadence from day-0 (first study day): **+1, +3, +7, +14, +30** days, trimmed to fit the time before the exam (e.g. if 3 weeks out, use +1/+3/+7/+14 and land a final pass 1–2 days before). Title `Review: <topic>`, 20 min.
- **Show the proposed dates and get an explicit yes before creating any event.**
- Either create them via the Google Calendar MCP here, or hand off to Johnny (the Telegram bot has a `schedule_spaced_reviews` tool — Austin can say "I learned <topic> today"). Prefer creating directly unless he asks Johnny to.

## Phase 6 — Active-recall quiz (Opus, interactive)

Offer to quiz him on the objectives now:
- Ask application/why questions, **withhold answers until he attempts** (recognition is not recall).
- Interleave across the activities.
- After each answer, mark gaps precisely; route weak topics into an extra review block (Phase 5).
- For clinical/case-style topics, hand off to **clinical-vignette-coach** instead.

---

## Output locations

| Artifact | Location |
|---|---|
| Study guide (`.md`) | `<course-folder>/_outputs/` (kept out of `_inbox/` so it is never re-read as a source) |
| Anki deck (`.apkg`) | `~/Desktop/Claude Code/Claude_For_School/Anki/` (canonical) |
| Processed source files | `<course-folder>/_processed/` (moved out of `_inbox/` after a successful run) |
| Quiz/review events | Medical School Google Calendar |
| Any case logs (if vignette-coach used) | `Claude_For_School/CaseReview/` |

## Guardrails

- Confirm before any calendar write. Show the dates first.
- Ground content in the provided materials; flag supplements; never fabricate.
- Don't reproduce full artifacts in chat — confirm with a tight summary (sections, card count, file paths).
- If the folder has no clear objectives file, ask — don't guess what to cover.

## Maintenance (standing rule)

After creating or changing this skill: update `Claude_For_School/Skills_Reference.txt`, copy this file to the backup at `Claude_For_School/skills/course-prep/SKILL.md`, then commit and push the Claude_For_School repo. Do not commit secrets.
