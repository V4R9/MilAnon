"""Domain protocols — abstract interfaces for adapters (Dependency Inversion)."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable

from milanon.domain.entities import (
    DetectedEntity,
    EntityMapping,
    EntityType,
    ExtractedDocument,
)


@runtime_checkable
class DocumentParser(Protocol):
    """Protocol for parsing documents into ExtractedDocument."""

    def parse(self, path: Path) -> ExtractedDocument:
        """Parse a file and return its extracted content."""
        ...

    def supported_extensions(self) -> list[str]:
        """Return the file extensions this parser can handle (e.g. ['.eml'])."""
        ...


@runtime_checkable
class EntityRecognizer(Protocol):
    """Protocol for detecting entities in extracted documents."""

    def recognize(self, document: ExtractedDocument) -> list[DetectedEntity]:
        """Detect entities in the given document and return them."""
        ...


@runtime_checkable
class MappingRepository(Protocol):
    """Protocol for persisting entity-to-placeholder mappings."""

    def get_mapping(
        self, entity_type: EntityType, original_value: str
    ) -> EntityMapping | None:
        """Look up an existing mapping by type and original value."""
        ...

    def create_mapping(
        self, entity_type: EntityType, original_value: str, source_document: str = ""
    ) -> EntityMapping:
        """Create a new mapping with an auto-generated placeholder."""
        ...

    def get_all_mappings(self) -> list[EntityMapping]:
        """Return all stored mappings."""
        ...

    def get_placeholder(self, placeholder: str) -> EntityMapping | None:
        """Look up a mapping by its placeholder string."""
        ...

    def import_entities(self, entities: list[dict]) -> int:
        """Import entities from a list of dicts. Return the count of imported entities."""
        ...

    def close(self) -> None:
        """Close the repository and release resources."""
        ...


@runtime_checkable
class FileTrackingRepository(Protocol):
    """Protocol for file tracking operations (incremental processing)."""

    def get_file_tracking(self, file_path: str, operation: str) -> dict | None:
        """Return tracking record for a file+operation, or None if not tracked."""
        ...

    def upsert_file_tracking(
        self,
        file_path: str,
        content_hash: str,
        operation: str,
        output_path: str = "",
        entity_count: int = 0,
    ) -> None:
        """Insert or update a file tracking record."""
        ...

    def get_file_tracking_by_hash(
        self, content_hash: str, operation: str
    ) -> dict | None:
        """Find a file tracking record by content hash (for rename detection)."""
        ...


@runtime_checkable
class ReferenceDataRepository(Protocol):
    """Protocol for reference data operations (municipalities, military units)."""

    def get_ref_municipality_count(self) -> int:
        """Return the number of rows in the ref_municipalities table."""
        ...

    def get_ref_military_unit_count(self) -> int:
        """Return the number of rows in the ref_military_units table."""
        ...

    def import_municipalities_full(self, rows: list[dict]) -> int:
        """Bulk-insert municipalities with plz/canton data."""
        ...

    def import_military_units(self, units: list[dict]) -> int:
        """Bulk-insert military unit/rank reference data."""
        ...

    def clear_reference_data(self) -> None:
        """Delete all reference data (municipalities and military units)."""
        ...
