"""ReviewCandidatesUseCase — scans anonymized output for potential name leaks."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path

from milanon.domain.entities import EntityType
from milanon.domain.mapping_service import MappingService

logger = logging.getLogger(__name__)

# Matches ALLCAPS words (≥3 chars, may contain umlauts and hyphens)
# e.g. MÜLLER, WEGMÜLLER, VON GUNTEN
_ALLCAPS_WORD_RE = re.compile(r"(?<!\w)[A-ZÄÖÜ][A-ZÄÖÜ\-]{2,}(?!\w)")

# Matches Title-case words (first letter uppercase, rest lowercase, ≥3 chars)
# e.g. Thomas, Xenia, Alessandro
_TITLECASE_WORD_RE = re.compile(r"(?<!\w)[A-ZÄÖÜ][a-zäöüé]{2,}(?!\w)")

# Context patterns: words near these are more likely names
_PERSONNEL_CONTEXT_RE = re.compile(
    r"(?:@|telefon|mobile|email|geb\.|geboren|"
    r"From:|To:|Cc:|Bcc:|Subject:|"
    r"PLZ|Adresse|Wohnort|Kontakt)",
    re.IGNORECASE,
)

_CONTEXT_WINDOW = 120  # chars to look around a candidate

# Supported file extensions for scanning
_SCAN_EXTENSIONS = {".md", ".eml", ".txt"}


@dataclass
class NameCandidate:
    """A potential name found in anonymized output that is NOT in the DB."""

    value: str
    occurrences: int = 0
    context_snippets: list[str] = field(default_factory=list)
    near_personnel_context: bool = False
    candidate_type: str = ""  # "ALLCAPS", "TITLECASE", "NEAR_RANK"


@dataclass
class ReviewResult:
    """Result of scanning anonymized output for potential name leaks."""

    files_scanned: int = 0
    candidates: list[NameCandidate] = field(default_factory=list)
    total_occurrences: int = 0


class ReviewCandidatesUseCase:
    """Scans anonymized output files for words that might be undetected names.

    Detection strategies:
    1. ALLCAPS words (≥3 chars) not in DB and not in military exclusion list
    2. Title-case words near rank abbreviations that weren't caught
    3. Title-case words near personnel context (email headers, phone numbers, addresses)

    The candidates are returned for user confirmation. Confirmed names can be
    added to the DB via add_confirmed_candidates().
    """

    def __init__(self, mapping_service: MappingService) -> None:
        self._mapping_service = mapping_service
        self._exclusions: set[str] = set()
        self._build_exclusion_list()

    def _build_exclusion_list(self) -> None:
        """Build a set of words that should NOT be flagged as name candidates.

        Includes: military abbreviations, common German words, known placeholders.
        """
        # Import military abbreviations
        try:
            from milanon.config.military_patterns import (
                BRANCH_ABBREVIATIONS,
                FUNCTION_ABBREVIATIONS,
                RANK_ABBREVIATIONS,
            )
            for lst in (RANK_ABBREVIATIONS, FUNCTION_ABBREVIATIONS, BRANCH_ABBREVIATIONS):
                for item in lst:
                    self._exclusions.add(item.upper())
                    for word in item.split():
                        self._exclusions.add(word.upper())
        except ImportError:
            pass

        # Common German/military words that are NOT names
        _COMMON_WORDS = {
            "ALLE", "ODER", "UND", "FÜR", "MIT", "VON", "DER", "DIE", "DAS",
            "NICHT", "SIND", "WIRD", "WURDE", "KANN", "MUSS", "SOLL", "HAT",
            "HABEN", "WERDEN", "SEIN", "NACH", "AUS", "BEI", "ZUR", "ZUM",
            "ÜBER", "UNTER", "DURCH", "GEGEN", "OHNE", "ZWISCHEN",
            # Military context words
            "WAST", "LUZI", "PASCHGA", "MAGLETSCH", "CASTELS",  # Known locations
            "MELS", "WALENSTADT",
            "TAKTISCH", "OPERATIV", "STRATEGISCH",
            "EINSATZ", "AUSBILDUNG", "ÜBUNG", "ERSTAUSBILDUNG",
            "BEREITSCHAFT", "VERTEIDIGUNG", "ANGRIFF",
            "MONTAG", "DIENSTAG", "MITTWOCH", "DONNERSTAG", "FREITAG",
            "SAMSTAG", "SONNTAG",
            "JANUAR", "FEBRUAR", "MÄRZ", "APRIL", "MAI", "JUNI",
            "JULI", "AUGUST", "SEPTEMBER", "OKTOBER", "NOVEMBER", "DEZEMBER",
            # Document structure words
            "MILANON", "LEGEND", "START", "END", "CONTEXT", "EINHEIT",
            "PERSON", "VORNAME", "NACHNAME", "FUNKTION", "GRAD",
            "EMAIL", "TELEFON", "ADRESSE", "GEBURTSDATUM", "MEDIZINISCH",
            "NOTE", "WARNING", "ANHANG", "BEILAGE", "BEFEHL",
            "DOKUMENT", "DOSSIER", "RAPPORT",
            # Abbreviations that look like ALLCAPS names
            "FGG", "LVZ", "PAB", "ALC", "LASSIM", "FUKO", "WEME",
            "KAVOR", "AVOR", "PRONTO", "ARAMIDE", "DIFESA", "ATTACO",
            "ITC", "CUF", "MEDEVAC", "ABC", "BEBECO",
            "SU", "SR", "KU", "HV", "ORBAT",
            "ELBONIA", "ELBONIAN",  # Fictional country from exercises
            "FEP", "ELTI",  # Fictional factions
        }
        self._exclusions.update(_COMMON_WORDS)

        # Add all existing DB values (already anonymized — no need to flag)
        try:
            all_mappings = self._mapping_service._repository.get_all_mappings()
            for m in all_mappings:
                self._exclusions.add(m.original_value.upper())
                for word in m.original_value.split():
                    self._exclusions.add(word.upper())
        except Exception:
            pass

    def scan(self, input_path: Path) -> ReviewResult:
        """Scan anonymized output files for potential name leaks.

        Args:
            input_path: File or directory of anonymized output to scan.

        Returns:
            ReviewResult with candidate names and their context.
        """
        result = ReviewResult()

        if input_path.is_file():
            files = [input_path]
        else:
            files = [
                f for f in input_path.glob("**/*")
                if f.is_file() and f.suffix.lower() in _SCAN_EXTENSIONS
            ]

        candidates_map: dict[str, NameCandidate] = {}

        for file_path in files:
            result.files_scanned += 1
            try:
                text = file_path.read_text(encoding="utf-8")
                self._scan_text(text, file_path.name, candidates_map)
            except Exception as exc:
                logger.warning("Could not scan %s: %s", file_path.name, exc)

        # Sort by occurrences (most frequent first)
        result.candidates = sorted(
            candidates_map.values(),
            key=lambda c: (-c.occurrences, c.value),
        )
        result.total_occurrences = sum(c.occurrences for c in result.candidates)

        return result

    def _scan_text(
        self, text: str, filename: str, candidates: dict[str, NameCandidate]
    ) -> None:
        """Scan a single text for ALLCAPS and title-case name candidates."""

        # Strategy 1: ALLCAPS words not in exclusions
        for match in _ALLCAPS_WORD_RE.finditer(text):
            word = match.group(0)
            if word.upper() in self._exclusions:
                continue
            # Skip if it's inside a placeholder like [PERSON_005]
            before = text[max(0, match.start() - 1) : match.start()]
            after = text[match.end() : match.end() + 1] if match.end() < len(text) else ""
            if before == "[" or after == "]" or before == "_":
                continue

            self._add_candidate(
                candidates, word, text, match.start(), "ALLCAPS", filename
            )

        # Strategy 2: Title-case words near personnel context
        for match in _TITLECASE_WORD_RE.finditer(text):
            word = match.group(0)
            if word.upper() in self._exclusions:
                continue
            # Only flag if near personnel context
            start = max(0, match.start() - _CONTEXT_WINDOW)
            end = min(len(text), match.end() + _CONTEXT_WINDOW)
            context = text[start:end]
            if _PERSONNEL_CONTEXT_RE.search(context):
                self._add_candidate(
                    candidates, word, text, match.start(), "NEAR_CONTEXT", filename
                )

    def _add_candidate(
        self,
        candidates: dict[str, NameCandidate],
        word: str,
        text: str,
        offset: int,
        candidate_type: str,
        filename: str,
    ) -> None:
        """Add or update a candidate in the map."""
        key = word.upper()
        if key not in candidates:
            candidates[key] = NameCandidate(
                value=word,
                candidate_type=candidate_type,
            )
        c = candidates[key]
        c.occurrences += 1

        # Add context snippet (max 3 per candidate)
        if len(c.context_snippets) < 3:
            start = max(0, offset - 40)
            end = min(len(text), offset + len(word) + 40)
            snippet = text[start:end].replace("\n", " ").strip()
            c.context_snippets.append(f"[{filename}] ...{snippet}...")

        if candidate_type == "NEAR_CONTEXT":
            c.near_personnel_context = True

    def add_confirmed_candidates(
        self,
        candidates: list[NameCandidate],
        source_document: str = "review",
    ) -> int:
        """Add user-confirmed candidates to the mapping database.

        Each confirmed candidate is added as a NACHNAME or VORNAME entity
        depending on its casing. Returns the number of newly added entities.
        """
        count = 0
        for candidate in candidates:
            value = candidate.value
            # Determine entity type based on case
            if value.isupper():
                entity_type = EntityType.NACHNAME
            else:
                entity_type = EntityType.VORNAME

            # Check if already exists before creating
            existing = self._mapping_service._repository.get_mapping(entity_type, value)
            if existing is None:
                self._mapping_service.get_or_create_placeholder(
                    entity_type, value, source_document
                )
                count += 1
                logger.info("Added %s: %s", entity_type.value, value)
        return count
