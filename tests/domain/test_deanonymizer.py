"""Tests for DeAnonymizer — placeholder restoration and warnings."""

from __future__ import annotations

import pytest

from milanon.adapters.repositories.sqlite_repository import SqliteMappingRepository
from milanon.domain.deanonymizer import DeAnonymizer
from milanon.domain.entities import EntityType
from milanon.domain.mapping_service import MappingService


@pytest.fixture
def service() -> MappingService:
    repo = SqliteMappingRepository(":memory:")
    return MappingService(repo)


@pytest.fixture
def deanonymizer(service) -> DeAnonymizer:
    return DeAnonymizer(service)


def _seed(service: MappingService, entity_type: EntityType, value: str) -> str:
    """Create a mapping and return its placeholder."""
    return service.get_or_create_placeholder(entity_type, value)


class TestDeanonymizerBasic:
    def test_single_placeholder_resolved(self, service, deanonymizer):
        ph = _seed(service, EntityType.PERSON, "Marco BERNASCONI")
        text = f"Kommandant: {ph}"
        restored, warnings = deanonymizer.deanonymize(text)
        assert "Marco BERNASCONI" in restored
        assert warnings == []

    def test_placeholder_removed_from_text(self, service, deanonymizer):
        ph = _seed(service, EntityType.PERSON, "Marco BERNASCONI")
        restored, _ = deanonymizer.deanonymize(f"Name: {ph}")
        assert ph not in restored

    def test_multiple_placeholders_resolved(self, service, deanonymizer):
        ph1 = _seed(service, EntityType.PERSON, "Marco BERNASCONI")
        ph2 = _seed(service, EntityType.AHV_NR, "756.1234.5678.97")
        text = f"Name: {ph1}, AHV: {ph2}"
        restored, warnings = deanonymizer.deanonymize(text)
        assert "Marco BERNASCONI" in restored
        assert "756.1234.5678.97" in restored
        assert warnings == []

    def test_same_placeholder_twice_both_resolved(self, service, deanonymizer):
        ph = _seed(service, EntityType.PERSON, "BERNASCONI")
        text = f"{ph} und {ph}"
        restored, _ = deanonymizer.deanonymize(text)
        assert restored == "BERNASCONI und BERNASCONI"

    def test_plain_text_unchanged(self, deanonymizer):
        text = "Kein Platzhalter hier."
        restored, warnings = deanonymizer.deanonymize(text)
        assert restored == text
        assert warnings == []


class TestDeanonymizerWarnings:
    def test_unresolved_placeholder_produces_warning(self, deanonymizer):
        _, warnings = deanonymizer.deanonymize("[PERSON_999]")
        assert len(warnings) == 1
        assert "PERSON_999" in warnings[0]

    def test_unresolved_placeholder_left_in_text(self, deanonymizer):
        restored, _ = deanonymizer.deanonymize("[PERSON_999]")
        assert "[PERSON_999]" in restored

    def test_mixed_resolved_and_unresolved(self, service, deanonymizer):
        ph = _seed(service, EntityType.PERSON, "MUSTER")
        text = f"{ph} und [PERSON_999]"
        restored, warnings = deanonymizer.deanonymize(text)
        assert "MUSTER" in restored
        assert "[PERSON_999]" in restored
        assert len(warnings) == 1

    def test_multiple_unresolved_each_produces_warning(self, deanonymizer):
        _, warnings = deanonymizer.deanonymize("[PERSON_001] [AHV_NR_001]")
        assert len(warnings) == 2


class TestLegendStripping:
    def test_legend_block_stripped_before_restoration(self, service, deanonymizer):
        ph = _seed(service, EntityType.PERSON, "BERNASCONI")
        content = (
            "<!-- MILANON LEGEND START\n"
            f"{ph} = PERSON\n"
            "MILANON LEGEND END -->\n\n"
            f"Kommandant: {ph}"
        )
        restored, _ = deanonymizer.deanonymize(content)
        assert "MILANON LEGEND" not in restored
        assert "BERNASCONI" in restored

    def test_content_without_legend_works(self, service, deanonymizer):
        ph = _seed(service, EntityType.PERSON, "BERNASCONI")
        restored, warnings = deanonymizer.deanonymize(f"Name: {ph}")
        assert "BERNASCONI" in restored
        assert warnings == []


class TestFindPlaceholders:
    def test_finds_all_placeholders(self, deanonymizer):
        text = "[PERSON_001] und [AHV_NR_002] und [EINHEIT_003]"
        found = deanonymizer.find_placeholders(text)
        assert found == ["[PERSON_001]", "[AHV_NR_002]", "[EINHEIT_003]"]

    def test_returns_empty_for_no_placeholders(self, deanonymizer):
        assert deanonymizer.find_placeholders("normaler Text") == []

    def test_duplicate_placeholders_counted(self, deanonymizer):
        text = "[PERSON_001] [PERSON_001]"
        found = deanonymizer.find_placeholders(text)
        assert len(found) == 2
