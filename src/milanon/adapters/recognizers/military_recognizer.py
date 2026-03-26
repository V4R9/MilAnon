"""Military recognizer — detects rank+name compounds, units, and functions."""

from __future__ import annotations

import re

from milanon.config.military_patterns import (
    FUNCTION_ABBREVIATIONS,
    RANK_ABBREVIATIONS,
    RANK_NAME_PATTERN,
    TER_DIV_PATTERN,
    UNIT_PATTERN,
)
from milanon.domain.entities import DetectedEntity, EntityType, ExtractedDocument

# Pre-compiled function patterns (longest-first to avoid partial matches).
# Use (?<!\w)/(?!\w) instead of \b — reliable with non-ASCII characters.
_FUNCTION_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    (fn, re.compile(r"(?<!\w)" + re.escape(fn) + r"(?!\w)"))
    for fn in FUNCTION_ABBREVIATIONS
]

# Pre-compiled standalone-rank pattern (rank NOT followed by a name).
# Used to detect rank designations used alone (e.g., in tables).
_RANK_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    (rank, re.compile(r"(?<!\w)" + re.escape(rank) + r"(?!\w)"))
    for rank in RANK_ABBREVIATIONS
]


class MilitaryRecognizer:
    """Detects Swiss Army-specific entities in extracted document text.

    Detection order per document (all non-overlapping):
    1. Rank + Name compounds  → GRAD_FUNKTION (rank) + PERSON (name)
    2. Unit designations      → EINHEIT
    3. Function designations  → FUNKTION
    """

    def recognize(self, document: ExtractedDocument) -> list[DetectedEntity]:
        """Detect military entities in document text."""
        text = document.text_content
        entities: list[DetectedEntity] = []
        entities.extend(self._detect_rank_name_compounds(text))
        entities.extend(self._detect_units(text))
        entities.extend(self._detect_functions(text))
        return entities

    # ------------------------------------------------------------------
    # Rank + Name detection
    # ------------------------------------------------------------------

    def _detect_rank_name_compounds(self, text: str) -> list[DetectedEntity]:
        """Detect 'Rank Firstname LASTNAME' compounds.

        For each match:
        - GRAD_FUNKTION entity for the rank token(s)
        - PERSON entity for the name part (firstname? + LASTNAME)
        """
        entities: list[DetectedEntity] = []
        for match in RANK_NAME_PATTERN.finditer(text):
            rank_value = match.group(1)

            rank_start = match.start(1)
            rank_end = match.end(1)
            name_start = match.start(2)
            name_end = match.end(2)

            # Trim trailing whitespace from name offsets
            while name_end > name_start and text[name_end - 1].isspace():
                name_end -= 1

            entities.append(
                DetectedEntity(
                    entity_type=EntityType.GRAD_FUNKTION,
                    original_value=rank_value,
                    start_offset=rank_start,
                    end_offset=rank_end,
                    confidence=1.0,
                    source="military",
                )
            )
            entities.append(
                DetectedEntity(
                    entity_type=EntityType.PERSON,
                    original_value=text[name_start:name_end],
                    start_offset=name_start,
                    end_offset=name_end,
                    confidence=1.0,
                    source="military",
                )
            )
        return entities

    # ------------------------------------------------------------------
    # Unit detection
    # ------------------------------------------------------------------

    def _detect_units(self, text: str) -> list[DetectedEntity]:
        """Detect unit designations like 'Inf Bat 56', 'Inf Kp 56/1', 'Ter Div 2'.

        Normalizes matched values (collapses newlines/whitespace) and skips
        single-word fragments (e.g. bare "Ter" or "Inf") that are not units.
        """
        entities: list[DetectedEntity] = []
        for pattern in (UNIT_PATTERN, TER_DIV_PATTERN):
            for match in pattern.finditer(text):
                normalized = re.sub(r"\s+", " ", match.group(0).strip())
                if len(normalized.split()) < 2:
                    continue
                entities.append(
                    DetectedEntity(
                        entity_type=EntityType.EINHEIT,
                        original_value=normalized,
                        start_offset=match.start(),
                        end_offset=match.end(),
                        confidence=1.0,
                        source="military",
                    )
                )
        return entities

    # ------------------------------------------------------------------
    # Function detection
    # ------------------------------------------------------------------

    def _detect_functions(self, text: str) -> list[DetectedEntity]:
        """Detect standalone function designations like 'Bat Kdt', 'Kdt Stv'."""
        entities: list[DetectedEntity] = []
        for _fn_value, pattern in _FUNCTION_PATTERNS:
            for match in pattern.finditer(text):
                entities.append(
                    DetectedEntity(
                        entity_type=EntityType.FUNKTION,
                        original_value=match.group(0),
                        start_offset=match.start(),
                        end_offset=match.end(),
                        confidence=0.9,
                        source="military",
                    )
                )
        return entities
