"""MappingService — business logic for entity-to-placeholder mapping."""

from __future__ import annotations

import re

from milanon.domain.entities import EntityType
from milanon.domain.protocols import MappingRepository


def normalize_value(value: str) -> str:
    """Normalize a value for case-insensitive, whitespace-insensitive matching.

    This is the single source of truth for normalization logic (CR-011).
    Collapses all internal whitespace (newlines, tabs, multiple spaces) to a
    single space so that 'Inf\\nBat 56' and 'Inf Bat 56' map to the same entry.

    Repository implementations should import this function rather than
    duplicating the normalization logic.
    """
    return re.sub(r"\s+", " ", value.strip()).lower()


class MappingService:
    """Orchestrates entity mapping operations via the repository protocol.

    This service sits in the domain layer and depends only on the
    MappingRepository protocol, not on any concrete implementation.
    """

    def __init__(self, repository: MappingRepository) -> None:
        self._repository = repository

    def has_mapping(self, entity_type: EntityType, value: str) -> bool:
        """Return True if a mapping already exists for this entity type and value."""
        return self._repository.get_mapping(entity_type, value) is not None

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

    def get_all_mappings(self):
        """Return all stored entity mappings (delegates to repository)."""
        return self._repository.get_all_mappings()

    def resolve_placeholder(self, placeholder: str) -> str | None:
        """Resolve a placeholder back to its original value.

        Returns None if the placeholder is not found.
        """
        mapping = self._repository.get_placeholder(placeholder)
        if mapping is None:
            return None
        return mapping.original_value

    def get_or_create_placeholder_with_alias(
        self, entity_type: EntityType, value: str, source_document: str = ""
    ) -> str:
        """Like get_or_create_placeholder, but checks EINHEIT aliases first.

        For EINHEIT entities, checks if the value is an alias of an existing
        mapping (e.g. 'Inf Ustü Kp 56' is an alias for 'Inf Ustü Kp 56/4').
        If so, returns the existing placeholder instead of creating a new one.
        """
        if entity_type != EntityType.EINHEIT:
            return self.get_or_create_placeholder(entity_type, value, source_document)

        # Check exact match first
        existing = self._repository.get_mapping(entity_type, value)
        if existing is not None:
            return existing.placeholder

        # Check aliases
        canonical = self._resolve_einheit_alias(value)
        if canonical and canonical != value:
            existing = self._repository.get_mapping(entity_type, canonical)
            if existing is not None:
                return existing.placeholder

        # No alias found — create new mapping
        mapping = self._repository.create_mapping(entity_type, value, source_document)
        return mapping.placeholder

    def _resolve_einheit_alias(self, value: str) -> str | None:
        """Resolve an EINHEIT value to its canonical form using naming conventions.

        Rules:
        - 'Inf Ustü Kp 56' → 'Inf Ustü Kp 56/4' (Ustü is always /4)
        - 'Inf Kp 56/0' → 'Inf Stabskp 56' (Kp XX/0 = Stabskp)
        - 'Inf Ustü Kp 56/4' → 'Inf Ustü Kp 56/4' (already canonical)

        Returns the canonical form, or None if no alias rule applies.
        """
        normalized = re.sub(r"\s+", " ", value.strip())

        # Rule 1: "Ustü Kp XX" without /4 → add /4
        if re.match(r".+Ustü\s+Kp\s+\d+$", normalized) and "/4" not in normalized:
            return normalized + "/4"

        # Rule 2: "Kp XX/0" → "Stabskp XX"
        kp0_match = re.match(r"(.+)\s+Kp\s+(\d+)/0$", normalized)
        if kp0_match:
            prefix = kp0_match.group(1)
            number = kp0_match.group(2)
            return f"{prefix} Stabskp {number}"

        # Rule 3: "Stabskp XX" is already canonical
        if re.match(r".+\s+Stabskp\s+\d+$", normalized):
            return normalized

        return None

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
