# Study Pipeline Plan
*Last updated: 2026-03-13 — pending LMS details before build*

---

## Overview

Automated pipeline: Drop lecture slides → auto-generate NotebookLM-ready `.md` files → manually upload to NotebookLM → export → auto-generate Anki cards in the right deck.

Inspired by the autoresearch concept (karpathy/autoresearch): wake up to study materials already processed.

---

## Status

- [x] Organization framework decided
- [ ] LMS details confirmed (Canvas? Blackboard? shared folder?)
- [ ] Block list finalized (update summer 2026)
- [ ] Build pipeline

---

## Folder Structure (source of truth)

```
Slides/
  OMS1/
    Foundations/
    Anatomy/
    MSK/
    Hem-Onc-ID/
    Neuro/
    Psych/
    GU/
    Endo/
    OMM/
    Patient-Care/
  OMS2/
    (update when OMS2 block list is known)
```

Drop a slide file into the correct folder → all downstream outputs (NotebookLM `.md`, Anki deck, tags) inherit the label automatically.

---

## NotebookLM Organization

- **One notebook per block** (e.g., "OMS1 - MSK", "OMS1 - Neuro")
- Manually upload the auto-generated `.md` file to the correct notebook
- Export study guide from NotebookLM, drop into `Exports/OMS1/<Block>/`

```
NotebookLM Notebooks:
  OMS1 - Foundations
  OMS1 - Anatomy
  OMS1 - MSK
  OMS1 - Hem-Onc-ID
  OMS1 - Neuro
  OMS1 - Psych
  OMS1 - GU
  OMS1 - Endo
  OMS1 - OMM
  OMS1 - Patient-Care
```

---

## Anki Organization

**Deck structure** (block level — not lecture level):
```
MSUCOM
  └── OMS1
        ├── MSK
        ├── Neuro
        ├── Hem-Onc-ID
        ├── Foundations
        ├── Anatomy
        ├── Psych
        ├── GU
        ├── Endo
        ├── OMM
        └── Patient-Care
```

**Tags** (lecture level — for lookup/filtering only):
```
OMS1::MSK::Lecture_Name
OMS1::Neuro::Lecture_Name
...
```

**Why block level:** Spaced repetition works best when cards from the same system mix together over time. Block exams and Step 1 test by system. Lecture-level subdecks would silo cards unnecessarily. Tags give lecture-level traceability without cluttering the deck structure.

---

## Full Pipeline (when built)

```
1. [AUTO]   Slides dropped into Slides/OMS1/<Block>/
                ↓
            lecture-to-notebooklm skill runs
                ↓
            Structured .md saved to NotebookLM_Ready/OMS1/<Block>/

2. [MANUAL] Upload .md to correct NotebookLM notebook ("OMS1 - <Block>")
            Export study guide from NotebookLM
            Drop export into Exports/OMS1/<Block>/

3. [AUTO]   notebooklm-to-anki skill runs on export
                ↓
            Cards created under MSUCOM::OMS1::<Block>
            Tagged OMS1::<Block>::<Lecture_Name>
```

---

## Pending Info (update when available)

- [ ] **LMS platform** — Canvas? Blackboard? Direct download link? This determines whether step 1 can be fully automated (watch folder vs. manual download).
- [ ] **Slide format** — Mostly PPTX? PDF? Mix?
- [ ] **OMS2 block list** — Update summer 2026 when curriculum details are available.
- [ ] **School email domain** — For Gmail filter integration (already pending in filter-rules.md).

---

## Notes

- NotebookLM has no public API — the upload step will always be manual.
- The automation before and after NotebookLM saves the most time (slide processing + Anki generation).
- Once LMS details are confirmed, revisit whether a nightly cron job or a manual trigger makes more sense.
