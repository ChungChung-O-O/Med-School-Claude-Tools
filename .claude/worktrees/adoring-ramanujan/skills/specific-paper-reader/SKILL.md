---
name: specific-paper-reader
description: Use this skill when the user provides a specific paper to analyze — via PubMed ID (e.g., "PMID: 12345678"), a URL to a paper, or by uploading/pasting the paper text. Generates a clinical expert summary as a PDF with related reading recommendations.
version: 1.0.0
---

# Specific Paper Reader

Analyze a user-specified paper and produce a clinical expert summary written from a healthcare professional's perspective. The summary is structured for a clinician preparing to critically appraise or present the work, and is delivered as a formatted PDF with curated related reading recommendations.

## When This Skill Applies

Activate when the user provides one of:
- A **PubMed ID** (e.g., "PMID: 38291045", "PubMed ID 38291045", "pmid:38291045")
- A **URL** to a paper or journal article
- An **uploaded PDF** or **pasted paper text**

## Known MCP Limitations

**PubMed MCP (pubmed via https://pubmed.mcp.claude.com/mcp):**
- Uses stateful HTTP sessions that expire mid-conversation. Delegate the full retrieval and related-article search to a subagent (Agent tool) — this initializes a fresh session and reliably avoids expiry errors.

**bioRxiv MCP (biorxiv via https://mcp.deepsense.ai/biorxiv/mcp):**
- May return HTTP 301 redirects. If this occurs, fall back to PubMed's cross-indexing of bioRxiv papers.

**Recommended pattern:** Always delegate literature retrieval and related-article search to a subagent via the Agent tool.

---

## Workflow

### Step 1: Identify and Retrieve the Paper

Determine the input type:

- **PMID** → Launch a subagent to fetch full metadata and abstract via PubMed MCP (`get_article_metadata`). Also attempt `convert_article_ids` to get the PMCID, then `get_full_text_article` if available.
- **URL** → Use WebFetch to retrieve and extract the paper content (title, authors, abstract, methods, results, conclusions). If the URL is paywalled, extract what is available and note the limitation.
- **Uploaded/pasted text** → Read the content directly from the file or user message.

If metadata is incomplete (e.g., no abstract via PMID), note this and proceed with what is available. Never fabricate missing content.

### Step 2: Extract Core Paper Details

From retrieved content, identify:
- Full title
- All authors (first, ..., last)
- Journal, year, DOI, PMID
- Study design (RCT, cohort, meta-analysis, case series, etc.)
- Population / clinical setting
- Intervention / exposure
- Comparator / control (if applicable)
- Primary and secondary outcomes
- Key quantitative results (effect sizes, p-values, CIs, NNT/NNH where applicable)
- Funding source and conflicts of interest (COI)

### Step 3: Clinical Framing

Before composing the summary, assess the paper from a clinical lens:

- **Level of evidence**: Classify using standard hierarchy (Level I: systematic review/RCT → Level V: expert opinion)
- **Clinical applicability**: Is the study population generalizable to typical patients? Note any inclusion/exclusion criteria that limit applicability.
- **Practice implications**: Does this paper support, challenge, or refine current guidelines or standard of care?
- **Patient relevance**: Does the effect size translate to meaningful patient benefit or harm?

State this framing to the user in two to three sentences before generating the PDF.

### Step 4: Find Related Articles via Subagent

Launch a subagent to retrieve related articles. Instructions for the subagent:

- If a PMID is available, use `find_related_articles` (link_type: `pubmed_pubmed`) to get similar articles
- Also run a targeted PubMed search using the paper's key clinical terms to find 2–3 landmark or highly cited papers in the same space
- For each candidate: retrieve title, authors, journal, year, DOI, citation count, and a one-sentence clinical relevance note
- Target 3–5 related articles total, prioritizing:
  1. Systematic reviews or meta-analyses on the same clinical question
  2. RCTs that agree or conflict with the indexed paper
  3. Clinical practice guidelines citing similar evidence
  4. High-impact papers (citations ≥ 50 or IF > 10) in the same specialty area

### Step 5: Compose the Clinical Expert Summary

Draft the structured summary using the Clinical Summary Structure below. Target **800–1,000 words in the body**. Write for a clinician — use precise medical terminology, cite quantitative results, and critically evaluate the evidence rather than just describing it.

### Step 6: Generate PDF Output

After composing the summary, generate a PDF using Python and fpdf2. Save to the Desktop as:

```
~/Desktop/PaperReview_<FirstAuthorLastName>_<Year>_<YYYY-MM-DD>.pdf
```

Use the following Python template, filling in all content:

```python
from fpdf import FPDF
from datetime import date
import os

class PaperPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(120, 120, 120)
        self.cell(0, 8, "Specific Paper Reader  |  Clinical Expert Summary", align="R")
        self.ln(4)
        self.set_draw_color(180, 180, 180)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}  —  Generated {date.today()}  |  For clinical education purposes only", align="C")

pdf = PaperPDF()
pdf.set_margins(18, 18, 18)
pdf.set_auto_page_break(auto=True, margin=20)
pdf.add_page()

# ── Study type / level of evidence banner ─────────────────────────────────────
pdf.set_fill_color(230, 245, 235)
pdf.set_draw_color(150, 200, 170)
pdf.rect(18, pdf.get_y(), 174, 12, style="FD")
pdf.set_font("Helvetica", "B", 10)
pdf.set_text_color(30, 100, 60)
pdf.set_xy(20, pdf.get_y() + 2)
pdf.cell(0, 8, "Study Design: <STUDY DESIGN>  ·  Level of Evidence: <LEVEL>  ·  Specialty: <SPECIALTY>")
pdf.ln(16)

# ── Clinical framing line ─────────────────────────────────────────────────────
pdf.set_font("Helvetica", "I", 10)
pdf.set_text_color(60, 60, 60)
pdf.multi_cell(0, 6, "<CLINICAL FRAMING — 2-3 sentences on practice relevance>")
pdf.ln(6)

# ── Paper title ───────────────────────────────────────────────────────────────
pdf.set_font("Helvetica", "B", 13)
pdf.set_text_color(20, 20, 20)
pdf.multi_cell(0, 7, "<FULL PAPER TITLE>")
pdf.ln(3)

# ── Authors / Journal / DOI ───────────────────────────────────────────────────
pdf.set_font("Helvetica", "", 9)
pdf.set_text_color(80, 80, 80)
pdf.multi_cell(0, 5, "Authors: <First Author>, ..., <Last Author>")
pdf.multi_cell(0, 5, "Journal: <JOURNAL>  |  Year: <YEAR>  |  DOI: <DOI>  |  PMID: <PMID>")
pdf.multi_cell(0, 5, "Impact: <CITATIONS> citations  |  IF: <IF>  |  Funding: <FUNDING SOURCE>")
pdf.ln(6)

# Horizontal rule
pdf.set_draw_color(200, 200, 200)
pdf.line(18, pdf.get_y(), 192, pdf.get_y())
pdf.ln(6)

W = 174  # usable body width (A4 210mm - 18mm left margin - 18mm right margin)

def section(pdf, title, body):
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(20, 80, 50)
    pdf.set_x(18)
    pdf.cell(W, 7, title)
    pdf.ln(5)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(30, 30, 30)
    pdf.set_x(18)
    pdf.multi_cell(W, 6, body)
    pdf.ln(5)

def bullets(pdf, title, items):
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(20, 80, 50)
    pdf.set_x(18)
    pdf.cell(W, 7, title)
    pdf.ln(5)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(30, 30, 30)
    for item in items:
        pdf.set_x(22)
        pdf.multi_cell(170, 6, f"-  {item}")
        pdf.ln(1)
    pdf.ln(4)

def related_articles(pdf, articles):
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(20, 80, 50)
    pdf.set_x(18)
    pdf.cell(W, 7, "Related Reading")
    pdf.ln(5)
    for i, art in enumerate(articles, 1):
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(30, 30, 30)
        pdf.set_x(18)
        pdf.multi_cell(W, 6, f"{i}. {art['title']}")
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(80, 80, 80)
        pdf.set_x(18)
        pdf.multi_cell(W, 5, f"   {art['citation']}  |  DOI: {art['doi']}")
        pdf.set_font("Helvetica", "I", 9)
        pdf.set_text_color(60, 100, 80)
        pdf.set_x(18)
        pdf.multi_cell(W, 5, f"   Why read this: {art['relevance']}")
        pdf.ln(3)
    pdf.ln(2)

section(pdf, "Clinical Relevance", "<CLINICAL RELEVANCE BODY — why a clinician should care, practice impact>")
section(pdf, "Background & Clinical Context", "<BACKGROUND BODY — clinical question, current standard of care, evidence gap>")
section(pdf, "Study Design & Methods", "<METHODS BODY — design, population, intervention, comparator, outcomes, statistical approach>")
section(pdf, "Key Findings", "<FINDINGS BODY — primary/secondary outcomes with effect sizes, CIs, p-values, NNT/NNH>")
section(pdf, "Critical Appraisal", "<APPRAISAL BODY — strengths, limitations, risk of bias, generalizability, COI>")
section(pdf, "Conclusions & Practice Implications", "<CONCLUSIONS BODY — what to take to the clinic, guideline alignment, caution flags>")
bullets(pdf, "Clinical Talking Points", [
    "<TALKING POINT 1 — e.g., primary outcome result in plain clinical terms>",
    "<TALKING POINT 2 — e.g., patient population applicability>",
    "<TALKING POINT 3 — e.g., key limitation to mention when sharing>",
    "<TALKING POINT 4 — e.g., how this changes or confirms practice>",
    "<TALKING POINT 5 — e.g., next question the field needs to answer>",
])

related_articles(pdf, [
    {
        "title": "<RELATED PAPER 1 TITLE>",
        "citation": "<Authors>. <Journal>. <Year>",
        "doi": "<DOI>",
        "relevance": "<One sentence: why a clinician reading the index paper should also read this>"
    },
    {
        "title": "<RELATED PAPER 2 TITLE>",
        "citation": "<Authors>. <Journal>. <Year>",
        "doi": "<DOI>",
        "relevance": "<One sentence>"
    },
    {
        "title": "<RELATED PAPER 3 TITLE>",
        "citation": "<Authors>. <Journal>. <Year>",
        "doi": "<DOI>",
        "relevance": "<One sentence>"
    },
])

# ── Footer note ────────────────────────────────────────────────────────────────
pdf.set_draw_color(200, 200, 200)
pdf.line(18, pdf.get_y(), 192, pdf.get_y())
pdf.ln(4)
pdf.set_font("Helvetica", "I", 8)
pdf.set_text_color(130, 130, 130)
pdf.multi_cell(0, 5, "Sources: PMID <PMID> (PubMed) | Full text: <PMC or DOI>\nThis summary is generated for educational purposes and does not constitute clinical advice.")

outpath = os.path.expanduser("~/Desktop/PaperReview_<FirstAuthorLastName>_<Year>_<DATE>.pdf")
pdf.output(outpath)
print(f"PDF saved: {outpath}")
```

Run this script via Bash. After it succeeds, confirm the file path to the user. Do not reproduce the full summary as chat text — a one-paragraph teaser plus the file path is sufficient.

### Step 7: Save to Zotero (Opt-In)

After confirming the PDF, ask the user:

> "Save this paper to your Zotero library? [y/N]"

If yes:

1. Read credentials from `~/Desktop/Medical School/Claude/config/zotero_config.json`. If the file has placeholder values (`YOUR_NUMERIC_USER_ID` / `YOUR_API_KEY`), tell the user to fill in their Zotero User ID and API key at that path and stop.

2. POST the paper to Zotero using Python with metadata already extracted during this skill run:

```python
import json, requests, os

config_path = os.path.expanduser("~/Desktop/Medical School/Claude/config/zotero_config.json")
config = json.load(open(config_path))

# Build creators list from authors extracted earlier
# Use {"creatorType": "author", "name": "LastName, FirstName"} format
creators = [
    {"creatorType": "author", "name": "<AUTHOR NAME>"},
    # repeat for each author
]

item = [{
    "itemType": "journalArticle",
    "title": "<FULL PAPER TITLE>",
    "creators": creators,
    "publicationTitle": "<JOURNAL>",
    "date": "<YEAR>",
    "DOI": "<DOI>",
    "extra": "PMID: <PMID>"
}]

r = requests.post(
    f"https://api.zotero.org/users/{config['user_id']}/items",
    headers={"Zotero-API-Key": config["api_key"], "Content-Type": "application/json"},
    json=item
)
if r.status_code in (200, 201):
    print("Saved to Zotero.")
else:
    print(f"Zotero error {r.status_code}: {r.text}")
```

3. Confirm "Saved to Zotero library." or report the error.

If the user says no, skip silently.

---

## Clinical Summary Structure

### Study Design & Level of Evidence Banner
- Study type (RCT, cohort, cross-sectional, meta-analysis, case-control, case series, etc.)
- Level of evidence (I–V using standard hierarchy)
- Medical specialty / clinical domain

### Clinical Framing (2–3 sentences)
*"This [study design] examines [clinical question] in [patient population]. The findings [support / challenge / refine] current [guideline or standard of care]. Clinicians in [specialty] should consider this evidence when [specific clinical scenario]."*

### Paper Header
- Title (full)
- Authors: First author, ..., last author
- Journal — Year — DOI — PMID
- Impact signal: citation count and/or journal IF
- Funding source and COI disclosure (mark as not reported if absent)

### Clinical Relevance (2–3 sentences)
Why does this paper matter to a practitioner today? Be specific about the clinical problem it addresses. Avoid vague praise — anchor to patient outcomes or workflow.

### Background & Clinical Context (3–5 sentences)
The clinical question being addressed, what current guidelines or practice patterns say, and what evidence gap this paper fills. Skip general pathophysiology unless directly relevant to interpreting results.

### Study Design & Methods (3–5 sentences)
Study design, patient population (include key eligibility criteria), intervention or exposure, comparator, primary and secondary outcomes, follow-up duration, and statistical approach. Highlight any methodological strengths (e.g., blinding, allocation concealment, pre-registration).

### Key Findings (4–6 sentences or bullet list)
Primary and secondary outcomes with full quantitative detail: effect sizes, 95% confidence intervals, p-values, absolute risk differences, NNT or NNH where applicable. Do not omit numbers. Note any subgroup findings relevant to clinical practice.

### Critical Appraisal (3–5 sentences)
Strengths and limitations of the study. Assess internal validity (risk of bias) and external validity (generalizability to typical patient populations). Flag funding sources or COI that could introduce bias. Note if results have been independently replicated.

### Conclusions & Practice Implications (3–5 sentences)
What the authors conclude and what clinicians should take away. Note alignment or tension with existing guidelines (cite specific guidelines if known). Flag any result that should not change practice until replicated or guideline-endorsed.

### Clinical Talking Points (3–5 bullets)
Crisp, memorable clinical claims — the "so what" for a morning report, grand rounds, or journal club. Each should be actionable or provoke meaningful clinical discussion.

### Related Reading (3–5 papers)
For each related paper:
- Full title
- Citation (Authors. Journal. Year.)
- DOI
- **Why read this** (one sentence from a clinical perspective — e.g., "This meta-analysis provides Level I evidence supporting the same intervention in a broader population.")

---

## Clinical Framing Principles

Write throughout with a healthcare professional's critical eye:

- **Quantify benefit in clinical terms**: Prefer absolute risk reduction and NNT over relative risk alone.
- **Identify the patient in the trial**: Call out restrictive eligibility criteria that reduce generalizability.
- **Flag statistical vs. clinical significance**: A statistically significant result with a trivial effect size is not practice-changing.
- **Surface conflicts of interest**: Industry-funded trials with positive results warrant explicit mention.
- **Anchor to guidelines**: Reference relevant society guidelines (AHA, ACC, IDSA, ACOG, etc.) where known.
- **Never fabricate**: Do not invent citation counts, impact factors, DOIs, or clinical data not present in the retrieved paper.

---

## Output Rules

- The primary deliverable is the PDF on the Desktop.
- In chat: paper identified (title + PMID/DOI), two-sentence clinical teaser, Desktop file path, and a one-line note on each related article.
- If the paper cannot be retrieved (paywalled, invalid ID, inaccessible URL), report clearly what was attempted and what partial information is available.
- If no related articles are found meeting quality thresholds, report this and describe search terms used.
- Do not exceed 1,000 words in the PDF body (excluding header and related reading section).
- Do not use hedging language ("it seems", "appears to") unless the paper itself expresses uncertainty.
