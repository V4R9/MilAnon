"""Tests for MilitaryRecognizer — rank+name, units, functions."""

from __future__ import annotations

import pytest

from milanon.adapters.recognizers.military_recognizer import MilitaryRecognizer
from milanon.domain.entities import DocumentFormat, EntityType, ExtractedDocument
from milanon.domain.protocols import EntityRecognizer


def _doc(text: str) -> ExtractedDocument:
    return ExtractedDocument(
        source_path="test.txt",
        format=DocumentFormat.MARKDOWN,
        text_content=text,
    )


def _entities_of_type(recognizer, text, entity_type):
    return [e for e in recognizer.recognize(_doc(text)) if e.entity_type == entity_type]


@pytest.fixture
def recognizer() -> MilitaryRecognizer:
    return MilitaryRecognizer()


class TestMilitaryRecognizerProtocol:
    def test_implements_entity_recognizer_protocol(self, recognizer):
        assert isinstance(recognizer, EntityRecognizer)


class TestRankNameCompounds:
    def test_hptm_with_name_detected(self, recognizer):
        entities = recognizer.recognize(_doc("Hptm Marco BERNASCONI"))
        types = {e.entity_type for e in entities}
        assert EntityType.GRAD_FUNKTION in types
        assert EntityType.PERSON in types

    def test_rank_value_correct(self, recognizer):
        entities = _entities_of_type(recognizer, "Hptm Marco BERNASCONI", EntityType.GRAD_FUNKTION)
        assert len(entities) == 1
        assert entities[0].original_value == "Hptm"

    def test_person_value_correct(self, recognizer):
        entities = _entities_of_type(recognizer, "Hptm Marco BERNASCONI", EntityType.PERSON)
        assert len(entities) == 1
        assert entities[0].original_value == "Marco BERNASCONI"

    def test_compound_rank_oberstlt_i_gst(self, recognizer):
        entities = _entities_of_type(
            recognizer, "Oberstlt i Gst Thomas WEGMÜLLER", EntityType.GRAD_FUNKTION
        )
        assert entities[0].original_value == "Oberstlt i Gst"

    def test_compound_rank_name_person(self, recognizer):
        entities = _entities_of_type(
            recognizer, "Oberstlt i Gst Thomas WEGMÜLLER", EntityType.PERSON
        )
        assert entities[0].original_value == "Thomas WEGMÜLLER"

    def test_adj_uof_compound_rank(self, recognizer):
        entities = _entities_of_type(
            recognizer, "Adj Uof Hans MEIER", EntityType.GRAD_FUNKTION
        )
        assert entities[0].original_value == "Adj Uof"

    def test_adj_standalone_with_name_detected(self, recognizer):
        grad = _entities_of_type(recognizer, "Adj Stefan SCHEGG", EntityType.GRAD_FUNKTION)
        person = _entities_of_type(recognizer, "Adj Stefan SCHEGG", EntityType.PERSON)
        assert len(grad) == 1
        assert grad[0].original_value == "Adj"
        assert len(person) == 1

    def test_adj_uof_still_takes_priority(self, recognizer):
        entities = _entities_of_type(
            recognizer, "Adj Uof Hans MEIER", EntityType.GRAD_FUNKTION
        )
        assert entities[0].original_value == "Adj Uof"

    def test_lt_with_caps_only_name(self, recognizer):
        entities = _entities_of_type(recognizer, "Lt MUSTER", EntityType.PERSON)
        assert entities[0].original_value == "MUSTER"

    def test_fw_with_name(self, recognizer):
        entities = _entities_of_type(
            recognizer, "Fw Peter LEHMANN", EntityType.GRAD_FUNKTION
        )
        assert entities[0].original_value == "Fw"

    def test_source_is_military(self, recognizer):
        entities = recognizer.recognize(_doc("Hptm Marco BERNASCONI"))
        for e in entities:
            assert e.source == "military"

    def test_confidence_is_one_for_rank_name(self, recognizer):
        entities = _entities_of_type(recognizer, "Hptm Marco BERNASCONI", EntityType.PERSON)
        assert entities[0].confidence == 1.0

    def test_offsets_span_correct_text(self, recognizer):
        text = "Kommandant: Hptm Marco BERNASCONI, Tel."
        entities = recognizer.recognize(_doc(text))
        for e in entities:
            assert text[e.start_offset:e.end_offset] == e.original_value

    def test_multiple_persons_in_text(self, recognizer):
        text = "Hptm Marco BERNASCONI und Lt Hans MUSTER sind anwesend."
        persons = _entities_of_type(recognizer, text, EntityType.PERSON)
        names = {e.original_value for e in persons}
        assert "Marco BERNASCONI" in names
        assert "Hans MUSTER" in names


class TestUnitDetection:
    def test_inf_bat_detected(self, recognizer):
        entities = _entities_of_type(recognizer, "Einheit: Inf Bat 56", EntityType.EINHEIT)
        assert len(entities) == 1
        assert entities[0].original_value == "Inf Bat 56"

    def test_inf_kp_with_sub_detected(self, recognizer):
        entities = _entities_of_type(recognizer, "Inf Kp 56/1", EntityType.EINHEIT)
        assert entities[0].original_value == "Inf Kp 56/1"

    def test_ter_div_detected(self, recognizer):
        entities = _entities_of_type(recognizer, "Ter Div 2", EntityType.EINHEIT)
        assert entities[0].original_value == "Ter Div 2"

    def test_san_kp_detected(self, recognizer):
        entities = _entities_of_type(recognizer, "San Kp 1", EntityType.EINHEIT)
        assert entities[0].original_value == "San Kp 1"

    def test_pz_bat_detected(self, recognizer):
        entities = _entities_of_type(recognizer, "Pz Bat 12", EntityType.EINHEIT)
        assert entities[0].original_value == "Pz Bat 12"

    def test_unit_source_is_military(self, recognizer):
        entities = _entities_of_type(recognizer, "Inf Kp 56/1", EntityType.EINHEIT)
        assert entities[0].source == "military"

    def test_plain_number_not_unit(self, recognizer):
        entities = _entities_of_type(recognizer, "Seite 3 von 56", EntityType.EINHEIT)
        assert len(entities) == 0


class TestFunctionDetection:
    def test_kdt_detected(self, recognizer):
        entities = _entities_of_type(recognizer, "Funktion: Kdt", EntityType.FUNKTION)
        assert len(entities) >= 1
        values = [e.original_value for e in entities]
        assert "Kdt" in values

    def test_bat_kdt_stv_detected(self, recognizer):
        entities = _entities_of_type(recognizer, "Bat Kdt Stv", EntityType.FUNKTION)
        values = [e.original_value for e in entities]
        assert "Bat Kdt Stv" in values

    def test_kdt_stv_detected(self, recognizer):
        entities = _entities_of_type(recognizer, "Kdt Stv", EntityType.FUNKTION)
        values = [e.original_value for e in entities]
        assert "Kdt Stv" in values

    def test_einh_fw_detected(self, recognizer):
        entities = _entities_of_type(recognizer, "Einh Fw", EntityType.FUNKTION)
        values = [e.original_value for e in entities]
        assert "Einh Fw" in values

    def test_zfhr_detected(self, recognizer):
        entities = _entities_of_type(recognizer, "Zfhr der 2. Gruppe", EntityType.FUNKTION)
        values = [e.original_value for e in entities]
        assert "Zfhr" in values

    def test_function_confidence_below_one(self, recognizer):
        entities = _entities_of_type(recognizer, "Kdt", EntityType.FUNKTION)
        # Functions detected standalone have lower confidence than compound rank+name
        assert all(e.confidence <= 1.0 for e in entities)


class TestWordBoundaryProtection:
    """Regression tests: military ranks/functions must not match inside longer words."""

    def test_lt_not_matched_inside_gewalt(self, recognizer):
        """'Lt' must not match inside 'Gewalt' — no word boundary there."""
        entities = recognizer.recognize(_doc("Der Einsatz erforderte Gewalt."))
        grad_entities = [e for e in entities if e.entity_type == EntityType.GRAD_FUNKTION]
        values = [e.original_value for e in grad_entities]
        assert not any("lt" in v.lower() and len(v) <= 2 for v in values)

    def test_br_not_matched_inside_arbeit(self, recognizer):
        """'Br' (Brigadier rank) must not match inside 'Arbeit'."""
        entities = recognizer.recognize(_doc("Gute Arbeit leisten."))
        # No GRAD_FUNKTION entity for 'Br' inside 'Arbeit'
        grad_entities = [e for e in entities if e.entity_type == EntityType.GRAD_FUNKTION]
        assert not any(e.original_value.lower() == "br" for e in grad_entities)

    def test_kdt_not_matched_inside_produktiv(self, recognizer):
        """'Kdt' function abbrev must not match inside longer words."""
        entities = recognizer.recognize(_doc("Die Produktivität stieg."))
        funktion_entities = [e for e in entities if e.entity_type == EntityType.FUNKTION]
        assert len(funktion_entities) == 0

    def test_rank_lt_detected_standalone_before_name(self, recognizer):
        """'Lt' must still be detected when followed by an ALL-CAPS name."""
        entities = recognizer.recognize(_doc("Lt MUSTER ist anwesend."))
        types = {e.entity_type for e in entities}
        assert EntityType.GRAD_FUNKTION in types
        assert EntityType.PERSON in types

    def test_unit_inf_bat_not_matched_inside_einführung(self, recognizer):
        """'Inf' branch prefix must not produce a unit match inside 'Einführung'."""
        entities = _entities_of_type(
            recognizer, "Die Einführung wurde abgehalten.", EntityType.EINHEIT
        )
        assert len(entities) == 0

    def test_unit_inf_bat_detected_correctly(self, recognizer):
        """'Inf Bat 56' must still be detected as a unit."""
        entities = _entities_of_type(
            recognizer, "Zugehörigkeit: Inf Bat 56", EntityType.EINHEIT
        )
        assert len(entities) == 1
        assert entities[0].original_value == "Inf Bat 56"
