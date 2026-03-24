"""Tests for SqliteMappingRepository — CRUD, persistence, import."""

import pytest

from milanon.adapters.repositories.sqlite_repository import SqliteMappingRepository
from milanon.domain.entities import EntityMapping, EntityType
from milanon.domain.protocols import MappingRepository


@pytest.fixture
def repo() -> SqliteMappingRepository:
    """In-memory SQLite repository for testing."""
    return SqliteMappingRepository(":memory:")


class TestProtocolCompliance:
    def test_implements_mapping_repository_protocol(self, repo: SqliteMappingRepository):
        assert isinstance(repo, MappingRepository)


class TestSchemaCreation:
    def test_tables_created_on_init(self, repo: SqliteMappingRepository):
        tables = repo._conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ).fetchall()
        table_names = {row["name"] for row in tables}
        assert "entity_mappings" in table_names
        assert "entity_aliases" in table_names
        assert "ref_municipalities" in table_names
        assert "ref_military_units" in table_names
        assert "file_tracking" in table_names
        assert "processing_log" in table_names

    def test_indexes_created_on_init(self, repo: SqliteMappingRepository):
        indexes = repo._conn.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'"
        ).fetchall()
        index_names = {row["name"] for row in indexes}
        assert "idx_mappings_type_normalized" in index_names
        assert "idx_mappings_placeholder" in index_names
        assert "idx_aliases_normalized" in index_names


class TestCreateMapping:
    def test_create_first_mapping(self, repo: SqliteMappingRepository):
        mapping = repo.create_mapping(EntityType.PERSON, "Hans Muster", "test.eml")
        assert mapping.entity_type == EntityType.PERSON
        assert mapping.original_value == "Hans Muster"
        assert mapping.placeholder == "[PERSON_001]"
        assert mapping.source_document == "test.eml"

    def test_create_increments_counter(self, repo: SqliteMappingRepository):
        m1 = repo.create_mapping(EntityType.PERSON, "Hans Muster")
        m2 = repo.create_mapping(EntityType.PERSON, "Peter Meier")
        assert m1.placeholder == "[PERSON_001]"
        assert m2.placeholder == "[PERSON_002]"

    def test_create_independent_counters_per_type(self, repo: SqliteMappingRepository):
        m_person = repo.create_mapping(EntityType.PERSON, "Hans Muster")
        m_ort = repo.create_mapping(EntityType.ORT, "Bern")
        assert m_person.placeholder == "[PERSON_001]"
        assert m_ort.placeholder == "[ORT_001]"

    def test_create_duplicate_raises(self, repo: SqliteMappingRepository):
        repo.create_mapping(EntityType.PERSON, "Hans Muster")
        with pytest.raises(Exception):
            repo.create_mapping(EntityType.PERSON, "Hans Muster")


class TestGetMapping:
    def test_get_existing_mapping(self, repo: SqliteMappingRepository):
        repo.create_mapping(EntityType.PERSON, "Hans Muster")
        result = repo.get_mapping(EntityType.PERSON, "Hans Muster")
        assert result is not None
        assert result.placeholder == "[PERSON_001]"

    def test_get_mapping_case_insensitive(self, repo: SqliteMappingRepository):
        repo.create_mapping(EntityType.PERSON, "Hans Muster")
        result = repo.get_mapping(EntityType.PERSON, "hans muster")
        assert result is not None
        assert result.placeholder == "[PERSON_001]"

    def test_get_mapping_with_whitespace(self, repo: SqliteMappingRepository):
        repo.create_mapping(EntityType.PERSON, "Hans Muster")
        result = repo.get_mapping(EntityType.PERSON, "  Hans Muster  ")
        assert result is not None

    def test_get_nonexistent_mapping_returns_none(self, repo: SqliteMappingRepository):
        result = repo.get_mapping(EntityType.PERSON, "Nobody")
        assert result is None

    def test_get_mapping_wrong_type_returns_none(self, repo: SqliteMappingRepository):
        repo.create_mapping(EntityType.PERSON, "Bern")
        result = repo.get_mapping(EntityType.ORT, "Bern")
        assert result is None


class TestGetPlaceholder:
    def test_get_existing_placeholder(self, repo: SqliteMappingRepository):
        repo.create_mapping(EntityType.ORT, "Bern")
        result = repo.get_placeholder("[ORT_001]")
        assert result is not None
        assert result.original_value == "Bern"

    def test_get_nonexistent_placeholder_returns_none(self, repo: SqliteMappingRepository):
        result = repo.get_placeholder("[ORT_999]")
        assert result is None


class TestGetAllMappings:
    def test_empty_repository(self, repo: SqliteMappingRepository):
        assert repo.get_all_mappings() == []

    def test_returns_all_mappings(self, repo: SqliteMappingRepository):
        repo.create_mapping(EntityType.PERSON, "Hans Muster")
        repo.create_mapping(EntityType.ORT, "Bern")
        repo.create_mapping(EntityType.EMAIL, "test@example.com")
        mappings = repo.get_all_mappings()
        assert len(mappings) == 3
        assert all(isinstance(m, EntityMapping) for m in mappings)


class TestImportEntities:
    def test_import_new_entities(self, repo: SqliteMappingRepository):
        entities = [
            {"entity_type": "PERSON", "original_value": "Hans Muster"},
            {"entity_type": "ORT", "original_value": "Bern"},
        ]
        count = repo.import_entities(entities)
        assert count == 2
        assert repo.get_total_mapping_count() == 2

    def test_import_skips_duplicates(self, repo: SqliteMappingRepository):
        repo.create_mapping(EntityType.PERSON, "Hans Muster")
        entities = [
            {"entity_type": "PERSON", "original_value": "Hans Muster"},
            {"entity_type": "ORT", "original_value": "Bern"},
        ]
        count = repo.import_entities(entities)
        assert count == 1
        assert repo.get_total_mapping_count() == 2

    def test_import_empty_list(self, repo: SqliteMappingRepository):
        count = repo.import_entities([])
        assert count == 0


class TestMappingCounts:
    def test_total_count(self, repo: SqliteMappingRepository):
        assert repo.get_total_mapping_count() == 0
        repo.create_mapping(EntityType.PERSON, "Hans Muster")
        repo.create_mapping(EntityType.ORT, "Bern")
        assert repo.get_total_mapping_count() == 2

    def test_count_by_type(self, repo: SqliteMappingRepository):
        repo.create_mapping(EntityType.PERSON, "Hans Muster")
        repo.create_mapping(EntityType.PERSON, "Peter Meier")
        repo.create_mapping(EntityType.ORT, "Bern")
        counts = repo.get_mapping_count_by_type()
        assert counts["PERSON"] == 2
        assert counts["ORT"] == 1


class TestDatabaseReset:
    def test_reset_all_mappings_clears_mappings_and_tracking(self, repo: SqliteMappingRepository):
        repo.create_mapping(EntityType.PERSON, "Hans Muster")
        repo.upsert_file_tracking("doc.pdf", "abc123", "anonymize")
        counts = repo.reset_all_mappings()
        assert counts["entity_mappings"] == 1
        assert counts["file_tracking"] == 1
        assert repo.get_total_mapping_count() == 0

    def test_reset_all_mappings_preserves_ref_data(self, repo: SqliteMappingRepository):
        repo.import_municipalities(["Basel", "Bern"])
        repo.create_mapping(EntityType.PERSON, "Hans Muster")
        repo.reset_all_mappings()
        assert repo.get_ref_municipality_count() == 2

    def test_reset_everything_clears_all_tables(self, repo: SqliteMappingRepository):
        repo.create_mapping(EntityType.PERSON, "Hans Muster")
        repo.import_municipalities(["Basel"])
        counts = repo.reset_everything()
        assert repo.get_total_mapping_count() == 0
        assert repo.get_ref_municipality_count() == 0
        assert sum(counts.values()) > 0

    def test_reset_everything_allows_reinit(self, repo: SqliteMappingRepository):
        repo.import_municipalities(["Basel", "Bern", "Zürich"])
        repo.reset_everything()
        # After full reset, municipalities can be re-imported
        repo.import_municipalities(["Luzern"])
        assert repo.get_ref_municipality_count() == 1


class TestPersistence:
    def test_data_persists_to_file(self, tmp_path):
        db_path = tmp_path / "test.db"
        repo1 = SqliteMappingRepository(db_path)
        repo1.create_mapping(EntityType.PERSON, "Hans Muster")
        repo1.close()

        repo2 = SqliteMappingRepository(db_path)
        result = repo2.get_mapping(EntityType.PERSON, "Hans Muster")
        assert result is not None
        assert result.placeholder == "[PERSON_001]"
        repo2.close()

    def test_counter_persists_across_sessions(self, tmp_path):
        db_path = tmp_path / "test.db"
        repo1 = SqliteMappingRepository(db_path)
        repo1.create_mapping(EntityType.PERSON, "Hans Muster")
        repo1.close()

        repo2 = SqliteMappingRepository(db_path)
        m2 = repo2.create_mapping(EntityType.PERSON, "Peter Meier")
        assert m2.placeholder == "[PERSON_002]"
        repo2.close()
