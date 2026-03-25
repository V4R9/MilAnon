"""Cross-source entity consistency tests (US-5.4, D4).

Verifies that entities from different sources (PISA import, municipality DB,
document processing) always resolve to the same placeholder.
"""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from milanon.adapters.recognizers.list_recognizer import ListRecognizer
from milanon.adapters.recognizers.military_recognizer import MilitaryRecognizer
from milanon.adapters.recognizers.pattern_recognizer import PatternRecognizer
from milanon.adapters.repositories.sqlite_repository import SqliteMappingRepository
from milanon.domain.anonymizer import Anonymizer
from milanon.domain.entities import DocumentFormat, EntityType, ExtractedDocument
from milanon.domain.mapping_service import MappingService
from milanon.domain.recognition import RecognitionPipeline
from milanon.usecases.anonymize import AnonymizeUseCase
from milanon.usecases.import_entities import ImportEntitiesUseCase
from milanon.usecases.init_reference_data import InitReferenceDataUseCase


@pytest.fixture
def repo():
    return SqliteMappingRepository(":memory:")


@pytest.fixture
def service(repo):
    return MappingService(repo)


def _make_data_dir(tmp_path: Path, municipalities: list[str]) -> Path:
    """Create a minimal data directory with the given municipality names."""
    tmp_path.mkdir(parents=True, exist_ok=True)
    muni_csv = tmp_path / "swiss_municipalities.csv"
    with muni_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["plz", "name", "canton", "canton_name", "municipality"])
        for name in municipalities:
            writer.writerow(["0000", name, "BS", "TestKanton", name])
    units_csv = tmp_path / "military_units.csv"
    units_csv.write_text(
        "type,full_name,abbreviation,category,pattern_example\n"
        "rank,Hauptmann,Hptm,Hauptmann,Hptm Muster\n",
        encoding="utf-8",
    )
    return tmp_path


def _make_pisa_csv(tmp_path: Path, name: str, city: str, ahv: str = "") -> Path:
    """Create a minimal PISA 410 CSV with one person."""
    path = tmp_path / "pisa.csv"
    # PISA format: title row, header row, data rows
    # Col indices from import_entities: 0=AHV,1=Einheit,3=Grad,4=i_gst,5=Nachname,6=Vorname,15=Wohnort
    row = [""] * 32
    row[0] = ahv
    row[5] = name
    row[6] = "Hans"
    row[15] = city
    rows = [
        ["PISA 410 Personalauszug"] + [""] * 31,
        ["AHV", "Einheit", "", "Grad", "i Gst", "Name", "Vorname"] + [""] * 25,
        row,
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter=";")
        for r in rows:
            writer.writerow(r)
    return path


class TestCaseInsensitiveNormalization:
    """MappingService.get_or_create_placeholder must be case-insensitive."""

    def test_same_placeholder_for_case_variants(self, service):
        ph_mixed = service.get_or_create_placeholder(EntityType.ORT, "Basel")
        ph_upper = service.get_or_create_placeholder(EntityType.ORT, "BASEL")
        ph_lower = service.get_or_create_placeholder(EntityType.ORT, "basel")
        assert ph_mixed == ph_upper == ph_lower

    def test_same_placeholder_with_whitespace_variants(self, service):
        ph1 = service.get_or_create_placeholder(EntityType.NACHNAME, "Müller")
        ph2 = service.get_or_create_placeholder(EntityType.NACHNAME, "  Müller  ")
        assert ph1 == ph2

    def test_different_types_different_placeholders(self, service):
        ph_ort = service.get_or_create_placeholder(EntityType.ORT, "Basel")
        ph_person = service.get_or_create_placeholder(EntityType.PERSON, "Basel")
        assert ph_ort != ph_person

    def test_placeholder_format_correct(self, service):
        ph = service.get_or_create_placeholder(EntityType.ORT, "Bern")
        assert ph.startswith("[ORT_")
        assert ph.endswith("]")


class TestCrossSourceOrtConsistency:
    """Basel from municipalities DB + PISA import = same [ORT_NNN]."""

    def test_municipality_and_pisa_same_placeholder(self, repo, tmp_path):
        service = MappingService(repo)

        # Source 1: manually create ORT mapping (simulates municipality init)
        ph_muni = service.get_or_create_placeholder(EntityType.ORT, "Basel", "municipality_db")

        # Source 2: PISA import with same city
        pisa_path = _make_pisa_csv(tmp_path, name="MUELLER", city="Basel")
        import_uc = ImportEntitiesUseCase(service)
        import_uc.execute(pisa_path)

        # After PISA import, ORT "Basel" must return the same placeholder
        ph_after_pisa = service.get_or_create_placeholder(EntityType.ORT, "Basel")
        assert ph_muni == ph_after_pisa

    def test_municipality_init_then_pisa_then_document(self, repo, tmp_path):
        """Full integration: db init → PISA import → anonymize document → same ORT placeholder."""
        # Step 1: db init loads "Basel"
        data_dir = _make_data_dir(tmp_path / "data", ["Basel"])
        init_uc = InitReferenceDataUseCase(repo, data_dir)
        init_uc.execute()

        # Simulate: the first mention of Basel (via ListRecognizer in anonymize)
        # creates the ORT mapping. Let's pre-create via service.
        service = MappingService(repo)
        ph_from_init = service.get_or_create_placeholder(EntityType.ORT, "Basel", "db_init")

        # Step 2: PISA import
        pisa_path = _make_pisa_csv(tmp_path, name="MUELLER", city="Basel")
        import_uc = ImportEntitiesUseCase(service)
        import_uc.execute(pisa_path)

        # Step 3: anonymize a document containing Basel
        pipeline = RecognitionPipeline(
            [PatternRecognizer(), MilitaryRecognizer(), ListRecognizer(repo)]
        )
        anonymizer = Anonymizer(service)
        anonymize_uc = AnonymizeUseCase(pipeline, anonymizer, repo)

        in_dir = tmp_path / "input"
        in_dir.mkdir()
        (in_dir / "report.csv").write_text("Ort\nBasel\n", encoding="utf-8")
        out_dir = tmp_path / "output"
        anonymize_uc.execute(in_dir, out_dir, include_spreadsheets=True, level="full")

        # The placeholder used in the document must be the same as from init
        ph_from_service = service.get_or_create_placeholder(EntityType.ORT, "Basel")
        assert ph_from_init == ph_from_service

        # The anonymized document must contain the same placeholder
        anon_content = next(out_dir.rglob("*.*")).read_text(encoding="utf-8")
        assert ph_from_init in anon_content

    def test_case_variant_in_document_matches_pisa_import(self, repo, tmp_path):
        """PISA imports "Basel"; document contains "BASEL" — must get same placeholder."""
        service = MappingService(repo)

        # PISA import creates ORT "Basel"
        pisa_path = _make_pisa_csv(tmp_path, name="MUELLER", city="Basel")
        import_uc = ImportEntitiesUseCase(service)
        import_uc.execute(pisa_path)
        ph_pisa = service.get_or_create_placeholder(EntityType.ORT, "Basel")

        # Document contains "BASEL"
        ph_doc = service.get_or_create_placeholder(EntityType.ORT, "BASEL")
        assert ph_pisa == ph_doc


class TestCrossSourcePersonConsistency:
    """Müller from PISA import and from document = same [NACHNAME_NNN]."""

    def test_nachname_consistent_across_sources(self, repo, tmp_path):
        service = MappingService(repo)

        # Source 1: PISA import
        pisa_path = _make_pisa_csv(tmp_path, name="Müller", city="Bern")
        import_uc = ImportEntitiesUseCase(service)
        import_uc.execute(pisa_path)
        ph_from_pisa = service.get_or_create_placeholder(EntityType.NACHNAME, "Müller")

        # Source 2: document processing (simulate via service call)
        ph_from_doc = service.get_or_create_placeholder(EntityType.NACHNAME, "Müller")
        assert ph_from_pisa == ph_from_doc

    def test_nachname_case_insensitive(self, repo, tmp_path):
        service = MappingService(repo)

        pisa_path = _make_pisa_csv(tmp_path, name="MÜLLER", city="Bern")
        import_uc = ImportEntitiesUseCase(service)
        import_uc.execute(pisa_path)

        ph_upper = service.get_or_create_placeholder(EntityType.NACHNAME, "MÜLLER")
        ph_mixed = service.get_or_create_placeholder(EntityType.NACHNAME, "Müller")
        ph_lower = service.get_or_create_placeholder(EntityType.NACHNAME, "müller")
        assert ph_upper == ph_mixed == ph_lower


class TestNoduplicatePlaceholders:
    """Different sources must not create duplicate placeholders for the same entity."""

    def test_three_sources_one_placeholder(self, repo, tmp_path):
        service = MappingService(repo)

        # Source 1: explicit service call
        ph1 = service.get_or_create_placeholder(EntityType.ORT, "Zürich", "manual")
        # Source 2: PISA import
        pisa_path = _make_pisa_csv(tmp_path, name="MEIER", city="Zürich")
        ImportEntitiesUseCase(service).execute(pisa_path)
        # Source 3: another explicit call
        ph3 = service.get_or_create_placeholder(EntityType.ORT, "Zürich", "document")

        assert ph1 == ph3

        # Only one ORT mapping for Zürich must exist
        from milanon.adapters.repositories.sqlite_repository import SqliteMappingRepository
        assert isinstance(repo, SqliteMappingRepository)
        zurich_mappings = [
            m for m in repo.get_all_mappings()
            if m.entity_type == EntityType.ORT and "rich" in m.original_value.lower()
        ]
        assert len(zurich_mappings) == 1
