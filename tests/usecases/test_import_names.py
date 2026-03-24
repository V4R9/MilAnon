"""Tests for ImportNamesUseCase — simple Grad;Vorname;Nachname CSV import."""

from __future__ import annotations

from pathlib import Path

import pytest

from milanon.adapters.repositories.sqlite_repository import SqliteMappingRepository
from milanon.domain.entities import EntityType
from milanon.domain.mapping_service import MappingService
from milanon.usecases.import_names import ImportNamesUseCase


@pytest.fixture
def repo() -> SqliteMappingRepository:
    return SqliteMappingRepository(":memory:")


@pytest.fixture
def service(repo) -> MappingService:
    return MappingService(repo)


@pytest.fixture
def use_case(service) -> ImportNamesUseCase:
    return ImportNamesUseCase(service)


def _csv(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "names.csv"
    p.write_text(content, encoding="utf-8")
    return p


class TestImportNamesBasic:
    def test_import_names_creates_person_vorname_nachname(self, use_case, repo, tmp_path):
        csv_path = _csv(tmp_path, "Grad;Vorname;Nachname\nHptm;Thomas;Wegmüller\n")
        use_case.execute(csv_path)
        assert repo.get_mapping(EntityType.PERSON, "Thomas WEGMÜLLER") is not None
        assert repo.get_mapping(EntityType.VORNAME, "Thomas") is not None
        assert repo.get_mapping(EntityType.NACHNAME, "Wegmüller") is not None

    def test_import_names_creates_grad_funktion(self, use_case, repo, tmp_path):
        csv_path = _csv(tmp_path, "Grad;Vorname;Nachname\nOberstlt i Gst;Simon;Kohler\n")
        use_case.execute(csv_path)
        assert repo.get_mapping(EntityType.GRAD_FUNKTION, "Oberstlt i Gst") is not None

    def test_import_names_skips_empty_rows(self, use_case, tmp_path):
        csv_path = _csv(tmp_path, "Grad;Vorname;Nachname\nHptm;Thomas;Wegmüller\n;;\n")
        result = use_case.execute(csv_path)
        assert result.rows_processed == 1
        assert result.rows_skipped == 1

    def test_import_names_no_duplicate_on_reimport(self, use_case, tmp_path):
        csv_path = _csv(tmp_path, "Grad;Vorname;Nachname\nHptm;Thomas;Wegmüller\n")
        r1 = use_case.execute(csv_path)
        r2 = use_case.execute(csv_path)
        assert r1.entities_imported > 0
        assert r2.entities_imported == 0

    def test_import_names_without_grad_column(self, use_case, repo, tmp_path):
        csv_path = _csv(tmp_path, "Vorname;Nachname\nSimon;Kohler\n")
        use_case.execute(csv_path)
        assert repo.get_mapping(EntityType.PERSON, "Simon KOHLER") is not None
        assert repo.get_mapping(EntityType.GRAD_FUNKTION, "") is None

    def test_import_names_nachname_uppercased_in_person(self, use_case, repo, tmp_path):
        csv_path = _csv(tmp_path, "Grad;Vorname;Nachname\nMaj;Roger;Siegrist\n")
        use_case.execute(csv_path)
        mapping = repo.get_mapping(EntityType.PERSON, "Roger SIEGRIST")
        assert mapping is not None
        assert "SIEGRIST" in mapping.original_value
