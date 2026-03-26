"""Tests for PdfParser — text extraction, page breaks, images, OCR fallback."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from milanon.adapters.parsers.pdf_parser import (
    _MEGA_CELL_CHAR_THRESHOLD,
    _OCR_CHAR_THRESHOLD,
    _VISUAL_TABLE_EMPTY_THRESHOLD,
    _VISUAL_TABLE_MAX_COLS,
    PdfParser,
    _remove_empty_columns,
)
from milanon.domain.entities import DocumentFormat
from milanon.domain.protocols import DocumentParser

from .conftest import MULTI_PAGE_PDF_TEXTS, TESSERACT_AVAILABLE


class TestPdfParserProtocol:
    def test_implements_document_parser_protocol(self, pdf_parser: PdfParser):
        assert isinstance(pdf_parser, DocumentParser)

    def test_supported_extensions_includes_pdf(self, pdf_parser: PdfParser):
        assert ".pdf" in pdf_parser.supported_extensions()

    def test_parse_returns_pdf_format(
        self, pdf_parser: PdfParser, simple_pdf_path: Path
    ):
        doc = pdf_parser.parse(simple_pdf_path)
        assert doc.format == DocumentFormat.PDF

    def test_parse_sets_source_path(
        self, pdf_parser: PdfParser, simple_pdf_path: Path
    ):
        doc = pdf_parser.parse(simple_pdf_path)
        assert "simple.pdf" in doc.source_path

    def test_parse_sample_fixture(self, pdf_parser: PdfParser):
        """Smoke-test against the committed sample.pdf fixture."""
        from tests.adapters.parsers.conftest import FIXTURES_DIR

        path = FIXTURES_DIR / "sample.pdf"
        doc = pdf_parser.parse(path)
        assert doc.format == DocumentFormat.PDF
        assert len(doc.text_content) > 0


class TestPdfParserTextExtraction:
    def test_digital_pdf_text_extracted(
        self, pdf_parser: PdfParser, simple_pdf_path: Path
    ):
        doc = pdf_parser.parse(simple_pdf_path)
        assert "Hptm Marco BERNASCONI" in doc.text_content

    def test_ahv_number_extracted(
        self, pdf_parser: PdfParser, simple_pdf_path: Path
    ):
        doc = pdf_parser.parse(simple_pdf_path)
        assert "756.1234.5678.97" in doc.text_content

    def test_military_unit_extracted(
        self, pdf_parser: PdfParser, simple_pdf_path: Path
    ):
        doc = pdf_parser.parse(simple_pdf_path)
        assert "Inf Kp 56/1" in doc.text_content

    def test_all_simple_pdf_content_present(
        self, pdf_parser: PdfParser, simple_pdf_path: Path
    ):
        doc = pdf_parser.parse(simple_pdf_path)
        for fragment in ("Hptm Marco BERNASCONI", "756.1234.5678.97", "Inf Kp 56/1", "Kommandant"):
            assert fragment in doc.text_content


class TestPdfParserMetadata:
    def test_single_page_count_in_metadata(
        self, pdf_parser: PdfParser, simple_pdf_path: Path
    ):
        doc = pdf_parser.parse(simple_pdf_path)
        assert doc.metadata.get("page_count") == "1"

    def test_multi_page_count_in_metadata(
        self, pdf_parser: PdfParser, multi_page_pdf_path: Path
    ):
        doc = pdf_parser.parse(multi_page_pdf_path)
        assert doc.metadata.get("page_count") == "2"

    def test_no_ocr_pages_in_metadata_for_digital_pdf(
        self, pdf_parser: PdfParser, simple_pdf_path: Path
    ):
        doc = pdf_parser.parse(simple_pdf_path)
        assert "ocr_pages" not in doc.metadata


class TestPdfParserPageBreaks:
    def test_single_page_no_separator(
        self, pdf_parser: PdfParser, simple_pdf_path: Path
    ):
        doc = pdf_parser.parse(simple_pdf_path)
        assert "---" not in doc.text_content

    def test_two_pages_has_one_separator(
        self, pdf_parser: PdfParser, multi_page_pdf_path: Path
    ):
        doc = pdf_parser.parse(multi_page_pdf_path)
        assert doc.text_content.count("---") == 1

    def test_separator_is_markdown_hr(
        self, pdf_parser: PdfParser, multi_page_pdf_path: Path
    ):
        doc = pdf_parser.parse(multi_page_pdf_path)
        assert "\n\n---\n\n" in doc.text_content

    def test_both_page_texts_present(
        self, pdf_parser: PdfParser, multi_page_pdf_path: Path
    ):
        doc = pdf_parser.parse(multi_page_pdf_path)
        for page_text in MULTI_PAGE_PDF_TEXTS:
            for fragment in page_text.split(", "):
                assert fragment in doc.text_content

    def test_multi_page_structured_content_has_pages(
        self, pdf_parser: PdfParser, multi_page_pdf_path: Path
    ):
        doc = pdf_parser.parse(multi_page_pdf_path)
        assert doc.structured_content is not None
        assert len(doc.structured_content["pages"]) == 2

    def test_single_page_structured_content_is_none(
        self, pdf_parser: PdfParser, simple_pdf_path: Path
    ):
        doc = pdf_parser.parse(simple_pdf_path)
        assert doc.structured_content is None


class TestPdfParserImages:
    def test_text_only_pdf_has_zero_images(
        self, pdf_parser: PdfParser, simple_pdf_path: Path
    ):
        doc = pdf_parser.parse(simple_pdf_path)
        assert doc.embedded_image_count == 0

    def test_pdf_with_images_detected(
        self, pdf_parser: PdfParser, pdf_with_images_path: Path
    ):
        doc = pdf_parser.parse(pdf_with_images_path)
        assert doc.embedded_image_count == 2

    def test_text_present_alongside_images(
        self, pdf_parser: PdfParser, pdf_with_images_path: Path
    ):
        doc = pdf_parser.parse(pdf_with_images_path)
        assert "Dokument mit Bildern" in doc.text_content


class TestPdfParserOcrThreshold:
    def test_long_text_does_not_trigger_ocr(
        self, pdf_parser: PdfParser, simple_pdf_path: Path
    ):
        """A digital PDF with sufficient text must NOT trigger the OCR path."""
        ocr_call_count = []

        original_try_ocr = pdf_parser._try_ocr

        def counting_try_ocr(path, page_num):
            ocr_call_count.append(page_num)
            return original_try_ocr(path, page_num)

        pdf_parser._try_ocr = counting_try_ocr
        pdf_parser.parse(simple_pdf_path)
        assert len(ocr_call_count) == 0, "OCR must not be called for a digital PDF"

    def test_short_text_triggers_ocr_attempt(
        self, pdf_parser: PdfParser, simple_pdf_path: Path
    ):
        """When pdfplumber returns < threshold chars, _try_ocr must be called."""
        ocr_called = []

        def stub_try_ocr(path, page_num):
            ocr_called.append(page_num)
            return ""  # simulate OCR unavailable

        with patch.object(pdf_parser, "_try_ocr", side_effect=stub_try_ocr), patch(
            "milanon.adapters.parsers.pdf_parser.pdfplumber"
        ) as mock_pdfplumber:
            mock_page = MagicMock()
            mock_page.find_tables.return_value = []
            mock_page.extract_text.return_value = "short"  # < threshold
            mock_page.images = []
            mock_pdf = MagicMock()
            mock_pdf.pages = [mock_page]
            mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
            mock_pdf.__exit__ = MagicMock(return_value=False)
            mock_pdfplumber.open.return_value = mock_pdf

            pdf_parser.parse(simple_pdf_path)

        assert len(ocr_called) == 1

    def test_ocr_threshold_value(self):
        """The OCR threshold should be exactly 50 chars as specified in ADR-006."""
        assert _OCR_CHAR_THRESHOLD == 50


@pytest.mark.skipif(not TESSERACT_AVAILABLE, reason="Tesseract not installed")
class TestPdfParserOcrFallback:
    def test_ocr_page_added_to_metadata(
        self, pdf_parser: PdfParser, simple_pdf_path: Path
    ):
        """On a page that triggers OCR, the page number appears in metadata."""
        with patch.object(
            pdf_parser,
            "_try_ocr",
            return_value="OCR extracted text with enough characters to count",
        ), patch(
            "milanon.adapters.parsers.pdf_parser.pdfplumber"
        ) as mock_pdfplumber:
            mock_page = MagicMock()
            mock_page.find_tables.return_value = []
            mock_page.extract_text.return_value = ""  # trigger OCR
            mock_page.images = []
            mock_pdf = MagicMock()
            mock_pdf.pages = [mock_page]
            mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
            mock_pdf.__exit__ = MagicMock(return_value=False)
            mock_pdfplumber.open.return_value = mock_pdf

            doc = pdf_parser.parse(simple_pdf_path)

        assert "ocr_pages" in doc.metadata
        assert "1" in doc.metadata["ocr_pages"]


class TestPdfParserTableExtraction:
    def test_pdf_with_table_produces_markdown_pipe_syntax(
        self, pdf_parser: PdfParser, pdf_with_table_path: Path
    ):
        doc = pdf_parser.parse(pdf_with_table_path)
        assert "|" in doc.text_content

    def test_pdf_table_has_header_separator_row(
        self, pdf_parser: PdfParser, pdf_with_table_path: Path
    ):
        doc = pdf_parser.parse(pdf_with_table_path)
        assert "| --- |" in doc.text_content or "---" in doc.text_content

    def test_pdf_mixed_content_no_duplicate_text(
        self, pdf_parser: PdfParser, pdf_with_table_path: Path
    ):
        """Heading text before the table must appear exactly once."""
        doc = pdf_parser.parse(pdf_with_table_path)
        assert doc.text_content.count("Personalliste") == 1

    def test_pdf_without_tables_unchanged(
        self, pdf_parser: PdfParser, simple_pdf_path: Path
    ):
        """A PDF with no tables must still return its plain text unchanged."""
        doc = pdf_parser.parse(simple_pdf_path)
        assert "Hptm Marco BERNASCONI" in doc.text_content
        assert "|" not in doc.text_content


class TestPdfParserVisualLayout:
    def _make_table_mock(self, num_cols: int, empty_fraction: float):
        """Build a mock pdfplumber Table with the given column count and empty ratio."""
        total_cells = num_cols * 3  # 3 rows
        empty_count = int(total_cells * empty_fraction)
        filled_count = total_cells - empty_count
        flat = ["data"] * filled_count + [""] * empty_count
        # Distribute into rows
        rows = [flat[i * num_cols:(i + 1) * num_cols] for i in range(3)]
        table = MagicMock()
        table.extract.return_value = rows
        return table

    def test_visual_layout_detected_when_both_conditions_met(self, pdf_parser: PdfParser):
        # >20 cols AND >70% empty → WAP/schedule grid
        table = self._make_table_mock(
            _VISUAL_TABLE_MAX_COLS + 1, _VISUAL_TABLE_EMPTY_THRESHOLD + 0.05
        )
        assert pdf_parser._is_visual_layout([table]) is True

    def test_many_columns_but_dense_data_is_not_visual(self, pdf_parser: PdfParser):
        # Wide table (e.g. Dokumentenbudget) with real data — not a visual page
        table = self._make_table_mock(_VISUAL_TABLE_MAX_COLS + 5, 0.10)
        assert pdf_parser._is_visual_layout([table]) is False

    def test_mostly_empty_but_few_columns_is_not_visual(self, pdf_parser: PdfParser):
        # Sparse narrow table (e.g. checklist) — not a visual page
        table = self._make_table_mock(5, _VISUAL_TABLE_EMPTY_THRESHOLD + 0.05)
        assert pdf_parser._is_visual_layout([table]) is False

    def test_normal_table_not_detected_as_visual(self, pdf_parser: PdfParser):
        table = self._make_table_mock(5, 0.10)
        assert pdf_parser._is_visual_layout([table]) is False

    def test_visual_page_marker_in_output(self, pdf_parser: PdfParser, simple_pdf_path: Path):
        """A page whose tables are visual must produce the warning marker."""
        visual_table = self._make_table_mock(
            _VISUAL_TABLE_MAX_COLS + 5, _VISUAL_TABLE_EMPTY_THRESHOLD + 0.05
        )
        with patch("milanon.adapters.parsers.pdf_parser.pdfplumber") as mock_pdfplumber:
            mock_page = MagicMock()
            mock_page.find_tables.return_value = [visual_table]
            mock_page.images = []
            mock_pdf = MagicMock()
            mock_pdf.pages = [mock_page]
            mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
            mock_pdf.__exit__ = MagicMock(return_value=False)
            mock_pdfplumber.open.return_value = mock_pdf

            doc = pdf_parser.parse(simple_pdf_path)

        assert "Visual layout" in doc.text_content
        assert "not extractable as text" in doc.text_content

    def test_visual_pages_list_populated(self, pdf_parser: PdfParser, simple_pdf_path: Path):
        visual_table = self._make_table_mock(
            _VISUAL_TABLE_MAX_COLS + 5, _VISUAL_TABLE_EMPTY_THRESHOLD + 0.05
        )
        with patch("milanon.adapters.parsers.pdf_parser.pdfplumber") as mock_pdfplumber:
            mock_page = MagicMock()
            mock_page.find_tables.return_value = [visual_table]
            mock_page.images = []
            mock_pdf = MagicMock()
            mock_pdf.pages = [mock_page]
            mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
            mock_pdf.__exit__ = MagicMock(return_value=False)
            mock_pdfplumber.open.return_value = mock_pdf

            doc = pdf_parser.parse(simple_pdf_path)

        assert 1 in doc.visual_pages


class TestMegaCellDetection:
    """B-013: Mega-cell visual detection."""

    class MockTable:
        def __init__(self, data):
            self._data = data
            self.bbox = (0, 0, 100, 100)

        def extract(self):
            return self._data

    def test_mega_cell_detected_as_visual(self):
        """A table with a single cell >500 chars should be detected as visual."""
        parser = PdfParser()
        long_content = "A" * (_MEGA_CELL_CHAR_THRESHOLD + 100)
        table = self.MockTable([["Header", "", ""], [long_content, "", ""]])
        assert parser._is_visual_layout([table]) is True

    def test_normal_table_not_mega_cell(self):
        """A table with short cells should NOT be detected as visual."""
        parser = PdfParser()
        table = self.MockTable([["Name", "Rank", "Unit"], ["Müller", "Hptm", "Inf Kp 56/1"]])
        assert parser._is_visual_layout([table]) is False

    def test_existing_wide_sparse_still_detected(self):
        """The existing WAP/Picasso detection (>20 cols, >70% empty) still works."""
        parser = PdfParser()
        row = [""] * 25
        row[0] = "Data"
        table = self.MockTable([row] * 5)
        assert parser._is_visual_layout([table]) is True


class TestRemoveEmptyColumns:
    """B-014: Empty column stripping."""

    def test_removes_empty_columns(self):
        table = [["A", "", "B", "", "C"], ["1", "", "2", "", "3"]]
        result = _remove_empty_columns(table)
        assert result == [["A", "B", "C"], ["1", "2", "3"]]

    def test_preserves_all_when_no_empty(self):
        table = [["A", "B"], ["1", "2"]]
        result = _remove_empty_columns(table)
        assert result == [["A", "B"], ["1", "2"]]

    def test_empty_table_unchanged(self):
        assert _remove_empty_columns([]) == []
        assert _remove_empty_columns([[]]) == [[]]

    def test_preserves_column_with_single_value(self):
        """A column with content in only one row should be kept."""
        table = [["A", "", "C"], ["1", "X", "3"], ["2", "", "4"]]
        result = _remove_empty_columns(table)
        assert result == [["A", "", "C"], ["1", "X", "3"], ["2", "", "4"]]

    def test_whitespace_only_treated_as_empty(self):
        table = [["A", "  ", "C"], ["1", "  ", "3"]]
        result = _remove_empty_columns(table)
        assert result == [["A", "C"], ["1", "3"]]
