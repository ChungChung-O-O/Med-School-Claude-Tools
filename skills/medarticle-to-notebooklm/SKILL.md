---
name: medarticle-to-notebooklm
description: Use this skill when the user wants to prepare research articles, UpToDate exports, or review articles for NotebookLM upload — including PubMed articles (via PMID or URL), journal PDFs, and UpToDate pages. Outputs a clean, structured .txt file optimized for NotebookLM ingestion. Do NOT use for lecture slides or PPTX files — use lecture-to-notebooklm for those.
version: 1.0.0
---

# MedArticle to NotebookLM

Convert any medical source into a structured `.txt` file optimized for NotebookLM upload. The output is designed so NotebookLM's AI can immediately produce useful summaries and answer questions accurately.

## When This Skill Applies

Activate when the user provides any of:
- A **PubMed ID** (e.g., "PMID: 38291045")
- A **URL** to a paper, UpToDate page, or journal article
- A **local PDF path** of a research article or UpToDate export
- **Pasted text** from a research article or UpToDate page
- **Multiple sources** in one request (process each, save as separate files)

Do NOT activate for `.pptx` files or lecture slide PDFs — use `lecture-to-notebooklm` for those.

Trigger phrases include:
- "prepare for notebooklm: ..."
- "notebooklm: ..."
- "structure this for notebooklm: ..."
- "ingest this for notebooklm: ..."

---

## MCP Notes

**PubMed MCP (pubmed via https://pubmed.mcp.claude.com/mcp):**
- Uses stateful HTTP sessions that can expire. Always delegate PubMed retrieval to a subagent via the Agent tool to get a fresh session.
- Use `get_article_metadata` for abstract + metadata, then `convert_article_ids` → `get_full_text_article` if a PMCID exists.

**Pattern:** Delegate all PubMed/bioRxiv retrieval to a subagent. Handle local files and pasted text directly.

---

## Step 1: Identify Input Type and Retrieve Content

Determine what was provided:

| Input | Action |
|-------|--------|
| PMID | Subagent → PubMed MCP: `get_article_metadata`, then `get_full_text_article` if PMCID available |
| URL (paper/journal) | WebFetch to extract title, abstract, methods, results, conclusions |
| URL (UpToDate) | WebFetch — extract clinical content sections |
| Local PDF | Read tool — supports PDFs up to ~50 pages; use `pages` param for large files |
| Pasted text / transcript | Read directly from user message |

If content is paywalled or incomplete, note this clearly and proceed with what is available. Never fabricate missing content.

---

## Step 2: Detect Content Schema

Auto-detect which schema to apply unless the user specifies:

**Use PICO Schema when the source is:**
- A research article, RCT, cohort study, meta-analysis, systematic review, case-control
- Contains Methods / Results / Statistics sections
- Has a defined patient population, intervention, and measurable outcomes

**Use Clinical Schema when the source is:**
- A lecture, review article, textbook chapter, UpToDate export, or transcript
- Organized around a disease, condition, or clinical topic
- Focused on pathophysiology, presentation, and management rather than a trial

If uncertain, default to Clinical Schema with a PICO block embedded if relevant data is present.

Tell the user which schema was selected and why (one sentence).

---

## Step 3: Extract and Structure Content

### PICO Schema (Research Articles)

Extract and organize into the following structure. Keep language clear — write for a med student who wants to understand *why this matters* and *what to do with it*, not methodological minutiae.

```
SOURCE INFORMATION
==================
Title: [Full title]
Authors: [First author et al.]
Journal / Year: [Journal, Year]
DOI / PMID: [identifiers]
Source Type: [RCT / Cohort / Meta-analysis / Case-control / etc.]
Level of Evidence: [I-V]
Topic Tags: [2-4 clinical keywords for NotebookLM]


WHY THIS PAPER MATTERS
======================
[2-3 sentences. What clinical problem does this address? How does it change or confirm
what we do? Write this for a student connecting it to what they are currently learning.
Avoid vague praise — be specific about the patient impact.]


CLINICAL QUESTION
=================
[One clear sentence: "In [population], does [intervention] compared to [comparator]
improve/reduce/affect [outcome]?"]


POPULATION
==========
Who was studied: [Age, condition, setting, key inclusion/exclusion criteria]
Sample size: [N total, N per arm if applicable]
Generalizability: [Brief note — does this match real-world patients? Any major
exclusions that limit applicability?]


INTERVENTION
============
[What was done, given, or exposed. Keep it clinical — dose, duration, route if
relevant. Skip trial logistics that don't affect interpretation.]


COMPARISON
==========
[What the intervention was compared to — placebo, standard of care, active comparator,
or none. Note if open-label vs blinded.]


OUTCOMES
========
Primary outcome: [What was measured, how, over what timeframe]
Key secondary outcomes: [2-3 that are clinically meaningful — skip purely exploratory]
How outcomes were measured: [Brief — validated scale, lab value, clinical event, etc.]


KEY FINDINGS
============
Primary result: [Effect size, 95% CI, p-value. State in plain terms: "Treatment X
reduced Y by Z% (ARR: _, NNT: _, p=_)". Include both relative and absolute numbers.]

Secondary results:
- [Finding 1 with numbers]
- [Finding 2 with numbers]
- [Any important subgroup finding relevant to clinical practice]

What did NOT show significance: [Worth noting if a key outcome was null]


STUDY LIMITATIONS
=================
[3-4 bullets. Focus on things that matter for interpreting results or applying them —
not technical stats details. E.g., short follow-up, selected population, industry
funding, surrogate endpoints, open-label design.]


CLINICAL TAKEAWAY
=================
[3-5 bullets. Crisp, actionable points. What should a student/clinician remember?
How does this connect to guidelines or standard of care? What question remains open?]


KEY CONCEPTS FOR NOTEBOOKLM
============================
[5-10 key terms, mechanisms, drug names, disease processes central to this paper.
These help NotebookLM link this source to related topics.]
```

---

### Clinical Schema (Lectures, Reviews, UpToDate, Transcripts)

```
SOURCE INFORMATION
==================
Title / Lecture: [Title or topic name]
Source Type: [Lecture / UpToDate / Review Article / Textbook Chapter / Transcript]
Author / Lecturer: [If known]
Date / Version: [If known]
Topic Tags: [2-4 clinical keywords for NotebookLM]


OVERVIEW
========
[2-3 sentences. What condition or topic is this? What is the core clinical problem?
Why does a med student need to know this?]


PATHOPHYSIOLOGY
===============
[Key mechanisms — what goes wrong and why. Keep it to what is necessary to understand
the clinical picture and management rationale. Skip molecular detail unless it directly
explains a drug mechanism or symptom.]


CLINICAL PRESENTATION
=====================
Symptoms: [Common presenting symptoms]
Signs: [Physical exam findings]
Classic / High-yield features: [Board-relevant or commonly tested patterns]
Atypical presentations: [If clinically important — e.g., elderly, immunocompromised]


DIAGNOSIS
=========
Key workup: [Lab, imaging, or criteria used to diagnose]
Diagnostic criteria: [If formal criteria exist — DSM, Rome, AHA, etc.]
Must-not-miss differentials: [2-4 conditions to rule out]


MANAGEMENT
==========
First-line treatment: [Drug/intervention, dose if relevant, duration]
Second-line / alternatives: [If applicable]
When to escalate / refer: [Key decision points]
Monitoring: [What to follow up, how often, what to watch for]


COMPLICATIONS
=============
[2-5 key complications — include timeframe and mechanism briefly if helpful]


KEY CONCEPTS FOR NOTEBOOKLM
============================
[5-10 key terms, drug classes, mechanisms, eponyms, or diseases central to this topic.
These help NotebookLM link this source to related topics in other notebooks.]
```

---

## Step 4: Generate the Output File

Save as a `.txt` file to:
```
/Users/austin_cheng/Desktop/Medical School/Claude/NotebookLM/
```

Filename format:
- Research article: `NLM_PICO_<FirstAuthorLastName>_<Year>_<YYYY-MM-DD>.txt`
- Clinical content: `NLM_Clinical_<TopicSlug>_<YYYY-MM-DD>.txt`

`<TopicSlug>` = 2-3 word topic in snake_case (e.g., `heart_failure`, `septic_shock`).

Write the file using the Write tool. After saving, confirm to the user:
- File path
- Schema used (PICO or Clinical) and why
- 2-3 sentence summary of what was captured
- Any gaps (e.g., full text unavailable, transcript was partial)

Do NOT reproduce the full structured output in chat. A brief confirmation is sufficient.

---

## Step 5: NotebookLM Upload Instruction

After confirming the file, always append this note to the user:

> **To upload:** Open NotebookLM → your notebook → Sources → Upload → select the `.txt` file from `Medical School/Claude/NotebookLM/`.

---

## Quality Rules

- **Write for a med student, not a reviewer.** The goal is efficient learning, not publication-grade appraisal. Include numbers because they matter clinically; skip methodological rabbit holes.
- **Never fabricate.** If full text is unavailable, note it. Do not invent statistics, author names, or clinical details.
- **Be specific with numbers** in the PICO schema — abstract effect sizes (ARR, NNT) are more useful than vague descriptions.
- **Keep Clinical Schema sections tight.** A student pasting a 60-minute lecture transcript should get a structured 1-2 page reference, not a 10-page dump.
- **Topic Tags and Key Concepts are essential.** NotebookLM uses these to cross-reference sources. Always include them.
- **For large PDFs** (>10 pages), read in chunks using the `pages` parameter and synthesize — do not try to read all at once.
