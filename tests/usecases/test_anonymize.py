"""Tests for AnonymizeUseCase — batch processing, incremental, file tracking."""

from __future__ import annotations

from pathlib import Path

import pytest

from milanon.adapters.recognizers.list_recognizer import ListRecognizer
from milanon.adapters.recognizers.military_recognizer import MilitaryRecognizer
from milanon.adapters.recognizers.pattern_recognizer import PatternRecognizer
from milanon.adapters.repositories.sqlite_repository import SqliteMappingRepository
from milanon.domain.anonymizer import Anonymizer
from milanon.domain.mapping_service import MappingService
from milanon.domain.recognition import RecognitionPipeline
from milanon.usecases.anonymize import AnonymizeUseCase


@pytest.fixture
def repo():
    return SqliteMappingRepository(":memory:")


@pytest.fixture
def use_case(repo):
    service = MappingService(repo)
    pipeline = RecognitionPipeline(
        [PatternRecognizer(), MilitaryRecognizer(), ListRecognizer(repo)]
    )
    anonymizer = Anonymizer(service)
    return AnonymizeUseCase(pipeline, anonymizer, repo)


def _write(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


class TestAnonymizeUseCaseSingleFile:
    def test_anonymizes_csv_file(self, use_case, tmp_path):
        src = _write(
            tmp_path / "input" / "data.csv",
            "Name;AHV\nMarco BERNASCONI;756.1234.5678.97\n",
        )
        out_dir = tmp_path / "output"
        result = use_case.execute(src, out_dir)
        assert result.files_scanned == 1
        assert result.files_new == 1
        assert result.files_error == 0

    def test_output_file_created(self, use_case, tmp_path):
        src = _write(tmp_path / "input" / "data.csv", "Name;AHV\nBERNASCONI;756.1234.5678.97\n")
        out_dir = tmp_path / "output"
        use_case.execute(src, out_dir)
        assert any(out_dir.rglob("*.csv"))

    def test_ahv_replaced_in_output(self, use_case, tmp_path):
        src = _write(tmp_path / "in" / "doc.csv", "AHV;Name\n756.1234.5678.97;BERNASCONI\n")
        out_dir = tmp_path / "out"
        use_case.execute(src, out_dir)
        out_file = next(out_dir.rglob("*.csv"))
        content = out_file.read_text(encoding="utf-8")
        assert "756.1234.5678.97" not in content
        assert "[AHV_NR_001]" in content


class TestIncrementalProcessing:
    def test_unchanged_file_skipped_on_second_run(self, use_case, tmp_path):
        src = _write(tmp_path / "in" / "data.csv", "AHV\n756.1234.5678.97\n")
        out_dir = tmp_path / "out"
        # First run
        r1 = use_case.execute(src, out_dir)
        assert r1.files_new == 1
        assert r1.files_skipped == 0
        # Second run — same content
        r2 = use_case.execute(src, out_dir)
        assert r2.files_skipped == 1
        assert r2.files_new == 0

    def test_changed_file_reprocessed(self, use_case, tmp_path):
        src = _write(tmp_path / "in" / "data.csv", "AHV\n756.1234.5678.97\n")
        out_dir = tmp_path / "out"
        use_case.execute(src, out_dir)
        # Modify the file
        src.write_text("AHV\n756.9876.5432.10\n", encoding="utf-8")
        r2 = use_case.execute(src, out_dir)
        assert r2.files_changed == 1
        assert r2.files_skipped == 0

    def test_force_flag_reprocesses_unchanged(self, use_case, tmp_path):
        src = _write(tmp_path / "in" / "data.csv", "AHV\n756.1234.5678.97\n")
        out_dir = tmp_path / "out"
        use_case.execute(src, out_dir)
        r2 = use_case.execute(src, out_dir, force=True)
        assert r2.files_skipped == 0
        assert r2.files_changed == 1

    def test_dry_run_does_not_write_files(self, use_case, tmp_path):
        src = _write(tmp_path / "in" / "data.csv", "AHV\n756.1234.5678.97\n")
        out_dir = tmp_path / "out"
        use_case.execute(src, out_dir, dry_run=True)
        assert not any(out_dir.rglob("*"))


class TestDirectoryProcessing:
    def test_multiple_files_in_directory(self, use_case, tmp_path):
        in_dir = tmp_path / "in"
        _write(in_dir / "a.csv", "AHV\n756.1111.1111.11\n")
        _write(in_dir / "b.csv", "AHV\n756.2222.2222.22\n")
        out_dir = tmp_path / "out"
        result = use_case.execute(in_dir, out_dir)
        assert result.files_scanned == 2
        assert result.files_new == 2

    def test_unsupported_files_ignored(self, use_case, tmp_path):
        in_dir = tmp_path / "in"
        _write(in_dir / "file.csv", "AHV\n756.1111.1111.11\n")
        _write(in_dir / "readme.txt", "Not a supported format")
        out_dir = tmp_path / "out"
        result = use_case.execute(in_dir, out_dir)
        assert result.files_scanned == 1  # only .csv counted
