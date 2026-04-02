#!/usr/bin/env python3
"""
Generate a Hot Paper Reader PDF from a JSON input file.

Usage:
    python3 generate_pdf.py <path_to_input.json>

Input JSON schema:
{
  "keywords": ["KeywordA", "KeywordB", "KeywordC"],
  "framing_line": "At the intersection of A, B, and C, this paper demonstrates...",
  "title": "Full paper title",
  "authors_first": "Smith et al.",
  "authors_last": "Jones",
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
  "talking_points": ["Point 1", "Point 2", "Point 3"],
  "sources_note": "PMID 12345678 (PubMed) | Full text: https://...",
  "output_path": "~/Desktop/HotPaper_A_B_C_2024-01-01.pdf"
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


def generate(data: dict):
    kw = data["keywords"]
    sec = data["sections"]

    pdf = PaperPDF()
    pdf.set_margins(18, 18, 18)
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # Keyword banner
    pdf.set_fill_color(240, 245, 255)
    pdf.set_draw_color(180, 200, 230)
    pdf.rect(18, pdf.get_y(), 174, 12, style="FD")
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(50, 80, 140)
    pdf.set_xy(20, pdf.get_y() + 2)
    pdf.cell(0, 8, f"Topics: {kw[0]}  ·  {kw[1]}  ·  {kw[2]}")
    pdf.ln(16)

    # Framing line
    pdf.set_font("Helvetica", "I", 10)
    pdf.set_text_color(60, 60, 60)
    pdf.multi_cell(0, 6, data["framing_line"])
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
    pdf.multi_cell(0, 5, f"Journal: {data['journal']}  |  Year: {data['year']}  |  DOI: {data['doi']}")
    pdf.multi_cell(0, 5, f"Impact: {data['citations']} citations  |  IF: {data['impact_factor']}")
    pdf.ln(6)

    pdf.set_draw_color(200, 200, 200)
    pdf.line(18, pdf.get_y(), 192, pdf.get_y())
    pdf.ln(6)

    section(pdf, "Why This Paper Matters", sec["why_it_matters"])
    section(pdf, "Background", sec["background"])
    section(pdf, "Key Methods", sec["key_methods"])
    section(pdf, "Main Findings", sec["main_findings"])
    section(pdf, "Conclusions & Implications", sec["conclusions"])
    bullets(pdf, "Presenter Talking Points", data["talking_points"])

    pdf.set_draw_color(200, 200, 200)
    pdf.line(18, pdf.get_y(), 192, pdf.get_y())
    pdf.ln(4)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(130, 130, 130)
    pdf.multi_cell(0, 5, f"Sources: {data['sources_note']}")

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
