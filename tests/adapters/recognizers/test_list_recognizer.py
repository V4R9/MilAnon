"""Tests for ListRecognizer — DB lookup and municipality matching."""

from __future__ import annotations

import pytest

from milanon.adapters.recognizers.list_recognizer import ListRecognizer
from milanon.adapters.repositories.sqlite_repository import SqliteMappingRepository
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
def repo() -> SqliteMappingRepository:
    return SqliteMappingRepository(":memory:")


@pytest.fixture
def recognizer(repo) -> ListRecognizer:
    return ListRecognizer(repo)


class TestListRecognizerProtocol:
    def test_implements_entity_recognizer_protocol(self, recognizer):
        assert isinstance(recognizer, EntityRecognizer)


class TestDbLookup:
    def test_known_person_detected(self, repo):
        repo.create_mapping(EntityType.PERSON, "Marco BERNASCONI")
        rec = ListRecognizer(repo)
        entities = _entities_of_type(rec, "Kommandant: Marco BERNASCONI", EntityType.PERSON)
        assert len(entities) == 1
        assert entities[0].original_value == "Marco BERNASCONI"

    def test_case_insensitive_match(self, repo):
        repo.create_mapping(EntityType.PERSON, "Marco BERNASCONI")
        rec = ListRecognizer(repo)
        # The recognizer matches regardless of case in text
        entities = _entities_of_type(rec, "marco bernasconi", EntityType.PERSON)
        assert len(entities) == 1

    def test_source_is_list(self, repo):
        repo.create_mapping(EntityType.ORT, "Basel")
        rec = ListRecognizer(repo)
        entities = rec.recognize(_doc("Wohnort: Basel"))
        assert all(e.source == "list" for e in entities)

    def test_confidence_is_09_for_db_match(self, repo):
        repo.create_mapping(EntityType.EMAIL, "hans@army.ch")
        rec = ListRecognizer(repo)
        entities = _entities_of_type(rec, "hans@army.ch", EntityType.EMAIL)
        assert entities[0].confidence == 0.9

    def test_multiple_entities_detected(self, repo):
        repo.create_mapping(EntityType.PERSON, "Hans MUSTER")
        repo.create_mapping(EntityType.PERSON, "Peter MEIER")
        rec = ListRecognizer(repo)
        entities = _entities_of_type(
            rec, "Hans MUSTER und Peter MEIER sind anwesend.", EntityType.PERSON
        )
        names = {e.original_value for e in entities}
        assert "Hans MUSTER" in names
        assert "Peter MEIER" in names

    def test_empty_db_returns_no_entities(self, recognizer):
        entities = recognizer.recognize(_doc("Beliebiger Text ohne bekannte Entities"))
        assert len(entities) == 0

    def test_entity_not_in_text_not_detected(self, repo):
        repo.create_mapping(EntityType.PERSON, "Jemand ANDERS")
        rec = ListRecognizer(repo)
        entities = _entities_of_type(rec, "Hier steht etwas anderes", EntityType.PERSON)
        assert len(entities) == 0


class TestMunicipalityLookup:
    def test_known_municipality_detected(self, repo):
        rec = ListRecognizer(repo, municipality_names=["Basel", "Zürich", "Bern"])
        entities = _entities_of_type(rec, "Wohnort: Basel", EntityType.ORT)
        assert len(entities) == 1
        assert entities[0].original_value == "Basel"

    def test_municipality_confidence_is_08(self, repo):
        rec = ListRecognizer(repo, municipality_names=["Lenzburg"])
        entities = _entities_of_type(rec, "PLZ: 5600 Lenzburg", EntityType.ORT)
        assert entities[0].confidence == 0.8

    def test_municipality_word_boundary(self, repo):
        rec = ListRecognizer(repo, municipality_names=["Baar"])
        # "Baarburg" should NOT match "Baar" (word boundary protection)
        entities = _entities_of_type(rec, "Baarburg", EntityType.ORT)
        assert len(entities) == 0

    def test_municipality_standalone_matches(self, repo):
        rec = ListRecognizer(repo, municipality_names=["Baar"])
        entities = _entities_of_type(rec, "Wohnort Baar.", EntityType.ORT)
        assert len(entities) == 1

    def test_no_municipalities_no_ort_entities(self, recognizer):
        entities = _entities_of_type(recognizer, "Bern ist die Hauptstadt", EntityType.ORT)
        assert len(entities) == 0

    def test_multiple_municipalities_all_detected(self, repo):
        rec = ListRecognizer(repo, municipality_names=["Basel", "Bern"])
        entities = _entities_of_type(
            rec, "Von Basel nach Bern reiste er.", EntityType.ORT
        )
        names = {e.original_value for e in entities}
        assert "Basel" in names
        assert "Bern" in names


class TestWordBoundaryProtection:
    """Regression tests for word-destruction bug (substring false positives).

    All six cases reported by user where the anonymizer corrupted German text:
    - "Ausbildung" → "[ORT]sbildung"  (Au=municipality matched inside word)
    - "Gewalt"     → "Gewa[GRAD_FUNKTION]"  (Lt matched inside word via DB)
    - "Einführung" → "E[FUNKTION]ührung"   (Inf matched inside word via DB)
    - "Einsatz"    → "E[ORT]atz"            (Ins=municipality matched inside word)
    - "Arbeitgebern" → "[ORT]"              (Bern matched inside word)
    - "Kurse"      → "K[VORNAME]e"          (Urs matched inside word via DB)
    """

    def test_short_municipality_au_not_matched_inside_ausbildung(self, repo):
        """'Au' (len 2) must never match inside 'Ausbildung'."""
        rec = ListRecognizer(repo, municipality_names=["Au"])
        entities = rec.recognize(_doc("Die Ausbildung war intensiv."))
        assert len(entities) == 0

    def test_short_municipality_ins_not_matched_inside_einsatz(self, repo):
        """'Ins' (len 3) must never match inside 'Einsatz'."""
        rec = ListRecognizer(repo, municipality_names=["Ins"])
        entities = rec.recognize(_doc("Der Einsatz begann um 06:00 Uhr."))
        assert len(entities) == 0

    def test_municipality_bern_not_matched_inside_arbeitgebern(self, repo):
        """'Bern' must not match inside 'Arbeitgebern'."""
        rec = ListRecognizer(repo, municipality_names=["Bern"])
        entities = rec.recognize(_doc("Pflichten gegenüber Arbeitgebern sind klar."))
        assert len(entities) == 0

    def test_municipality_bern_matched_standalone(self, repo):
        """'Bern' must still be detected when it stands alone."""
        rec = ListRecognizer(repo, municipality_names=["Bern"])
        entities = _entities_of_type(rec, "Stationiert in Bern.", EntityType.ORT)
        assert len(entities) == 1

    def test_db_entity_lt_not_matched_inside_gewalt(self, repo):
        """'Lt' from DB must not match inside 'Gewalt'."""
        repo.create_mapping(EntityType.GRAD_FUNKTION, "Lt")
        rec = ListRecognizer(repo)
        entities = rec.recognize(_doc("Der Einsatz erforderte Gewalt."))
        assert len(entities) == 0

    def test_db_entity_inf_not_matched_inside_einführung(self, repo):
        """'Inf' from DB must not match inside 'Einführung'."""
        repo.create_mapping(EntityType.FUNKTION, "Inf")
        rec = ListRecognizer(repo)
        entities = rec.recognize(_doc("Die Einführung ins Thema war klar."))
        assert len(entities) == 0

    def test_db_entity_urs_not_matched_inside_kurse(self, repo):
        """'Urs' (a first name) from DB must not match inside 'Kurse'."""
        repo.create_mapping(EntityType.VORNAME, "Urs")
        rec = ListRecognizer(repo)
        entities = rec.recognize(_doc("Die Kurse dauern drei Tage."))
        assert len(entities) == 0

    def test_db_entity_urs_matched_standalone(self, repo):
        """'Urs' from DB must still be detected when it stands alone."""
        repo.create_mapping(EntityType.VORNAME, "Urs")
        rec = ListRecognizer(repo)
        entities = _entities_of_type(rec, "Kontakt: Urs Müller", EntityType.VORNAME)
        assert len(entities) == 1

    def test_min_municipality_length_skips_two_char_names(self, repo):
        """Municipality names shorter than 4 chars are never matched."""
        rec = ListRecognizer(repo, municipality_names=["Au", "Gy", "Ef"])
        entities = rec.recognize(_doc("Aufgabe: Ausgabe der Unterlagen."))
        assert len(entities) == 0

    def test_min_municipality_length_skips_three_char_names(self, repo):
        """Municipality names of exactly 3 chars (Ins, Egg) are never matched."""
        rec = ListRecognizer(repo, municipality_names=["Ins", "Egg"])
        entities = rec.recognize(_doc("Insgesamt wurden drei Einheiten eingesetzt."))
        assert len(entities) == 0

    def test_four_char_municipality_is_matched(self, repo):
        """Municipality names of 4 chars (minimum) are matched."""
        rec = ListRecognizer(repo, municipality_names=["Baar"])
        entities = _entities_of_type(rec, "Wohnort: Baar", EntityType.ORT)
        assert len(entities) == 1


class TestMunicipalityStopwords:
    """Stopword municipalities must not fire on plain German text without context."""

    def test_stopword_wald_not_detected_in_plain_text(self, repo):
        rec = ListRecognizer(repo, municipality_names=["Wald"])
        entities = _entities_of_type(rec, "Im Wald stehen Bäume.", EntityType.ORT)
        assert len(entities) == 0

    def test_stopword_wald_detected_with_preposition(self, repo):
        rec = ListRecognizer(repo, municipality_names=["Wald"])
        entities = _entities_of_type(rec, "nach Wald gefahren", EntityType.ORT)
        assert len(entities) == 1

    def test_non_stopword_municipality_detected_normally(self, repo):
        """A municipality not in the stopword list is detected without context."""
        rec = ListRecognizer(repo, municipality_names=["Lenzburg"])
        entities = _entities_of_type(rec, "Standort Lenzburg", EntityType.ORT)
        assert len(entities) == 1

    def test_stopword_list_does_not_include_alle(self):
        """'alle' was promoted to _MUNICIPALITY_EXCLUDED — no longer just a stopword."""
        from milanon.adapters.recognizers.list_recognizer import _MUNICIPALITY_STOPWORDS
        assert "alle" not in _MUNICIPALITY_STOPWORDS


class TestMunicipalityExcluded:
    """Excluded municipalities are never matched regardless of context."""

    def test_excluded_municipality_alle_never_matched(self, repo):
        rec = ListRecognizer(repo, municipality_names=["Alle"])
        entities = _entities_of_type(rec, "Alle haben zugestimmt.", EntityType.ORT)
        assert len(entities) == 0

    def test_excluded_municipality_alle_with_plz_still_not_matched(self, repo):
        rec = ListRecognizer(repo, municipality_names=["Alle"])
        entities = _entities_of_type(rec, "2942 Alle", EntityType.ORT)
        assert len(entities) == 0

    def test_excluded_set_includes_alle(self):
        from milanon.adapters.recognizers.list_recognizer import _MUNICIPALITY_EXCLUDED
        assert "alle" in _MUNICIPALITY_EXCLUDED
