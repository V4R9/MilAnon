"""Anonymizer — replaces detected entities with placeholders and generates a legend."""

from __future__ import annotations

import re

from milanon.domain.entities import (
    AnonymizedDocument,
    DetectedEntity,
    DocumentFormat,
    EntityType,
    ExtractedDocument,
)
from milanon.domain.mapping_service import MappingService

# Canonical pattern for the embedded legend block — shared by deanonymizer and writers.
LEGEND_PATTERN: re.Pattern[str] = re.compile(
    r"<!--\s*MILANON LEGEND START.*?MILANON LEGEND END\s*-->",
    re.DOTALL,
)

# Canonical placeholder pattern — single source of truth for all modules.
PLACEHOLDER_PATTERN: re.Pattern[str] = re.compile(r"\[([A-Z_]+)_(\d{3})\]")

_LEGEND_HEADER_TEMPLATE = """\
<!-- MILANON LEGEND START
{entries}
MILANON LEGEND END -->

"""


class Anonymizer:
    """Replaces sensitive entities in extracted documents with placeholders.

    Entity replacement is applied in reverse offset order so earlier offsets
    are not disturbed by later substitutions.

    The legend header lists all placeholder → entity_type mappings used
    in this document. It is prepended to the output text.
    """

    def __init__(self, mapping_service: MappingService) -> None:
        self._mapping_service = mapping_service

    def anonymize(
        self,
        document: ExtractedDocument,
        entities: list[DetectedEntity],
        source_document: str = "",
    ) -> AnonymizedDocument:
        """Anonymize a document by replacing all detected entities.

        Args:
            document: The parsed document to anonymize.
            entities: Pre-detected entities (from RecognitionPipeline).
            source_document: Filename label stored with each new mapping.

        Returns:
            AnonymizedDocument with placeholders, legend, and warnings.
        """
        if not entities:
            return AnonymizedDocument(
                source_path=document.source_path,
                output_format=DocumentFormat.MARKDOWN,
                content=document.text_content,
                entities_found=[],
                legend="",
                warnings=[],
            )

        # Sort entities by offset descending so substitutions don't shift offsets
        sorted_entities = sorted(entities, key=lambda e: e.start_offset, reverse=True)

        text = document.text_content
        placeholder_map: dict[str, str] = {}  # original_value → placeholder
        warnings: list[str] = []

        for entity in sorted_entities:
            try:
                placeholder = self._mapping_service.get_or_create_placeholder(
                    entity.entity_type,
                    entity.original_value,
                    source_document,
                )
                placeholder_map[entity.original_value] = placeholder
                text = (
                    text[: entity.start_offset]
                    + placeholder
                    + text[entity.end_offset :]
                )
            except Exception as exc:
                warnings.append(
                    f"Could not anonymize {entity.entity_type.value} at offset "
                    f"{entity.start_offset}-{entity.end_offset}: {exc}"
                )

        legend = self._build_legend(placeholder_map, entities)
        if legend:
            content = _LEGEND_HEADER_TEMPLATE.format(entries=legend) + text
        else:
            content = text

        return AnonymizedDocument(
            source_path=document.source_path,
            output_format=DocumentFormat.MARKDOWN,
            content=content,
            entities_found=list(entities),
            legend=legend,
            warnings=warnings,
        )

    # ------------------------------------------------------------------

    def _build_legend(
        self,
        placeholder_map: dict[str, str],
        entities: list[DetectedEntity],
    ) -> str:
        """Build a legend string mapping placeholders to entity types."""
        # Collect unique placeholder → entity_type mappings
        seen: dict[str, EntityType] = {}
        for entity in entities:
            ph = placeholder_map.get(entity.original_value)
            if ph and ph not in seen:
                seen[ph] = entity.entity_type

        if not seen:
            return ""

        lines = [
            f"{placeholder} = {entity_type.value}"
            for placeholder, entity_type in sorted(seen.items())
        ]
        return "\n".join(lines)
