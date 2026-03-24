"""End-to-end tests — full pipeline: anonymize → validate → deanonymize → verify."""

from __future__ import annotations

from pathlib import Path

import pytest

from milanon.adapters.recognizers.list_recognizer import ListRecognizer
from milanon.adapters.recognizers.military_recognizer import MilitaryRecognizer
from milanon.adapters.recognizers.pattern_recognizer import PatternRecognizer
from milanon.adapters.repositories.sqlite_repository import SqliteMappingRepository
from milanon.domain.anonymizer import Anonymizer
from milanon.domain.deanonymizer import DeAnonymizer
from milanon.domain.mapping_service import MappingService
from milanon.domain.recognition import RecognitionPipeline
from milanon.usecases.anonymize import AnonymizeUseCase
from milanon.usecases.deanonymize import DeAnonymizeUseCase
from milanon.usecases.validate_output import ValidateOutputUseCase

_FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def repo():
    return SqliteMappingRepository(":memory:")


@pytest.fixture
def pipeline(repo):
    return RecognitionPipeline(
        [PatternRecognizer(), MilitaryRecognizer(), ListRecognizer(repo)]
    )


@pytest.fixture
def anonymize_uc(repo, pipeline):
    service = MappingService(repo)
    anonymizer = Anonymizer(service)
    return AnonymizeUseCase(pipeline, anonymizer, repo)


@pytest.fixture
def deanonymize_uc(repo):
    service = MappingService(repo)
    deanonymizer = DeAnonymizer(service)
    return DeAnonymizeUseCase(deanonymizer, repo)


@pytest.fixture
def validate_uc(repo):
    service = MappingService(repo)
    deanonymizer = DeAnonymizer(service)
    return ValidateOutputUseCase(deanonymizer)


def _write(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


class TestFullPipelineCsv:
    """CSV with AHV, email, and rank+name — full round trip."""

    def test_csv_round_trip(self, anonymize_uc, deanonymize_uc, validate_uc, tmp_path):
        src = _write(
            tmp_path / "in" / "data.csv",
            "Name;AHV;Email\nMarco BERNASCONI;756.1234.5678.97;bernasconi@mil.ch\n",
        )
        anon_dir = tmp_path / "anon"
        deanon_dir = tmp_path / "deanon"

        # Step 1: Anonymize
        anon_result = anonymize_uc.execute(src, anon_dir)
        assert anon_result.files_new == 1
        assert anon_result.files_error == 0

        anon_file = next(anon_dir.rglob("*.*"))
        anon_content = anon_file.read_text(encoding="utf-8")

        # Sensitive values must be replaced
        assert "756.1234.5678.97" not in anon_content
        assert "bernasconi@mil.ch" not in anon_content
        assert "[" in anon_content  # at least one placeholder

        # Step 2: Validate
        val_result = validate_uc.execute(anon_file)
        assert val_result.is_valid, f"Unresolved: {val_result.unresolved_list}"

        # Step 3: De-anonymize
        deanon_result = deanonymize_uc.execute(anon_file, deanon_dir)
        assert deanon_result.files_new == 1
        assert deanon_result.files_error == 0

        restored = next(deanon_dir.rglob("*.*")).read_text(encoding="utf-8")

        # Originals must be restored
        assert "756.1234.5678.97" in restored
        assert "bernasconi@mil.ch" in restored
        # No placeholders left
        assert "[AHV_NR_" not in restored
        assert "[EMAIL_" not in restored

    def test_ahv_replaced_with_placeholder(self, anonymize_uc, tmp_path):
        src = _write(tmp_path / "in" / "doc.csv", "AHV\n756.9876.5432.10\n")
        anon_dir = tmp_path / "anon"
        anonymize_uc.execute(src, anon_dir)
        content = next(anon_dir.rglob("*.*")).read_text(encoding="utf-8")
        assert "756.9876.5432.10" not in content
        assert "[AHV_NR_001]" in content

    def test_no_sensitive_data_in_anonymized_output(self, anonymize_uc, tmp_path):
        src = _write(
            tmp_path / "in" / "doc.csv",
            "AHV;Tel;Email\n756.1234.5678.97;079 535 80 46;test@example.com\n",
        )
        anon_dir = tmp_path / "anon"
        anonymize_uc.execute(src, anon_dir)
        content = next(anon_dir.rglob("*.*")).read_text(encoding="utf-8")
        assert "756.1234.5678.97" not in content
        assert "079 535 80 46" not in content
        assert "test@example.com" not in content


class TestFullPipelineMixedFolder:
    """Directory with multiple file types."""

    def test_multiple_csv_files_processed(self, anonymize_uc, tmp_path):
        in_dir = tmp_path / "in"
        _write(in_dir / "a.csv", "AHV\n756.1111.1111.11\n")
        _write(in_dir / "b.csv", "Email\nuser@test.ch\n")
        anon_dir = tmp_path / "anon"

        result = anonymize_uc.execute(in_dir, anon_dir)
        assert result.files_scanned == 2
        assert result.files_new == 2
        assert result.files_error == 0

    def test_txt_files_ignored(self, anonymize_uc, tmp_path):
        in_dir = tmp_path / "in"
        _write(in_dir / "doc.csv", "AHV\n756.1111.1111.11\n")
        _write(in_dir / "notes.txt", "Some text 756.1111.1111.11")
        anon_dir = tmp_path / "anon"

        result = anonymize_uc.execute(in_dir, anon_dir)
        assert result.files_scanned == 1  # only csv

    def test_incremental_second_run_skips_unchanged(self, anonymize_uc, tmp_path):
        src = _write(tmp_path / "in" / "data.csv", "AHV\n756.1111.1111.11\n")
        anon_dir = tmp_path / "anon"

        r1 = anonymize_uc.execute(src, anon_dir)
        assert r1.files_new == 1

        r2 = anonymize_uc.execute(src, anon_dir)
        assert r2.files_skipped == 1
        assert r2.files_new == 0


class TestFixtureFiles:
    """Smoke tests using the bundled fixture files."""

    def test_sample_csv_anonymized(self, anonymize_uc, tmp_path):
        src = _FIXTURES / "sample.csv"
        if not src.exists():
            pytest.skip("sample.csv fixture not found")
        anon_dir = tmp_path / "anon"
        result = anonymize_uc.execute(src, anon_dir)
        assert result.files_new == 1
        assert result.files_error == 0

    def test_sample_eml_anonymized(self, anonymize_uc, tmp_path):
        src = _FIXTURES / "sample.eml"
        if not src.exists():
            pytest.skip("sample.eml fixture not found")
        anon_dir = tmp_path / "anon"
        result = anonymize_uc.execute(src, anon_dir)
        assert result.files_new == 1
        assert result.files_error == 0

    def test_sample_docx_anonymized(self, anonymize_uc, tmp_path):
        src = _FIXTURES / "sample.docx"
        if not src.exists():
            pytest.skip("sample.docx fixture not found")
        anon_dir = tmp_path / "anon"
        result = anonymize_uc.execute(src, anon_dir)
        assert result.files_new == 1
        assert result.files_error == 0

    def test_sample_csv_round_trip(
        self, anonymize_uc, deanonymize_uc, validate_uc, tmp_path
    ):
        src = _FIXTURES / "sample.csv"
        if not src.exists():
            pytest.skip("sample.csv fixture not found")

        anon_dir = tmp_path / "anon"
        deanon_dir = tmp_path / "deanon"

        anonymize_uc.execute(src, anon_dir)
        anon_file = next(anon_dir.rglob("*.*"))

        val_result = validate_uc.execute(anon_file)
        assert val_result.is_valid, f"Unresolved: {val_result.unresolved_list}"

        deanon_result = deanonymize_uc.execute(anon_file, deanon_dir)
        assert deanon_result.files_new == 1

        original = src.read_text(encoding="utf-8")
        restored = next(deanon_dir.rglob("*.*")).read_text(encoding="utf-8")

        # Emails from original must appear in restored
        import re
        emails = re.findall(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", original)
        for email in emails:
            assert email in restored, f"Email {email!r} not restored"


class TestValidationUseCase:
    def test_all_placeholders_resolved(self, repo, validate_uc, tmp_path):
        service = MappingService(repo)
        ph = service.get_or_create_placeholder(
            __import__("milanon.domain.entities", fromlist=["EntityType"]).EntityType.PERSON,
            "Marco BERNASCONI",
        )
        doc = _write(tmp_path / "doc.md", f"Report for {ph}.\n")
        result = validate_uc.execute(doc)
        assert result.total_placeholders == 1
        assert result.resolved == 1
        assert result.unresolved == 0
        assert result.is_valid

    def test_unresolved_placeholders_detected(self, validate_uc, tmp_path):
        doc = _write(tmp_path / "doc.md", "See [PERSON_099] and [EMAIL_042].\n")
        result = validate_uc.execute(doc)
        assert result.unresolved == 2
        assert not result.is_valid
        assert "[PERSON_099]" in result.unresolved_list
        assert "[EMAIL_042]" in result.unresolved_list
