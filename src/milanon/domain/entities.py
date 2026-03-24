"""Domain entities — core data structures with zero external dependencies."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class EntityType(Enum):
    """Types of sensitive entities that can be detected and anonymized."""

    PERSON = "PERSON"
    VORNAME = "VORNAME"
    NACHNAME = "NACHNAME"
    EMAIL = "EMAIL"
    TELEFON = "TELEFON"
    AHV_NR = "AHV_NR"
    GEBURTSDATUM = "GEBURTSDATUM"
    ORT = "ORT"
    ADRESSE = "ADRESSE"
    ARBEITGEBER = "ARBEITGEBER"
    EINHEIT = "EINHEIT"
    FUNKTION = "FUNKTION"
    GRAD_FUNKTION = "GRAD_FUNKTION"
    MEDIZINISCH = "MEDIZINISCH"
    FAMILIAER = "FAMILIAER"
    STANDORT_MIL = "STANDORT_MIL"


class DocumentFormat(Enum):
    """Supported document formats for parsing and output."""

    EML = "EML"
    DOCX = "DOCX"
    PDF = "PDF"
    XLSX = "XLSX"
    CSV = "CSV"
    MARKDOWN = "MARKDOWN"


@dataclass(frozen=True)
class DetectedEntity:
    """An entity detected in a document by a recognizer.

    Attributes:
        entity_type: The category of the detected entity.
        original_value: The original text that was detected.
        start_offset: Character offset where the entity starts in the text.
        end_offset: Character offset where the entity ends in the text.
        confidence: Detection confidence score between 0.0 and 1.0.
        source: Which recognizer produced this detection.
    """

    entity_type: EntityType
    original_value: str
    start_offset: int
    end_offset: int
    confidence: float = 1.0
    source: str = "unknown"

    def __post_init__(self) -> None:
        if not self.original_value:
            raise ValueError("original_value must not be empty")
        if self.start_offset < 0:
            raise ValueError("start_offset must be non-negative")
        if self.end_offset <= self.start_offset:
            raise ValueError("end_offset must be greater than start_offset")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")

    @property
    def span_length(self) -> int:
        """Length of the detected text span."""
        return self.end_offset - self.start_offset


@dataclass
class EntityMapping:
    """A mapping between an original entity value and its placeholder.

    Attributes:
        entity_type: The category of the entity.
        original_value: The original sensitive text.
        placeholder: The anonymized placeholder (e.g. '[PERSON_001]').
        first_seen: When this entity was first encountered.
        last_seen: When this entity was last encountered.
        source_document: The document where this entity was first found.
    """

    entity_type: EntityType
    original_value: str
    placeholder: str
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    source_document: str = ""

    def __post_init__(self) -> None:
        if not self.original_value:
            raise ValueError("original_value must not be empty")
        if not self.placeholder:
            raise ValueError("placeholder must not be empty")


@dataclass
class ExtractedDocument:
    """A document parsed into its text content and metadata.

    Attributes:
        source_path: Path to the original file.
        format: The document format.
        text_content: The full extracted text content.
        structured_content: Optional structured data (e.g. table rows).
        metadata: Document metadata (author, date, subject, etc.).
        embedded_image_count: Number of embedded images detected.
    """

    source_path: str
    format: DocumentFormat
    text_content: str
    structured_content: dict | None = None
    metadata: dict = field(default_factory=dict)
    embedded_image_count: int = 0
    visual_pages: list[int] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.source_path:
            raise ValueError("source_path must not be empty")


@dataclass
class AnonymizedDocument:
    """The result of anonymizing a document.

    Attributes:
        source_path: Path to the original document.
        output_format: The format for the anonymized output.
        content: The anonymized text content.
        entities_found: All entities that were detected and replaced.
        legend: A legend mapping placeholders to entity types.
        warnings: Any warnings generated during anonymization.
        structured_content: Optional structured data for format-preserving output.
    """

    source_path: str
    output_format: DocumentFormat
    content: str
    entities_found: list[DetectedEntity] = field(default_factory=list)
    legend: str = ""
    warnings: list[str] = field(default_factory=list)
    structured_content: dict | None = None
