"""ImportNamesUseCase — imports entities from a simple name CSV (Grad;Vorname;Nachname)."""

from __future__ import annotations

import csv
import io
import logging
from pathlib import Path


def _detect_delimiter(text: str) -> str:
    """Auto-detect CSV delimiter via Sniffer. Falls back to first-line counting."""
    try:
        dialect = csv.Sniffer().sniff(text[:4096], delimiters=";,\t")
        return dialect.delimiter
    except csv.Error:
        first_line = text.split("\n")[0]
        if first_line.count(";") > first_line.count(","):
            return ";"
        return ","

from milanon.domain.entities import EntityType
from milanon.domain.mapping_service import MappingService
from milanon.usecases.import_entities import ImportResult

logger = logging.getLogger(__name__)

# Column name variants for the combined "Name / Vorname" field
_COMBINED_NAME_VARIANTS: frozenset[str] = frozenset(
    {"name / vorname", "name, vorname", "name/vorname"}
)

# Column name variants for the rank field
_GRAD_VARIANTS: frozenset[str] = frozenset({"grad", "grad kurzform"})


def _normalise_header(name: str) -> str:
    return name.strip().lower()


def _detect_combined_col(fieldnames: list[str]) -> str | None:
    """Return the actual column name if a combined Name/Vorname column is present."""
    for fn in fieldnames:
        if _normalise_header(fn) in _COMBINED_NAME_VARIANTS:
            return fn
    return None


def _detect_grad_col(fieldnames: list[str]) -> str | None:
    """Return the actual column name for the rank field (any known variant)."""
    for fn in fieldnames:
        if _normalise_header(fn) in _GRAD_VARIANTS:
            return fn
    return None


def _split_combined(value: str) -> tuple[str, str]:
    """Split 'Nachname, Vorname' at the first comma.

    Returns (nachname, vorname).  If no comma is present the whole value is
    treated as the Nachname and Vorname is returned empty.
    """
    if "," in value:
        nachname, _, vorname = value.partition(",")
        return nachname.strip(), vorname.strip()
    return value.strip(), ""


class ImportNamesUseCase:
    """Imports entities from a simple name CSV.

    Supported formats (UTF-8, header row required, delimiter auto-detected):

    Format A — separate columns (existing behaviour):
        Grad;Vorname;Nachname
        Hptm;Thomas;Wegmüller

    Format B — combined Name/Vorname column (auto-detected):
        Grad Kurzform;Name / Vorname
        Hptm;von Gunten, Jürg

    The format is detected automatically from the header row.
    "Grad Kurzform" is treated identically to "Grad".

    Per row, creates mappings for:
    - PERSON  = "Vorname NACHNAME"  (only if both present)
    - VORNAME = Vorname             (only if present)
    - NACHNAME = Nachname
    - GRAD_FUNKTION = Grad          (only when the column is present and non-empty)

    Duplicates are silently skipped via MappingService.get_or_create_placeholder().
    """

    def __init__(self, mapping_service: MappingService) -> None:
        self._mapping_service = mapping_service

    def execute(self, csv_path: Path, source_document: str = "") -> ImportResult:
        """Import entities from a simple name CSV file."""
        text = csv_path.read_text(encoding="utf-8-sig")
        delimiter = _detect_delimiter(text)
        reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)

        fieldnames: list[str] = list(reader.fieldnames or [])
        combined_col = _detect_combined_col(fieldnames)
        grad_col = _detect_grad_col(fieldnames)

        result = ImportResult()

        for row in reader:
            if combined_col is not None:
                raw = (row.get(combined_col) or "").strip()
                if not raw:
                    result.rows_skipped += 1
                    continue
                nachname, vorname = _split_combined(raw)
            else:
                vorname = (row.get("Vorname") or "").strip()
                nachname = (row.get("Nachname") or "").strip()

            if not vorname and not nachname:
                result.rows_skipped += 1
                continue

            grad = (row.get(grad_col) or "").strip() if grad_col else ""

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
