"""DOCX Befehl writer — converts structured Markdown into a formatted DOCX
using the official Armee-Vorlage as template.

Style mapping (verified against befehl_vorlage.docx — all styles confirmed present):
  # Grundlagen       → "Heading 1"          ✓ exists in template
  ## "DECKNAME"      → "Subject heading"     ✓ exists in template
  ### 1 Title        → "1. Main title"       ✓ exists in template
  #### 1.1 Title     → "1.1 Title"           ✓ exists in template
  ##### 1.1.1 Title  → "1.1.1 Title"         ✓ exists in template
  Body text          → "Text Indent"         ✓ exists in template
  - Bullet item      → "Bullet List 1"       ✓ exists in template
  1. Item            → "Numbered List 2"     ✓ exists in template
  | Table |          → DOCX Table (Aufträge) — table cells use "Bullet List 1"
"""

from __future__ import annotations

import re
from pathlib import Path

from docx import Document
from docx.shared import Cm

# Regex to detect Markdown table rows (pipe-delimited)
_TABLE_ROW_RE = re.compile(r"^\|(.+)\|$")
# Separator row in Markdown tables (e.g. |---|---|)
_TABLE_SEP_RE = re.compile(r"^\|[\s\-:|]+\|$")
# Ordered list item
_ORDERED_LIST_RE = re.compile(r"^\d+\.\s+(.*)$")


class DocxBefehlWriter:
    """Converts structured Markdown into a DOCX using the Armee-Vorlage template."""

    # Column widths for Aufträge table (Element | Auftrag)
    COL_WIDTH_LEFT = Cm(4.0)
    COL_WIDTH_RIGHT = Cm(4.3)

    def write(self, markdown_text: str, template_path: Path, output_path: Path) -> Path:
        """Convert Markdown text to a DOCX file based on the template.

        Args:
            markdown_text: Structured Markdown content (Befehl).
            template_path: Path to befehl_vorlage.docx.
            output_path: Where to save the generated DOCX.

        Returns:
            The path to the written DOCX file.
        """
        doc = Document(str(template_path))
        self._clear_body(doc)

        lines = markdown_text.splitlines()
        i = 0
        while i < len(lines):
            line = lines[i]

            # Detect Markdown table block
            if _TABLE_ROW_RE.match(line):
                table_lines = []
                while i < len(lines) and _TABLE_ROW_RE.match(lines[i]):
                    if not _TABLE_SEP_RE.match(lines[i]):
                        table_lines.append(lines[i])
                    i += 1
                # Skip header row (first line is column headers)
                data_rows = table_lines[1:] if len(table_lines) > 1 else table_lines
                self._add_table(doc, data_rows)
                continue

            self._add_line(doc, line)
            i += 1

        output_path.parent.mkdir(parents=True, exist_ok=True)
        doc.save(str(output_path))
        return output_path

    def _clear_body(self, doc: Document) -> None:
        """Remove all paragraphs and tables from the document body, keeping styles."""
        body = doc.element.body
        for child in list(body):
            tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
            if tag in ("p", "tbl"):
                body.remove(child)

    def _add_line(self, doc: Document, line: str) -> None:
        """Map a single Markdown line to a styled DOCX paragraph."""
        stripped = line.strip()

        if not stripped:
            # Empty line → empty Text Indent paragraph (spacing)
            doc.add_paragraph("", style="Text Indent")
            return

        # Heading detection (order matters: check ##### before ####, etc.)
        if stripped.startswith("##### "):
            text = stripped[6:]
            doc.add_paragraph(text, style="1.1.1 Title")
        elif stripped.startswith("#### "):
            text = stripped[5:]
            doc.add_paragraph(text, style="1.1 Title")
        elif stripped.startswith("### "):
            text = stripped[4:]
            doc.add_paragraph(text, style="1. Main title")
        elif stripped.startswith("## "):
            text = stripped[3:]
            doc.add_paragraph(text, style="Subject heading")
        elif stripped.startswith("# "):
            text = stripped[2:]
            doc.add_paragraph(text, style="Heading 1")
        elif stripped.startswith("- "):
            text = stripped[2:]
            doc.add_paragraph(text, style="Bullet List 1")
        elif (m := _ORDERED_LIST_RE.match(stripped)):
            text = m.group(1)
            doc.add_paragraph(text, style="Numbered List 2")
        else:
            doc.add_paragraph(stripped, style="Text Indent")

    def _add_table(self, doc: Document, data_rows: list[str]) -> None:
        """Create an Aufträge table (Nx2) from Markdown table rows."""
        if not data_rows:
            return

        table = doc.add_table(rows=len(data_rows), cols=2)

        # Set column widths
        for row in table.rows:
            row.cells[0].width = self.COL_WIDTH_LEFT
            row.cells[1].width = self.COL_WIDTH_RIGHT

        for row_idx, row_text in enumerate(data_rows):
            cells = [c.strip() for c in row_text.strip("|").split("|")]
            if len(cells) < 2:
                continue

            element_name = cells[0].strip()
            auftrag_text = cells[1].strip()

            # Left column: Einheitsbezeichnung (Normal style)
            table.rows[row_idx].cells[0].text = element_name

            # Right column: Auftrag lines with Bullet List 1 style
            right_cell = table.rows[row_idx].cells[1]
            # Clear default paragraph
            right_cell.text = ""

            # Split auftrag into individual bullet lines if separated by <br> or ;
            auftrag_lines = [
                al.strip().lstrip("- ").strip()
                for al in re.split(r"<br>|;\s*(?=-)", auftrag_text)
                if al.strip()
            ]
            if not auftrag_lines:
                auftrag_lines = [auftrag_text]

            for line_idx, aline in enumerate(auftrag_lines):
                p = right_cell.paragraphs[0] if line_idx == 0 else right_cell.add_paragraph()
                p.text = aline
                p.style = doc.styles["Bullet List 1"]
