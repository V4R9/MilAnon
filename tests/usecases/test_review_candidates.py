"""Tests for the post-anonymization review candidate scanner."""

import pytest

from milanon.adapters.repositories.sqlite_repository import SqliteMappingRepository
from milanon.domain.entities import EntityType
from milanon.domain.mapping_service import MappingService
from milanon.usecases.review_candidates import (
    NameCandidate,
    ReviewCandidatesUseCase,
)


@pytest.fixture
def review_setup():
    """Create a repo with some known mappings and return (repo, service, use_case)."""
    repo = SqliteMappingRepository(":memory:")
    service = MappingService(repo)
    # Add some known names so they're excluded from candidates
    service.get_or_create_placeholder(EntityType.PERSON, "Thomas WEGMÜLLER")
    service.get_or_create_placeholder(EntityType.NACHNAME, "WEGMÜLLER")
    service.get_or_create_placeholder(EntityType.VORNAME, "Thomas")
    uc = ReviewCandidatesUseCase(service)
    return repo, service, uc


class TestCandidateScanning:
    """Scanning anonymized output for name candidates."""

    def test_allcaps_unknown_word_detected(self, review_setup, tmp_path):
        _, _, uc = review_setup
        test_file = tmp_path / "output.md"
        test_file.write_text(
            "Der Sdt BÄRTSCHI meldet sich krank.\n"
            "BÄRTSCHI hat 21 DT offen.",
            encoding="utf-8",
        )
        result = uc.scan(tmp_path)
        names = [c.value for c in result.candidates]
        assert "BÄRTSCHI" in names

    def test_known_name_not_flagged(self, review_setup, tmp_path):
        """Names already in the DB should not appear as candidates."""
        _, _, uc = review_setup
        test_file = tmp_path / "output.md"
        test_file.write_text("WEGMÜLLER reported for duty.", encoding="utf-8")
        result = uc.scan(tmp_path)
        names = [c.value for c in result.candidates]
        assert "WEGMÜLLER" not in names

    def test_military_abbreviation_excluded(self, review_setup, tmp_path):
        """Military abbreviations like WAST, AVOR should not be flagged."""
        _, _, uc = review_setup
        test_file = tmp_path / "output.md"
        test_file.write_text("AVOR WAST PASCHGA MAGLETSCH", encoding="utf-8")
        result = uc.scan(tmp_path)
        names = [c.value.upper() for c in result.candidates]
        assert "AVOR" not in names
        assert "WAST" not in names

    def test_titlecase_near_email_detected(self, review_setup, tmp_path):
        """Title-case words near email context are flagged."""
        _, _, uc = review_setup
        test_file = tmp_path / "output.eml"
        test_file.write_text(
            "From: Milo Bärtschi <milo@example.com>\nContent here.",
            encoding="utf-8",
        )
        result = uc.scan(tmp_path)
        names = [c.value for c in result.candidates]
        # "Milo" or "Bärtschi" should be candidates (near email context)
        assert any("Milo" in n or "Bärtschi" in n for n in names)

    def test_placeholder_words_not_flagged(self, review_setup, tmp_path):
        """Words inside placeholders like [PERSON_005] should not be flagged."""
        _, _, uc = review_setup
        test_file = tmp_path / "output.md"
        test_file.write_text("[PERSON_005] met with [EINHEIT_010].", encoding="utf-8")
        result = uc.scan(tmp_path)
        names = [c.value for c in result.candidates]
        assert "PERSON" not in names
        assert "EINHEIT" not in names

    def test_occurrence_counting(self, review_setup, tmp_path):
        """Same name appearing multiple times gets correct count."""
        _, _, uc = review_setup
        test_file = tmp_path / "output.md"
        test_file.write_text(
            "DÜRST reported.\nDÜRST confirmed.\nDÜRST departed.",
            encoding="utf-8",
        )
        result = uc.scan(tmp_path)
        dursts = [c for c in result.candidates if c.value == "DÜRST"]
        assert len(dursts) == 1
        assert dursts[0].occurrences == 3

    def test_context_snippets_collected(self, review_setup, tmp_path):
        """Candidates include context snippets for review."""
        _, _, uc = review_setup
        test_file = tmp_path / "output.md"
        test_file.write_text(
            "Der Sdt BÄRTSCHI meldet sich für die Teildienstleistung.",
            encoding="utf-8",
        )
        result = uc.scan(tmp_path)
        barts = [c for c in result.candidates if c.value == "BÄRTSCHI"]
        assert len(barts) == 1
        assert len(barts[0].context_snippets) >= 1
        assert "BÄRTSCHI" in barts[0].context_snippets[0]

    def test_empty_directory_returns_zero(self, review_setup, tmp_path):
        _, _, uc = review_setup
        result = uc.scan(tmp_path)
        assert result.files_scanned == 0
        assert result.candidates == []

    def test_scan_multiple_files(self, review_setup, tmp_path):
        """Candidates are aggregated across multiple files."""
        _, _, uc = review_setup
        (tmp_path / "a.md").write_text("DÜRST hier.", encoding="utf-8")
        (tmp_path / "b.md").write_text("DÜRST dort.", encoding="utf-8")
        result = uc.scan(tmp_path)
        assert result.files_scanned == 2
        dursts = [c for c in result.candidates if c.value == "DÜRST"]
        assert dursts[0].occurrences == 2


class TestAddConfirmedCandidates:
    """Adding confirmed candidates to the DB."""

    def test_confirmed_candidate_added_to_db(self, review_setup):
        repo, service, uc = review_setup
        candidate = NameCandidate(value="BÄRTSCHI", occurrences=3, candidate_type="ALLCAPS")
        count = uc.add_confirmed_candidates([candidate])
        assert count == 1
        # Verify it's in the DB
        mapping = repo.get_mapping(EntityType.NACHNAME, "BÄRTSCHI")
        assert mapping is not None
        assert mapping.placeholder.startswith("[NACHNAME_")

    def test_titlecase_added_as_vorname(self, review_setup):
        repo, service, uc = review_setup
        candidate = NameCandidate(value="Milo", occurrences=2, candidate_type="NEAR_CONTEXT")
        count = uc.add_confirmed_candidates([candidate])
        assert count == 1
        mapping = repo.get_mapping(EntityType.VORNAME, "Milo")
        assert mapping is not None

    def test_duplicate_not_added_twice(self, review_setup):
        repo, service, uc = review_setup
        candidate = NameCandidate(value="BÄRTSCHI", occurrences=3)
        uc.add_confirmed_candidates([candidate])
        count = uc.add_confirmed_candidates([candidate])  # second time
        assert count == 0

    def test_multiple_candidates_added(self, review_setup):
        _, _, uc = review_setup
        candidates = [
            NameCandidate(value="DÜRST", occurrences=2),
            NameCandidate(value="SCHEGG", occurrences=1),
            NameCandidate(value="Milo", occurrences=3, candidate_type="NEAR_CONTEXT"),
        ]
        count = uc.add_confirmed_candidates(candidates)
        assert count == 3
