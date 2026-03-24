"""ImportEntitiesUseCase — imports entities from PISA 410 CSV exports."""

from __future__ import annotations

import csv
import io
import logging
from dataclasses import dataclass
from pathlib import Path

from milanon.utils.csv_helpers import detect_delimiter

from milanon.domain.entities import EntityType
from milanon.domain.mapping_service import MappingService

logger = logging.getLogger(__name__)

# PISA 410 column indices (0-based, after skipping row 1 title)
_COL_AHV = 0
_COL_EINHEIT = 1
_COL_GRAD = 3
_COL_I_GST = 4
_COL_NACHNAME = 5
_COL_VORNAME = 6
_COL_FUNKTION = 9
_COL_FUNKTION_ZUSATZ = 10
_COL_ADRESSE1 = 11
_COL_PLZ = 14
_COL_WOHNORT = 15
_COL_TEL_PRIVAT = 23
_COL_TEL_GESCHAEFT = 24
_COL_MOBILE_PRIVAT = 25
_COL_MOBILE_GESCHAEFT = 26
_COL_EMAIL_GESCHAEFT = 27
_COL_EMAIL_PRIVAT = 28
_COL_EMAIL_SONST = 29
_COL_GEBURTSDATUM = 31


def _strip_star(value: str) -> str:
    """Strip PISA '*' primary-contact prefix."""
    return value.lstrip("*").strip()


def _cell(row: list[str], idx: int) -> str:
    return _strip_star(row[idx]) if idx < len(row) else ""


@dataclass
class ImportResult:
    rows_processed: int = 0
    entities_imported: int = 0
    rows_skipped: int = 0


class ImportEntitiesUseCase:
    """Imports entities from a PISA 410 personnel CSV export.

    Row 1 (index 0): report title — skipped.
    Row 2 (index 1): column headers — used for validation, then skipped.
    Rows 3+ (index 2+): data rows — processed.

    For each data row, creates mappings for:
    PERSON, VORNAME, NACHNAME, GRAD_FUNKTION, AHV_NR, EINHEIT,
    FUNKTION, ADRESSE, ORT, TELEFON (all columns), EMAIL (all columns),
    GEBURTSDATUM.
    """

    def __init__(self, mapping_service: MappingService) -> None:
        self._mapping_service = mapping_service

    def execute(self, csv_path: Path, source_document: str = "") -> ImportResult:
        """Import entities from a PISA 410 CSV file.

        Args:
            csv_path: Path to the PISA 410 CSV export.
            source_document: Label stored in each mapping's source_document field.

        Returns:
            ImportResult with statistics.
        """
        text = csv_path.read_text(encoding="utf-8-sig")
        delimiter = detect_delimiter(text)
        rows = list(csv.reader(io.StringIO(text), delimiter=delimiter))

        result = ImportResult()

        # Skip title row (row 0) and header row (row 1)
        data_rows = rows[2:] if len(rows) >= 3 else []

        for row in data_rows:
            if not any(cell.strip() for cell in row):
                result.rows_skipped += 1
                continue
            result.entities_imported += self._import_row(row, source_document)
            result.rows_processed += 1

        return result

    def _import_row(self, row: list[str], source: str) -> int:
        """Import all entities from a single data row. Returns count of new imports."""
        count = 0
        src = source

        nachname = _cell(row, _COL_NACHNAME)
        vorname = _cell(row, _COL_VORNAME)

        # PERSON = "Vorname NACHNAME"
        if nachname and vorname:
            full_name = f"{vorname} {nachname.upper()}"
            count += self._create(EntityType.PERSON, full_name, src)

        if nachname:
            count += self._create(EntityType.NACHNAME, nachname, src)
        if vorname:
            count += self._create(EntityType.VORNAME, vorname, src)

        # GRAD_FUNKTION
        grad = _cell(row, _COL_GRAD)
        i_gst = _cell(row, _COL_I_GST)
        if grad:
            rank = f"{grad} i Gst" if i_gst.upper() == "J" else grad
            count += self._create(EntityType.GRAD_FUNKTION, rank, src)

        # AHV_NR
        ahv = _cell(row, _COL_AHV)
        if ahv:
            count += self._create(EntityType.AHV_NR, ahv, src)

        # EINHEIT
        einheit = _cell(row, _COL_EINHEIT)
        if einheit:
            count += self._create(EntityType.EINHEIT, einheit, src)

        # FUNKTION
        funktion = _cell(row, _COL_FUNKTION)
        funktion_zusatz = _cell(row, _COL_FUNKTION_ZUSATZ)
        if funktion:
            fn = f"{funktion} {funktion_zusatz}".strip() if funktion_zusatz else funktion
            count += self._create(EntityType.FUNKTION, fn, src)

        # ADRESSE
        adresse1 = _cell(row, _COL_ADRESSE1)
        plz = _cell(row, _COL_PLZ)
        wohnort = _cell(row, _COL_WOHNORT)
        if adresse1:
            parts = [adresse1]
            if plz:
                parts.append(plz)
            if wohnort:
                parts.append(wohnort)
            count += self._create(EntityType.ADRESSE, " ".join(parts), src)

        # ORT
        if wohnort:
            count += self._create(EntityType.ORT, wohnort, src)

        # TELEFON — all non-empty phone columns
        for col in (
            _COL_TEL_PRIVAT,
            _COL_TEL_GESCHAEFT,
            _COL_MOBILE_PRIVAT,
            _COL_MOBILE_GESCHAEFT,
        ):
            tel = _cell(row, col)
            if tel:
                count += self._create(EntityType.TELEFON, tel, src)

        # EMAIL — all non-empty email columns
        for col in (_COL_EMAIL_GESCHAEFT, _COL_EMAIL_PRIVAT, _COL_EMAIL_SONST):
            email = _cell(row, col)
            if email:
                count += self._create(EntityType.EMAIL, email, src)

        # GEBURTSDATUM
        geb = _cell(row, _COL_GEBURTSDATUM)
        if geb:
            count += self._create(EntityType.GEBURTSDATUM, geb, src)

        return count

    def _create(self, entity_type: EntityType, value: str, source: str) -> int:
        """Create mapping if not exists. Returns 1 if new, 0 if duplicate."""
        if not value:
            return 0
        if self._mapping_service.has_mapping(entity_type, value):
            return 0
        self._mapping_service.get_or_create_placeholder(entity_type, value, source)
        return 1
