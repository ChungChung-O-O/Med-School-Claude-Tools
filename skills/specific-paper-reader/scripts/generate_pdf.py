#!/usr/bin/env python3
"""
Generate a Specific Paper Reader PDF from a JSON input file.

Usage:
    python3 generate_pdf.py <path_to_input.json>

Input JSON schema:
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
  "talking_points": ["Point 1", "Point 2", "Point 3"],
  "related_articles": [
    {
      "title": "Related paper title",
      "citation": "Authors. Journal. Year.",
      "doi": "10.xxxx/xxxxx",
      "relevance": "Why a clinician should read this."
    }
  ],
  "sources_note": "PMID 12345678 (PubMed) | Full text: https://...",
  "output_path": "~/Desktop/PaperReview_Smith_2024_2024-01-01.pdf"
}
"""

import json
import os
import sys
from datetime import date

try:
    from fpdf import FPDF
except ImportError:
    print("fpdf2 not installed. Run: pip3 install fpdf2")
    sys.exit(1)

W = 174  # usable body width (A4 210mm - 18mm margins each side)


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


def related_articles_section(pdf, articles):
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


def generate(data: dict):
    sec = data["sections"]

    pdf = PaperPDF()
    pdf.set_margins(18, 18, 18)
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # Study design banner
    pdf.set_fill_color(230, 245, 235)
    pdf.set_draw_color(150, 200, 170)
    pdf.rect(18, pdf.get_y(), 174, 12, style="FD")
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(30, 100, 60)
    pdf.set_xy(20, pdf.get_y() + 2)
    pdf.cell(0, 8, f"Study Design: {data['study_design']}  ·  Level of Evidence: {data['level_of_evidence']}  ·  Specialty: {data['specialty']}")
    pdf.ln(16)

    # Clinical framing
    pdf.set_font("Helvetica", "I", 10)
    pdf.set_text_color(60, 60, 60)
    pdf.multi_cell(0, 6, data["clinical_framing"])
    pdf.ln(6)

    # Paper title
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(20, 20, 20)
    pdf.multi_cell(0, 7, data["title"])
    pdf.ln(3)

    # Authors / Journal / DOI
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(80, 80, 80)
    pdf.multi_cell(0, 5, f"Authors: {data['authors_first']}, ..., {data['authors_last']}")
    pdf.multi_cell(0, 5, f"Journal: {data['journal']}  |  Year: {data['year']}  |  DOI: {data['doi']}  |  PMID: {data['pmid']}")
    pdf.multi_cell(0, 5, f"Impact: {data['citations']} citations  |  IF: {data['impact_factor']}  |  Funding: {data['funding']}")
    pdf.ln(6)

    pdf.set_draw_color(200, 200, 200)
    pdf.line(18, pdf.get_y(), 192, pdf.get_y())
    pdf.ln(6)

    section(pdf, "Clinical Relevance", sec["clinical_relevance"])
    section(pdf, "Background & Clinical Context", sec["background"])
    section(pdf, "Study Design & Methods", sec["methods"])
    section(pdf, "Key Findings", sec["findings"])
    section(pdf, "Critical Appraisal", sec["appraisal"])
    section(pdf, "Conclusions & Practice Implications", sec["conclusions"])
    bullets(pdf, "Clinical Talking Points", data["talking_points"])
    related_articles_section(pdf, data.get("related_articles", []))

    pdf.set_draw_color(200, 200, 200)
    pdf.line(18, pdf.get_y(), 192, pdf.get_y())
    pdf.ln(4)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(130, 130, 130)
    sources = data.get("sources_note", "")
    pdf.multi_cell(0, 5, f"Sources: {sources}\nThis summary is generated for educational purposes and does not constitute clinical advice.")

    outpath = os.path.expanduser(data["output_path"])
    os.makedirs(os.path.dirname(outpath), exist_ok=True)
    pdf.output(outpath)
    print(f"PDF saved: {outpath}")
    return outpath


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 generate_pdf.py <input.json>")
        sys.exit(1)
    with open(sys.argv[1]) as f:
        data = json.load(f)
    generate(data)
