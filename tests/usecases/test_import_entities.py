"""Tests for ImportEntitiesUseCase — PISA 410 CSV import."""

from __future__ import annotations

from pathlib import Path

import pytest

from milanon.adapters.repositories.sqlite_repository import SqliteMappingRepository
from milanon.domain.entities import EntityType
from milanon.domain.mapping_service import MappingService
from milanon.usecases.import_entities import ImportEntitiesUseCase


@pytest.fixture
def repo():
    return SqliteMappingRepository(":memory:")


@pytest.fixture
def use_case(repo):
    service = MappingService(repo)
    return ImportEntitiesUseCase(service)


def _write_csv(path: Path, rows: list[list[str]]) -> Path:
    """Write a semicolon-delimited CSV with PISA 410 structure (title row, header row, data rows)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [";".join(r) for r in rows]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _make_pisa_row(
    ahv="756.1234.5678.97",
    einheit="Inf Bat 56",
    grad="Hptm",
    i_gst="",
    nachname="BERNASCONI",
    vorname="Marco",
    funktion="Kdt",
    funktion_zusatz="",
    adresse1="Hauptstrasse 12",
    plz="3000",
    wohnort="Bern",
    tel_privat="079 535 80 46",
    tel_geschaeft="",
    mobile_privat="",
    mobile_geschaeft="",
    email_geschaeft="marco.bernasconi@mil.ch",
    email_privat="",
    email_sonst="",
    geburtsdatum="01.01.1990",
) -> list[str]:
    """Build a PISA 410 data row (32 columns, 0-indexed per _COL_* constants)."""
    row = [""] * 32
    row[0] = ahv
    row[1] = einheit
    row[3] = grad
    row[4] = i_gst
    row[5] = nachname
    row[6] = vorname
    row[9] = funktion
    row[10] = funktion_zusatz
    row[11] = adresse1
    row[14] = plz
    row[15] = wohnort
    row[23] = tel_privat
    row[24] = tel_geschaeft
    row[25] = mobile_privat
    row[26] = mobile_geschaeft
    row[27] = email_geschaeft
    row[28] = email_privat
    row[29] = email_sonst
    row[31] = geburtsdatum
    return row


_TITLE_ROW = ["PISA 410 Personalauszug"] + [""] * 31
_HEADER_ROW = ["AHV", "Einheit", "", "Grad", "i Gst", "Name", "Vorname"] + [""] * 25


class TestImportEntitiesBasic:
    def test_returns_import_result(self, use_case, tmp_path):
        csv_path = _write_csv(
            tmp_path / "pisa.csv",
            [_TITLE_ROW, _HEADER_ROW, _make_pisa_row()],
        )
        result = use_case.execute(csv_path)
        assert result.rows_processed == 1
        assert result.entities_imported > 0

    def test_skips_title_and_header_rows(self, use_case, tmp_path):
        csv_path = _write_csv(
            tmp_path / "pisa.csv",
            [_TITLE_ROW, _HEADER_ROW],  # no data rows
        )
        result = use_case.execute(csv_path)
        assert result.rows_processed == 0
        assert result.entities_imported == 0

    def test_person_entity_created(self, use_case, repo, tmp_path):
        csv_path = _write_csv(
            tmp_path / "pisa.csv",
            [_TITLE_ROW, _HEADER_ROW, _make_pisa_row(nachname="BERNASCONI", vorname="Marco")],
        )
        use_case.execute(csv_path)
        mapping = repo.get_mapping(EntityType.PERSON, "Marco BERNASCONI")
        assert mapping is not None

    def test_nachname_entity_created(self, use_case, repo, tmp_path):
        csv_path = _write_csv(
            tmp_path / "pisa.csv",
            [_TITLE_ROW, _HEADER_ROW, _make_pisa_row(nachname="BERNASCONI")],
        )
        use_case.execute(csv_path)
        assert repo.get_mapping(EntityType.NACHNAME, "BERNASCONI") is not None

    def test_vorname_entity_created(self, use_case, repo, tmp_path):
        csv_path = _write_csv(
            tmp_path / "pisa.csv",
            [_TITLE_ROW, _HEADER_ROW, _make_pisa_row(vorname="Marco")],
        )
        use_case.execute(csv_path)
        assert repo.get_mapping(EntityType.VORNAME, "Marco") is not None

    def test_ahv_entity_created(self, use_case, repo, tmp_path):
        ahv = "756.1234.5678.97"
        csv_path = _write_csv(
            tmp_path / "pisa.csv",
            [_TITLE_ROW, _HEADER_ROW, _make_pisa_row(ahv=ahv)],
        )
        use_case.execute(csv_path)
        assert repo.get_mapping(EntityType.AHV_NR, ahv) is not None

    def test_einheit_entity_created(self, use_case, repo, tmp_path):
        csv_path = _write_csv(
            tmp_path / "pisa.csv",
            [_TITLE_ROW, _HEADER_ROW, _make_pisa_row(einheit="Inf Bat 56")],
        )
        use_case.execute(csv_path)
        assert repo.get_mapping(EntityType.EINHEIT, "Inf Bat 56") is not None

    def test_email_entity_created(self, use_case, repo, tmp_path):
        csv_path = _write_csv(
            tmp_path / "pisa.csv",
            [_TITLE_ROW, _HEADER_ROW, _make_pisa_row(email_geschaeft="marco.bernasconi@mil.ch")],
        )
        use_case.execute(csv_path)
        assert repo.get_mapping(EntityType.EMAIL, "marco.bernasconi@mil.ch") is not None

    def test_telefon_entity_created(self, use_case, repo, tmp_path):
        csv_path = _write_csv(
            tmp_path / "pisa.csv",
            [_TITLE_ROW, _HEADER_ROW, _make_pisa_row(tel_privat="079 535 80 46")],
        )
        use_case.execute(csv_path)
        assert repo.get_mapping(EntityType.TELEFON, "079 535 80 46") is not None

    def test_geburtsdatum_entity_created(self, use_case, repo, tmp_path):
        csv_path = _write_csv(
            tmp_path / "pisa.csv",
            [_TITLE_ROW, _HEADER_ROW, _make_pisa_row(geburtsdatum="01.01.1990")],
        )
        use_case.execute(csv_path)
        assert repo.get_mapping(EntityType.GEBURTSDATUM, "01.01.1990") is not None


class TestImportEntitiesEdgeCases:
    def test_star_prefix_stripped_from_phone(self, use_case, repo, tmp_path):
        row = _make_pisa_row(tel_privat="*079 535 80 46")
        csv_path = _write_csv(tmp_path / "pisa.csv", [_TITLE_ROW, _HEADER_ROW, row])
        use_case.execute(csv_path)
        assert repo.get_mapping(EntityType.TELEFON, "079 535 80 46") is not None

    def test_star_prefix_stripped_from_email(self, use_case, repo, tmp_path):
        row = _make_pisa_row(email_geschaeft="*flavio@mil.ch")
        csv_path = _write_csv(tmp_path / "pisa.csv", [_TITLE_ROW, _HEADER_ROW, row])
        use_case.execute(csv_path)
        assert repo.get_mapping(EntityType.EMAIL, "flavio@mil.ch") is not None

    def test_grad_funktion_with_i_gst(self, use_case, repo, tmp_path):
        row = _make_pisa_row(grad="Oberstlt", i_gst="J")
        csv_path = _write_csv(tmp_path / "pisa.csv", [_TITLE_ROW, _HEADER_ROW, row])
        use_case.execute(csv_path)
        assert repo.get_mapping(EntityType.GRAD_FUNKTION, "Oberstlt i Gst") is not None

    def test_grad_funktion_without_i_gst(self, use_case, repo, tmp_path):
        row = _make_pisa_row(grad="Hptm", i_gst="")
        csv_path = _write_csv(tmp_path / "pisa.csv", [_TITLE_ROW, _HEADER_ROW, row])
        use_case.execute(csv_path)
        assert repo.get_mapping(EntityType.GRAD_FUNKTION, "Hptm") is not None

    def test_empty_row_skipped(self, use_case, tmp_path):
        empty_row = [""] * 32
        csv_path = _write_csv(
            tmp_path / "pisa.csv",
            [_TITLE_ROW, _HEADER_ROW, empty_row],
        )
        result = use_case.execute(csv_path)
        assert result.rows_processed == 0
        assert result.rows_skipped == 1

    def test_duplicate_entity_not_reimported(self, use_case, tmp_path):
        csv_path = _write_csv(
            tmp_path / "pisa.csv",
            [_TITLE_ROW, _HEADER_ROW, _make_pisa_row(), _make_pisa_row()],
        )
        result = use_case.execute(csv_path)
        assert result.rows_processed == 2
        # Second row duplicates first — no new entities on second row
        first_run_count = result.entities_imported
        csv_path2 = _write_csv(
            tmp_path / "pisa2.csv",
            [_TITLE_ROW, _HEADER_ROW, _make_pisa_row()],
        )
        result2 = use_case.execute(csv_path2)
        assert result2.entities_imported == 0  # all already exist

    def test_multiple_rows_processed(self, use_case, tmp_path):
        row1 = _make_pisa_row(nachname="BERNASCONI", vorname="Marco", ahv="756.1111.1111.11")
        row2 = _make_pisa_row(nachname="MUELLER", vorname="Hans", ahv="756.2222.2222.22")
        csv_path = _write_csv(
            tmp_path / "pisa.csv",
            [_TITLE_ROW, _HEADER_ROW, row1, row2],
        )
        result = use_case.execute(csv_path)
        assert result.rows_processed == 2
