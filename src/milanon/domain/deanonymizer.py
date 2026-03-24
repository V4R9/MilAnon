"""DeAnonymizer — restores placeholders to their original values."""

from __future__ import annotations

import logging
import re

from milanon.domain.anonymizer import LEGEND_PATTERN
from milanon.domain.mapping_service import MappingService

logger = logging.getLogger(__name__)

# Matches any placeholder of the form [ENTITY_TYPE_NNN]
_PLACEHOLDER_RE = re.compile(r"\[([A-Z_]+)_(\d{3})\]")


class DeAnonymizer:
    """Restores placeholder tokens to their original values.

    Uses MappingService to look up each [ENTITY_TYPE_NNN] token.
    Placeholders not found in the DB are left as-is with a warning.
    """

    def __init__(self, mapping_service: MappingService) -> None:
        self._mapping_service = mapping_service

    def deanonymize(self, content: str) -> tuple[str, list[str]]:
        """Replace all placeholders in content with their original values.

        Args:
            content: Anonymized text (may include a legend block).

        Returns:
            Tuple of (restored_text, warnings).
            warnings contains one entry per unresolved placeholder.
        """
        # Strip legend header if present
        text = LEGEND_PATTERN.sub("", content).lstrip()

        warnings: list[str] = []
        resolved: set[str] = set()
        unresolved: set[str] = set()

        def _replace(match: re.Match[str]) -> str:
            placeholder = match.group(0)
            original = self._mapping_service.resolve_placeholder(placeholder)
            if original is not None:
                resolved.add(placeholder)
                return original
            unresolved.add(placeholder)
            logger.warning("Unresolved placeholder: %s", placeholder)
            return placeholder  # leave as-is

        restored = _PLACEHOLDER_RE.sub(_replace, text)

        for ph in sorted(unresolved):
            warnings.append(f"Placeholder not found in mapping DB: {ph}")

        return restored, warnings

    def resolve_placeholder(self, placeholder: str) -> str | None:
        """Return the original value for a placeholder token, or None if not found."""
        return self._mapping_service.resolve_placeholder(placeholder)

    def find_placeholders(self, content: str) -> list[str]:
        """Return all placeholder tokens found in the text (in order, no dedup)."""
        return [m.group(0) for m in _PLACEHOLDER_RE.finditer(content)]
