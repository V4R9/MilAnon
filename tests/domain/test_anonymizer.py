"""Tests for Anonymizer — placeholder replacement and legend generation."""

from __future__ import annotations

import pytest

from milanon.adapters.repositories.sqlite_repository import SqliteMappingRepository
from milanon.domain.anonymizer import Anonymizer
from milanon.domain.entities import (
    DetectedEntity,
    DocumentFormat,
    EntityType,
    ExtractedDocument,
)
from milanon.domain.mapping_service import MappingService


def _doc(text: str) -> ExtractedDocument:
    return ExtractedDocument(
        source_path="test.txt",
        format=DocumentFormat.MARKDOWN,
        text_content=text,
    )


def _entity(entity_type, value, start, end):
    return DetectedEntity(
        entity_type=entity_type,
        original_value=value,
        start_offset=start,
        end_offset=end,
    )


@pytest.fixture
def service() -> MappingService:
    return MappingService(SqliteMappingRepository(":memory:"))


@pytest.fixture
def anonymizer(service) -> Anonymizer:
    return Anonymizer(service)


class TestAnonymizerBasic:
    def test_no_entities_returns_original_text(self, anonymizer):
        doc = _doc("Kein PII hier.")
        result = anonymizer.anonymize(doc, [])
        assert result.content == "Kein PII hier."

    def test_single_entity_replaced(self, anonymizer):
        doc = _doc("Name: Marco BERNASCONI")
        entity = _entity(EntityType.PERSON, "Marco BERNASCONI", 6, 22)
        result = anonymizer.anonymize(doc, [entity])
        assert "Marco BERNASCONI" not in result.content
        assert "[PERSON_001]" in result.content

    def test_placeholder_format_correct(self, anonymizer):
        doc = _doc("756.1234.5678.97")
        entity = _entity(EntityType.AHV_NR, "756.1234.5678.97", 0, 16)
        result = anonymizer.anonymize(doc, [entity])
        assert "[AHV_NR_001]" in result.content

    def test_multiple_entities_all_replaced(self, anonymizer):
        text = "AHV: 756.1234.5678.97, Name: Marco BERNASCONI"
        entities = [
            _entity(EntityType.AHV_NR, "756.1234.5678.97", 5, 21),
            _entity(EntityType.PERSON, "Marco BERNASCONI", 29, 45),
        ]
        result = anonymizer.anonymize(_doc(text), entities)
        assert "756.1234.5678.97" not in result.content
        assert "Marco BERNASCONI" not in result.content
        assert "[AHV_NR_001]" in result.content
        assert "[PERSON_001]" in result.content

    def test_same_entity_same_placeholder(self, anonymizer):
        text = "BERNASCONI hier und auch BERNASCONI dort"
        entities = [
            _entity(EntityType.PERSON, "BERNASCONI", 0, 10),
            _entity(EntityType.PERSON, "BERNASCONI", 25, 35),
        ]
        result = anonymizer.anonymize(_doc(text), entities)
        # Body text (after legend) must have exactly 2 occurrences
        body = result.content.split("MILANON LEGEND END -->")[-1]
        assert body.count("[PERSON_001]") == 2
        assert "[PERSON_002]" not in result.content

    def test_source_path_preserved(self, anonymizer):
        doc = ExtractedDocument(
            source_path="/data/order.pdf",
            format=DocumentFormat.PDF,
            text_content="text",
        )
        result = anonymizer.anonymize(doc, [])
        assert result.source_path == "/data/order.pdf"

    def test_entities_found_list_populated(self, anonymizer):
        doc = _doc("Marco BERNASCONI")
        entity = _entity(EntityType.PERSON, "Marco BERNASCONI", 0, 16)
        result = anonymizer.anonymize(doc, [entity])
        assert len(result.entities_found) == 1

    def test_no_warnings_on_success(self, anonymizer):
        doc = _doc("756.1234.5678.97")
        entity = _entity(EntityType.AHV_NR, "756.1234.5678.97", 0, 16)
        result = anonymizer.anonymize(doc, [entity])
        assert result.warnings == []


class TestAnonymizerLegend:
    def test_legend_included_in_content(self, anonymizer):
        doc = _doc("Marco BERNASCONI")
        entity = _entity(EntityType.PERSON, "Marco BERNASCONI", 0, 16)
        result = anonymizer.anonymize(doc, [entity])
        assert "MILANON LEGEND START" in result.content
        assert "PERSON_001" in result.content

    def test_legend_not_included_for_no_entities(self, anonymizer):
        result = anonymizer.anonymize(_doc("Text"), [])
        assert "MILANON LEGEND" not in result.content

    def test_legend_has_entity_type_label(self, anonymizer):
        doc = _doc("756.1234.5678.97")
        entity = _entity(EntityType.AHV_NR, "756.1234.5678.97", 0, 16)
        result = anonymizer.anonymize(doc, [entity])
        assert "AHV_NR" in result.legend

    def test_legend_field_separate_from_content(self, anonymizer):
        doc = _doc("Marco BERNASCONI")
        entity = _entity(EntityType.PERSON, "Marco BERNASCONI", 0, 16)
        result = anonymizer.anonymize(doc, [entity])
        assert "[PERSON_001] = PERSON" in result.legend

    def test_multiple_types_in_legend(self, anonymizer):
        text = "AHV: 756.1234.5678.97 Name: BERNASCONI"
        entities = [
            _entity(EntityType.AHV_NR, "756.1234.5678.97", 5, 21),
            _entity(EntityType.PERSON, "BERNASCONI", 28, 38),
        ]
        result = anonymizer.anonymize(_doc(text), entities)
        assert "AHV_NR" in result.legend
        assert "PERSON" in result.legend


class TestAnonymizerConsistency:
    def test_counter_increments_across_calls(self, anonymizer):
        doc1 = _doc("BERNASCONI")
        doc2 = _doc("MUSTER")
        e1 = _entity(EntityType.PERSON, "BERNASCONI", 0, 10)
        e2 = _entity(EntityType.PERSON, "MUSTER", 0, 6)
        r1 = anonymizer.anonymize(doc1, [e1])
        r2 = anonymizer.anonymize(doc2, [e2])
        assert "[PERSON_001]" in r1.content
        assert "[PERSON_002]" in r2.content

    def test_existing_mapping_reused(self, anonymizer):
        doc = _doc("BERNASCONI")
        entity = _entity(EntityType.PERSON, "BERNASCONI", 0, 10)
        r1 = anonymizer.anonymize(doc, [entity])
        r2 = anonymizer.anonymize(doc, [entity])
        # Same value → same placeholder in both runs
        assert "[PERSON_001]" in r1.content
        assert "[PERSON_001]" in r2.content
