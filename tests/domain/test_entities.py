"""Tests for domain entities — creation, validation, and properties."""

from datetime import datetime

import pytest

from milanon.domain.entities import (
    AnonymizedDocument,
    DetectedEntity,
    DocumentFormat,
    EntityMapping,
    EntityType,
    ExtractedDocument,
)


# --- EntityType ---


class TestEntityType:
    def test_all_entity_types_defined(self):
        expected = {
            "PERSON", "VORNAME", "NACHNAME", "EMAIL", "TELEFON",
            "AHV_NR", "GEBURTSDATUM", "ORT", "ADRESSE", "ARBEITGEBER",
            "EINHEIT", "FUNKTION", "GRAD_FUNKTION", "MEDIZINISCH",
            "FAMILIAER", "STANDORT_MIL",
        }
        actual = {e.value for e in EntityType}
        assert actual == expected

    def test_entity_type_value_matches_name(self):
        for entity_type in EntityType:
            assert entity_type.value == entity_type.name


# --- DocumentFormat ---


class TestDocumentFormat:
    def test_all_formats_defined(self):
        expected = {"EML", "DOCX", "PDF", "XLSX", "CSV", "MARKDOWN"}
        actual = {f.value for f in DocumentFormat}
        assert actual == expected


# --- DetectedEntity ---


class TestDetectedEntity:
    def test_create_valid_entity(self):
        entity = DetectedEntity(
            entity_type=EntityType.PERSON,
            original_value="Hans Muster",
            start_offset=0,
            end_offset=11,
            confidence=0.95,
            source="pattern",
        )
        assert entity.entity_type == EntityType.PERSON
        assert entity.original_value == "Hans Muster"
        assert entity.span_length == 11

    def test_create_entity_with_defaults(self):
        entity = DetectedEntity(
            entity_type=EntityType.EMAIL,
            original_value="test@example.com",
            start_offset=10,
            end_offset=26,
        )
        assert entity.confidence == 1.0
        assert entity.source == "unknown"

    def test_create_entity_empty_value_raises(self):
        with pytest.raises(ValueError, match="original_value must not be empty"):
            DetectedEntity(
                entity_type=EntityType.PERSON,
                original_value="",
                start_offset=0,
                end_offset=5,
            )

    def test_create_entity_negative_start_raises(self):
        with pytest.raises(ValueError, match="start_offset must be non-negative"):
            DetectedEntity(
                entity_type=EntityType.PERSON,
                original_value="Test",
                start_offset=-1,
                end_offset=4,
            )

    def test_create_entity_end_not_greater_than_start_raises(self):
        with pytest.raises(ValueError, match="end_offset must be greater than start_offset"):
            DetectedEntity(
                entity_type=EntityType.PERSON,
                original_value="Test",
                start_offset=5,
                end_offset=5,
            )

    def test_create_entity_confidence_out_of_range_raises(self):
        with pytest.raises(ValueError, match="confidence must be between"):
            DetectedEntity(
                entity_type=EntityType.PERSON,
                original_value="Test",
                start_offset=0,
                end_offset=4,
                confidence=1.5,
            )

    def test_entity_is_frozen(self):
        entity = DetectedEntity(
            entity_type=EntityType.ORT,
            original_value="Bern",
            start_offset=0,
            end_offset=4,
        )
        with pytest.raises(AttributeError):
            entity.original_value = "Zürich"

    def test_span_length(self):
        entity = DetectedEntity(
            entity_type=EntityType.AHV_NR,
            original_value="756.1234.5678.97",
            start_offset=10,
            end_offset=27,
        )
        assert entity.span_length == 17


# --- EntityMapping ---


class TestEntityMapping:
    def test_create_valid_mapping(self):
        mapping = EntityMapping(
            entity_type=EntityType.PERSON,
            original_value="Hans Muster",
            placeholder="[PERSON_001]",
            source_document="test.eml",
        )
        assert mapping.entity_type == EntityType.PERSON
        assert mapping.placeholder == "[PERSON_001]"
        assert isinstance(mapping.first_seen, datetime)

    def test_create_mapping_empty_value_raises(self):
        with pytest.raises(ValueError, match="original_value must not be empty"):
            EntityMapping(
                entity_type=EntityType.PERSON,
                original_value="",
                placeholder="[PERSON_001]",
            )

    def test_create_mapping_empty_placeholder_raises(self):
        with pytest.raises(ValueError, match="placeholder must not be empty"):
            EntityMapping(
                entity_type=EntityType.PERSON,
                original_value="Hans Muster",
                placeholder="",
            )

    def test_mapping_is_mutable(self):
        mapping = EntityMapping(
            entity_type=EntityType.ORT,
            original_value="Bern",
            placeholder="[ORT_001]",
        )
        new_time = datetime(2026, 1, 1)
        mapping.last_seen = new_time
        assert mapping.last_seen == new_time


# --- ExtractedDocument ---


class TestExtractedDocument:
    def test_create_valid_document(self):
        doc = ExtractedDocument(
            source_path="/path/to/file.eml",
            format=DocumentFormat.EML,
            text_content="Hello World",
        )
        assert doc.source_path == "/path/to/file.eml"
        assert doc.format == DocumentFormat.EML
        assert doc.text_content == "Hello World"
        assert doc.structured_content is None
        assert doc.metadata == {}
        assert doc.embedded_image_count == 0

    def test_create_document_empty_path_raises(self):
        with pytest.raises(ValueError, match="source_path must not be empty"):
            ExtractedDocument(
                source_path="",
                format=DocumentFormat.PDF,
                text_content="content",
            )

    def test_create_document_with_structured_content(self):
        structured = {"sheets": [{"name": "Sheet1", "rows": [["A", "B"]]}]}
        doc = ExtractedDocument(
            source_path="data.xlsx",
            format=DocumentFormat.XLSX,
            text_content="A\tB",
            structured_content=structured,
        )
        assert doc.structured_content == structured

    def test_create_document_with_metadata(self):
        doc = ExtractedDocument(
            source_path="report.pdf",
            format=DocumentFormat.PDF,
            text_content="Report content",
            metadata={"author": "Test", "pages": 3},
            embedded_image_count=2,
        )
        assert doc.metadata["author"] == "Test"
        assert doc.embedded_image_count == 2


# --- AnonymizedDocument ---


class TestAnonymizedDocument:
    def test_create_valid_anonymized_document(self):
        doc = AnonymizedDocument(
            source_path="input.eml",
            output_format=DocumentFormat.MARKDOWN,
            content="[PERSON_001] wrote an email.",
        )
        assert doc.source_path == "input.eml"
        assert doc.content == "[PERSON_001] wrote an email."
        assert doc.entities_found == []
        assert doc.legend == ""
        assert doc.warnings == []

    def test_create_anonymized_document_with_entities(self):
        entity = DetectedEntity(
            entity_type=EntityType.PERSON,
            original_value="Hans Muster",
            start_offset=0,
            end_offset=11,
        )
        doc = AnonymizedDocument(
            source_path="input.eml",
            output_format=DocumentFormat.MARKDOWN,
            content="[PERSON_001] wrote an email.",
            entities_found=[entity],
            legend="PERSON_001 = Person\n",
            warnings=["1 embedded image skipped"],
        )
        assert len(doc.entities_found) == 1
        assert doc.warnings == ["1 embedded image skipped"]
