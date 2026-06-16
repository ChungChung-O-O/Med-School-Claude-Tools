---
name: lecture-to-notebooklm
description: Use this skill when the user wants to process lecture slides (PPTX, PDF, or Word .docx) into a structured NotebookLM-ready document. Applies either a Step 1 schema (Physiology → Pathology → Pharmacology → Clinical Correlation) or Step 2 schema (Presentation → Workup → Management → Complications) with bolded high-yield terms. Outputs a .md file optimized for NotebookLM upload. Trigger when the user provides a slide file (pptx, pdf, docx) and wants it structured for NotebookLM, or says "lecture:", "slides:", "process lecture:", "prep slides:", or "lecture to notebooklm".
---

# Lecture to NotebookLM

Convert lecture slides (PPTX or PDF) into a structured `.md` file with bolded high-yield terms, ready for NotebookLM upload. Every lecture enters NotebookLM in the same schema so cross-notebook queries work reliably.

## When This Skill Applies

Activate when the user provides any of:
- A **`.pptx` file path**
- A **`.docx` Word file path**
- A **PDF of lecture slides**
- **Pasted lecture transcript or notes**

Trigger phrases include:
- `lecture: /path/to/slides.pptx`
- `lecture: /path/to/notes.docx`
- `slides: ...`
- `process lecture: ...`
- `prep slides: ...`

Do NOT activate for research articles, UpToDate exports, or review articles — use `medarticle-to-notebooklm` for those.

---

## Step 1: Extract Content from Source

### PPTX Files

Run the following to extract text slide-by-slide:

```bash
python3 -c "
from pptx import Presentation
prs = Presentation('/path/to/file.pptx')
for i, slide in enumerate(prs.slides, 1):
    print(f'--- SLIDE {i} ---')
    for shape in slide.shapes:
        if hasattr(shape, 'text') and shape.text.strip():
            print(shape.text.strip())
    print()
"
```

If `python-pptx` is not installed, run first:
```bash
pip3 install python-pptx
```

Capture the full output. Note the slide count. If the PPTX path contains spaces, wrap it in quotes.

### Word (.docx) Files

Run the following to extract text:

```bash
python3 -c "
from docx import Document
doc = Document('/path/to/file.docx')
for i, para in enumerate(doc.paragraphs):
    if para.text.strip():
        print(para.text.strip())
for table in doc.tables:
    for row in table.rows:
        for cell in row.cells:
            if cell.text.strip():
                print(cell.text.strip())
"
```

If `python-docx` is not installed, run first:
```bash
pip3 install python-docx
```

### PDF Lecture Slides

Use the Read tool directly. For files >10 pages, read in chunks using the `pages` parameter and synthesize across all chunks before writing output.

### Pasted Text / Transcript

Read directly from the user message.

---

## Step 2: Determine Schema (Step 1 vs Step 2)

Auto-detect based on the lecture topic or course name:

**Use Step 1 Schema when:**
- Course or topic is basic science: physiology, pathophysiology, biochemistry, pharmacology, immunology, microbiology, anatomy, embryology, histology, genetics, neuroscience
- The lecture covers mechanisms, molecular pathways, or drug classes in the absence of a specific patient workup context
- Keywords: "mechanism", "pathway", "receptor", "enzyme", "gene", "synthesis", "regulation"

**Use Step 2 Schema when:**
- Topic is a named disease, syndrome, or clinical condition taught in a clinical context
- The lecture is organized around diagnosis and management of a patient problem
- Course context is internal medicine, surgery, OB/GYN, pediatrics, psychiatry, or a clinical clerkship
- Keywords: "presentation", "workup", "treatment", "management", "prognosis", "criteria"

**When ambiguous** (e.g., "Hypertension" could be either):
- Before proceeding, state your best guess in one line and ask: "This looks like a **Step 1 Basic Science** lecture. Correct, or should I use the Step 2 Clinical schema?"
- Wait for confirmation before continuing.

For clear cases, proceed without asking — just note which schema you applied and why in one sentence at the end.

---

## Step 3: Apply Schema and Write Output

Bold all high-yield terms, drug names, mechanisms, eponyms, lab values, and testable facts using `**bold**` throughout. Do not bold every other word — bold only genuinely high-yield items a student should flag.

---

### Step 1 Schema (Basic Science / Preclinical)

```
# [Lecture Title]

**Source:** [Filename or course name]
**Schema:** Step 1 — Basic Science
**Topic Tags:** [2-4 keywords for NotebookLM]
**Date Processed:** [YYYY-MM-DD]

---

## Overview
[2-3 sentences. What system, process, or drug class is this lecture about? What is the core concept a student must walk away understanding?]

---

## Normal Physiology
[Baseline — what does this system or process do under normal conditions? Include key regulatory mechanisms. This is the foundation for understanding what breaks.]

---

## Pathophysiology
[What goes wrong and why? Walk through the mechanism of disease step by step. Connect clearly to the normal physiology above. Bold the name of the disease process, key mediators, and the downstream consequences.]

---

## Pharmacology
[Drugs relevant to this topic. For each drug or drug class:]

### [Drug / Drug Class]
- **Mechanism:** [MOA — be specific, e.g., receptor type, enzyme target]
- **Indication:** [When it is used]
- **Key side effects:** [Clinically important — especially board-tested]
- **Contraindications:** [If notable]
- **Mnemonic / high-yield note:** [If one exists or is useful]

[Repeat block for additional drugs. Omit section entirely if lecture has no pharmacology content.]

---

## Clinical Correlation
[How does this basic science connect to the clinical picture? What symptoms or signs result directly from the pathophysiology? What does the student need to recognize on an exam or at the bedside? Keep this brief — full clinical management belongs in Step 2 schema.]

---

## High-Yield Points
- **[Term or concept]:** [One-line explanation]
- **[Term or concept]:** [One-line explanation]
- [Continue for all testable facts from the lecture — typically 8-15 bullets]

---

## Key Concepts for NotebookLM
[List 5-10 terms, drug names, diseases, mechanisms, or eponyms central to this lecture. These help NotebookLM cross-reference this source with related notebooks.]
```

---

### Step 2 Schema (Clinical / Clerkship)

```
# [Lecture Title]

**Source:** [Filename or course name]
**Schema:** Step 2 — Clinical
**Topic Tags:** [2-4 keywords for NotebookLM]
**Date Processed:** [YYYY-MM-DD]

---

## Overview
[2-3 sentences. What condition is this? Who gets it and why does it matter clinically?]

---

## Pathophysiology
[Brief mechanism — what breaks and why. Include only what is necessary to understand the clinical presentation and management rationale. Skip deep molecular detail unless it directly explains a drug target or symptom.]

---

## Clinical Presentation
**Symptoms:** [Common presenting symptoms]
**Signs:** [Physical exam findings]
**Classic / high-yield features:** [Board-tested patterns — e.g., "**triad of**...", "**pathognomonic** finding is..."]
**Atypical presentations:** [Elderly, immunocompromised, pediatric if clinically important]

---

## Workup / Diagnosis
**Key tests:** [Labs, imaging, biopsy — what to order and what you are looking for]
**Diagnostic criteria:** [If formal criteria exist — DSM, Rome, AHA/ACC, Ranson, etc. Bold the criteria names]
**Must-not-miss differentials:** [2-4 conditions to rule out early]

---

## Management
**First-line:** [Drug/intervention, dose if relevant, duration]
**Second-line / alternatives:** [If applicable]
**When to escalate / refer:** [Key decision thresholds — e.g., ICU transfer, surgery consult]
**Monitoring:** [What to follow, how often, what to watch for]

---

## Complications & Prognosis
- **[Complication]:** [Brief mechanism or timeframe if relevant]
- [Continue for 2-5 key complications]

---

## High-Yield Points
- **[Term or concept]:** [One-line explanation]
- **[Term or concept]:** [One-line explanation]
- [Continue for all testable facts — typically 8-15 bullets]

---

## Key Concepts for NotebookLM
[List 5-10 terms, drug names, diseases, criteria, or eponyms central to this lecture. These help NotebookLM cross-reference this source with related notebooks.]
```

---

## Step 4: Save the Output File

Save to:
```
/Users/austin_cheng/Desktop/Claude Code/Claude/NotebookLM/
```

Filename format:
- Step 1 lecture: `NLM_Lec_Step1_<TopicSlug>_<YYYY-MM-DD>.md`
- Step 2 lecture: `NLM_Lec_Step2_<TopicSlug>_<YYYY-MM-DD>.md`

`<TopicSlug>` = 2-3 word topic in snake_case (e.g., `cardiac_physiology`, `heart_failure`, `beta_blockers`).

Write the file using the Write tool. After saving, read back the first 5 lines to confirm the file was written correctly (non-empty, correct schema header). Then confirm to the user:
- File path and size (word count or approximate)
- Schema used and why (one sentence)
- Slide count processed (if PPTX)
- Any gaps (slides with no extractable text, images-only slides, etc.)

Do not reproduce the full structured output in chat. A brief confirmation is sufficient.

---

## Step 5: NotebookLM Upload Instruction

After confirming the file, always append:

> **To upload:** Open NotebookLM → your notebook → Sources → Upload → select the `.md` file from `Medical School/Claude/NotebookLM/`.

---

## Quality Rules

- **Bold purposefully.** Only bold terms a student genuinely needs to memorize or recognize on an exam. Over-bolding degrades usefulness.
- **Never fabricate.** If a slide has no text (image-only), note it. Do not invent content from what the image might contain.
- **Keep it tight.** A 50-slide lecture should produce a structured 2-3 page reference, not a 15-page transcript dump. Synthesize, don't transcribe.
- **Pharmacology gets its own block.** Even if drug content is sparse, always pull it out of the general flow into the Pharmacology section for Step 1, or into Management for Step 2.
- **Topic Tags and Key Concepts are essential.** NotebookLM uses these to cross-reference sources across notebooks.
- **Image-heavy slides:** If a PPTX slide has no text but the title suggests important content (e.g., "Mechanism of Action Diagram"), note it as: `[Slide N: image-only — [slide title]. Review slide manually.]`
