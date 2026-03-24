"""PDF parser — extracts text from digital and scanned PDFs via pdfplumber + Tesseract."""

from __future__ import annotations

import logging
from pathlib import Path

import pdfplumber
import pytesseract
from pdf2image import convert_from_path

from milanon.domain.entities import DocumentFormat, ExtractedDocument

logger = logging.getLogger(__name__)

# Threshold: pages with fewer characters trigger OCR fallback
_OCR_CHAR_THRESHOLD = 50
_OCR_DPI = 300
_OCR_LANG = "deu"

# Visual layout detection: tables with too many columns or mostly-empty cells
# are WAP/schedule grids — not meaningful data tables.
_VISUAL_TABLE_MAX_COLS = 20
_VISUAL_TABLE_EMPTY_THRESHOLD = 0.70

# Markers for visual/schedule pages — exported so anonymize.py can reference them.
VISUAL_PAGE_SKIP_MARKER = (
    "\n\n⚠ **Page {page_num}: Visual layout (WAP/schedule) — "
    "not extractable as text. See original PDF.**\n\n"
)
VISUAL_PAGE_EMBED_MARKER = (
    "\n\n⚠ **Page {page_num}: Visual layout (WAP/schedule) — "
    "embedded as image. NOT ANONYMIZED.**\n\n"
    "![Page {page_num}]({png_name})\n\n"
)


def _tesseract_available() -> bool:
    """Return True if the Tesseract binary is accessible on this system."""
    try:
        pytesseract.get_tesseract_version()
        return True
    except Exception:
        return False


def _table_to_markdown(table: list[list]) -> str:
    """Convert a pdfplumber table (list of rows) to a Markdown table string.

    Each cell is stripped, internal newlines replaced with spaces, and pipe
    characters escaped so they don't break the Markdown syntax.
    """
    if not table or not table[0]:
        return ""
    rows = [
        [(cell or "").replace("\n", " ").replace("|", "\\|").strip() for cell in row]
        for row in table
    ]
    header = "| " + " | ".join(rows[0]) + " |"
    separator = "| " + " | ".join("---" for _ in rows[0]) + " |"
    if len(rows) > 1:
        body = "\n".join("| " + " | ".join(row) + " |" for row in rows[1:])
        return f"{header}\n{separator}\n{body}"
    return f"{header}\n{separator}"


class PdfParser:
    """Parses PDF files into ExtractedDocument.

    Strategy per page (ADR-006):
    1. Detect tables via pdfplumber and render them as Markdown table syntax,
       interleaved with surrounding text in reading order (y-coordinate).
    2. For pages without tables, extract plain text with pdfplumber.
    3. If fewer than 50 characters are extracted, rasterize the page at 300 DPI
       and run Tesseract OCR (German language).
    4. If OCR is unavailable, keep the short (possibly empty) text and log a warning.

    Output text_content uses Markdown-style `---` page-break separators,
    which is the format expected by the anonymization output writer (ADR-005).
    """

    def parse(self, path: Path) -> ExtractedDocument:
        """Parse a PDF file and return its extracted content."""
        page_texts: list[str] = []
        total_images = 0
        ocr_pages: list[int] = []
        visual_pages: list[int] = []

        with pdfplumber.open(str(path)) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                text, used_ocr, is_visual = self._extract_page_text(path, page, page_num)
                page_texts.append(text.strip())
                total_images += len(page.images)
                if used_ocr:
                    ocr_pages.append(page_num)
                if is_visual:
                    visual_pages.append(page_num)

        text_content = "\n\n---\n\n".join(page_texts)
        metadata: dict[str, str] = {"page_count": str(len(page_texts))}
        if ocr_pages:
            metadata["ocr_pages"] = ", ".join(str(p) for p in ocr_pages)
        if visual_pages:
            metadata["visual_pages"] = ", ".join(str(p) for p in visual_pages)

        return ExtractedDocument(
            source_path=str(path),
            format=DocumentFormat.PDF,
            text_content=text_content,
            structured_content={"pages": page_texts} if len(page_texts) > 1 else None,
            metadata=metadata,
            embedded_image_count=total_images,
            visual_pages=visual_pages,
        )

    def supported_extensions(self) -> list[str]:
        """Return the file extensions this parser handles."""
        return [".pdf"]

    # ------------------------------------------------------------------
    # Per-page extraction
    # ------------------------------------------------------------------

    def _extract_page_text(
        self, path: Path, page, page_num: int
    ) -> tuple[str, bool, bool]:
        """Extract text from one page. Returns (text, used_ocr, is_visual).

        When tables are detected, renders them as Markdown and interleaves
        with surrounding text. Falls back to plain text + OCR for table-free pages
        or when table extraction produces insufficient content.

        Visual layout pages (WAP/schedule grids) are replaced with a marker
        and flagged via is_visual=True.
        """
        tables = page.find_tables()
        if tables:
            if self._is_visual_layout(tables):
                logger.info("Page %d: visual layout detected — skipping table extraction", page_num)
                marker = VISUAL_PAGE_SKIP_MARKER.format(page_num=page_num)
                return marker, False, True

            content = self._extract_with_tables(page, tables)
            if len(content.strip()) >= _OCR_CHAR_THRESHOLD:
                return content, False, False

        # No tables (or too little content after table extraction) — plain text + OCR
        text = page.extract_text() or ""
        if len(text.strip()) >= _OCR_CHAR_THRESHOLD:
            return text, False, False

        ocr_text = self._try_ocr(path, page_num)
        if ocr_text:
            logger.info("Page %d: OCR fallback used (%d chars)", page_num, len(ocr_text))
            return ocr_text, True, False

        # OCR unavailable or failed — keep original short text
        if text.strip():
            logger.warning(
                "Page %d: only %d chars extracted, OCR unavailable",
                page_num,
                len(text.strip()),
            )
        return text, False, False

    def _is_visual_layout(self, tables) -> bool:
        """Return True if any table looks like a visual/schedule grid.

        Both conditions must hold simultaneously:
        - A table has more than _VISUAL_TABLE_MAX_COLS columns (WAP-style grid), AND
        - More than _VISUAL_TABLE_EMPTY_THRESHOLD fraction of cells are empty.

        Requiring both conditions prevents false positives:
        - Wide tables with dense data (e.g. Dokumentenbudget) → not visual.
        - Narrow sparse tables (e.g. checklists with blanks) → not visual.
        """
        for table in tables:
            data = table.extract()
            if not data:
                continue
            num_cols = max(len(row) for row in data)
            if num_cols <= _VISUAL_TABLE_MAX_COLS:
                continue
            total_cells = sum(len(row) for row in data)
            if total_cells == 0:
                continue
            empty_cells = sum(
                1 for row in data for cell in row if not (cell or "").strip()
            )
            if empty_cells / total_cells > _VISUAL_TABLE_EMPTY_THRESHOLD:
                return True
        return False

    def _extract_with_tables(self, page, tables) -> str:
        """Extract page content with tables rendered as Markdown, in reading order.

        Crops text regions above/between/below each table to avoid duplicating
        content that pdfplumber would otherwise include in both the table cells
        and the plain text extraction.
        """
        tables_sorted = sorted(tables, key=lambda t: t.bbox[1])
        segments: list[str] = []
        prev_bottom = 0.0

        for table in tables_sorted:
            x0, top, x1, bottom = table.bbox

            # Text above this table
            if top > prev_bottom:
                region = page.crop((0, prev_bottom, page.width, top))
                above = (region.extract_text() or "").strip()
                if above:
                    segments.append(above)

            # Table rendered as Markdown
            data = table.extract()
            if data:
                md = _table_to_markdown(data)
                if md:
                    segments.append(md)

            prev_bottom = bottom

        # Text after last table
        if prev_bottom < page.height:
            region = page.crop((0, prev_bottom, page.width, page.height))
            below = (region.extract_text() or "").strip()
            if below:
                segments.append(below)

        return "\n\n".join(segments)

    def _try_ocr(self, path: Path, page_num: int) -> str:
        """Rasterize one page at 300 DPI and run Tesseract OCR.

        Returns empty string if Tesseract or poppler is not available,
        or if rasterization/OCR fails for any reason.
        """
        try:
            images = convert_from_path(
                str(path),
                first_page=page_num,
                last_page=page_num,
                dpi=_OCR_DPI,
            )
            if not images:
                return ""
            return pytesseract.image_to_string(images[0], lang=_OCR_LANG)
        except Exception as exc:
            logger.debug("OCR failed for page %d: %s", page_num, exc)
            return ""
