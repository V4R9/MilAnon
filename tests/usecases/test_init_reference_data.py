"""Tests for InitReferenceDataUseCase — reference data loading and idempotency."""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from milanon.adapters.repositories.sqlite_repository import SqliteMappingRepository
from milanon.adapters.recognizers.list_recognizer import ListRecognizer
from milanon.domain.entities import ExtractedDocument, DocumentFormat
from milanon.usecases.init_reference_data import InitReferenceDataUseCase


@pytest.fixture
def repo():
    return SqliteMappingRepository(":memory:")


@pytest.fixture
def data_dir(tmp_path) -> Path:
    """Create a minimal data directory with test CSVs."""
    # Municipalities CSV
    muni_csv = tmp_path / "swiss_municipalities.csv"
    with muni_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["plz", "name", "canton", "canton_name", "municipality"])
        writer.writerow(["4001", "Basel", "BS", "Basel-Stadt", "Basel"])
        writer.writerow(["3000", "Bern", "BE", "Bern", "Bern"])
        writer.writerow(["8001", "Zürich", "ZH", "Zürich", "Zürich"])
        writer.writerow(["6300", "Zug", "ZG", "Zug", "Zug"])

    # Military units CSV (minimal, matching the real format)
    units_csv = tmp_path / "military_units.csv"
    with units_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["type", "full_name", "abbreviation", "category", "pattern_example"])
        writer.writerow(["rank", "Hauptmann", "Hptm", "Hauptmann", "Hptm Muster"])
        writer.writerow(["rank", "Leutnant", "Lt", "Subalternoffizier", "Lt Muster"])
        writer.writerow(["branch", "Infanterie", "Inf", "Truppengattung", "Inf Bat 56"])

    return tmp_path


class TestInitReferenceDataUseCase:
    def test_loads_municipalities(self, repo, data_dir):
        uc = InitReferenceDataUseCase(repo, data_dir)
        result = uc.execute()
        assert result.municipalities_loaded == 4
        assert not result.municipalities_skipped

    def test_loads_military_units(self, repo, data_dir):
        uc = InitReferenceDataUseCase(repo, data_dir)
        result = uc.execute()
        assert result.military_units_loaded == 3
        assert not result.military_units_skipped

    def test_municipalities_accessible_via_repo(self, repo, data_dir):
        uc = InitReferenceDataUseCase(repo, data_dir)
        uc.execute()
        names = repo.get_municipality_names()
        assert "Basel" in names
        assert "Bern" in names
        assert "Zürich" in names

    def test_idempotent_municipalities(self, repo, data_dir):
        uc = InitReferenceDataUseCase(repo, data_dir)
        uc.execute()
        result2 = uc.execute()
        assert result2.municipalities_skipped
        assert result2.municipalities_loaded == 0
        # Count must not double
        assert repo.get_ref_municipality_count() == 4

    def test_idempotent_military_units(self, repo, data_dir):
        uc = InitReferenceDataUseCase(repo, data_dir)
        uc.execute()
        result2 = uc.execute()
        assert result2.military_units_skipped
        assert result2.military_units_loaded == 0
        assert repo.get_ref_military_unit_count() == 3

    def test_already_initialized_flag(self, repo, data_dir):
        uc = InitReferenceDataUseCase(repo, data_dir)
        uc.execute()
        result2 = uc.execute()
        assert result2.already_initialized

    def test_missing_csv_returns_zero(self, repo, tmp_path):
        # Empty data dir — no CSV files
        uc = InitReferenceDataUseCase(repo, tmp_path)
        result = uc.execute()
        assert result.municipalities_loaded == 0
        assert result.military_units_loaded == 0


class TestListRecognizerWithDB:
    """ListRecognizer fetches municipality names from DB when no list is given."""

    def test_recognizes_municipality_from_db(self, repo, data_dir):
        uc = InitReferenceDataUseCase(repo, data_dir)
        uc.execute()

        recognizer = ListRecognizer(repo)  # no municipality_names — uses DB
        doc = ExtractedDocument(
            source_path=Path("test.csv"),
            format=DocumentFormat.CSV,
            text_content="Der Soldat wohnt in Basel.",
        )
        entities = recognizer.recognize(doc)
        ort_entities = [e for e in entities if e.entity_type.value == "ORT"]
        assert any(e.original_value.lower() == "basel" for e in ort_entities)

    def test_empty_db_returns_no_municipality_entities(self, repo):
        recognizer = ListRecognizer(repo)  # DB empty, no municipalities
        doc = ExtractedDocument(
            source_path=Path("test.csv"),
            format=DocumentFormat.CSV,
            text_content="Der Soldat wohnt in Basel.",
        )
        entities = recognizer.recognize(doc)
        ort_entities = [e for e in entities if e.entity_type.value == "ORT"]
        assert len(ort_entities) == 0

    def test_explicit_list_overrides_db(self, repo, data_dir):
        uc = InitReferenceDataUseCase(repo, data_dir)
        uc.execute()

        # Pass explicit list that doesn't include Basel
        recognizer = ListRecognizer(repo, municipality_names=["Zürich"])
        doc = ExtractedDocument(
            source_path=Path("test.csv"),
            format=DocumentFormat.CSV,
            text_content="Städte: Basel und Zürich.",
        )
        entities = recognizer.recognize(doc)
        ort_entities = [e for e in entities if e.entity_type.value == "ORT"]
        values = [e.original_value.lower() for e in ort_entities]
        assert "zürich" in values
        assert "basel" not in values  # not in explicit list


class TestDBInitIdempotencyWithRealData:
    """Integration test with the real bundled data files."""

    def test_real_municipalities_load(self, repo):
        # Use the actual bundled data dir
        real_data_dir = Path(__file__).parent.parent.parent / "data"
        if not (real_data_dir / "swiss_municipalities.csv").exists():
            pytest.skip("Bundled municipalities CSV not found")

        uc = InitReferenceDataUseCase(repo, real_data_dir)
        result = uc.execute()
        assert result.municipalities_loaded > 3000  # ~3958 names

    def test_real_municipalities_idempotent(self, repo):
        real_data_dir = Path(__file__).parent.parent.parent / "data"
        if not (real_data_dir / "swiss_municipalities.csv").exists():
            pytest.skip("Bundled municipalities CSV not found")

        uc = InitReferenceDataUseCase(repo, real_data_dir)
        count_before = uc.execute().municipalities_loaded
        result2 = uc.execute()
        assert result2.municipalities_skipped
        assert repo.get_ref_municipality_count() == count_before
