"""Tests for RecognitionPipeline — orchestration and conflict resolution."""

from __future__ import annotations

import pytest

from milanon.domain.entities import (
    DetectedEntity,
    DocumentFormat,
    EntityType,
    ExtractedDocument,
)
from milanon.domain.recognition import RecognitionPipeline


def _doc(text: str) -> ExtractedDocument:
    return ExtractedDocument(
        source_path="test.txt",
        format=DocumentFormat.MARKDOWN,
        text_content=text,
    )


def _entity(
    entity_type: EntityType,
    value: str,
    start: int,
    end: int,
    source: str = "pattern",
    confidence: float = 1.0,
) -> DetectedEntity:
    return DetectedEntity(
        entity_type=entity_type,
        original_value=value,
        start_offset=start,
        end_offset=end,
        confidence=confidence,
        source=source,
    )


class _StubRecognizer:
    """Returns a fixed list of entities."""

    def __init__(self, entities: list[DetectedEntity]) -> None:
        self._entities = entities

    def recognize(self, document: ExtractedDocument) -> list[DetectedEntity]:
        return list(self._entities)


@pytest.fixture
def pipeline_with_all_recognizers():
    from milanon.adapters.recognizers.list_recognizer import ListRecognizer
    from milanon.adapters.recognizers.military_recognizer import MilitaryRecognizer
    from milanon.adapters.recognizers.pattern_recognizer import PatternRecognizer
    from milanon.adapters.repositories.sqlite_repository import SqliteMappingRepository

    repo = SqliteMappingRepository(":memory:")
    return RecognitionPipeline(
        [PatternRecognizer(), MilitaryRecognizer(), ListRecognizer(repo)]
    )


class TestPipelineBasic:
    def test_empty_pipeline_returns_empty(self):
        pipeline = RecognitionPipeline([])
        assert pipeline.recognize(_doc("some text")) == []

    def test_single_recognizer_entities_returned(self):
        entity = _entity(EntityType.AHV_NR, "756.1234.5678.97", 0, 16)
        pipeline = RecognitionPipeline([_StubRecognizer([entity])])
        result = pipeline.recognize(_doc("756.1234.5678.97"))
        assert len(result) == 1
        assert result[0].original_value == "756.1234.5678.97"

    def test_result_sorted_by_start_offset(self):
        # Non-overlapping entities: e1 is later in text, e2 is earlier
        e1 = _entity(EntityType.EMAIL, "a@b.com", 20, 27)
        e2 = _entity(EntityType.AHV_NR, "756.1234.5678.97", 0, 16)
        pipeline = RecognitionPipeline([_StubRecognizer([e1, e2])])
        result = pipeline.recognize(_doc("x" * 30))
        assert result[0].start_offset < result[1].start_offset


class TestConflictResolution:
    def test_higher_priority_wins_on_overlap(self):
        """Pattern (prio 1) beats list (prio 3) on same span."""
        pattern_entity = _entity(EntityType.AHV_NR, "756.1234.5678.97", 0, 16, source="pattern")
        list_entity = _entity(EntityType.PERSON, "756.1234.5678.97", 0, 16, source="list")
        pipeline = RecognitionPipeline(
            [_StubRecognizer([pattern_entity, list_entity])]
        )
        result = pipeline.recognize(_doc("756.1234.5678.97"))
        assert len(result) == 1
        assert result[0].source == "pattern"
        assert result[0].entity_type == EntityType.AHV_NR

    def test_longer_match_wins_at_same_priority(self):
        """At same priority, the longer span wins."""
        short = _entity(EntityType.PERSON, "BERNASCONI", 6, 16, source="military")
        long_ = _entity(EntityType.PERSON, "Marco BERNASCONI", 0, 16, source="military")
        pipeline = RecognitionPipeline([_StubRecognizer([short, long_])])
        result = pipeline.recognize(_doc("Marco BERNASCONI"))
        assert len(result) == 1
        assert result[0].original_value == "Marco BERNASCONI"

    def test_non_overlapping_entities_both_kept(self):
        e1 = _entity(EntityType.AHV_NR, "756.0000.0000.00", 0, 16)
        e2 = _entity(EntityType.EMAIL, "a@b.ch", 20, 26)
        pipeline = RecognitionPipeline([_StubRecognizer([e1, e2])])
        result = pipeline.recognize(_doc("x" * 30))
        assert len(result) == 2

    def test_partial_overlap_higher_priority_wins(self):
        """If entity A (prio 1) partially overlaps entity B (prio 3), A wins."""
        high = _entity(EntityType.EMAIL, "a@b.com", 5, 12, source="pattern")
        low = _entity(EntityType.PERSON, "b.com Person", 8, 20, source="list")
        pipeline = RecognitionPipeline([_StubRecognizer([high, low])])
        result = pipeline.recognize(_doc("x" * 25))
        assert len(result) == 1
        assert result[0].source == "pattern"

    def test_military_beats_list_on_overlap(self):
        """Military (prio 2) beats list (prio 3) on same span."""
        mil = _entity(EntityType.PERSON, "Marco BERNASCONI", 0, 16, source="military")
        lst = _entity(EntityType.PERSON, "Marco BERNASCONI", 0, 16, source="list")
        pipeline = RecognitionPipeline([_StubRecognizer([mil, lst])])
        result = pipeline.recognize(_doc("Marco BERNASCONI"))
        assert len(result) == 1
        assert result[0].source == "military"


class TestFullPipeline:
    def test_ahv_detected_in_full_pipeline(self, pipeline_with_all_recognizers):
        text = "AHV: 756.1234.5678.97"
        result = pipeline_with_all_recognizers.recognize(_doc(text))
        ahv = [e for e in result if e.entity_type == EntityType.AHV_NR]
        assert len(ahv) == 1

    def test_person_and_rank_detected_in_full_pipeline(self, pipeline_with_all_recognizers):
        text = "Kommandant: Hptm Marco BERNASCONI"
        result = pipeline_with_all_recognizers.recognize(_doc(text))
        persons = [e for e in result if e.entity_type == EntityType.PERSON]
        ranks = [e for e in result if e.entity_type == EntityType.GRAD_FUNKTION]
        assert any("BERNASCONI" in e.original_value for e in persons)
        assert any(e.original_value == "Hptm" for e in ranks)

    def test_unit_detected_in_full_pipeline(self, pipeline_with_all_recognizers):
        text = "Einheit: Inf Kp 56/1"
        result = pipeline_with_all_recognizers.recognize(_doc(text))
        units = [e for e in result if e.entity_type == EntityType.EINHEIT]
        assert any("Inf Kp 56/1" in e.original_value for e in units)

    def test_no_overlap_in_results(self, pipeline_with_all_recognizers):
        text = (
            "AHV: 756.1234.5678.97\n"
            "Hptm Marco BERNASCONI\n"
            "Inf Kp 56/1\n"
        )
        result = pipeline_with_all_recognizers.recognize(_doc(text))
        for i, a in enumerate(result):
            for b in result[i + 1:]:
                assert not (
                    a.start_offset < b.end_offset and b.start_offset < a.end_offset
                ), f"Overlap: {a!r} vs {b!r}"
