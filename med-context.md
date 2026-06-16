# med-context.md — Personal Medical Study Tagging Schema
> **Version:** 1.0 | **Last updated:** 2026-03-05
> Every script in this pipeline MUST import and apply this schema for consistent tagging. NotebookLM cross-notebook reasoning depends on uniform metadata.

---

## 1. Required Metadata Block

Every output file (summary, question set, briefing, etc.) must include a YAML front-matter block at the top:

```yaml
---
organ_system: <value>          # see §2
yield: <value>                 # see §3
source_type: <value>           # see §4
source_ref: "<string>"         # e.g. "First Aid 2025 p.342", "Amboss: Renal"
date_created: YYYY-MM-DD
date_reviewed: YYYY-MM-DD      # update on each active recall session
tags: [<tag1>, <tag2>, ...]    # free-form supplemental tags (see §5)
---
```

---

## 2. Organ System Tags

Use exactly one value from this controlled list:

| Tag | Scope |
|-----|-------|
| `cardiology` | Heart, great vessels, arrhythmias |
| `pulmonology` | Lungs, airways, pleura |
| `gastroenterology` | GI tract, liver, pancreas, biliary |
| `nephrology` | Kidneys, fluid/electrolytes, acid-base |
| `neurology` | CNS, PNS, neuromuscular junction |
| `psychiatry` | DSM disorders, psychopharmacology |
| `endocrinology` | Hormones, metabolism, thyroid, adrenal, pituitary |
| `hematology` | Blood cells, coagulation, transfusion |
| `oncology` | Malignancies, chemotherapy, tumor biology |
| `immunology` | Immune system, hypersensitivity, autoimmune |
| `infectious-disease` | Bacteria, viruses, fungi, parasites |
| `musculoskeletal` | Bone, joints, connective tissue |
| `dermatology` | Skin, hair, nails |
| `reproductive` | OB/GYN, male reproductive, fertility |
| `pediatrics` | Age-specific conditions, development |
| `ophthalmology` | Eye and vision |
| `otolaryngology` | Ear, nose, throat |
| `urology` | Bladder, prostate, urinary tract (non-renal) |
| `surgery` | Surgical principles, trauma, perioperative |
| `pharmacology` | Drug mechanisms, side effects (cross-cutting) |
| `pathology` | General pathologic mechanisms (cross-cutting) |
| `biochemistry` | Metabolism, genetics, molecular (cross-cutting) |
| `biostatistics` | Epidemiology, study design, stats |
| `ethics-law` | Medical ethics, legal principles |

---

## 3. Yield Level Tags

Use exactly one value. Calibrated to USMLE Step 1/2 CK high-yield frameworks:

| Tag | Meaning |
|-----|---------|
| `yield-high` | Heavily tested; core pathophysiology, classic presentations, first-line tx |
| `yield-medium` | Regularly tested; important but not always primary focus |
| `yield-low` | Rarely tested; zebras, obscure details, completeness only |
| `yield-review` | Previously missed; needs active recall prioritization |

---

## 4. Source Type Tags

Use exactly one value:

| Tag | Source |
|-----|--------|
| `first-aid` | First Aid for the USMLE |
| `amboss` | AMBOSS platform (qbank or library) |
| `uworld` | UWorld qbank |
| `sketchy` | Sketchy Medical (micro, pharm, path) |
| `pathoma` | Pathoma |
| `anki` | Anki deck (specify deck in `source_ref`) |
| `lecturio` | Lecturio |
| `uptodate` | UpToDate |
| `lecture` | Course lecture or recorded session |
| `textbook` | Formal textbook (specify in `source_ref`) |
| `paper` | Primary literature / research paper |
| `ai-generated` | AI-synthesized content (this pipeline) |

---

## 5. Supplemental Tags (Free-form)

Use `tags: []` for additional cross-cutting concepts. Recommended patterns:

- **Mechanism:** `mechanism-genetic`, `mechanism-autoimmune`, `mechanism-infectious`
- **Presentation type:** `classic-presentation`, `atypical-presentation`
- **Study format:** `question-set`, `summary`, `briefing`, `mnemonic`, `table`
- **Exam relevance:** `step1`, `step2ck`, `shelf-internal`, `shelf-surgery`, etc.
- **Clinical context:** `emergency`, `inpatient`, `outpatient`, `pediatric-variant`
- **Difficulty:** `tricky`, `commonly-confused`, `high-miss-rate`

---

## 6. Script Compliance Requirements

Every script in this pipeline must:

1. **Import this schema** by reading `med-context.md` or referencing it in its prompt/config.
2. **Prompt for or infer** all required fields (`organ_system`, `yield`, `source_type`, `source_ref`, `date_created`) before writing output.
3. **Validate** that `organ_system` and `source_type` values match the controlled lists in §2 and §4 exactly (case-sensitive, hyphenated).
4. **Append** `date_reviewed` whenever an existing file is updated.
5. **Never omit** the YAML front-matter block, even for short outputs.

---

## 7. Example Compliant Output Header

```yaml
---
organ_system: nephrology
yield: yield-high
source_type: amboss
source_ref: "AMBOSS: Acute Kidney Injury"
date_created: 2026-03-05
date_reviewed: 2026-03-05
tags: [step2ck, classic-presentation, mechanism-ischemic, tricky]
---
```

---

## 8. Skills Maintenance Protocol

Whenever a new skill is added or an existing skill is meaningfully changed:

1. **Update `Skills_Reference.txt`** at `~/Desktop/Claude Code/Claude/Skills_Reference.txt`:
   - Add the skill to the SKILL OVERVIEW numbered list
   - Add a full documentation section following the existing format
   - Update the INSTALLED DEPENDENCIES table if new packages were added
   - Update the workflow diagram in `notebooklm-to-anki` if the pipeline changes
   - Update the "Last updated" line at the top

2. **Update the skill description** in `~/.claude/skills/<skill-name>/SKILL.md` if scope changes affect triggering.

3. **Install any new dependencies immediately** via `pip3 install <package>` and mark them as INSTALLED in `Skills_Reference.txt`.

4. **Back up to GitHub** by running `sync.sh`:
   ```bash
   cd ~/Desktop/Medical\ School/Claude && ./sync.sh
   ```
   This copies all skills from `~/.claude/skills/`, commits with a timestamp, and pushes to the private repo at `github.com/ChungChung-O-O/med-school-claude-config`. Run this as the final step after every skill addition or change.

---

## 9. NotebookLM Integration Notes

- Keep `organ_system` values consistent — NotebookLM uses these as implicit cluster anchors across notebooks.
- `yield-review` is your active signal: filter on this tag when building review sessions.
- `source_ref` should be granular enough (page number, AMBOSS article title) to trace back to the original source.
- When uploading to NotebookLM, filename convention: `YYYY-MM-DD_<organ_system>_<topic-slug>.<ext>` (e.g. `2026-03-05_nephrology_aki-summary.md`).
