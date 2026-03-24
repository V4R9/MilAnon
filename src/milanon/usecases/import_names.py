"""ImportNamesUseCase — imports entities from a simple name CSV (Grad;Vorname;Nachname)."""

from __future__ import annotations

import csv
import io
import logging
from pathlib import Path

from milanon.domain.entities import EntityType
from milanon.domain.mapping_service import MappingService
from milanon.usecases.import_entities import ImportResult

logger = logging.getLogger(__name__)


class ImportNamesUseCase:
    """Imports entities from a simple 3-column name CSV.

    Expected format (semicolon-delimited, UTF-8, with header row):
        Grad;Vorname;Nachname
        Hptm;Thomas;Wegmüller
        Oberstlt i Gst;Simon;Kohler

    The "Grad" column is optional — files without it are also accepted.

    Per row, creates mappings for:
    - PERSON  = "Vorname NACHNAME"
    - VORNAME = Vorname
    - NACHNAME = Nachname
    - GRAD_FUNKTION = Grad (only when the column is present and non-empty)

    Duplicates are silently skipped via MappingService.get_or_create_placeholder().
    """

    def __init__(self, mapping_service: MappingService) -> None:
        self._mapping_service = mapping_service

    def execute(self, csv_path: Path, source_document: str = "") -> ImportResult:
        """Import entities from a simple name CSV file."""
        text = csv_path.read_text(encoding="utf-8-sig")
        reader = csv.DictReader(io.StringIO(text), delimiter=";")

        result = ImportResult()

        for row in reader:
            vorname = (row.get("Vorname") or "").strip()
            nachname = (row.get("Nachname") or "").strip()

            if not vorname and not nachname:
                result.rows_skipped += 1
                continue

            grad = (row.get("Grad") or "").strip()
            result.entities_imported += self._import_person(
                vorname, nachname, grad, source_document
            )
            result.rows_processed += 1

        return result

    def _import_person(
        self, vorname: str, nachname: str, grad: str, source: str
    ) -> int:
        """Create mappings for one person. Returns count of newly created entities."""
        count = 0

        if vorname and nachname:
            full_name = f"{vorname} {nachname.upper()}"
            count += self._create(EntityType.PERSON, full_name, source)

        if nachname:
            count += self._create(EntityType.NACHNAME, nachname, source)
        if vorname:
            count += self._create(EntityType.VORNAME, vorname, source)
        if grad:
            count += self._create(EntityType.GRAD_FUNKTION, grad, source)

        return count

    def _create(self, entity_type: EntityType, value: str, source: str) -> int:
        """Create mapping if not exists. Returns 1 if new, 0 if duplicate."""
        if not value:
            return 0
        repo = self._mapping_service._repository  # type: ignore[attr-defined]
        if repo.get_mapping(entity_type, value) is not None:
            return 0
        self._mapping_service.get_or_create_placeholder(entity_type, value, source)
        return 1
