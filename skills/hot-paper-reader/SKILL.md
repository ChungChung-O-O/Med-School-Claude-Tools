---
name: hot-paper-reader
description: This skill should be used when the user says "Topic for today: <keyword1>, <keyword2>, and <keyword3>", asks to "find a hot paper on [topics]", wants to "summarize a recent paper about [topics]", or provides three research keywords to search scientific literature.
version: 1.1.0
---

# Hot Paper Reader

Find and summarize the single most relevant, high-impact recent paper at the intersection of three user-provided research keywords. The summary is written for a domain expert preparing to give a short presentation on the work, and delivered as a formatted PDF file.

## When This Skill Applies

Activate when the user provides three research keywords using the pattern "Topic for today: <A>, <B>, and <C>", or otherwise asks to find and summarize a hot or recent paper on specific scientific topics.

## Known MCP Limitations

**PubMed MCP (pubmed via https://pubmed.mcp.claude.com/mcp):**
- Uses stateful HTTP sessions that expire mid-conversation. Deep multi-step searches work best at the start of a fresh Claude Code session. If session errors appear ("Session not found"), delegate the full search to a subagent (Agent tool) which initializes its own session — this reliably works around the expiry.

**bioRxiv MCP (biorxiv via https://mcp.deepsense.ai/biorxiv/mcp):**
- The configured endpoint may return HTTP 301 redirects to documentation pages and reject direct POST requests without OAuth. If this occurs, the subagent should fall back to Europe PMC's preprint index and PubMed's cross-indexing of bioRxiv papers for coverage.

**Recommended pattern:** Always delegate literature search to a subagent via the Agent tool. This isolates MCP session state and prevents expiry from affecting the main conversation.

## Workflow

### Step 1: Parse Keywords and Identify Their Intersection

Extract the three keywords from the user's input. Before searching, briefly analyze:

- The conceptual relationship between the three terms
- Which intersection is most scientifically novel or active
- What study types are likely (mechanistic, clinical, computational, meta-analysis, etc.)

State this framing to the user in one sentence before proceeding.

### Step 2: Search PubMed and bioRxiv via Subagent

Launch a subagent (Agent tool, general-purpose) with instructions to:

- Search PubMed with all three terms combined (AND logic), prioritizing last 12 months
- Search bioRxiv with the same terms
- If results are sparse (< 5), relax to two-term combinations and note this
- Retrieve for each result: title, authors, journal, publication date, abstract, citation count, DOI

### Step 3: Filter by Impact

Retain only papers meeting at least one threshold:

- **Citations ≥ 20** — the community has engaged with the work
- **Journal Impact Factor > 10** — e.g., Nature, Science, Cell, NEJM, Lancet, PNAS, Nature Methods, Nature Communications, JAMA, BMJ, eLife (IF ~8, acceptable exception)

If no paper meets either threshold, lower the bar to citations ≥ 10 or IF > 5 and explicitly tell the user that the best available match does not meet the original criteria.

### Step 4: Select the Single Best Paper

Rank filtered candidates by:

1. **Keyword coverage** — all three terms are substantively addressed, not just mentioned
2. **Recency** — more recent preferred among equivalent candidates
3. **Impact signal** — higher citations or IF breaks ties

Select one paper. If two are genuinely tied, choose the one with broader field-wide implications. Do not present multiple papers unless the user asks.

### Step 5: Compose the Expert Summary

Draft the structured summary (see Summary Structure below). Target length: **800–1,000 words in the body** (~4–5 minutes of reading). Do not simplify terminology. Use precise, confident language.

### Step 6: Generate PDF Output

After composing the summary, generate a PDF file using Python and fpdf2. Save the file to the user's Desktop as:

```
~/Desktop/HotPaper_<KeywordA>_<KeywordB>_<KeywordC>_<YYYY-MM-DD>.pdf
```

Use the following Python template, filling in all content from the summary:

```python
from fpdf import FPDF
from datetime import date
import os

class PaperPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(120, 120, 120)
        self.cell(0, 8, "Hot Paper Reader", align="R")
        self.ln(4)
        self.set_draw_color(180, 180, 180)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()} — Generated {date.today()}", align="C")

pdf = PaperPDF()
pdf.set_margins(18, 18, 18)
pdf.set_auto_page_break(auto=True, margin=20)
pdf.add_page()

# ── Keyword framing banner ───────────────────────────────────────────────────
pdf.set_fill_color(240, 245, 255)
pdf.set_draw_color(180, 200, 230)
pdf.rect(18, pdf.get_y(), 174, 12, style="FD")
pdf.set_font("Helvetica", "B", 10)
pdf.set_text_color(50, 80, 140)
pdf.set_xy(20, pdf.get_y() + 2)
pdf.cell(0, 8, "Topics: <KeywordA>  ·  <KeywordB>  ·  <KeywordC>")
pdf.ln(16)

# ── Framing line ─────────────────────────────────────────────────────────────
pdf.set_font("Helvetica", "I", 10)
pdf.set_text_color(60, 60, 60)
pdf.multi_cell(0, 6, "<FRAMING LINE — one sentence describing intersection>")
pdf.ln(6)

# ── Paper title ──────────────────────────────────────────────────────────────
pdf.set_font("Helvetica", "B", 13)
pdf.set_text_color(20, 20, 20)
pdf.multi_cell(0, 7, "<FULL PAPER TITLE>")
pdf.ln(3)

# ── Authors / Journal / DOI ───────────────────────────────────────────────────
pdf.set_font("Helvetica", "", 9)
pdf.set_text_color(80, 80, 80)
pdf.multi_cell(0, 5, "Authors: <First Author>, ..., <Last Author>")
pdf.multi_cell(0, 5, "Journal: <JOURNAL>  |  Year: <YEAR>  |  DOI: <DOI>")
pdf.multi_cell(0, 5, "Impact: <CITATIONS> citations  |  IF: <IF>")
pdf.ln(6)

# Horizontal rule
pdf.set_draw_color(200, 200, 200)
pdf.line(18, pdf.get_y(), 192, pdf.get_y())
pdf.ln(6)

def section(pdf, title, body):
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(30, 60, 120)
    pdf.cell(0, 7, title)
    pdf.ln(5)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(30, 30, 30)
    pdf.multi_cell(0, 6, body)
    pdf.ln(5)

def bullets(pdf, title, items):
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(30, 60, 120)
    pdf.cell(0, 7, title)
    pdf.ln(5)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(30, 30, 30)
    for item in items:
        pdf.set_x(22)
        pdf.multi_cell(170, 6, f"-  {item}")
        pdf.ln(1)
    pdf.ln(4)

section(pdf, "Why This Paper Matters", "<WHY THIS PAPER MATTERS BODY>")
section(pdf, "Background", "<BACKGROUND BODY>")
section(pdf, "Key Methods", "<KEY METHODS BODY>")
section(pdf, "Main Findings", "<MAIN FINDINGS BODY>")
section(pdf, "Conclusions & Implications", "<CONCLUSIONS BODY>")
bullets(pdf, "Presenter Talking Points", [
    "<TALKING POINT 1>",
    "<TALKING POINT 2>",
    "<TALKING POINT 3>",
    "<TALKING POINT 4>",
    "<TALKING POINT 5>",
])

# ── Footer note ───────────────────────────────────────────────────────────────
pdf.set_draw_color(200, 200, 200)
pdf.line(18, pdf.get_y(), 192, pdf.get_y())
pdf.ln(4)
pdf.set_font("Helvetica", "I", 8)
pdf.set_text_color(130, 130, 130)
pdf.multi_cell(0, 5, "Sources: PMID <PMID> (PubMed) | Full text: <PMC or DOI>")

outpath = os.path.expanduser("~/Desktop/HotPaper_<KeywordA>_<KeywordB>_<KeywordC>_<DATE>.pdf")
pdf.output(outpath)
print(f"PDF saved: {outpath}")
```

Run this script via Bash. After it succeeds, tell the user the file path. Do not print the full summary in the chat — the PDF is the deliverable. A one-paragraph plain-text teaser in the chat is sufficient to confirm what was found.

---

## Summary Structure (for PDF content)

**Framing line** (1 sentence)
*"At the intersection of [A], [B], and [C], this paper demonstrates..."*

**Paper Header**
- Title (full)
- Authors: First author, ..., Last author
- Journal — Year — DOI
- Impact signal: citation count and/or journal IF (mark as unavailable if MCP cannot retrieve it)

**Why This Paper Matters** (2–3 sentences)
Specify the gap it fills and why the timing is relevant. Avoid vague phrases like "groundbreaking" — be concrete.

**Background** (3–5 sentences)
The minimum prior knowledge an expert needs to follow the argument. Skip textbook basics. Focus on the specific open question this paper addresses.

**Key Methods** (3–5 sentences)
The experimental or computational approaches used. Call out any novel or particularly rigorous techniques. Include sample sizes or dataset scale where relevant.

**Main Findings** (4–6 sentences or a tight bullet list)
Central results with quantitative detail: p-values, effect sizes, fold-changes, accuracy metrics. Do not omit the numbers.

**Conclusions and Implications** (3–5 sentences)
What the authors claim and what the broader field should take from it. Note any limitations or caveats. Flag any result that may require replication.

**Presenter Talking Points** (3–5 bullets)
The "so what" moments to emphasize in a short talk. Each should be a crisp, memorable claim.

---

## Output Rules

- The primary deliverable is the PDF file on the Desktop. Do not reproduce the full summary as chat text.
- In chat, confirm: paper selected, one-paragraph teaser, and the Desktop file path.
- Never fabricate citation counts, impact factors, or DOIs.
- If no qualifying paper is found, report this clearly in chat and describe the closest results found.
- Do not exceed 1,000 words in the PDF summary body (excluding the paper header).
- Do not use hedging language like "it seems" unless the paper itself expresses uncertainty.
