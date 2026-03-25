"""InitReferenceDataUseCase — loads Swiss municipalities and military units into the DB."""

from __future__ import annotations

import csv
import logging
from dataclasses import dataclass
from pathlib import Path

from milanon.domain.protocols import ReferenceDataRepository

logger = logging.getLogger(__name__)

# Default data directory (bundled with the package)
_DEFAULT_DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"
_MUNICIPALITIES_CSV = "swiss_municipalities.csv"
_MILITARY_UNITS_CSV = "military_units.csv"


@dataclass
class InitResult:
    municipalities_loaded: int = 0
    municipalities_skipped: bool = False
    military_units_loaded: int = 0
    military_units_skipped: bool = False

    @property
    def already_initialized(self) -> bool:
        return self.municipalities_skipped and self.military_units_skipped


class InitReferenceDataUseCase:
    """Loads bundled reference data (municipalities, military units) into the SQLite DB.

    Idempotent: if ref tables are already populated, nothing is loaded.
    """

    def __init__(self, repository: ReferenceDataRepository, data_dir: Path | None = None) -> None:
        self._repo = repository
        self._data_dir = data_dir or _DEFAULT_DATA_DIR

    def execute(self) -> InitResult:
        """Load reference data into the database.

        Returns:
            InitResult with counts of loaded rows and skip flags.
        """
        result = InitResult()

        # Municipalities
        if self._repo.get_ref_municipality_count() > 0:
            result.municipalities_skipped = True
            logger.debug("ref_municipalities already populated — skipping")
        else:
            rows = self._load_municipalities()
            result.municipalities_loaded = self._repo.import_municipalities_full(rows)
            logger.info("Loaded %d municipalities", result.municipalities_loaded)

        # Military units
        if self._repo.get_ref_military_unit_count() > 0:
            result.military_units_skipped = True
            logger.debug("ref_military_units already populated — skipping")
        else:
            units = self._load_military_units()
            result.military_units_loaded = self._repo.import_military_units(units)
            logger.info("Loaded %d military unit entries", result.military_units_loaded)

        return result

    def _load_municipalities(self) -> list[dict]:
        csv_path = self._data_dir / _MUNICIPALITIES_CSV
        if not csv_path.exists():
            logger.warning("Municipalities CSV not found: %s", csv_path)
            return []
        rows = []
        with csv_path.open(encoding="utf-8") as f:
            for row in csv.DictReader(f):
                name = row.get("name", "").strip()
                if name and len(name) >= 2:
                    rows.append({
                        "name": name,
                        "canton": row.get("canton", ""),
                        "plz": row.get("plz", ""),
                    })
        return rows

    def _load_military_units(self) -> list[dict]:
        csv_path = self._data_dir / _MILITARY_UNITS_CSV
        if not csv_path.exists():
            logger.warning("Military units CSV not found: %s", csv_path)
            return []
        units = []
        with csv_path.open(encoding="utf-8") as f:
            for row in csv.DictReader(f):
                abbrev = row.get("abbreviation", "").strip()
                if abbrev:
                    units.append(dict(row))
        return units
