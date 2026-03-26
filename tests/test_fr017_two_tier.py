"""Tests for FR-017: Two-Tier Anonymization (DSG / Full).

Covers unit tests for the filter function, integration tests for the
anonymization pipeline, and edge case tests for the enum and entity sets.
"""


from milanon.domain.entities import (
    DSG_ENTITY_TYPES,
    ISG_ENTITY_TYPES,
    AnonymizationLevel,
    DetectedEntity,
    EntityType,
    filter_entities_by_level,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_entity(
    entity_type: EntityType,
    value: str = "test_value",
    start: int = 0,
) -> DetectedEntity:
    """Create a DetectedEntity with sensible defaults."""
    return DetectedEntity(
        entity_type=entity_type,
        original_value=value,
        start_offset=start,
        end_offset=start + len(value),
        confidence=1.0,
        source="test",
    )


def _all_entity_types_sample() -> list[DetectedEntity]:
    """Return one DetectedEntity per EntityType, non-overlapping offsets."""
    entities = []
    offset = 0
    for et in EntityType:
        value = f"sample_{et.value}"
        entities.append(_make_entity(et, value=value, start=offset))
        offset += len(value) + 1
    return entities


# ===========================================================================
# Unit tests for filter_entities_by_level
# ===========================================================================


class TestFilterEntitiesByLevel:
    """Unit tests for the domain filter function."""

    def test_filter_full_returns_all_entities(self) -> None:
        """FULL mode must return every entity unchanged."""
        entities = _all_entity_types_sample()

        result = filter_entities_by_level(entities, AnonymizationLevel.FULL)

        assert result == entities
        assert len(result) == len(EntityType)

    def test_filter_dsg_keeps_personal_data(self) -> None:
        """DSG mode must keep all DSG entity types (personal data)."""
        entities = _all_entity_types_sample()

        result = filter_entities_by_level(entities, AnonymizationLevel.DSG)

        result_types = {e.entity_type for e in result}
        for dsg_type in DSG_ENTITY_TYPES:
            assert dsg_type in result_types, f"{dsg_type} should be kept in DSG mode"

    def test_filter_dsg_removes_operational_data(self) -> None:
        """DSG mode must remove ISG entity types (operational/military data)."""
        entities = _all_entity_types_sample()

        result = filter_entities_by_level(entities, AnonymizationLevel.DSG)

        result_types = {e.entity_type for e in result}
        for isg_type in ISG_ENTITY_TYPES:
            assert isg_type not in result_types, (
                f"{isg_type} should be removed in DSG mode"
            )

    def test_filter_dsg_keeps_grad_funktion(self) -> None:
        """GRAD_FUNKTION contains personal data and must stay in DSG mode."""
        entity = _make_entity(EntityType.GRAD_FUNKTION, "Hptm BERNASCONI, Kdt Inf Kp 56/1")

        result = filter_entities_by_level([entity], AnonymizationLevel.DSG)

        assert len(result) == 1
        assert result[0].entity_type == EntityType.GRAD_FUNKTION

    def test_filter_empty_list(self) -> None:
        """Empty input must return empty output for both levels."""
        assert filter_entities_by_level([], AnonymizationLevel.DSG) == []
        assert filter_entities_by_level([], AnonymizationLevel.FULL) == []


# ===========================================================================
# Entity set completeness tests
# ===========================================================================


class TestEntitySets:
    """Verify DSG and ISG entity sets are exhaustive and disjoint."""

    def test_entity_sets_exhaustive(self) -> None:
        """DSG_ENTITY_TYPES | ISG_ENTITY_TYPES must cover all EntityTypes."""
        all_types = set(EntityType)
        covered = DSG_ENTITY_TYPES | ISG_ENTITY_TYPES

        assert covered == all_types, (
            f"Missing from DSG|ISG: {all_types - covered}"
        )

    def test_entity_sets_disjoint(self) -> None:
        """DSG and ISG entity sets must not overlap."""
        overlap = DSG_ENTITY_TYPES & ISG_ENTITY_TYPES

        assert overlap == frozenset(), (
            f"Overlap between DSG and ISG: {overlap}"
        )


# ===========================================================================
# Integration tests — pipeline-level scenarios
# ===========================================================================


class TestDsgModePipeline:
    """Integration tests that simulate the anonymize pipeline filter step."""

    def test_dsg_mode_preserves_unit_names(self) -> None:
        """DSG mode: person anonymized, unit name preserved (not filtered)."""
        person = _make_entity(EntityType.PERSON, "Hptm Marco BERNASCONI", start=0)
        unit = _make_entity(EntityType.EINHEIT, "Inf Bat 56", start=30)

        result = filter_entities_by_level([person, unit], AnonymizationLevel.DSG)

        result_types = {e.entity_type for e in result}
        assert EntityType.PERSON in result_types
        assert EntityType.EINHEIT not in result_types

    def test_full_mode_anonymizes_everything(self) -> None:
        """FULL mode: both person and unit are included for anonymization."""
        person = _make_entity(EntityType.PERSON, "Hptm Marco BERNASCONI", start=0)
        unit = _make_entity(EntityType.EINHEIT, "Inf Bat 56", start=30)

        result = filter_entities_by_level([person, unit], AnonymizationLevel.FULL)

        result_types = {e.entity_type for e in result}
        assert EntityType.PERSON in result_types
        assert EntityType.EINHEIT in result_types
        assert len(result) == 2

    def test_dsg_mode_preserves_locations(self) -> None:
        """DSG mode: phone anonymized, location (ORT) preserved."""
        phone = _make_entity(EntityType.TELEFON, "079 535 80 46", start=0)
        location = _make_entity(EntityType.ORT, "WALENSTADT", start=20)

        result = filter_entities_by_level([phone, location], AnonymizationLevel.DSG)

        result_types = {e.entity_type for e in result}
        assert EntityType.TELEFON in result_types, "Phone must be anonymized in DSG"
        assert EntityType.ORT not in result_types, "Location must be preserved in DSG"


# ===========================================================================
# Edge case tests
# ===========================================================================


class TestEdgeCases:
    """Edge cases for entity filtering and enum behavior."""

    def test_mixed_entity_types_in_dsg(self) -> None:
        """Mix of DSG and ISG entities: verify correct partition."""
        entities = [
            _make_entity(EntityType.PERSON, "Marco BERNASCONI", start=0),
            _make_entity(EntityType.EINHEIT, "Inf Kp 56/1", start=20),
            _make_entity(EntityType.EMAIL, "marco@example.com", start=40),
            _make_entity(EntityType.STANDORT_MIL, "WAST", start=60),
            _make_entity(EntityType.AHV_NR, "756.1234.5678.90", start=70),
            _make_entity(EntityType.FUNKTION, "S4", start=90),
            _make_entity(EntityType.MEDIZINISCH, "Rückenprobleme", start=95),
            _make_entity(EntityType.ORT, "MELS", start=115),
        ]

        result = filter_entities_by_level(entities, AnonymizationLevel.DSG)

        result_types = {e.entity_type for e in result}
        # DSG types kept
        assert EntityType.PERSON in result_types
        assert EntityType.EMAIL in result_types
        assert EntityType.AHV_NR in result_types
        assert EntityType.MEDIZINISCH in result_types
        # ISG types removed
        assert EntityType.EINHEIT not in result_types
        assert EntityType.STANDORT_MIL not in result_types
        assert EntityType.FUNKTION not in result_types
        assert EntityType.ORT not in result_types
        # Exactly 4 DSG entities kept
        assert len(result) == 4

    def test_anonymization_level_enum_values(self) -> None:
        """Verify the string values of the enum members."""
        assert AnonymizationLevel.DSG.value == "dsg"
        assert AnonymizationLevel.FULL.value == "full"

    def test_anonymization_level_is_string_enum(self) -> None:
        """AnonymizationLevel values can be used for string comparison."""
        assert AnonymizationLevel.DSG.value == "dsg"
        assert AnonymizationLevel.FULL.value == "full"
        # Can construct from string value
        assert AnonymizationLevel("dsg") == AnonymizationLevel.DSG
        assert AnonymizationLevel("full") == AnonymizationLevel.FULL
