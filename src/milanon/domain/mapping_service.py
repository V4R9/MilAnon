"""MappingService — business logic for entity-to-placeholder mapping."""

from __future__ import annotations

from milanon.domain.entities import EntityType
from milanon.domain.protocols import MappingRepository


class MappingService:
    """Orchestrates entity mapping operations via the repository protocol.

    This service sits in the domain layer and depends only on the
    MappingRepository protocol, not on any concrete implementation.
    """

    def __init__(self, repository: MappingRepository) -> None:
        self._repository = repository

    def get_or_create_placeholder(
        self, entity_type: EntityType, value: str, source_document: str = ""
    ) -> str:
        """Return the placeholder for a value, creating a new mapping if needed.

        If the entity already exists, its last_seen timestamp is updated
        and the existing placeholder is returned.
        """
        existing = self._repository.get_mapping(entity_type, value)
        if existing is not None:
            return existing.placeholder
        mapping = self._repository.create_mapping(
            entity_type, value, source_document
        )
        return mapping.placeholder

    def resolve_placeholder(self, placeholder: str) -> str | None:
        """Resolve a placeholder back to its original value.

        Returns None if the placeholder is not found.
        """
        mapping = self._repository.get_placeholder(placeholder)
        if mapping is None:
            return None
        return mapping.original_value

    def get_statistics(self) -> dict:
        """Return mapping statistics: total count and per-type breakdown."""
        all_mappings = self._repository.get_all_mappings()
        by_type: dict[str, int] = {}
        for mapping in all_mappings:
            key = mapping.entity_type.value
            by_type[key] = by_type.get(key, 0) + 1
        return {
            "total": len(all_mappings),
            "by_type": by_type,
        }
