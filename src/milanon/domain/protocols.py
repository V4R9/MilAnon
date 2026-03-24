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
