"""Pattern recognizer — regex-based detection for structured PII."""

from __future__ import annotations

import re

from milanon.config.military_patterns import (
    ADRESSE_PATTERN,
    AHV_PATTERN,
    CO_NAME_PATTERN,
    EMAIL_PATTERN,
    INITIAL_SURNAME_PATTERN,
    NEAR_AHV_PATTERN,
    PHONE_COMPACT_PATTERN,
    PHONE_INTL_GENERIC_PATTERN,
    PHONE_INTL_PATTERN,
    PHONE_LOCAL_PATTERN,
)
from milanon.domain.entities import DetectedEntity, EntityType, ExtractedDocument

# Ordered list of (EntityType, compiled pattern) pairs.
# Phone patterns are tried in order: international first (longer match wins
# naturally since they start with + which compact/local can't match).
_PATTERNS: list[tuple[EntityType, re.Pattern[str]]] = [
    (EntityType.AHV_NR, AHV_PATTERN),
    (EntityType.EMAIL, EMAIL_PATTERN),
    (EntityType.TELEFON, PHONE_INTL_PATTERN),
    (EntityType.TELEFON, PHONE_LOCAL_PATTERN),
    (EntityType.TELEFON, PHONE_COMPACT_PATTERN),
    (EntityType.TELEFON, PHONE_INTL_GENERIC_PATTERN),
    (EntityType.ADRESSE, ADRESSE_PATTERN),
    (EntityType.PERSON, INITIAL_SURNAME_PATTERN),
]

# dd.mm.yyyy — only matched in personnel context (B-006)
_DATE_PATTERN: re.Pattern[str] = re.compile(r"\b\d{2}\.\d{2}\.\d{4}\b")

# Keywords that signal a date is a birth date, not an operational date.
# Look-back window: 80 characters before the date match.
_BIRTHDATE_CONTEXT_WINDOW: int = 80
_BIRTHDATE_KEYWORDS: re.Pattern[str] = re.compile(
    r"(?:geboren|Geburtsdatum|Geburtstag|geb\.|Jahrgang|JG|Geb\.)",
    re.IGNORECASE,
)


class PatternRecognizer:
    """Recognizes structured PII in documents via compiled regex patterns.

    Detects: AHV_NR, EMAIL, TELEFON (3 formats), GEBURTSDATUM, ADRESSE.
    All matches have confidence=1.0 (deterministic regex).
    """

    def recognize(self, document: ExtractedDocument) -> list[DetectedEntity]:
        """Find all pattern-detectable entities in the document text.

        Returns a list of DetectedEntity objects, one per match.
        Overlapping matches (e.g. same phone in different formats) are
        resolved by the RecognitionPipeline, not here.
        """
        text = document.text_content
        entities: list[DetectedEntity] = []
        for entity_type, pattern in _PATTERNS:
            for match in pattern.finditer(text):
                entities.append(
                    DetectedEntity(
                        entity_type=entity_type,
                        original_value=match.group(0).strip(),
                        start_offset=match.start(),
                        end_offset=match.end(),
                        confidence=1.0,
                        source="pattern",
                    )
                )
        entities.extend(self._match_birthdates(text))
        entities.extend(self._match_display_names(document))
        entities.extend(self._match_co_names(text))
        entities.extend(self._match_near_ahv(text))
        return entities

    def _match_display_names(self, document: ExtractedDocument) -> list[DetectedEntity]:
        """Detect display names extracted from EML headers.

        Uses metadata["display_names"] populated by EmlParser. Each name
        is searched in the document text with word boundaries and flagged
        as PERSON with confidence 0.85 (we KNOW it's a name because the
        EML header format guarantees it).
        """
        display_names = document.metadata.get("display_names", [])
        if not display_names:
            return []

        entities: list[DetectedEntity] = []
        text = document.text_content
        for name in display_names:
            pattern = re.compile(r"(?<!\w)" + re.escape(name) + r"(?!\w)")
            for match in pattern.finditer(text):
                entities.append(
                    DetectedEntity(
                        entity_type=EntityType.PERSON,
                        original_value=match.group(0),
                        start_offset=match.start(),
                        end_offset=match.end(),
                        confidence=0.85,
                        source="pattern",
                    )
                )
        return entities

    def _match_co_names(self, text: str) -> list[DetectedEntity]:
        """Detect person names in c/o address prefixes (B-016).

        Matches patterns like 'c/o Walter Fanger', 'p.A. Maria Schmidt',
        'bei Hans Müller'. The name part (group 1) is flagged as PERSON
        with confidence 0.8.
        """
        entities: list[DetectedEntity] = []
        for match in CO_NAME_PATTERN.finditer(text):
            name = match.group(1).strip()
            entities.append(
                DetectedEntity(
                    entity_type=EntityType.PERSON,
                    original_value=name,
                    start_offset=match.start(1),
                    end_offset=match.end(1),
                    confidence=0.8,
                    source="pattern",
                )
            )
        return entities

    def _match_near_ahv(self, text: str) -> list[DetectedEntity]:
        """Detect possible AHV numbers with transposed prefix (B-017).

        Numbers like 765.xxxx.xxxx.xx are flagged as AHV_NR with
        confidence 0.5 to signal they are likely AHV numbers with a
        transposed prefix and should be anonymized as a precaution.
        """
        entities: list[DetectedEntity] = []
        for match in NEAR_AHV_PATTERN.finditer(text):
            entities.append(
                DetectedEntity(
                    entity_type=EntityType.AHV_NR,
                    original_value=match.group(0),
                    start_offset=match.start(),
                    end_offset=match.end(),
                    confidence=0.5,
                    source="pattern",
                )
            )
        return entities

    def _match_birthdates(self, text: str) -> list[DetectedEntity]:
        """Detect dd.mm.yyyy dates that are preceded by a birth-date keyword.

        Only dates with a personnel-context keyword (e.g. "Geburtsdatum",
        "geboren", "geb.", "Jahrgang") within _BIRTHDATE_CONTEXT_WINDOW
        characters before the match are returned as GEBURTSDATUM entities.
        Operational dates (mission dates, report dates, etc.) are ignored.
        """
        entities: list[DetectedEntity] = []
        for match in _DATE_PATTERN.finditer(text):
            preceding = text[max(0, match.start() - _BIRTHDATE_CONTEXT_WINDOW) : match.start()]
            if _BIRTHDATE_KEYWORDS.search(preceding):
                entities.append(
                    DetectedEntity(
                        entity_type=EntityType.GEBURTSDATUM,
                        original_value=match.group(0),
                        start_offset=match.start(),
                        end_offset=match.end(),
                        confidence=1.0,
                        source="pattern",
                    )
                )
        return entities
