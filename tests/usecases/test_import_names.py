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


class TestImportNamesCombinedFormat:
    def test_import_combined_name_vorname_column(self, use_case, repo, tmp_path):
        csv_path = _csv(tmp_path, "Grad;Name / Vorname\nHptm;Egger, Pascal\n")
        use_case.execute(csv_path)
        assert repo.get_mapping(EntityType.NACHNAME, "Egger") is not None
        assert repo.get_mapping(EntityType.VORNAME, "Pascal") is not None
        assert repo.get_mapping(EntityType.PERSON, "Pascal EGGER") is not None

    def test_import_grad_kurzform_column(self, use_case, repo, tmp_path):
        csv_path = _csv(tmp_path, "Grad Kurzform;Vorname;Nachname\nMaj;Roger;Siegrist\n")
        use_case.execute(csv_path)
        assert repo.get_mapping(EntityType.GRAD_FUNKTION, "Maj") is not None

    def test_import_combined_name_without_comma(self, use_case, repo, tmp_path):
        # No comma → entire value becomes Nachname, Vorname is empty
        csv_path = _csv(tmp_path, "Grad;Name / Vorname\nHptm;Muster\n")
        use_case.execute(csv_path)
        assert repo.get_mapping(EntityType.NACHNAME, "Muster") is not None
        # PERSON requires both vorname+nachname → should not be created
        assert repo.get_mapping(EntityType.PERSON, "MUSTER") is None

    def test_import_separate_columns_still_works(self, use_case, repo, tmp_path):
        csv_path = _csv(tmp_path, "Grad;Vorname;Nachname\nHptm;Thomas;Wegmüller\n")
        use_case.execute(csv_path)
        assert repo.get_mapping(EntityType.PERSON, "Thomas WEGMÜLLER") is not None

    def test_import_von_gunten_split_correctly(self, use_case, repo, tmp_path):
        # Multi-word Nachname with comma separator
        csv_path = _csv(tmp_path, "Grad;Name / Vorname\nOberstlt i Gst;von Gunten, Jürg\n")
        use_case.execute(csv_path)
        assert repo.get_mapping(EntityType.NACHNAME, "von Gunten") is not None
        assert repo.get_mapping(EntityType.VORNAME, "Jürg") is not None
        assert repo.get_mapping(EntityType.PERSON, "Jürg VON GUNTEN") is not None
        assert repo.get_mapping(EntityType.GRAD_FUNKTION, "Oberstlt i Gst") is not None


class TestImportNamesDelimiterDetection:
    def test_import_names_semicolon_delimiter(self, use_case, repo, tmp_path):
        # Standard semicolon-delimited format
        csv_path = _csv(tmp_path, "Grad;Vorname;Nachname\nMaj;Roger;Siegrist\n")
        use_case.execute(csv_path)
        assert repo.get_mapping(EntityType.PERSON, "Roger SIEGRIST") is not None

    def test_import_names_comma_delimiter(self, use_case, repo, tmp_path):
        # Comma-delimited with simple (non-quoted) values
        csv_path = _csv(tmp_path, "Grad,Vorname,Nachname\nMaj,Roger,Siegrist\n")
        use_case.execute(csv_path)
        assert repo.get_mapping(EntityType.PERSON, "Roger SIEGRIST") is not None

    def test_import_names_tab_delimiter(self, use_case, repo, tmp_path):
        # Tab-delimited export (some tools default to TSV)
        csv_path = _csv(tmp_path, "Grad\tVorname\tNachname\nMaj\tRoger\tSiegrist\n")
        use_case.execute(csv_path)
        assert repo.get_mapping(EntityType.PERSON, "Roger SIEGRIST") is not None

    def test_import_names_quoted_values_with_comma(self, use_case, repo, tmp_path):
        # Real MilOffice export: comma delimiter, combined Name/Vorname column,
        # values quoted because the Nachname itself contains a comma
        content = (
            'Name / Vorname,Grad Kurzform\n'
            '"von Gunten, Jürg",Maj\n'
            '"Egger, Pascal",Maj\n'
        )
        csv_path = _csv(tmp_path, content)
        use_case.execute(csv_path)
        assert repo.get_mapping(EntityType.NACHNAME, "von Gunten") is not None
        assert repo.get_mapping(EntityType.VORNAME, "Jürg") is not None
        assert repo.get_mapping(EntityType.PERSON, "Jürg VON GUNTEN") is not None
        assert repo.get_mapping(EntityType.NACHNAME, "Egger") is not None
        assert repo.get_mapping(EntityType.VORNAME, "Pascal") is not None
        assert repo.get_mapping(EntityType.PERSON, "Pascal EGGER") is not None
