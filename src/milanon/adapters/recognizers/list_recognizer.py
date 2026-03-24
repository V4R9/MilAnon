"""List recognizer — lookup against mapping DB and reference municipalities."""

from __future__ import annotations

import re

from milanon.domain.entities import DetectedEntity, EntityType, ExtractedDocument
from milanon.domain.protocols import MappingRepository

# Minimum character length for municipality name matching.
# Names shorter than this are skipped: ultra-short names like "Au" (2), "Ins" (3),
# "Egg" (3) cause far too many false positives even with word-boundary checks.
_MIN_MUNICIPALITY_LEN: int = 4

# Minimum length for DB entity values to be matched in free text.
# Single characters are never matched to avoid trivial false positives.
_MIN_ENTITY_LEN: int = 2

# Municipalities excluded entirely from matching — no context check can save them.
# "Alle" (PLZ 2942, JU) excluded entirely — too common as German word "alle"
# (= everyone/all). 20 false positives in real-world test on 70-page military
# document. Risk of missing a genuine reference to this 107-resident municipality
# is negligible compared to the text destruction caused by false matches.
_MUNICIPALITY_EXCLUDED: frozenset[str] = frozenset({"alle"})

# Municipalities whose names are also common German words.  These are only
# matched when a context signal (PLZ or locative preposition) appears within
# _CONTEXT_WINDOW characters before the match.
_MUNICIPALITY_STOPWORDS: frozenset[str] = frozenset(
    {
        "wald",   # multiple — common German word
        "berg",   # multiple — common German word
        "matt",   # multiple — common German word
        "horn",   # multiple — common German word
    }
)

# Characters of look-back text scanned for a context signal
_CONTEXT_WINDOW: int = 40

# Signals that a place reference is intended: 4-digit PLZ or locative preposition
_CONTEXT_SIGNAL_PATTERN: re.Pattern[str] = re.compile(
    r"(?:\b\d{4}\b|(?<!\w)(?:in|nach|bei|von|aus|nach|via)(?!\w))",
    re.IGNORECASE,
)


def _word_boundary_pattern(value: str) -> re.Pattern[str]:
    """Return a case-insensitive pattern with reliable Unicode word boundaries.

    Uses (?<!\\w) / (?!\\w) lookbehind/lookahead instead of \\b because
    Python's \\b is unreliable with non-ASCII characters (umlauts, accents).
    This prevents matching 'Bern' inside 'Arbeitgebern' or 'Au' inside 'Ausbildung'.
    """
    return re.compile(r"(?<!\w)" + re.escape(value) + r"(?!\w)", re.IGNORECASE)


class ListRecognizer:
    """Recognizes known entities by looking them up in the mapping database.

    Also detects Swiss municipality names from an optional reference list.
    Matching is case-insensitive via normalized comparison.
    All matches are word-boundary protected using (?<!\\w)/(?!\\w) lookbehind/
    lookahead to prevent matching inside longer words.

    Priority: lower than PatternRecognizer and MilitaryRecognizer.
    Confidence: 0.9 for DB matches, 0.8 for municipality matches.
    """

    def __init__(
        self,
        repository: MappingRepository,
        municipality_names: list[str] | None = None,
    ) -> None:
        self._repository = repository
        # None = fetch from DB on demand; empty list = no municipalities
        self._municipality_names: list[str] | None = municipality_names

    def recognize(self, document: ExtractedDocument) -> list[DetectedEntity]:
        """Find all known entities in the document text."""
        text = document.text_content
        entities: list[DetectedEntity] = []
        entities.extend(self._match_known_mappings(text))
        entities.extend(self._match_municipalities(text))
        return entities

    # ------------------------------------------------------------------

    def _match_known_mappings(self, text: str) -> list[DetectedEntity]:
        """Match all known entity values from the mapping DB.

        Each value is matched with Unicode-safe word boundaries to prevent
        false positives inside longer words (e.g. 'Bern' in 'Arbeitgebern').

        PERFORMANCE NOTE: This compiles one regex per DB mapping on every call.
        For large databases (thousands of mappings), consider caching compiled
        patterns keyed by (mapping_id, original_value) or building a single
        combined alternation pattern.
        """
        entities: list[DetectedEntity] = []
        all_mappings = self._repository.get_all_mappings()
        for mapping in all_mappings:
            value = mapping.original_value
            if not value or len(value) < _MIN_ENTITY_LEN:
                continue
            pattern = _word_boundary_pattern(value)
            for match in pattern.finditer(text):
                entities.append(
                    DetectedEntity(
                        entity_type=mapping.entity_type,
                        original_value=match.group(0),
                        start_offset=match.start(),
                        end_offset=match.end(),
                        confidence=0.9,
                        source="list",
                    )
                )
        return entities

    def _match_municipalities(self, text: str) -> list[DetectedEntity]:
        """Match Swiss municipality names — word-boundary protected.

        Names shorter than _MIN_MUNICIPALITY_LEN characters are skipped entirely
        because ultra-short names (Au=2, Ins=3, Egg=3) cause too many false positives
        even with word boundary checks.
        """
        # If no explicit list was given, fetch from the repository's ref table
        names = (
            self._municipality_names
            if self._municipality_names is not None
            else self._repository.get_municipality_names()
        )
        entities: list[DetectedEntity] = []
        for name in names:
            if not name or len(name) < _MIN_MUNICIPALITY_LEN:
                continue
            if name.lower() in _MUNICIPALITY_EXCLUDED:
                continue
            is_stopword = name.lower() in _MUNICIPALITY_STOPWORDS
            pattern = _word_boundary_pattern(name)
            for match in pattern.finditer(text):
                if is_stopword:
                    preceding = text[max(0, match.start() - _CONTEXT_WINDOW) : match.start()]
                    if not _CONTEXT_SIGNAL_PATTERN.search(preceding):
                        continue
                entities.append(
                    DetectedEntity(
                        entity_type=EntityType.ORT,
                        original_value=match.group(0),
                        start_offset=match.start(),
                        end_offset=match.end(),
                        confidence=0.8,
                        source="list",
                    )
                )
        return entities
