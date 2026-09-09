---
name: missed-question-generator
description: Generate source-grounded remediation questions from a question-bank analysis export, missed question IDs, or a user description of weak topics. Trigger on requests such as "generate the missed question(s)," "make new questions from what I got wrong," or "add practice for my misses."
---

# Missed Question Generator

Turn Austin's misses into fresh practice that tests the same weak concept from a different angle. The result must teach through the answer review, not merely identify the key.

## Intake and resolution

Accept any of these inputs:

- the OST 520 `Copy analysis for Claude/Codex` export;
- one or more stable question IDs;
- Austin's description or screenshot of what he missed.

For an analysis export, prioritize `CURRENTLY WRONG`, then `CORRECT BUT GUESSED`, recurrent confusion pairs, and high-signal weak concepts. Resolve every cited ID against the current bank before drafting. For a user-described miss, search the bank, source manifest, objectives, and course materials first; ask Austin only when the intended concept or course scope remains ambiguous.

Distinguish a content weakness from a defective original item. If the original rationale is thin, ambiguous, unsupported, or contradicted by its key, stage a rationale repair separately. Do not use a new remediation item to conceal a faulty original.

## Grounding

Identify the original question, its `covers` objective IDs, its concept tags, and the primary course source. Read the relevant objective and source section before writing. Use the source's terminology and level of detail. Record an auditable `sourceRef` with the document plus page, slide, section, or transcript timestamp. Do not invent a locator.

If the available source does not support the intended key and distractor distinctions, stop that item in staging. Do not fill a course-specific gap from general medical knowledge without clearly obtaining approval to treat it as supplemental.

## Drafting rules

Create a transfer variant, not a paraphrase:

- Preserve the weak concept and objective, but change at least two of presentation, reasoning direction, patient context, data representation, or closest distractor.
- Prefer application, mechanism, and discrimination over isolated recall when the source supports them.
- Make every distractor plausible for a specific misconception. Avoid nonsense, overlapping choices, hidden qualifiers, `all/none of the above`, and answer-length or formatting cues.
- Use five options for OST 520 unless preserving a faculty-authored format. The app shuffles choices, so explanations must identify options by their text or concept, never by letter.
- Add one non-empty string to `optionExplanations` for every option, aligned by original option index. The string at `answer` explains why the key is correct; every other string explains the exact fact or reasoning error that makes that option incorrect.
- Keep `rationale` as the concise overall teaching explanation. The app reveals the aligned per-option panel after grading, including after choices are shuffled, so do not duplicate all five explanations in `rationale`.
- Set `sourceBlock` to the lecture or reading block that controls when the item becomes eligible. For an OST 520 Unit 2 variant derived from an existing question, inherit that parent's `sourceBlock`; do not substitute a namespaced objective tag because the daily plan routes by block.
- Use `source: "missed-remediation"`, `holdout: false`, and `requiresMedia: false`. A media-dependent item stays outside the live bank until the required image is licensed, attached, and validated.

Read [references/ost520-contract.md](references/ost520-contract.md) before staging an OST 520 batch.

## Identity, progress, and privacy

Assign a new stable ID in the form `MQG-<source-or-objective>-<two-digit-sequence>`. Check all released, staged, media-gated, and private collections before choosing it. Never renumber, reuse, or silently replace a released ID; appending new IDs preserves browser progress and backup compatibility.

Treat first-use holdouts as private assessment material:

- Compare candidate stems, option sets, tested distinctions, and presentations against the private holdout inventory.
- Never copy, quote, summarize, log, or expose a holdout stem, key, rationale, or distinctive presentation in learner-facing artifacts.
- Run the validator with `--require-holdouts` before integration. If the private inventory is unavailable, the batch may remain staged but must not ship.

## Stage, validate, integrate

Write candidates to a staging JSON file outside the released bank. Do not modify `index.html`, `bank.json`, progress data, or a release file while drafting.

Run:

```bash
node scripts/validate_batch.js BATCH.json --bank PATH/TO/bank.json --reference PATH/TO/media_gated.json --holdouts PATH/TO/private_holdouts.json --require-holdouts
```

Repeat `--reference FILE` for any other staged or reserved public collection and require a clean pass. The script checks structure, aligned per-choice explanations, stable-ID collisions, source ancestry, exact and near duplicates, option-set reuse, and private-holdout separation. Its similarity check is only a screen; manually compare the clinical setup, inference path, and closest distractor.

Before integrating:

1. Verify each key and each option explanation against the cited source.
2. Confirm the item tests the diagnosed weakness from a genuinely new angle.
3. For a large batch, Sol owns the blueprint and final review, bounded drafting or mechanical work may go to Terra, and an independent Astra pass must approve content, duplication risk, cues, source support, holdout safety, and integration behavior.
4. Use the repository's guarded, idempotent ingest pattern. Preserve existing IDs and data, regenerate derived copies, and run the full repository tests and quality audit.
5. Simulate a public clone without private holdouts, then verify the learner-facing bank and deployed surface when publication is in scope.

Return the number generated, the weak concepts covered, source locations used, validation evidence, and the exact practice recommendation. Do not expose private holdout details or give Austin a Markdown study file to read.
