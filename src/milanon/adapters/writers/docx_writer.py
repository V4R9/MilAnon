"""DOCX writer — writes anonymized content as a .docx file."""

from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

from milanon.domain.anonymizer import LEGEND_PATTERN
from milanon.domain.entities import AnonymizedDocument


class DocxWriter:
    """Writes anonymized plain-text content to a Word document.

    Each paragraph in the content becomes a DOCX paragraph.
    Page-break markers (---) are converted to DOCX page breaks.
    The legend block is stripped (not suitable for DOCX).
    """

    def write(self, document: AnonymizedDocument, output_path: Path) -> Path:
        """Write anonymized content to a DOCX file.

        Args:
            document: The anonymized document.
            output_path: Destination .docx path (created if needed).

        Returns:
            The path to the written file.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Strip legend
        text = LEGEND_PATTERN.sub("", document.content).strip()

        doc = Document()
        pages = text.split("\n\n---\n\n")

        for page_idx, page_text in enumerate(pages):
            if page_idx > 0:
                # Add a page break before each subsequent page
                last_para = doc.paragraphs[-1] if doc.paragraphs else doc.add_paragraph()
                run = last_para.add_run()
                br = OxmlElement("w:br")
                br.set(qn("w:type"), "page")
                run._r.append(br)

            for line in page_text.splitlines():
                doc.add_paragraph(line)

        doc.save(str(output_path))
        return output_path

    def default_extension(self) -> str:
        return ".docx"
