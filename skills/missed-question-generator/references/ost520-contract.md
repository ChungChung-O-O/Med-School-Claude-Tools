# OST 520 remediation batch contract

Read this reference only for OST 520 question-bank work.

## Source of truth and inputs

- Repository: `/Users/austin_cheng/Desktop/Agent/OST520_QBank`
- Released source of truth: the `let BANK = [...]` array in `index.html`
- Derived released copy: `bank.json`
- Week 3 practice source: `week3/qbank_practice_ready.json`
- Media-gated practice: `week3/qbank_media_gated_questions.json`
- Private holdouts, when present: `week3/qbank_holdout_questions.json` (gitignored)
- Analysis export header: `OST 520 analysis export`

The analysis export intentionally omits answer keys and rationales. Resolve its IDs against the released bank. Its useful sections are `CURRENTLY WRONG`, `CORRECT BUT GUESSED`, `WEAK CONCEPTS`, `CONCEPTS YOU CONFUSE`, document performance, and question reports.

Pass the media-gated collection and any separate staged collection to the validator with a repeated `--reference FILE`. These additional collections participate in ID and duplication checks but are not valid `derivedFrom` ancestry; ancestry must resolve in the released bank.

## Candidate fields

Each staged MCQ must contain the normal bank fields plus remediation metadata:

```json
{
  "id": "MQG-W3-L029-01",
  "topic": "Biochemistry",
  "src": "B",
  "stem": "...",
  "options": ["...", "...", "...", "...", "..."],
  "answer": 2,
  "optionExplanations": [
    "Incorrect because...",
    "Incorrect because...",
    "Correct because...",
    "Incorrect because...",
    "Incorrect because..."
  ],
  "rationale": "A concise mechanism-level explanation of the correct inference.",
  "type": "mcq",
  "context": "",
  "unit": "UE2",
  "course": "OST520",
  "concepts": ["L029-O4"],
  "covers": ["O4"],
  "source": "missed-remediation",
  "sourceRef": "OST520 (029) L - Glycogen Metabolism, slide 18",
  "sourceBlock": "L029",
  "derivedFrom": ["W3-L029-03"],
  "missDescription": "Confused phosphorylase kinase with glycogen phosphorylase.",
  "variantAngle": "Infer the affected enzyme from a perturbation instead of recalling its substrate.",
  "holdout": false,
  "requiresMedia": false
}
```

`answer` is zero-based. `optionExplanations` is an array of plain, non-empty strings aligned by index with `options`. The answer index determines which explanation is shown as correct; do not put separate verdict objects in this array.

At least one of `derivedFrom` or `missDescription` is required. Every `derivedFrom` ID must resolve in the released bank. Use `missDescription` for a user-described gap that does not map cleanly to a prior question.

`sourceBlock` controls taught-date and daily-plan eligibility. A Unit 2 candidate must carry a non-empty block found in the released Unit 2 bank. When `derivedFrom` parents have source blocks, the candidate must inherit one of them. Objective tags in `covers` do not replace `sourceBlock`.

## Explanation display

The current app displays `rationale` plus a per-option explanation panel after grading and shuffles options at runtime. The app maps `optionExplanations` through the original option index, so never use A-E labels inside an explanation. Keep `rationale` focused on the governing mechanism or inference; use `optionExplanations` for the option-specific teaching.

## Integration invariants

- Append only; never regenerate or renumber existing IDs.
- Do not include `holdout: true` or a private holdout-derived presentation.
- Keep `index.html` and `bank.json` synchronized using the repository's existing ingest pattern.
- Run `node tests.js`, `node quality-audit.js`, syntax checks, and `git diff --check`.
- Large releases require Sol final review and an independent Astra gate.
