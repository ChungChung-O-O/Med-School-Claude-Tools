---
name: filtered-deck
description: Use this skill when the user wants to study or test only a SLICE of their single MedSchool Anki home deck — one document, system, yield level, or exam — rather than the whole deck. Creates an Anki filtered (dynamic) deck driven by the tag schema. Because AnkiConnect cannot create filtered decks, this skill auto-applies the precise targeting tag and then walks the user through the one-time creation + one-click rebuild. Trigger on "filtered deck", "filter deck", "make a deck for just X", "drill only X", "study just X", "test me on <document/topic>", or when the user wants to isolate a subset of cards to review.
---

# Filtered Deck Builder

Help the user drill a precise slice of the single `MedSchool` home deck (e.g. one lecture/document, one system, one yield tier) using an Anki filtered deck, while keeping the one-home-deck + tags architecture intact.

## Key constraint (read first)

AnkiConnect has **no action to create a filtered/dynamic deck** (verified via apiReflect: no createFilteredDeck / scheduler wrapper). So this skill does the automatable parts and teaches the 3-click manual step:
1. Resolve the user's request to the correct Anki search string from the tag schema.
2. Ensure a precise targeting tag exists on the right cards (auto-apply via AnkiConnect addTags if missing).
3. Give the user the exact search string and click-by-click create/rebuild instructions.

## Tag schema (7 axes)

The MedSchool deck uses these tag axes:
- `Course::<code>` — e.g. Course::OST510
- `System::<system>` — e.g. System::Anatomy, System::Cardiovascular
- `Source::<material>` — e.g. Source::FACts, Source::Lecture
- `Yield::High` | `Yield::Mid` | `Yield::Low`
- `Boards::<section>` — e.g. Boards::Anatomy
- `Exam::<id>` — e.g. Exam::2026-07-16
- `Doc::<document_name>` — the specific source document/lecture, underscores for spaces, e.g. Doc::Basic_Anatomical_Terminology

`Doc::` is the axis that lets the user isolate "the cards from one document." If the cards the user wants to drill have no `Doc::` tag yet, identify the exact subset (confirm with the user, and use the `System::` signature trick: cards belonging to other lectures carry a second System tag), then apply a `Doc::<name>` tag via AnkiConnect addTags before building the filtered deck.

## Step 1 — Resolve the search string

Map the request to a search:
- A document  -> `tag:Doc::<name>`
- A system    -> `tag:System::<system>`
- High-yield only for a doc -> `tag:Doc::<name> tag:Yield::High`
- An exam     -> `tag:Exam::<id>`
Always scope to the home deck if needed: `deck:MedSchool tag:...`

## Step 2 — Ensure the targeting tag exists

If targeting by `Doc::` and the tag is missing, find the note IDs for the subset and apply the tag:
curl -s localhost:8765 -X POST -d '{"action":"addTags","version":6,"params":{"notes":[<ids>],"tags":"Doc::<name>"}}'
Verify with findNotes on the new tag and confirm the count matches the intended subset.

## Step 3 — Teach the user to create the filtered deck

Give the user these exact steps (AnkiConnect cannot do this for them):
1. In Anki's main window, top menu: **Tools -> Create Filtered Deck...**
2. In the dialog:
   - **Name:** something clear, e.g. `Drill: Basic Anatomical Terminology`
   - **Search:** paste the search string from Step 1, e.g. `tag:Doc::Basic_Anatomical_Terminology`
   - **Cards selected by:** leave default (or "Random")
   - **Limit:** raise it above the card count if needed (default 100 is plenty for most single docs)
   - **Reschedule cards based on my answers:**
     - CHECK it for normal learning (reviews count toward real due dates) — recommended.
     - UNCHECK it for pure pre-exam cram that should NOT change your schedule.
3. Click **Build**. The matching cards move into the filtered deck temporarily.
4. Study it like any deck.

## Step 4 — Reusing it later

The filtered deck is reusable forever — no need to recreate:
- Click the filtered deck, then **Rebuild** to re-pull current matching cards.
- Click **Empty** to return cards to the home deck without studying.

## Notes / gotchas
- A card can only live in ONE filtered deck at a time; suspended cards are not pulled.
- Cards return to `MedSchool` automatically when the filtered deck is emptied or after study — the home deck stays the single source of truth.
- Never tell the user to manually move cards between decks; use tags + filtered decks.
