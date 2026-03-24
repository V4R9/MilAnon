"""Tests for MappingService — business logic for entity-to-placeholder mapping."""

import pytest

from milanon.adapters.repositories.sqlite_repository import SqliteMappingRepository
from milanon.domain.entities import EntityType
from milanon.domain.mapping_service import MappingService


@pytest.fixture
def repository() -> SqliteMappingRepository:
    """In-memory SQLite repository for testing."""
    return SqliteMappingRepository(":memory:")


@pytest.fixture
def service(repository: SqliteMappingRepository) -> MappingService:
    """MappingService wired to an in-memory repository."""
    return MappingService(repository)


class TestGetOrCreatePlaceholder:
    def test_creates_new_placeholder_for_unknown_entity(self, service: MappingService):
        placeholder = service.get_or_create_placeholder(
            EntityType.PERSON, "Hans Muster", "test.eml"
        )
        assert placeholder == "[PERSON_001]"

    def test_returns_existing_placeholder_for_known_entity(self, service: MappingService):
        first = service.get_or_create_placeholder(EntityType.PERSON, "Hans Muster")
        second = service.get_or_create_placeholder(EntityType.PERSON, "Hans Muster")
        assert first == second == "[PERSON_001]"

    def test_case_insensitive_matching(self, service: MappingService):
        first = service.get_or_create_placeholder(EntityType.PERSON, "Hans Muster")
        second = service.get_or_create_placeholder(EntityType.PERSON, "hans muster")
        assert first == second

    def test_increments_placeholder_number(self, service: MappingService):
        p1 = service.get_or_create_placeholder(EntityType.ORT, "Bern")
        p2 = service.get_or_create_placeholder(EntityType.ORT, "Zürich")
        p3 = service.get_or_create_placeholder(EntityType.ORT, "Basel")
        assert p1 == "[ORT_001]"
        assert p2 == "[ORT_002]"
        assert p3 == "[ORT_003]"

    def test_different_types_have_independent_counters(self, service: MappingService):
        p_person = service.get_or_create_placeholder(EntityType.PERSON, "Hans Muster")
        p_ort = service.get_or_create_placeholder(EntityType.ORT, "Bern")
        assert p_person == "[PERSON_001]"
        assert p_ort == "[ORT_001]"

    def test_whitespace_trimming_in_matching(self, service: MappingService):
        first = service.get_or_create_placeholder(EntityType.PERSON, "Hans Muster")
        second = service.get_or_create_placeholder(EntityType.PERSON, "  Hans Muster  ")
        assert first == second

    def test_mapping_service_normalizes_internal_whitespace(self, service: MappingService):
        # Newline inside value (PDF line-break) must map to same placeholder as space version
        first = service.get_or_create_placeholder(EntityType.EINHEIT, "Inf Bat 56")
        second = service.get_or_create_placeholder(EntityType.EINHEIT, "Inf\nBat 56")
        assert first == second

    def test_duplicate_einheit_not_created(self, service: MappingService):
        # Multiple-space variant must not produce a second mapping
        first = service.get_or_create_placeholder(EntityType.EINHEIT, "Inf Bat 56")
        second = service.get_or_create_placeholder(EntityType.EINHEIT, "Inf  Bat  56")
        assert first == second


class TestResolvePlaceholder:
    def test_resolve_existing_placeholder(self, service: MappingService):
        service.get_or_create_placeholder(EntityType.PERSON, "Hans Muster")
        result = service.resolve_placeholder("[PERSON_001]")
        assert result == "Hans Muster"

    def test_resolve_unknown_placeholder_returns_none(self, service: MappingService):
        result = service.resolve_placeholder("[PERSON_999]")
        assert result is None

    def test_resolve_after_multiple_creations(self, service: MappingService):
        service.get_or_create_placeholder(EntityType.ORT, "Bern")
        service.get_or_create_placeholder(EntityType.ORT, "Zürich")
        assert service.resolve_placeholder("[ORT_001]") == "Bern"
        assert service.resolve_placeholder("[ORT_002]") == "Zürich"


class TestGetStatistics:
    def test_empty_statistics(self, service: MappingService):
        stats = service.get_statistics()
        assert stats == {"total": 0, "by_type": {}}

    def test_statistics_after_creating_mappings(self, service: MappingService):
        service.get_or_create_placeholder(EntityType.PERSON, "Hans Muster")
        service.get_or_create_placeholder(EntityType.PERSON, "Peter Meier")
        service.get_or_create_placeholder(EntityType.ORT, "Bern")
        service.get_or_create_placeholder(EntityType.AHV_NR, "756.1234.5678.97")

        stats = service.get_statistics()
        assert stats["total"] == 4
        assert stats["by_type"]["PERSON"] == 2
        assert stats["by_type"]["ORT"] == 1
        assert stats["by_type"]["AHV_NR"] == 1

    def test_statistics_no_duplicates(self, service: MappingService):
        service.get_or_create_placeholder(EntityType.PERSON, "Hans Muster")
        service.get_or_create_placeholder(EntityType.PERSON, "Hans Muster")
        stats = service.get_statistics()
        assert stats["total"] == 1
