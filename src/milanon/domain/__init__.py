"""Domain layer — core business logic with zero external dependencies."""

from milanon.domain.anonymizer import Anonymizer
from milanon.domain.deanonymizer import DeAnonymizer
from milanon.domain.entities import (
    AnonymizedDocument,
    DetectedEntity,
    DocumentFormat,
    EntityMapping,
    EntityType,
    ExtractedDocument,
)
from milanon.domain.mapping_service import MappingService
from milanon.domain.protocols import DocumentParser, EntityRecognizer, MappingRepository
from milanon.domain.recognition import RecognitionPipeline

__all__ = [
    "Anonymizer",
    "AnonymizedDocument",
    "DeAnonymizer",
    "DetectedEntity",
    "DocumentFormat",
    "DocumentParser",
    "EntityMapping",
    "EntityRecognizer",
    "EntityType",
    "ExtractedDocument",
    "MappingRepository",
    "MappingService",
    "RecognitionPipeline",
]
