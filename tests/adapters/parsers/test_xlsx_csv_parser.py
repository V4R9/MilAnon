"""Tests for XlsxCsvParser — XLSX multi-sheet, CSV delimiter detection, PISA 410."""

from pathlib import Path

from milanon.adapters.parsers.xlsx_csv_parser import XlsxCsvParser
from milanon.domain.entities import DocumentFormat
from milanon.domain.protocols import DocumentParser

from .conftest import (
    FIXTURES_DIR,
    PISA_410_HEADERS,
    PISA_410_PERSON_ROW,
)


class TestXlsxCsvParserProtocol:
    def test_implements_document_parser_protocol(self, xlsx_csv_parser: XlsxCsvParser):
        assert isinstance(xlsx_csv_parser, DocumentParser)

    def test_supported_extensions_includes_xlsx(self, xlsx_csv_parser: XlsxCsvParser):
        assert ".xlsx" in xlsx_csv_parser.supported_extensions()

    def test_supported_extensions_includes_csv(self, xlsx_csv_parser: XlsxCsvParser):
        assert ".csv" in xlsx_csv_parser.supported_extensions()

    def test_parse_xlsx_returns_xlsx_format(
        self, xlsx_csv_parser: XlsxCsvParser, simple_xlsx_path: Path
    ):
        doc = xlsx_csv_parser.parse(simple_xlsx_path)
        assert doc.format == DocumentFormat.XLSX

    def test_parse_csv_returns_csv_format(
        self, xlsx_csv_parser: XlsxCsvParser, semicolon_csv_path: Path
    ):
        doc = xlsx_csv_parser.parse(semicolon_csv_path)
        assert doc.format == DocumentFormat.CSV

    def test_parse_xlsx_sets_source_path(
        self, xlsx_csv_parser: XlsxCsvParser, simple_xlsx_path: Path
    ):
        doc = xlsx_csv_parser.parse(simple_xlsx_path)
        assert "simple.xlsx" in doc.source_path

    def test_parse_sample_fixture(self, xlsx_csv_parser: XlsxCsvParser):
        """Smoke-test against the committed sample.csv fixture."""
        path = FIXTURES_DIR / "sample.csv"
        doc = xlsx_csv_parser.parse(path)
        assert doc.format == DocumentFormat.CSV
        assert len(doc.text_content) > 0


class TestXlsxParserSingleSheet:
    def test_header_row_extracted(
        self, xlsx_csv_parser: XlsxCsvParser, simple_xlsx_path: Path
    ):
        doc = xlsx_csv_parser.parse(simple_xlsx_path)
        assert "Name" in doc.text_content
        assert "Grad" in doc.text_content
        assert "Einheit" in doc.text_content

    def test_data_rows_extracted(
        self, xlsx_csv_parser: XlsxCsvParser, simple_xlsx_path: Path
    ):
        doc = xlsx_csv_parser.parse(simple_xlsx_path)
        assert "Hans Muster" in doc.text_content
        assert "Hptm" in doc.text_content

    def test_structured_content_has_tables(
        self, xlsx_csv_parser: XlsxCsvParser, simple_xlsx_path: Path
    ):
        doc = xlsx_csv_parser.parse(simple_xlsx_path)
        assert doc.structured_content is not None
        assert "tables" in doc.structured_content
        assert len(doc.structured_content["tables"]) == 1

    def test_structured_content_header_row(
        self, xlsx_csv_parser: XlsxCsvParser, simple_xlsx_path: Path
    ):
        doc = xlsx_csv_parser.parse(simple_xlsx_path)
        table = doc.structured_content["tables"][0]
        assert table[0] == ["Name", "Grad", "Einheit"]

    def test_structured_content_data_row(
        self, xlsx_csv_parser: XlsxCsvParser, simple_xlsx_path: Path
    ):
        doc = xlsx_csv_parser.parse(simple_xlsx_path)
        table = doc.structured_content["tables"][0]
        assert table[1] == ["Hans Muster", "Hptm", "Inf Kp 56/1"]

    def test_metadata_sheet_count(
        self, xlsx_csv_parser: XlsxCsvParser, simple_xlsx_path: Path
    ):
        doc = xlsx_csv_parser.parse(simple_xlsx_path)
        assert doc.metadata.get("sheet_count") == "1"


class TestXlsxParserMultiSheet:
    def test_two_sheets_detected(
        self, xlsx_csv_parser: XlsxCsvParser, multi_sheet_xlsx_path: Path
    ):
        doc = xlsx_csv_parser.parse(multi_sheet_xlsx_path)
        assert doc.metadata.get("sheet_count") == "2"

    def test_content_from_both_sheets_present(
        self, xlsx_csv_parser: XlsxCsvParser, multi_sheet_xlsx_path: Path
    ):
        doc = xlsx_csv_parser.parse(multi_sheet_xlsx_path)
        assert "Offiziere" in doc.text_content
        assert "Unteroffiziere" in doc.text_content

    def test_multi_sheet_separator_in_text(
        self, xlsx_csv_parser: XlsxCsvParser, multi_sheet_xlsx_path: Path
    ):
        doc = xlsx_csv_parser.parse(multi_sheet_xlsx_path)
        assert "\n\n---\n\n" in doc.text_content

    def test_structured_content_has_two_tables(
        self, xlsx_csv_parser: XlsxCsvParser, multi_sheet_xlsx_path: Path
    ):
        doc = xlsx_csv_parser.parse(multi_sheet_xlsx_path)
        assert doc.structured_content is not None
        assert len(doc.structured_content["tables"]) == 2

    def test_sheet_names_in_metadata(
        self, xlsx_csv_parser: XlsxCsvParser, multi_sheet_xlsx_path: Path
    ):
        doc = xlsx_csv_parser.parse(multi_sheet_xlsx_path)
        assert "Offiziere" in doc.metadata.get("sheet_names", "")
        assert "Unteroffiziere" in doc.metadata.get("sheet_names", "")


class TestXlsxParserPisa410:
    def test_title_row_skipped(
        self, xlsx_csv_parser: XlsxCsvParser, pisa_410_xlsx_path: Path
    ):
        doc = xlsx_csv_parser.parse(pisa_410_xlsx_path)
        # The title cell content must NOT appear as a header or data value
        assert "PISA Standardliste 410" not in doc.text_content

    def test_header_row_is_pisa_columns(
        self, xlsx_csv_parser: XlsxCsvParser, pisa_410_xlsx_path: Path
    ):
        doc = xlsx_csv_parser.parse(pisa_410_xlsx_path)
        table = doc.structured_content["tables"][0]
        assert table[0] == PISA_410_HEADERS

    def test_data_row_extracted(
        self, xlsx_csv_parser: XlsxCsvParser, pisa_410_xlsx_path: Path
    ):
        doc = xlsx_csv_parser.parse(pisa_410_xlsx_path)
        assert "Fischer" in doc.text_content
        assert "756.1234.5678.97" in doc.text_content

    def test_pisa_data_row_values(
        self, xlsx_csv_parser: XlsxCsvParser, pisa_410_xlsx_path: Path
    ):
        doc = xlsx_csv_parser.parse(pisa_410_xlsx_path)
        table = doc.structured_content["tables"][0]
        assert table[1] == PISA_410_PERSON_ROW


class TestCsvParserDelimiter:
    def test_semicolon_csv_parsed(
        self, xlsx_csv_parser: XlsxCsvParser, semicolon_csv_path: Path
    ):
        doc = xlsx_csv_parser.parse(semicolon_csv_path)
        assert "Hans Muster" in doc.text_content
        assert "Hptm" in doc.text_content

    def test_comma_csv_parsed(
        self, xlsx_csv_parser: XlsxCsvParser, comma_csv_path: Path
    ):
        doc = xlsx_csv_parser.parse(comma_csv_path)
        assert "Peter Meier" in doc.text_content
        assert "Lt" in doc.text_content

    def test_semicolon_structured_content(
        self, xlsx_csv_parser: XlsxCsvParser, semicolon_csv_path: Path
    ):
        doc = xlsx_csv_parser.parse(semicolon_csv_path)
        assert doc.structured_content is not None
        table = doc.structured_content["tables"][0]
        assert table[0] == ["Name", "Grad", "Einheit"]

    def test_csv_row_count_in_metadata(
        self, xlsx_csv_parser: XlsxCsvParser, semicolon_csv_path: Path
    ):
        doc = xlsx_csv_parser.parse(semicolon_csv_path)
        # header + 2 data rows = 3
        assert doc.metadata.get("row_count") == "3"

    def test_pipe_separator_in_text(
        self, xlsx_csv_parser: XlsxCsvParser, semicolon_csv_path: Path
    ):
        doc = xlsx_csv_parser.parse(semicolon_csv_path)
        assert " | " in doc.text_content


class TestCsvParserPisa410:
    def test_pisa_csv_title_row_skipped(
        self, xlsx_csv_parser: XlsxCsvParser, pisa_410_csv_path: Path
    ):
        doc = xlsx_csv_parser.parse(pisa_410_csv_path)
        assert "PISA Standardliste 410" not in doc.text_content

    def test_pisa_csv_header_present(
        self, xlsx_csv_parser: XlsxCsvParser, pisa_410_csv_path: Path
    ):
        doc = xlsx_csv_parser.parse(pisa_410_csv_path)
        assert "Versicherten Nr" in doc.text_content

    def test_pisa_csv_data_present(
        self, xlsx_csv_parser: XlsxCsvParser, pisa_410_csv_path: Path
    ):
        doc = xlsx_csv_parser.parse(pisa_410_csv_path)
        assert "Fischer" in doc.text_content
