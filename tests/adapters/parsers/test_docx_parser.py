"""Tests for DocxParser — paragraphs, tables, headers/footers, image detection."""

from pathlib import Path

from milanon.adapters.parsers.docx_parser import DocxParser
from milanon.domain.entities import DocumentFormat
from milanon.domain.protocols import DocumentParser

from .conftest import SIMPLE_DOCX_TEXTS


class TestDocxParserProtocol:
    def test_implements_document_parser_protocol(self, docx_parser: DocxParser):
        assert isinstance(docx_parser, DocumentParser)

    def test_supported_extensions_includes_docx(self, docx_parser: DocxParser):
        assert ".docx" in docx_parser.supported_extensions()

    def test_parse_returns_docx_format(
        self, docx_parser: DocxParser, simple_docx_path: Path
    ):
        doc = docx_parser.parse(simple_docx_path)
        assert doc.format == DocumentFormat.DOCX

    def test_parse_sets_source_path(
        self, docx_parser: DocxParser, simple_docx_path: Path
    ):
        doc = docx_parser.parse(simple_docx_path)
        assert "simple.docx" in doc.source_path

    def test_parse_sample_fixture(self, docx_parser: DocxParser):
        """Smoke-test against the committed sample.docx fixture."""
        from tests.adapters.parsers.conftest import FIXTURES_DIR

        path = FIXTURES_DIR / "sample.docx"
        doc = docx_parser.parse(path)
        assert doc.format == DocumentFormat.DOCX
        assert len(doc.text_content) > 0


class TestDocxParserParagraphs:
    def test_heading_text_extracted(
        self, docx_parser: DocxParser, simple_docx_path: Path
    ):
        doc = docx_parser.parse(simple_docx_path)
        assert "Befehl Inf Kp 56/1" in doc.text_content

    def test_all_paragraph_texts_extracted(
        self, docx_parser: DocxParser, simple_docx_path: Path
    ):
        doc = docx_parser.parse(simple_docx_path)
        for expected in SIMPLE_DOCX_TEXTS:
            assert expected in doc.text_content

    def test_military_rank_and_name_extracted(
        self, docx_parser: DocxParser, simple_docx_path: Path
    ):
        doc = docx_parser.parse(simple_docx_path)
        assert "Hptm Marco BERNASCONI" in doc.text_content

    def test_ahv_number_extracted(
        self, docx_parser: DocxParser, simple_docx_path: Path
    ):
        doc = docx_parser.parse(simple_docx_path)
        assert "756.1234.5678.97" in doc.text_content

    def test_paragraphs_in_reading_order(
        self, docx_parser: DocxParser, simple_docx_path: Path
    ):
        doc = docx_parser.parse(simple_docx_path)
        heading_pos = doc.text_content.find("Befehl Inf Kp 56/1")
        standort_pos = doc.text_content.find("Kaserne Wangen")
        assert heading_pos < standort_pos


class TestDocxParserTables:
    def test_table_content_not_dropped(
        self, docx_parser: DocxParser, docx_with_table_path: Path
    ):
        doc = docx_parser.parse(docx_with_table_path)
        assert "Hans Muster" in doc.text_content
        assert "Peter Meier" in doc.text_content

    def test_table_header_row_extracted(
        self, docx_parser: DocxParser, docx_with_table_path: Path
    ):
        doc = docx_parser.parse(docx_with_table_path)
        assert "Name" in doc.text_content
        assert "Grad" in doc.text_content
        assert "Telefon" in doc.text_content

    def test_table_phone_numbers_extracted(
        self, docx_parser: DocxParser, docx_with_table_path: Path
    ):
        doc = docx_parser.parse(docx_with_table_path)
        assert "079 535 80 46" in doc.text_content
        assert "079 123 45 67" in doc.text_content

    def test_table_rows_use_cell_separator(
        self, docx_parser: DocxParser, docx_with_table_path: Path
    ):
        doc = docx_parser.parse(docx_with_table_path)
        # Each row is on its own line, cells joined with " | "
        assert "Hans Muster | Hptm | 079 535 80 46" in doc.text_content

    def test_paragraph_before_table_in_text(
        self, docx_parser: DocxParser, docx_with_table_path: Path
    ):
        doc = docx_parser.parse(docx_with_table_path)
        para_pos = doc.text_content.find("Personalliste")
        table_pos = doc.text_content.find("Hans Muster")
        assert para_pos < table_pos

    def test_structured_content_contains_table_rows(
        self, docx_parser: DocxParser, docx_with_table_path: Path
    ):
        doc = docx_parser.parse(docx_with_table_path)
        assert doc.structured_content is not None
        tables = doc.structured_content["tables"]
        assert len(tables) == 1
        rows = tables[0]
        assert rows[0] == ["Name", "Grad", "Telefon"]
        assert rows[1] == ["Hans Muster", "Hptm", "079 535 80 46"]

    def test_structured_content_none_when_no_tables(
        self, docx_parser: DocxParser, simple_docx_path: Path
    ):
        doc = docx_parser.parse(simple_docx_path)
        assert doc.structured_content is None


class TestDocxParserHeaderFooter:
    def test_header_text_in_text_content(
        self, docx_parser: DocxParser, docx_with_header_footer_path: Path
    ):
        doc = docx_parser.parse(docx_with_header_footer_path)
        assert "VERTRAULICH" in doc.text_content
        assert "Inf Kp 56/1" in doc.text_content

    def test_footer_text_in_text_content(
        self, docx_parser: DocxParser, docx_with_header_footer_path: Path
    ):
        doc = docx_parser.parse(docx_with_header_footer_path)
        assert "hans.muster@army.ch" in doc.text_content

    def test_footer_name_in_text_content(
        self, docx_parser: DocxParser, docx_with_header_footer_path: Path
    ):
        doc = docx_parser.parse(docx_with_header_footer_path)
        assert "Hans Muster" in doc.text_content

    def test_header_precedes_body_in_text(
        self, docx_parser: DocxParser, docx_with_header_footer_path: Path
    ):
        doc = docx_parser.parse(docx_with_header_footer_path)
        header_pos = doc.text_content.find("VERTRAULICH")
        body_pos = doc.text_content.find("Hauptinhalt")
        assert header_pos < body_pos

    def test_body_precedes_footer_in_text(
        self, docx_parser: DocxParser, docx_with_header_footer_path: Path
    ):
        doc = docx_parser.parse(docx_with_header_footer_path)
        body_pos = doc.text_content.find("Hauptinhalt")
        footer_pos = doc.text_content.find("hans.muster@army.ch")
        assert body_pos < footer_pos


class TestDocxParserImages:
    def test_embedded_image_count_correct(
        self, docx_parser: DocxParser, docx_with_images_path: Path
    ):
        doc = docx_parser.parse(docx_with_images_path)
        assert doc.embedded_image_count == 2

    def test_no_images_gives_zero_count(
        self, docx_parser: DocxParser, simple_docx_path: Path
    ):
        doc = docx_parser.parse(simple_docx_path)
        assert doc.embedded_image_count == 0

    def test_text_extracted_alongside_images(
        self, docx_parser: DocxParser, docx_with_images_path: Path
    ):
        doc = docx_parser.parse(docx_with_images_path)
        assert "Dokument mit eingebetteten Bildern" in doc.text_content
        assert "Text nach den Bildern" in doc.text_content
