"""Tests for PatternRecognizer — AHV, phone, email, date, address."""

from __future__ import annotations

import pytest

from milanon.adapters.recognizers.pattern_recognizer import PatternRecognizer
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
def recognizer() -> PatternRecognizer:
    return PatternRecognizer()


class TestPatternRecognizerProtocol:
    def test_implements_entity_recognizer_protocol(self, recognizer):
        assert isinstance(recognizer, EntityRecognizer)


class TestAhvNrDetection:
    def test_standard_ahv_detected(self, recognizer):
        entities = _entities_of_type(recognizer, "AHV-Nr: 756.1234.5678.97", EntityType.AHV_NR)
        assert len(entities) == 1
        assert entities[0].original_value == "756.1234.5678.97"

    def test_ahv_value_correct(self, recognizer):
        entities = _entities_of_type(recognizer, "756.9876.5432.10", EntityType.AHV_NR)
        assert entities[0].original_value == "756.9876.5432.10"

    def test_ahv_confidence_is_one(self, recognizer):
        entities = _entities_of_type(recognizer, "756.1234.5678.97", EntityType.AHV_NR)
        assert entities[0].confidence == 1.0

    def test_ahv_source_is_pattern(self, recognizer):
        entities = _entities_of_type(recognizer, "756.1234.5678.97", EntityType.AHV_NR)
        assert entities[0].source == "pattern"

    def test_non_ahv_number_not_detected(self, recognizer):
        entities = _entities_of_type(recognizer, "123.4567.8901.23", EntityType.AHV_NR)
        assert len(entities) == 0

    def test_ahv_offset_correct(self, recognizer):
        text = "Nr: 756.1234.5678.97 Ende"
        entities = _entities_of_type(recognizer, text, EntityType.AHV_NR)
        assert entities[0].start_offset == text.index("756")
        assert entities[0].end_offset == text.index("756") + len("756.1234.5678.97")


class TestEmailDetection:
    def test_standard_email_detected(self, recognizer):
        entities = _entities_of_type(recognizer, "hans.muster@army.ch", EntityType.EMAIL)
        assert len(entities) == 1
        assert entities[0].original_value == "hans.muster@army.ch"

    def test_milweb_email_detected(self, recognizer):
        entities = _entities_of_type(
            recognizer, "marco.bernasconi@milweb.ch", EntityType.EMAIL
        )
        assert entities[0].original_value == "marco.bernasconi@milweb.ch"

    def test_email_with_plus_detected(self, recognizer):
        entities = _entities_of_type(recognizer, "user+tag@example.com", EntityType.EMAIL)
        assert len(entities) == 1

    def test_email_in_sentence(self, recognizer):
        entities = _entities_of_type(
            recognizer, "Kontakt: lukas.fischer@example.com für Details.", EntityType.EMAIL
        )
        assert entities[0].original_value == "lukas.fischer@example.com"

    def test_no_email_in_plain_text(self, recognizer):
        entities = _entities_of_type(recognizer, "Kein Email hier", EntityType.EMAIL)
        assert len(entities) == 0


class TestPhoneDetection:
    def test_local_format_detected(self, recognizer):
        entities = _entities_of_type(recognizer, "Tel: 079 535 80 46", EntityType.TELEFON)
        assert len(entities) == 1
        assert "079 535 80 46" in entities[0].original_value

    def test_international_format_detected(self, recognizer):
        entities = _entities_of_type(
            recognizer, "Mobile: +41 79 535 80 46", EntityType.TELEFON
        )
        assert any("+41" in e.original_value for e in entities)

    def test_compact_format_detected(self, recognizer):
        entities = _entities_of_type(recognizer, "0795358046", EntityType.TELEFON)
        assert len(entities) == 1
        assert entities[0].original_value == "0795358046"

    def test_landline_local_format(self, recognizer):
        entities = _entities_of_type(recognizer, "044 123 45 67", EntityType.TELEFON)
        assert len(entities) == 1

    def test_phone_with_dashes(self, recognizer):
        entities = _entities_of_type(recognizer, "079-535-80-46", EntityType.TELEFON)
        assert len(entities) == 1

    def test_no_phone_in_plain_text(self, recognizer):
        entities = _entities_of_type(recognizer, "Seite 3 von 12", EntityType.TELEFON)
        assert len(entities) == 0


class TestGeburtsdatumDetection:
    def test_standard_date_detected(self, recognizer):
        entities = _entities_of_type(
            recognizer, "Geburtsdatum: 15.03.1995", EntityType.GEBURTSDATUM
        )
        assert len(entities) == 1
        assert entities[0].original_value == "15.03.1995"

    def test_date_in_sentence(self, recognizer):
        entities = _entities_of_type(
            recognizer, "Geboren am 15.03.1985 in Basel.", EntityType.GEBURTSDATUM
        )
        assert entities[0].original_value == "15.03.1985"

    def test_operational_dates_not_detected(self, recognizer):
        # Dates without personnel context keyword must NOT be detected as GEBURTSDATUM
        entities = _entities_of_type(
            recognizer, "Von 01.01.2020 bis 31.12.2023", EntityType.GEBURTSDATUM
        )
        assert len(entities) == 0

    def test_invalid_date_not_detected(self, recognizer):
        # Dates without leading zeros are not in dd.mm.yyyy format
        entities = _entities_of_type(recognizer, "1.1.2020", EntityType.GEBURTSDATUM)
        assert len(entities) == 0


class TestGeburtsdatumContextDetection:
    def test_geburtsdatum_keyword_triggers_detection(self, recognizer):
        entities = _entities_of_type(
            recognizer, "Geburtsdatum: 15.03.1995", EntityType.GEBURTSDATUM
        )
        assert len(entities) == 1

    def test_geboren_keyword_triggers_detection(self, recognizer):
        entities = _entities_of_type(
            recognizer, "geboren am 15.03.1985", EntityType.GEBURTSDATUM
        )
        assert len(entities) == 1

    def test_geb_abbreviation_triggers_detection(self, recognizer):
        entities = _entities_of_type(
            recognizer, "geb. 15.03.1990", EntityType.GEBURTSDATUM
        )
        assert len(entities) == 1

    def test_jahrgang_keyword_triggers_detection(self, recognizer):
        entities = _entities_of_type(
            recognizer, "Jahrgang 15.03.1988", EntityType.GEBURTSDATUM
        )
        assert len(entities) == 1

    def test_operational_date_without_keyword_not_detected(self, recognizer):
        entities = _entities_of_type(
            recognizer, "Auftrag vom 15.03.2026", EntityType.GEBURTSDATUM
        )
        assert len(entities) == 0

    def test_date_beyond_context_window_not_detected(self, recognizer):
        # Keyword is more than 80 chars before the date — too far away
        far_context = "Geburtsdatum" + " " * 85 + "15.03.1995"
        entities = _entities_of_type(recognizer, far_context, EntityType.GEBURTSDATUM)
        assert len(entities) == 0


class TestAdresseDetection:
    def test_street_with_abbreviated_suffix(self, recognizer):
        entities = _entities_of_type(
            recognizer, "Bahnhofstr. 42", EntityType.ADRESSE
        )
        assert len(entities) == 1
        assert "Bahnhofstr." in entities[0].original_value
        assert "42" in entities[0].original_value

    def test_full_address_with_plz(self, recognizer):
        entities = _entities_of_type(
            recognizer, "Bahnhofstr. 42, 4058 Basel", EntityType.ADRESSE
        )
        assert len(entities) == 1
        assert "4058" in entities[0].original_value
        assert "Basel" in entities[0].original_value

    def test_strasse_suffix(self, recognizer):
        entities = _entities_of_type(
            recognizer, "Hauptstrasse 5", EntityType.ADRESSE
        )
        assert len(entities) == 1

    def test_gasse_suffix(self, recognizer):
        entities = _entities_of_type(recognizer, "Kirchgasse 12", EntityType.ADRESSE)
        assert len(entities) == 1

    def test_weg_suffix(self, recognizer):
        entities = _entities_of_type(recognizer, "Bergweg 3", EntityType.ADRESSE)
        assert len(entities) == 1

    def test_no_address_without_number(self, recognizer):
        # "Hauptstrasse" without a number should not be detected
        entities = _entities_of_type(recognizer, "Die Hauptstrasse ist lang", EntityType.ADRESSE)
        assert len(entities) == 0


class TestInitialSurnameDetection:
    def test_initial_dot_allcaps_surname_detected(self, recognizer):
        entities = _entities_of_type(recognizer, "D. MUFFLER", EntityType.PERSON)
        assert len(entities) == 1

    def test_initial_surname_value_correct(self, recognizer):
        entities = _entities_of_type(recognizer, "M. KOCH", EntityType.PERSON)
        assert entities[0].original_value == "M. KOCH"

    def test_multiple_initial_surnames_detected(self, recognizer):
        entities = _entities_of_type(
            recognizer, "L. STORRER und M. KOCH", EntityType.PERSON
        )
        assert len(entities) == 2

    def test_initial_surname_not_detected_as_substring(self, recognizer):
        # "SD. MUFFLER" — letter before initial must not be a word char
        entities = _entities_of_type(recognizer, "SD. MUFFLER", EntityType.PERSON)
        assert len(entities) == 0

    def test_initial_surname_confidence_is_one(self, recognizer):
        entities = _entities_of_type(recognizer, "D. MUFFLER", EntityType.PERSON)
        assert entities[0].confidence == 1.0

    def test_lowercase_initial_not_detected(self, recognizer):
        entities = _entities_of_type(recognizer, "d. MUFFLER", EntityType.PERSON)
        assert len(entities) == 0


class TestMultipleEntitiesInDocument:
    def test_all_entity_types_detected(self, recognizer):
        text = (
            "AHV: 756.1234.5678.97\n"
            "E-Mail: hans.muster@army.ch\n"
            "Tel: 079 535 80 46\n"
            "Geburtsdatum: 15.03.1985\n"
            "Adresse: Bahnhofstr. 42\n"
        )
        entities = recognizer.recognize(_doc(text))
        types_found = {e.entity_type for e in entities}
        assert EntityType.AHV_NR in types_found
        assert EntityType.EMAIL in types_found
        assert EntityType.TELEFON in types_found
        assert EntityType.GEBURTSDATUM in types_found
        assert EntityType.ADRESSE in types_found

    def test_offsets_are_correct(self, recognizer):
        text = "AHV: 756.1234.5678.97 Ende"
        entities = recognizer.recognize(_doc(text))
        ahv = next(e for e in entities if e.entity_type == EntityType.AHV_NR)
        assert text[ahv.start_offset:ahv.end_offset] == ahv.original_value
