"""SQLite implementation of the MappingRepository protocol."""

from __future__ import annotations

import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from milanon.domain.entities import EntityMapping, EntityType

# Full schema DDL
_SCHEMA_SQL = """\
CREATE TABLE IF NOT EXISTS entity_mappings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type TEXT NOT NULL,
    original_value TEXT NOT NULL,
    normalized_value TEXT NOT NULL,
    placeholder TEXT NOT NULL UNIQUE,
    first_seen_at TEXT NOT NULL,
    last_seen_at TEXT NOT NULL,
    source_document TEXT,
    created_by TEXT DEFAULT 'auto',
    UNIQUE(entity_type, normalized_value)
);

CREATE TABLE IF NOT EXISTS entity_aliases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mapping_id INTEGER NOT NULL REFERENCES entity_mappings(id),
    alias_value TEXT NOT NULL,
    normalized_alias TEXT NOT NULL,
    UNIQUE(mapping_id, normalized_alias)
);

CREATE TABLE IF NOT EXISTS ref_municipalities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    canton TEXT,
    plz TEXT,
    bfs_number INTEGER
);

CREATE TABLE IF NOT EXISTS ref_military_units (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern TEXT NOT NULL,
    unit_type TEXT,
    parent_unit TEXT,
    full_name TEXT DEFAULT '',
    abbreviation TEXT DEFAULT '',
    level TEXT DEFAULT '',
    category TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS file_tracking (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    output_path TEXT,
    operation TEXT NOT NULL,
    processed_at TEXT NOT NULL,
    entity_count INTEGER DEFAULT 0,
    UNIQUE(file_path, operation)
);

CREATE TABLE IF NOT EXISTS processing_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    operation TEXT NOT NULL,
    input_path TEXT NOT NULL,
    output_path TEXT,
    entities_processed INTEGER DEFAULT 0,
    warnings INTEGER DEFAULT 0,
    errors INTEGER DEFAULT 0,
    duration_ms INTEGER
);

CREATE INDEX IF NOT EXISTS idx_mappings_type_normalized
    ON entity_mappings(entity_type, normalized_value);
CREATE INDEX IF NOT EXISTS idx_mappings_placeholder
    ON entity_mappings(placeholder);
CREATE INDEX IF NOT EXISTS idx_aliases_normalized
    ON entity_aliases(normalized_alias);
CREATE INDEX IF NOT EXISTS idx_municipalities_name
    ON ref_municipalities(name COLLATE NOCASE);
CREATE INDEX IF NOT EXISTS idx_tracking_path
    ON file_tracking(file_path, operation);
"""


def _normalize(value: str) -> str:
    """Normalize a value for case-insensitive, whitespace-insensitive matching.

    Collapses all internal whitespace (newlines, tabs, multiple spaces) to a
    single space so that 'Inf\\nBat 56' and 'Inf Bat 56' map to the same entry.
    """
    return re.sub(r"\s+", " ", value.strip()).lower()


def _now_iso() -> str:
    """Return current UTC time as ISO 8601 string."""
    return datetime.now(timezone.utc).isoformat()


class SqliteMappingRepository:
    """SQLite-backed repository for entity-to-placeholder mappings.

    NOTE (SRP): This class currently handles entity mappings, reference data
    (municipalities, military units), and file tracking in one place.
    If any of these concerns grow significantly, consider splitting them into
    dedicated repository classes (e.g. FileTrackingRepository, RefDataRepository).
    """

    def __init__(self, db_path: str | Path = ":memory:") -> None:
        self._db_path = str(db_path)
        self._conn = sqlite3.connect(self._db_path)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA foreign_keys=ON")
        self._init_schema()

    def _init_schema(self) -> None:
        """Create tables and indexes if they don't exist."""
        self._conn.executescript(_SCHEMA_SQL)
        self._migrate_schema()

    def _migrate_schema(self) -> None:
        """Add new columns to existing tables (safe to run multiple times)."""
        migrations = [
            "ALTER TABLE ref_military_units ADD COLUMN full_name TEXT DEFAULT ''",
            "ALTER TABLE ref_military_units ADD COLUMN abbreviation TEXT DEFAULT ''",
            "ALTER TABLE ref_military_units ADD COLUMN level TEXT DEFAULT ''",
            "ALTER TABLE ref_military_units ADD COLUMN category TEXT DEFAULT ''",
        ]
        for sql in migrations:
            try:
                self._conn.execute(sql)
            except sqlite3.OperationalError:
                pass  # Column already exists
        self._conn.commit()

    def close(self) -> None:
        """Close the database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None

    def __enter__(self) -> "SqliteMappingRepository":
        """Support use as a context manager."""
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> bool:
        """Close connection on context manager exit."""
        self.close()
        return False

    def get_mapping(
        self, entity_type: EntityType, original_value: str
    ) -> EntityMapping | None:
        """Look up an existing mapping by type and normalized value."""
        row = self._conn.execute(
            "SELECT * FROM entity_mappings WHERE entity_type = ? AND normalized_value = ?",
            (entity_type.value, _normalize(original_value)),
        ).fetchone()
        if row is None:
            return None
        return self._row_to_mapping(row)

    def create_mapping(
        self, entity_type: EntityType, original_value: str, source_document: str = ""
    ) -> EntityMapping:
        """Create a new mapping with an auto-generated placeholder.

        Uses BEGIN IMMEDIATE to acquire an exclusive write lock for the entire
        read-check-write sequence, preventing duplicate placeholders under
        concurrent Streamlit sessions.
        """
        now = _now_iso()
        self._conn.execute("BEGIN IMMEDIATE")
        try:
            placeholder = self._next_placeholder(entity_type)
            self._conn.execute(
                """INSERT INTO entity_mappings
                   (entity_type, original_value, normalized_value, placeholder,
                    first_seen_at, last_seen_at, source_document, created_by)
                   VALUES (?, ?, ?, ?, ?, ?, ?, 'auto')""",
                (
                    entity_type.value,
                    original_value,
                    _normalize(original_value),
                    placeholder,
                    now,
                    now,
                    source_document,
                ),
            )
            self._conn.commit()
        except Exception:
            self._conn.rollback()
            raise
        return EntityMapping(
            entity_type=entity_type,
            original_value=original_value,
            placeholder=placeholder,
            first_seen=datetime.fromisoformat(now),
            last_seen=datetime.fromisoformat(now),
            source_document=source_document,
        )

    def get_all_mappings(self) -> list[EntityMapping]:
        """Return all stored mappings."""
        rows = self._conn.execute(
            "SELECT * FROM entity_mappings ORDER BY entity_type, placeholder"
        ).fetchall()
        return [self._row_to_mapping(r) for r in rows]

    def get_placeholder(self, placeholder: str) -> EntityMapping | None:
        """Look up a mapping by its placeholder string."""
        row = self._conn.execute(
            "SELECT * FROM entity_mappings WHERE placeholder = ?",
            (placeholder,),
        ).fetchone()
        if row is None:
            return None
        return self._row_to_mapping(row)

    def import_entities(self, entities: list[dict]) -> int:
        """Import entities from a list of dicts.

        Each dict must have 'entity_type' and 'original_value' keys,
        and optionally 'source_document'.
        Returns the count of newly imported entities (duplicates are skipped).
        """
        imported = 0
        for entry in entities:
            entity_type = EntityType(entry["entity_type"])
            original_value = entry["original_value"]
            source_document = entry.get("source_document", "")
            existing = self.get_mapping(entity_type, original_value)
            if existing is None:
                now = _now_iso()
                placeholder = self._next_placeholder(entity_type)
                self._conn.execute(
                    """INSERT INTO entity_mappings
                       (entity_type, original_value, normalized_value, placeholder,
                        first_seen_at, last_seen_at, source_document, created_by)
                       VALUES (?, ?, ?, ?, ?, ?, ?, 'import')""",
                    (
                        entity_type.value,
                        original_value,
                        _normalize(original_value),
                        placeholder,
                        now,
                        now,
                        source_document,
                    ),
                )
                imported += 1
        self._conn.commit()
        return imported

    def update_last_seen(
        self, entity_type: EntityType, original_value: str
    ) -> None:
        """Update the last_seen timestamp for an existing mapping."""
        self._conn.execute(
            """UPDATE entity_mappings SET last_seen_at = ?
               WHERE entity_type = ? AND normalized_value = ?""",
            (_now_iso(), entity_type.value, _normalize(original_value)),
        )
        self._conn.commit()

    def get_mapping_count_by_type(self) -> dict[str, int]:
        """Return a count of mappings grouped by entity type."""
        rows = self._conn.execute(
            "SELECT entity_type, COUNT(*) as cnt FROM entity_mappings GROUP BY entity_type"
        ).fetchall()
        return {row["entity_type"]: row["cnt"] for row in rows}

    def get_total_mapping_count(self) -> int:
        """Return the total number of mappings."""
        row = self._conn.execute(
            "SELECT COUNT(*) as cnt FROM entity_mappings"
        ).fetchone()
        return row["cnt"]

    def get_municipality_names(self) -> list[str]:
        """Return all municipality names from the reference table."""
        rows = self._conn.execute(
            "SELECT name FROM ref_municipalities ORDER BY name"
        ).fetchall()
        return [row["name"] for row in rows]

    def get_ref_municipality_count(self) -> int:
        """Return the number of rows in the ref_municipalities table."""
        row = self._conn.execute(
            "SELECT COUNT(*) as cnt FROM ref_municipalities"
        ).fetchone()
        return row["cnt"]

    def get_ref_military_unit_count(self) -> int:
        """Return the number of rows in the ref_military_units table."""
        row = self._conn.execute(
            "SELECT COUNT(*) as cnt FROM ref_military_units"
        ).fetchone()
        return row["cnt"]

    def import_municipalities(self, names: list[str]) -> int:
        """Bulk-insert municipality names (duplicates are silently skipped)."""
        imported = 0
        for name in names:
            try:
                self._conn.execute(
                    "INSERT OR IGNORE INTO ref_municipalities (name) VALUES (?)",
                    (name,),
                )
                imported += 1
            except sqlite3.OperationalError:
                pass
        self._conn.commit()
        return imported

    def import_municipalities_full(self, rows: list[dict]) -> int:
        """Bulk-insert municipalities with plz/canton data. Skips if table already populated."""
        if self.get_ref_municipality_count() > 0:
            return 0
        for row in rows:
            name = row.get("name", "").strip()
            if not name:
                continue
            self._conn.execute(
                "INSERT INTO ref_municipalities (name, canton, plz) VALUES (?, ?, ?)",
                (name, row.get("canton", ""), row.get("plz", "")),
            )
        self._conn.commit()
        return self.get_ref_municipality_count()

    def import_military_units(self, units: list[dict]) -> int:
        """Bulk-insert military unit/rank reference data. Skips if table already populated."""
        if self.get_ref_military_unit_count() > 0:
            return 0
        for unit in units:
            pattern = unit.get("abbreviation", "").strip()
            unit_type = unit.get("type", "").strip()
            if not pattern:
                continue
            self._conn.execute(
                """INSERT INTO ref_military_units
                   (pattern, unit_type, parent_unit, full_name, abbreviation, level, category)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    pattern,
                    unit_type,
                    unit.get("parent", ""),
                    unit.get("full_name", ""),
                    unit.get("abbreviation", pattern),
                    unit.get("level", ""),
                    unit.get("category", ""),
                ),
            )
        self._conn.commit()
        return self.get_ref_military_unit_count()

    def get_unit_by_abbreviation(self, abbreviation: str) -> dict | None:
        """Look up a concrete unit by its abbreviation."""
        row = self._conn.execute(
            "SELECT * FROM ref_military_units WHERE abbreviation = ? AND unit_type = 'concrete_unit'",
            (abbreviation,),
        ).fetchone()
        return dict(row) if row else None

    def get_unit_parent_chain(self, full_name: str) -> list[dict]:
        """Return the parent chain from the given unit up to root.

        Returns list starting from root down to (and including) the given unit.
        """
        chain: list[dict] = []
        current = full_name
        seen: set[str] = set()
        while current and current != "_root" and current not in seen:
            seen.add(current)
            row = self._conn.execute(
                "SELECT * FROM ref_military_units WHERE full_name = ?",
                (current,),
            ).fetchone()
            if row is None:
                break
            chain.append(dict(row))
            current = row["parent_unit"] if "parent_unit" in row.keys() else ""
        chain.reverse()  # root first
        return chain

    def get_unit_children(self, parent_full_name: str) -> list[dict]:
        """Return direct children of a unit ordered by abbreviation."""
        rows = self._conn.execute(
            "SELECT * FROM ref_military_units WHERE parent_unit = ? ORDER BY abbreviation",
            (parent_full_name,),
        ).fetchall()
        return [dict(r) for r in rows]

    def get_unit_siblings(self, full_name: str) -> list[dict]:
        """Return sibling units (same parent, excluding self) ordered by abbreviation."""
        row = self._conn.execute(
            "SELECT parent_unit FROM ref_military_units WHERE full_name = ?",
            (full_name,),
        ).fetchone()
        if row is None:
            return []
        parent = row["parent_unit"]
        rows = self._conn.execute(
            "SELECT * FROM ref_military_units WHERE parent_unit = ? AND full_name != ? ORDER BY abbreviation",
            (parent, full_name),
        ).fetchall()
        return [dict(r) for r in rows]

    def get_file_tracking(
        self, file_path: str, operation: str
    ) -> dict | None:
        """Return tracking record for a file+operation, or None if not tracked."""
        row = self._conn.execute(
            "SELECT * FROM file_tracking WHERE file_path = ? AND operation = ?",
            (file_path, operation),
        ).fetchone()
        if row is None:
            return None
        return dict(row)

    def upsert_file_tracking(
        self,
        file_path: str,
        content_hash: str,
        operation: str,
        output_path: str = "",
        entity_count: int = 0,
    ) -> None:
        """Insert or update a file tracking record."""
        now = _now_iso()
        self._conn.execute(
            """INSERT INTO file_tracking
               (file_path, content_hash, output_path, operation, processed_at, entity_count)
               VALUES (?, ?, ?, ?, ?, ?)
               ON CONFLICT(file_path, operation) DO UPDATE SET
                   content_hash = excluded.content_hash,
                   output_path = excluded.output_path,
                   processed_at = excluded.processed_at,
                   entity_count = excluded.entity_count""",
            (file_path, content_hash, output_path, operation, now, entity_count),
        )
        self._conn.commit()

    def clear_reference_data(self) -> None:
        """Delete all reference data (municipalities and military units).

        Used by 'milanon db init --force' to allow clean re-initialization.
        """
        self._conn.execute("DELETE FROM ref_municipalities")
        self._conn.execute("DELETE FROM ref_military_units")
        self._conn.commit()

    def reset_all_mappings(self) -> dict[str, int]:
        """Delete all entity mappings and file tracking records.

        Reference data (municipalities, military units) is preserved.
        Returns a dict with counts of deleted rows per table.
        """
        mappings_deleted = self._conn.execute("DELETE FROM entity_mappings").rowcount
        tracking_deleted = self._conn.execute("DELETE FROM file_tracking").rowcount
        self._conn.commit()
        return {"entity_mappings": mappings_deleted, "file_tracking": tracking_deleted}

    def reset_everything(self) -> dict[str, int]:
        """Delete ALL rows from every table, including reference data.

        After this call the database is empty and ready for re-initialization.
        Returns a dict with counts of deleted rows per table.
        """
        tables = [
            "entity_mappings",
            "entity_aliases",
            "file_tracking",
            "processing_log",
            "ref_municipalities",
            "ref_military_units",
        ]
        counts: dict[str, int] = {}
        for table in tables:
            counts[table] = self._conn.execute(f"DELETE FROM {table}").rowcount  # noqa: S608
        self._conn.commit()
        return counts

    def _next_placeholder(self, entity_type: EntityType) -> str:
        """Generate the next placeholder for a given entity type.

        Uses MAX of existing numeric suffixes (not COUNT) so that placeholder
        numbers remain monotonically increasing even when mappings are deleted.
        """
        # Placeholder format: [ENTITY_TYPE_NNN]
        # Extract the trailing 3-digit number by taking the 4 chars before the ']',
        # i.e. substr(placeholder, length-4, 3) gives the numeric suffix.
        row = self._conn.execute(
            """SELECT COALESCE(
                   MAX(CAST(substr(placeholder,
                       length(placeholder) - 3,
                       3
                   ) AS INTEGER)),
                   0
               ) AS max_num
               FROM entity_mappings
               WHERE entity_type = ?""",
            (entity_type.value,),
        ).fetchone()
        next_num = (row["max_num"] or 0) + 1
        return f"[{entity_type.value}_{next_num:03d}]"

    @staticmethod
    def _row_to_mapping(row: sqlite3.Row) -> EntityMapping:
        """Convert a database row to an EntityMapping."""
        return EntityMapping(
            entity_type=EntityType(row["entity_type"]),
            original_value=row["original_value"],
            placeholder=row["placeholder"],
            first_seen=datetime.fromisoformat(row["first_seen_at"]),
            last_seen=datetime.fromisoformat(row["last_seen_at"]),
            source_document=row["source_document"] or "",
        )
