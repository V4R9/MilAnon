"""Tests for the parser registry — auto-selection by file extension."""

from pathlib import Path

import pytest

from milanon.adapters.parsers import get_parser
from milanon.adapters.parsers.docx_parser import DocxParser
from milanon.adapters.parsers.eml_parser import EmlParser
from milanon.adapters.parsers.pdf_parser import PdfParser
from milanon.adapters.parsers.xlsx_csv_parser import XlsxCsvParser


class TestGetParserByExtension:
    def test_eml_returns_eml_parser(self):
        assert isinstance(get_parser(Path("test.eml")), EmlParser)

    def test_docx_returns_docx_parser(self):
        assert isinstance(get_parser(Path("test.docx")), DocxParser)

    def test_pdf_returns_pdf_parser(self):
        assert isinstance(get_parser(Path("test.pdf")), PdfParser)

    def test_xlsx_returns_xlsx_csv_parser(self):
        assert isinstance(get_parser(Path("test.xlsx")), XlsxCsvParser)

    def test_csv_returns_xlsx_csv_parser(self):
        assert isinstance(get_parser(Path("test.csv")), XlsxCsvParser)

    def test_unknown_extension_raises_value_error(self):
        with pytest.raises(ValueError, match="No parser available"):
            get_parser(Path("test.unknown"))

    def test_error_message_lists_supported_extensions(self):
        with pytest.raises(ValueError, match=r"\.(pdf|docx|eml|csv|xlsx)"):
            get_parser(Path("test.xyz"))

    def test_extension_case_insensitive_pdf(self):
        assert isinstance(get_parser(Path("DOCUMENT.PDF")), PdfParser)

    def test_extension_case_insensitive_docx(self):
        assert isinstance(get_parser(Path("report.DOCX")), DocxParser)

    def test_full_path_works(self):
        assert isinstance(get_parser(Path("/data/classified/order.docx")), DocxParser)

    def test_same_parser_instance_returned(self):
        """Registry returns the same singleton parser instance."""
        parser_a = get_parser(Path("a.pdf"))
        parser_b = get_parser(Path("b.pdf"))
        assert parser_a is parser_b
