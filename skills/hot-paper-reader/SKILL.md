---
name: hot-paper-reader
description: Use this skill when the user says "Topic for today: <keyword1>, <keyword2>, and <keyword3>", asks to "find a hot paper on [topics]", wants to "summarize a recent paper about [topics]", or provides three research keywords to search scientific literature. Trigger even if the user phrases it casually, e.g. "find me a paper on X, Y, Z" or "what's a good recent paper about CRISPR, cancer, and immunotherapy".
---

# Hot Paper Reader

Find and summarize the single most relevant, high-impact recent paper at the intersection of three user-provided research keywords. The summary is written for a domain expert preparing to give a short presentation on the work, and delivered as a formatted PDF file.

## When This Skill Applies

Activate when the user provides three research keywords using the pattern "Topic for today: <A>, <B>, and <C>", or otherwise asks to find and summarize a hot or recent paper on specific scientific topics.

## Available MCPs

**Fetch MCP (`fetch` tool):**
- Use for fetching DOI landing pages, journal article URLs, or abstract pages when the subagent needs to retrieve full-text or supplementary content from a URL.
- Preferred over WebFetch — provides richer HTML-to-markdown conversion. Use it in the subagent when retrieving paper content from a URL.

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

After composing the summary, generate a PDF using the bundled script. This avoids re-writing boilerplate every time.

**Step 6a: Write a JSON file to `/tmp/hotpaper_input.json`** with this structure:

```json
{
  "keywords": ["KeywordA", "KeywordB", "KeywordC"],
  "framing_line": "At the intersection of ...",
  "title": "Full paper title",
  "authors_first": "First Author",
  "authors_last": "Last Author",
  "journal": "Nature",
  "year": "2024",
  "doi": "10.xxxx/xxxxx",
  "pmid": "12345678",
  "citations": "42",
  "impact_factor": "50.5",
  "sections": {
    "why_it_matters": "...",
    "background": "...",
    "key_methods": "...",
    "main_findings": "...",
    "conclusions": "..."
  },
  "talking_points": ["Point 1", "Point 2", "Point 3", "Point 4", "Point 5"],
  "sources_note": "PMID 12345678 (PubMed) | Full text: https://...",
  "output_path": "~/Desktop/HotPaper_KeywordA_KeywordB_KeywordC_YYYY-MM-DD.pdf"
}
```

**Step 6b: Run the bundled script:**

```bash
python3 ~/.claude/skills/hot-paper-reader/scripts/generate_pdf.py /tmp/hotpaper_input.json
```

If fpdf2 is not installed, run `pip3 install fpdf2` first and retry.

**Step 6c: Verify the output** — confirm the file exists and has a non-zero size, then report the file path to the user.

The PDF is the deliverable. A one-paragraph plain-text teaser in the chat is enough to confirm what was found — don't reproduce the full summary in chat.

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
