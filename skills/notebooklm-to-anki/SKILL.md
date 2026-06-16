---
name: notebooklm-to-anki
description: Use this skill when the user wants to generate Anki flashcards from any NotebookLM output — including .txt study guides, .pdf exports, .mp3 audio overviews, or pasted notes. Outputs a .apkg file ready to import into Anki under the "Claude" deck. Trigger on phrases like "make anki cards from this", "anki:", "notebooklm to anki", "generate cards from", or whenever a user provides a .txt/.pdf/.mp3 file and wants flashcards from it.
---

# NotebookLM to Anki

Read any NotebookLM output, extract high-value content, and generate a comprehensive, context-aware Anki deck as a `.apkg` file. Uses genanki locally — no API key required.

## When This Skill Applies

Activate when the user provides:
- A path to a `.txt` file (e.g., output from `medarticle-to-notebooklm` skill)
- A path to a `.pdf` (NotebookLM export, lecture notes)
- A path to a `.mp3` (NotebookLM audio overview)
- Pasted text (NotebookLM study guide copy-paste)

Trigger phrases:
- "make anki cards from: ..."
- "anki: ..."
- "notebooklm to anki: ..."
- "generate cards from: ..."

---

## Step 1: Read and Ingest the Source

Determine input type:

| Input | Action |
|-------|--------|
| `.txt` | Read tool — read entire file |
| `.pdf` | Read tool — if >10 pages, read in chunks using `pages` param |
| `.mp3` | Transcribe first (see MP3 Handling below) |
| Pasted text | Read directly from user message |

### MP3 Handling

Check if `openai-whisper` is installed:
```bash
python3 -c "import whisper" 2>&1
```
If available, transcribe:
```python
import whisper
model = whisper.load_model("base")
result = model.transcribe("/path/to/file.mp3")
text = result["text"]
```
If not available, tell the user:
> "openai-whisper is not installed. Run `pip3 install openai-whisper` to enable .mp3 support, or paste the transcript text directly."
Then stop and wait — do not proceed with an empty transcript.

---

## Step 2: Analyze Content and Determine Topic

From the ingested content, extract:
- **Topic / subject**: the primary clinical topic (e.g., "Heart Failure", "Sepsis", "Thyroid Pharmacology")
- **Medical domain**: organ system or discipline (Cardiology, Pulmonology, GI, Hematology, Neurology, Endocrinology, Nephrology, Infectious Disease, Pharmacology, Immunology, Biochemistry, etc.)
- **Source type**: research article (PICO-structured) vs. clinical review/lecture
- **Content density**: estimate total number of distinct testable facts

Tell the user in one sentence: topic detected, domain, and approximate card count target.

---

## Step 3: Generate Cards

### Card Type Selection (Context-Detected)

**Use CLOZE when content contains:**
- Mechanisms ("X leads to Y via Z")
- Physiological pathways or cascades
- Drug mechanisms of action
- Sequences or ordered steps (e.g., coagulation cascade, complement)
- Fill-in-the-blank facts where the deleted word IS the testable concept

**Use BASIC (Q&A) when content contains:**
- Definitions
- Named criteria or scoring systems (CURB-65, Wells, CHADS-VASc)
- Drug name ↔ indication / drug class pairings
- Lab values, thresholds, cutoffs
- Classic clinical presentations (symptom triad, pathognomonic findings)
- Management algorithms ("first-line treatment for X is Y")
- Complications and their mechanisms (concisely)

A single fact may produce BOTH a cloze and a basic card if it merits both (e.g., a drug mechanism could be cloze for the pathway and basic for the drug name → class mapping). This is encouraged for high-yield facts.

### Card Quality Rules

- **One fact per card.** Never combine two unrelated facts in one card.
- **Cloze**: delete 1–3 words per card. Don't delete so much that the card becomes ambiguous. Use `{{c1::word}}` for the primary deletion; use `{{c2::word}}` only if it's a second independent testable fact in the same sentence.
- **Basic Front**: phrase as a direct question. Start with "What", "Which", "How", or a completion stem ("The classic triad of X is..."). Keep under 20 words.
- **Basic Back**: concise answer. If listing items, use a short bullet list.
- **Extra field** (both types): one sentence of context — why this matters or a memory aid. Optional but always add for high-yield cards.
- **Never fabricate.** Only generate cards from facts explicitly stated in the source.

### Yield Classification

Assign each card a yield level based on content signals:
- **HighYield**: first-line treatments, classic presentations, diagnostic criteria, primary outcomes with key numbers, pathognomonic findings, board-tested mechanisms
- **MidYield**: second-line treatments, important complications, secondary outcomes, supporting mechanisms
- **LowYield**: methodology notes, statistical approaches, minor variants, background context

### Card Volume Target

| Source length | Target card count |
|---|---|
| Short (1 page / <500 words) | 15–25 cards |
| Medium (1–3 pages / 500–1500 words) | 30–50 cards |
| Long (3+ pages / >1500 words) | 50–80 cards |

Prioritize depth over breadth — it is better to generate 40 well-formed cards than 70 shallow ones.

---

## Step 4: Build the Card List as Structured Data

Before writing the Python script, internally organize all generated cards as a list. Each card must have:

```
type: "basic" or "cloze"
front: "..." (basic only)
back: "..." (basic only)
text: "..." (cloze only — must contain {{c1::...}} syntax)
extra: "..." (optional context/memory aid)
tags: ["AutoTag", "FirstAid::Section", "YieldLevel"]
```

### Tagging System (Double Tags)

Every card gets **two tag layers**:

**Layer 1 — Auto-detected topic tag:**
Organ system or discipline detected in Step 2. Use clean single-word tags:
`Cardiology`, `Pulmonology`, `GI`, `Hematology`, `Neurology`, `Endocrinology`, `Nephrology`, `InfectiousDisease`, `Pharmacology`, `Immunology`, `Biochemistry`, `Psychiatry`, `Musculoskeletal`, `Dermatology`, `Reproductive`, `Pediatrics`

If the source covers multiple systems (e.g., a sepsis article touching ID + critical care), tag with the primary domain.

**Layer 2 — First Aid standard tag:**
Map to First Aid 2nd edition section using `FirstAid::` prefix:
- `FirstAid::Cardiology`
- `FirstAid::Pulmonology`
- `FirstAid::Gastroenterology`
- `FirstAid::Hematology`
- `FirstAid::Neurology`
- `FirstAid::Endocrinology`
- `FirstAid::Nephrology`
- `FirstAid::InfectiousDisease`
- `FirstAid::Pharmacology`
- `FirstAid::Immunology`
- `FirstAid::Biochemistry`
- `FirstAid::Psychiatry`
- `FirstAid::Musculoskeletal`
- `FirstAid::Dermatology`
- `FirstAid::ReproductiveEndocrinology`
- `FirstAid::Pediatrics`
- `FirstAid::Pathology` (for general pathology principles)

**Layer 3 — Yield tag:**
`HighYield`, `MidYield`, or `LowYield`

Example final tags for a card: `["Cardiology", "FirstAid::Cardiology", "HighYield"]`

---

## Step 5: Deliver Cards — Anki-Connect or .apkg Fallback

**First, check if Anki is open.** Attempt to use the `anki` MCP tool to list deck names as a connectivity test.

- **If successful (Anki is running with AnkiConnect):** Use Path A — add cards directly. No file needed.
- **If failed (connection refused, Anki not open):** Use Path B — generate .apkg for manual import.

### Path A: Direct Import via Anki-Connect MCP (preferred)

1. Create the deck if it doesn't exist: use the `anki` MCP `createDeck` tool with name `Claude::<TopicSlug>_<TODAY>`.
2. Add all cards in batch using the `anki` MCP `addNotes` tool.
   - For Basic cards: model = `"Claude Medical Basic"`, fields: Front, Back, Extra, tags as generated
   - For Cloze cards: model = `"Claude Medical Cloze"`, fields: Text, Extra, tags as generated
3. Confirm to the user:
   - Cards added directly to Anki — no import step required
   - Deck name, total count (X basic + Y cloze), tag summary

Skip Path B entirely if Path A succeeds.

### Path B: Generate the .apkg via bundled script (fallback — Anki not running)

After generating all card data, write a JSON file and run the bundled script. The model IDs are fixed constants in the script (Anki uses them to identify note types — never change them).

**Step 1: Write card data to `/tmp/anki_input.json`:**

```json
{
  "topic_slug": "HeartFailure",
  "output_path": "~/Desktop/Claude Code/Claude_For_School/Anki/Anki_HeartFailure_YYYY-MM-DD.apkg",
  "cards": [
    {
      "type": "basic",
      "front": "Question text",
      "back": "Answer text",
      "extra": "Memory aid or context",
      "tags": ["Cardiology", "FirstAid::Cardiology", "HighYield"]
    },
    {
      "type": "cloze",
      "text": "In HFrEF, {{c1::ACE inhibitors}} reduce afterload.",
      "extra": "Memory aid",
      "tags": ["Cardiology", "FirstAid::Cardiology", "HighYield"]
    }
  ]
}
```

**Step 2: Run the bundled script:**

```bash
python3 ~/.claude/skills/notebooklm-to-anki/scripts/generate_apkg.py /tmp/anki_input.json
```

If genanki is not installed, run `pip3 install genanki` first and retry.

If the script fails:
- Cloze cards must contain at least one `{{c1::...}}` — the script will warn and skip cards missing this
- Check for unescaped quotes in card text fields

---

## Step 6: Confirm Output to User

After the script succeeds, verify the output file exists and has a non-zero size before reporting. Then report:
- Deck name (e.g., `Claude::HeartFailure_2026-03-05`)
- Total card count, broken down: X basic + Y cloze
- File path
- Tag summary: which auto-tag and First Aid section were applied
- Import instruction (always include):

> **To import:** Open Anki → File → Import → select the `.apkg` file. It will appear as a subdeck under "Claude". If the "Claude" parent deck doesn't exist yet, Anki will create it automatically.

Do NOT print all cards to chat. A brief per-section breakdown is fine (e.g., "Generated 18 HighYield, 14 MidYield, 8 LowYield cards").

---

## Handling Edge Cases

**Source is very short (<10 sentences):**
Generate what you can — don't pad with trivial cards. Note the low card count to the user.

**Source covers multiple distinct topics** (e.g., a lecture covering both HF and arrhythmias):
Create a single deck with both topics' cards. Use the broader topic as the slug (e.g., `Cardiology_Overview`). Tag cards individually by subtopic.

**Content is ambiguous or context is thin:**
Prefer skipping a card over generating a low-confidence one. If a fact needs more context to be testable, add that context to the Extra field.

**genanki not installed:**
```bash
pip3 install genanki
```
Run this and retry.
