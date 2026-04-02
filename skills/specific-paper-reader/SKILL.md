---
name: specific-paper-reader
description: Use this skill when the user provides a specific paper to analyze — via PubMed ID (e.g., "PMID: 12345678"), a URL to a paper, or by uploading/pasting the paper text. Generates a clinical expert summary as a PDF with related reading recommendations. Trigger on any PMID, DOI, journal URL, or pasted abstract the user wants analyzed, even if they just say "can you summarize this paper for me" and paste text.
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
- **URL** → Use the `fetch` MCP tool (preferred over WebFetch — better HTML-to-markdown conversion). If fetch MCP is unavailable, fall back to WebFetch. If the URL is paywalled, extract what is available and note the limitation.
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

After composing the summary, generate a PDF using the bundled script. This avoids re-writing boilerplate every time.

**Step 6a: Write a JSON file to `/tmp/paperreview_input.json`** with this structure:

```json
{
  "study_design": "RCT",
  "level_of_evidence": "Level I",
  "specialty": "Cardiology",
  "clinical_framing": "2-3 sentence clinical framing...",
  "title": "Full paper title",
  "authors_first": "Smith",
  "authors_last": "Jones",
  "journal": "NEJM",
  "year": "2024",
  "doi": "10.xxxx/xxxxx",
  "pmid": "12345678",
  "citations": "150",
  "impact_factor": "91.2",
  "funding": "NIH",
  "sections": {
    "clinical_relevance": "...",
    "background": "...",
    "methods": "...",
    "findings": "...",
    "appraisal": "...",
    "conclusions": "..."
  },
  "talking_points": ["Point 1", "Point 2", "Point 3", "Point 4", "Point 5"],
  "related_articles": [
    {
      "title": "Related paper title",
      "citation": "Authors. Journal. Year.",
      "doi": "10.xxxx/xxxxx",
      "relevance": "Why a clinician should read this."
    }
  ],
  "sources_note": "PMID 12345678 (PubMed) | Full text: https://...",
  "output_path": "~/Desktop/PaperReview_Smith_2024_YYYY-MM-DD.pdf"
}
```

**Step 6b: Run the bundled script:**

```bash
python3 ~/.claude/skills/specific-paper-reader/scripts/generate_pdf.py /tmp/paperreview_input.json
```

If fpdf2 is not installed, run `pip3 install fpdf2` first and retry.

**Step 6c: Verify the output** — confirm the file exists and has a non-zero size, then report the file path to the user.

The PDF is the deliverable. A one-paragraph clinical teaser plus the file path is all that's needed in chat — don't reproduce the full summary.

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
