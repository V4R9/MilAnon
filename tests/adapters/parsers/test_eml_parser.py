"""Tests for EmlParser — MIME decoding, header extraction, multipart, signatures."""

from pathlib import Path

import pytest

from milanon.adapters.parsers.eml_parser import EmlParser
from milanon.domain.entities import DocumentFormat
from milanon.domain.protocols import DocumentParser

from .conftest import SAMPLE_BASE64_BODY


class TestEmlParserProtocol:
    def test_implements_document_parser_protocol(self, eml_parser: EmlParser):
        assert isinstance(eml_parser, DocumentParser)

    def test_supported_extensions_includes_eml(self, eml_parser: EmlParser):
        assert ".eml" in eml_parser.supported_extensions()

    def test_parse_returns_extracted_document_with_eml_format(
        self, eml_parser: EmlParser, sample_eml_path: Path
    ):
        doc = eml_parser.parse(sample_eml_path)
        assert doc.format == DocumentFormat.EML

    def test_parse_sets_source_path(
        self, eml_parser: EmlParser, sample_eml_path: Path
    ):
        doc = eml_parser.parse(sample_eml_path)
        assert "sample.eml" in doc.source_path


class TestEmlParserHeaders:
    def test_extracts_from_header_into_metadata(
        self, eml_parser: EmlParser, sample_eml_path: Path
    ):
        doc = eml_parser.parse(sample_eml_path)
        assert "from" in doc.metadata
        assert "hans.muster@army.ch" in doc.metadata["from"]

    def test_extracts_to_header_into_metadata(
        self, eml_parser: EmlParser, sample_eml_path: Path
    ):
        doc = eml_parser.parse(sample_eml_path)
        assert "to" in doc.metadata
        assert "peter.meier@army.ch" in doc.metadata["to"]

    def test_extracts_subject_header_into_metadata(
        self, eml_parser: EmlParser, sample_eml_path: Path
    ):
        doc = eml_parser.parse(sample_eml_path)
        assert "subject" in doc.metadata
        assert "Inf Kp 56/1" in doc.metadata["subject"]

    def test_extracts_date_header_into_metadata(
        self, eml_parser: EmlParser, sample_eml_path: Path
    ):
        doc = eml_parser.parse(sample_eml_path)
        assert "date" in doc.metadata
        assert "2026" in doc.metadata["date"]

    def test_from_header_included_in_text_content(
        self, eml_parser: EmlParser, sample_eml_path: Path
    ):
        doc = eml_parser.parse(sample_eml_path)
        assert "hans.muster@army.ch" in doc.text_content

    def test_subject_header_included_in_text_content(
        self, eml_parser: EmlParser, sample_eml_path: Path
    ):
        doc = eml_parser.parse(sample_eml_path)
        assert "Inf Kp 56/1" in doc.text_content

    def test_headers_precede_body_in_text_content(
        self, eml_parser: EmlParser, sample_eml_path: Path
    ):
        doc = eml_parser.parse(sample_eml_path)
        from_pos = doc.text_content.find("From:")
        body_pos = doc.text_content.find("Sehr geehrter")
        assert from_pos < body_pos


class TestEmlParserQuotedPrintable:
    def test_qp_decodes_u_umlaut(
        self, eml_parser: EmlParser, sample_eml_path: Path
    ):
        doc = eml_parser.parse(sample_eml_path)
        # =C3=9C -> Ü  (in "Übung")
        assert "Ü" in doc.text_content

    def test_qp_decodes_lowercase_u_umlaut(
        self, eml_parser: EmlParser, sample_eml_path: Path
    ):
        doc = eml_parser.parse(sample_eml_path)
        # =C3=BC -> ü  (in "Grüssen")
        assert "ü" in doc.text_content

    def test_qp_body_text_fully_extracted(
        self, eml_parser: EmlParser, sample_eml_path: Path
    ):
        doc = eml_parser.parse(sample_eml_path)
        assert "Hptm Marco BERNASCONI" in doc.text_content
        assert "756.1234.5678.97" in doc.text_content


class TestEmlParserBase64:
    def test_base64_body_is_decoded(
        self, eml_parser: EmlParser, sample_base64_eml_path: Path
    ):
        doc = eml_parser.parse(sample_base64_eml_path)
        assert SAMPLE_BASE64_BODY in doc.text_content

    def test_base64_format_is_eml(
        self, eml_parser: EmlParser, sample_base64_eml_path: Path
    ):
        doc = eml_parser.parse(sample_base64_eml_path)
        assert doc.format == DocumentFormat.EML


class TestEmlParserMultipart:
    def test_multipart_alternative_prefers_plain_text(
        self, eml_parser: EmlParser, sample_multipart_eml_path: Path
    ):
        doc = eml_parser.parse(sample_multipart_eml_path)
        assert "Plaintext body content here." in doc.text_content

    def test_multipart_alternative_no_html_tags_in_output(
        self, eml_parser: EmlParser, sample_multipart_eml_path: Path
    ):
        doc = eml_parser.parse(sample_multipart_eml_path)
        assert "<html>" not in doc.text_content.lower()
        assert "<p>" not in doc.text_content.lower()

    def test_multipart_alternative_html_content_not_included(
        self, eml_parser: EmlParser, sample_multipart_eml_path: Path
    ):
        # When plain text part exists, HTML content should not be in text
        doc = eml_parser.parse(sample_multipart_eml_path)
        assert "HTML body content here." not in doc.text_content

    def test_multipart_mixed_body_extracted_attachment_skipped(
        self, eml_parser: EmlParser, sample_attachment_eml_path: Path
    ):
        doc = eml_parser.parse(sample_attachment_eml_path)
        assert "im Anhang" in doc.text_content
        # Raw PDF bytes should not appear in text
        assert "JVBERi" not in doc.text_content


class TestEmlParserSignature:
    def test_signature_phone_in_text_content(
        self, eml_parser: EmlParser, sample_signature_eml_path: Path
    ):
        doc = eml_parser.parse(sample_signature_eml_path)
        assert "079 535 80 46" in doc.text_content

    def test_signature_email_address_in_text_content(
        self, eml_parser: EmlParser, sample_signature_eml_path: Path
    ):
        doc = eml_parser.parse(sample_signature_eml_path)
        assert "hans.muster@army.ch" in doc.text_content

    def test_signature_street_address_in_text_content(
        self, eml_parser: EmlParser, sample_signature_eml_path: Path
    ):
        doc = eml_parser.parse(sample_signature_eml_path)
        assert "Hauptstrasse 42" in doc.text_content

    def test_signature_city_in_text_content(
        self, eml_parser: EmlParser, sample_signature_eml_path: Path
    ):
        doc = eml_parser.parse(sample_signature_eml_path)
        assert "St. Gallen" in doc.text_content

    def test_signature_rank_and_name_in_text_content(
        self, eml_parser: EmlParser, sample_signature_eml_path: Path
    ):
        doc = eml_parser.parse(sample_signature_eml_path)
        assert "Hptm Hans Muster" in doc.text_content


class TestDisplayNameExtraction:
    """B-022: Display names extracted from EML headers."""

    def test_display_name_from_from_header(self, tmp_path):
        eml = (
            "From: Thomas Müller <thomas@example.com>\r\n"
            "To: info@test.com\r\n"
            "Subject: Test\r\n"
            "Date: Mon, 1 Jan 2026 10:00:00 +0100\r\n"
            "\r\n"
            "Body text.\r\n"
        )
        eml_path = tmp_path / "test.eml"
        eml_path.write_bytes(eml.encode("utf-8"))

        from milanon.adapters.parsers.eml_parser import EmlParser
        doc = EmlParser().parse(eml_path)
        assert "display_names" in doc.metadata
        assert "Thomas Müller" in doc.metadata["display_names"]

    def test_multiple_display_names_in_to(self, tmp_path):
        eml = (
            "From: sender@test.com\r\n"
            "To: Hans Muster <hans@ex.com>, Anna Keller <anna@ex.com>\r\n"
            "Subject: Test\r\n"
            "Date: Mon, 1 Jan 2026 10:00:00 +0100\r\n"
            "\r\n"
            "Body.\r\n"
        )
        eml_path = tmp_path / "test.eml"
        eml_path.write_bytes(eml.encode("utf-8"))

        from milanon.adapters.parsers.eml_parser import EmlParser
        doc = EmlParser().parse(eml_path)
        names = doc.metadata.get("display_names", [])
        assert "Hans Muster" in names
        assert "Anna Keller" in names

    def test_no_display_name_when_email_only(self, tmp_path):
        eml = (
            "From: info@company.com\r\n"
            "To: test@test.com\r\n"
            "Subject: Test\r\n"
            "Date: Mon, 1 Jan 2026 10:00:00 +0100\r\n"
            "\r\n"
            "Body.\r\n"
        )
        eml_path = tmp_path / "test.eml"
        eml_path.write_bytes(eml.encode("utf-8"))

        from milanon.adapters.parsers.eml_parser import EmlParser
        doc = EmlParser().parse(eml_path)
        names = doc.metadata.get("display_names", [])
        assert len(names) == 0

    def test_single_word_name_excluded(self, tmp_path):
        """Single-word display names (likely companies) are excluded."""
        eml = (
            "From: Swisscom <info@swisscom.ch>\r\n"
            "To: test@test.com\r\n"
            "Subject: Test\r\n"
            "Date: Mon, 1 Jan 2026 10:00:00 +0100\r\n"
            "\r\n"
            "Body.\r\n"
        )
        eml_path = tmp_path / "test.eml"
        eml_path.write_bytes(eml.encode("utf-8"))

        from milanon.adapters.parsers.eml_parser import EmlParser
        doc = EmlParser().parse(eml_path)
        names = doc.metadata.get("display_names", [])
        assert "Swisscom" not in names
