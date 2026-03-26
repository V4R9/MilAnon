"""DOCX parser — parses .docx files into ExtractedDocument using python-docx."""

from __future__ import annotations

from pathlib import Path

from docx import Document as OpenDocx
from docx.document import Document as DocxDocument
from docx.enum.shape import WD_INLINE_SHAPE
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph

from milanon.domain.entities import DocumentFormat, ExtractedDocument

_CELL_SEP = " | "


class DocxParser:
    """Parses .docx files into ExtractedDocument.

    Extracts:
    - Paragraphs and tables in reading order (interleaved body traversal)
    - Headers and footers from all document sections
    - Inline image count for embedded-image warnings (US-3.5)
    - Document core properties as metadata
    """

    def parse(self, path: Path) -> ExtractedDocument:
        """Parse a .docx file and return its extracted content."""
        doc = OpenDocx(str(path))

        header_text, footer_text = self._extract_headers_footers(doc)
        body_text, tables = self._extract_body(doc)
        image_count = self._count_images(doc)
        metadata = self._extract_metadata(doc)
        text_content = self._build_text_content(header_text, body_text, footer_text)

        return ExtractedDocument(
            source_path=str(path),
            format=DocumentFormat.DOCX,
            text_content=text_content,
            structured_content={"tables": tables} if tables else None,
            metadata=metadata,
            embedded_image_count=image_count,
        )

    def supported_extensions(self) -> list[str]:
        """Return the file extensions this parser handles."""
        return [".docx"]

    # ------------------------------------------------------------------
    # Body extraction
    # ------------------------------------------------------------------

    def _extract_body(self, doc: DocxDocument) -> tuple[str, list]:
        """Extract paragraphs and tables interleaved in document reading order."""
        lines: list[str] = []
        tables: list[list[list[str]]] = []

        for block in self._iter_body_blocks(doc):
            if isinstance(block, Paragraph):
                text = block.text.strip()
                if text:
                    lines.append(text)
            elif isinstance(block, Table):
                rows_data, row_lines = self._extract_table(block)
                tables.append(rows_data)
                lines.extend(row_lines)
                lines.append("")  # blank line after table

        return "\n".join(lines), tables

    def _extract_table(self, table: Table) -> tuple[list[list[str]], list[str]]:
        """Extract table rows as structured data and as formatted text lines."""
        rows_data: list[list[str]] = []
        text_lines: list[str] = []

        for row in table.rows:
            cells = [cell.text.strip() for cell in row.cells]
            # Merge duplicate adjacent cells (merged cells repeat content in python-docx)
            deduped = _dedup_adjacent(cells)
            rows_data.append(deduped)
            text_lines.append(_CELL_SEP.join(deduped))

        return rows_data, text_lines

    # ------------------------------------------------------------------
    # Headers / footers
    # ------------------------------------------------------------------

    def _extract_headers_footers(self, doc: DocxDocument) -> tuple[str, str]:
        """Extract unique header and footer texts across all sections."""
        header_parts: list[str] = []
        footer_parts: list[str] = []
        seen_headers: set[str] = set()
        seen_footers: set[str] = set()

        for section in doc.sections:
            hdr = self._section_hf_text(section.header)
            if hdr and hdr not in seen_headers:
                header_parts.append(hdr)
                seen_headers.add(hdr)

            ftr = self._section_hf_text(section.footer)
            if ftr and ftr not in seen_footers:
                footer_parts.append(ftr)
                seen_footers.add(ftr)

        return "\n".join(header_parts), "\n".join(footer_parts)

    @staticmethod
    def _section_hf_text(hf) -> str:
        """Extract text from a single header/footer; returns '' if linked or empty."""
        try:
            if hf.is_linked_to_previous:
                return ""
        except AttributeError:
            pass
        texts = [p.text.strip() for p in hf.paragraphs if p.text.strip()]
        return "\n".join(texts)

    # ------------------------------------------------------------------
    # Image counting
    # ------------------------------------------------------------------

    @staticmethod
    def _count_images(doc: DocxDocument) -> int:
        """Count embedded inline picture shapes in the document."""
        return sum(
            1
            for shape in doc.inline_shapes
            if shape.type == WD_INLINE_SHAPE.PICTURE
        )

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_metadata(doc: DocxDocument) -> dict:
        """Extract document core properties."""
        props = doc.core_properties
        result: dict[str, str] = {}
        for attr in ("author", "title", "subject", "created", "modified"):
            value = getattr(props, attr, None)
            if value:
                result[attr] = str(value)
        return result

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _iter_body_blocks(doc: DocxDocument):
        """Yield Paragraphs and Tables from the document body in XML order."""
        for child in doc.element.body.iterchildren():
            if child.tag == qn("w:p"):
                yield Paragraph(child, doc)
            elif child.tag == qn("w:tbl"):
                yield Table(child, doc)

    @staticmethod
    def _build_text_content(header: str, body: str, footer: str) -> str:
        """Combine header, body, and footer into one text string."""
        parts: list[str] = []
        if header:
            parts.append(header)
            parts.append("")
        parts.append(body)
        if footer:
            parts.append("")
            parts.append(footer)
        return "\n".join(parts)


def _dedup_adjacent(cells: list[str]) -> list[str]:
    """Remove consecutive duplicate values (merged-cell artefact in python-docx)."""
    if not cells:
        return cells
    result = [cells[0]]
    for cell in cells[1:]:
        if cell != result[-1]:
            result.append(cell)
    return result
