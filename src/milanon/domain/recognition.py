"""Recognition pipeline — orchestrates all recognizers with conflict resolution."""

from __future__ import annotations

from milanon.domain.entities import DetectedEntity, ExtractedDocument
from milanon.domain.protocols import EntityRecognizer

# Priority constants — lower number = higher priority
_PRIORITY: dict[str, int] = {
    "pattern": 1,
    "military": 2,
    "list": 3,
}

_DEFAULT_PRIORITY = 99


def _source_priority(entity: DetectedEntity) -> int:
    return _PRIORITY.get(entity.source, _DEFAULT_PRIORITY)


def _spans_overlap(a: DetectedEntity, b: DetectedEntity) -> bool:
    """Return True if two entities have any character overlap."""
    return a.start_offset < b.end_offset and b.start_offset < a.end_offset


class RecognitionPipeline:
    """Orchestrates multiple EntityRecognizers with priority-based conflict resolution.

    Pipeline (ADR-004):
    1. PatternRecognizer  (priority 1 — highest)
    2. MilitaryRecognizer (priority 2)
    3. ListRecognizer     (priority 3 — lowest)

    Conflict resolution (overlapping spans):
    - Higher-priority recognizer wins.
    - At equal priority, longer span wins.
    - At equal priority and equal length, first encountered wins.
    """

    def __init__(self, recognizers: list[EntityRecognizer]) -> None:
        self._recognizers = recognizers

    def recognize(self, document: ExtractedDocument) -> list[DetectedEntity]:
        """Run all recognizers and return a deduplicated, conflict-free list."""
        all_entities: list[DetectedEntity] = []
        for recognizer in self._recognizers:
            all_entities.extend(recognizer.recognize(document))
        return self._resolve_conflicts(all_entities)

    # ------------------------------------------------------------------

    def _resolve_conflicts(
        self, entities: list[DetectedEntity]
    ) -> list[DetectedEntity]:
        """Return conflict-free entities, applying priority and length rules."""
        # Sort: highest priority first, then longest span, then earliest start
        candidates = sorted(
            entities,
            key=lambda e: (
                _source_priority(e),   # lower = more important
                -e.span_length,        # longer = more important (negate for ascending sort)
                e.start_offset,
            ),
        )

        accepted: list[DetectedEntity] = []
        for candidate in candidates:
            if not any(_spans_overlap(candidate, kept) for kept in accepted):
                accepted.append(candidate)

        # Return sorted by offset for convenient processing
        return sorted(accepted, key=lambda e: e.start_offset)
