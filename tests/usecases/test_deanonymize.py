"""Tests for DeAnonymizeUseCase — batch processing, incremental, warnings."""

from __future__ import annotations

from pathlib import Path

import pytest

from milanon.adapters.repositories.sqlite_repository import SqliteMappingRepository
from milanon.domain.deanonymizer import DeAnonymizer
from milanon.domain.mapping_service import MappingService
from milanon.usecases.deanonymize import DeAnonymizeUseCase


@pytest.fixture
def repo():
    return SqliteMappingRepository(":memory:")


@pytest.fixture
def use_case(repo):
    service = MappingService(repo)
    deanonymizer = DeAnonymizer(service)
    return DeAnonymizeUseCase(deanonymizer, repo)


def _write(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def _seed(repo: SqliteMappingRepository, placeholder: str, original: str) -> None:
    """Insert a placeholder→original mapping directly."""
    from milanon.domain.entities import EntityType
    service = MappingService(repo)
    service.get_or_create_placeholder(EntityType.PERSON, original)


class TestDeAnonymizeUseCaseSingleFile:
    def test_restores_placeholder(self, repo, tmp_path):
        from milanon.domain.entities import EntityType
        service = MappingService(repo)
        ph = service.get_or_create_placeholder(EntityType.PERSON, "Marco BERNASCONI")

        src = _write(
            tmp_path / "input" / "doc.md",
            f"Befehl an {ph}.\n",
        )
        out_dir = tmp_path / "output"
        deanonymizer = DeAnonymizer(service)
        uc = DeAnonymizeUseCase(deanonymizer, repo)
        result = uc.execute(src, out_dir)

        assert result.files_scanned == 1
        assert result.files_new == 1
        assert result.files_error == 0

        out_file = next(out_dir.rglob("*.md"))
        content = out_file.read_text(encoding="utf-8")
        assert "Marco BERNASCONI" in content
        assert ph not in content

    def test_output_file_created(self, repo, tmp_path):
        src = _write(tmp_path / "input" / "doc.md", "Hello [PERSON_001].\n")
        out_dir = tmp_path / "output"
        service = MappingService(repo)
        deanonymizer = DeAnonymizer(service)
        uc = DeAnonymizeUseCase(deanonymizer, repo)
        uc.execute(src, out_dir)
        assert any(out_dir.rglob("*.md"))

    def test_unresolved_placeholder_warns(self, repo, tmp_path):
        src = _write(tmp_path / "in" / "doc.md", "Hello [PERSON_099].\n")
        out_dir = tmp_path / "out"
        service = MappingService(repo)
        deanonymizer = DeAnonymizer(service)
        uc = DeAnonymizeUseCase(deanonymizer, repo)
        result = uc.execute(src, out_dir)
        assert len(result.warnings) > 0


class TestDeAnonymizeIncrementalProcessing:
    def test_unchanged_file_skipped_on_second_run(self, use_case, tmp_path):
        src = _write(tmp_path / "in" / "doc.md", "No placeholders here.\n")
        out_dir = tmp_path / "out"
        r1 = use_case.execute(src, out_dir)
        assert r1.files_new == 1
        r2 = use_case.execute(src, out_dir)
        assert r2.files_skipped == 1
        assert r2.files_new == 0

    def test_changed_file_reprocessed(self, use_case, tmp_path):
        src = _write(tmp_path / "in" / "doc.md", "Version 1.\n")
        out_dir = tmp_path / "out"
        use_case.execute(src, out_dir)
        src.write_text("Version 2.\n", encoding="utf-8")
        r2 = use_case.execute(src, out_dir)
        assert r2.files_changed == 1
        assert r2.files_skipped == 0

    def test_force_flag_reprocesses_unchanged(self, use_case, tmp_path):
        src = _write(tmp_path / "in" / "doc.md", "Static content.\n")
        out_dir = tmp_path / "out"
        use_case.execute(src, out_dir)
        r2 = use_case.execute(src, out_dir, force=True)
        assert r2.files_skipped == 0
        assert r2.files_changed == 1

    def test_dry_run_does_not_write_files(self, use_case, tmp_path):
        src = _write(tmp_path / "in" / "doc.md", "Content.\n")
        out_dir = tmp_path / "out"
        use_case.execute(src, out_dir, dry_run=True)
        assert not any(out_dir.rglob("*"))


class TestDeAnonymizeDirectoryProcessing:
    def test_multiple_files_processed(self, use_case, tmp_path):
        in_dir = tmp_path / "in"
        _write(in_dir / "a.md", "File A.\n")
        _write(in_dir / "b.txt", "File B.\n")
        out_dir = tmp_path / "out"
        result = use_case.execute(in_dir, out_dir)
        assert result.files_scanned == 2
        assert result.files_new == 2

    def test_unsupported_files_ignored(self, use_case, tmp_path):
        in_dir = tmp_path / "in"
        _write(in_dir / "doc.md", "Supported.\n")
        _write(in_dir / "data.csv", "Unsupported format.\n")
        out_dir = tmp_path / "out"
        result = use_case.execute(in_dir, out_dir)
        assert result.files_scanned == 1


class TestFilenameDeanonymization:
    """B-023: Placeholder filenames are resolved."""

    def test_placeholder_filename_resolved(self, tmp_path):
        """[PERSON_001].md → Wegmüller_Thomas.md"""
        from milanon.adapters.repositories.sqlite_repository import SqliteMappingRepository
        from milanon.domain.entities import EntityType
        from milanon.domain.mapping_service import MappingService
        from milanon.domain.deanonymizer import DeAnonymizer
        from milanon.usecases.deanonymize import DeAnonymizeUseCase

        repo = SqliteMappingRepository(":memory:")
        repo.create_mapping(EntityType.PERSON, "Thomas WEGMÜLLER")
        service = MappingService(repo)
        da = DeAnonymizer(service)
        uc = DeAnonymizeUseCase(da, repo)

        input_dir = tmp_path / "input"
        input_dir.mkdir()
        input_file = input_dir / "[PERSON_001].md"
        input_file.write_text("# [PERSON_001]\nSome content about [PERSON_001].", encoding="utf-8")

        output_dir = tmp_path / "output"
        result = uc.execute(input_dir, output_dir)

        assert (output_dir / "Wegmüller_Thomas.md").exists()
        assert not (output_dir / "[PERSON_001].md").exists()

        content = (output_dir / "Wegmüller_Thomas.md").read_text(encoding="utf-8")
        assert "Thomas WEGMÜLLER" in content

    def test_normal_filename_unchanged(self, tmp_path):
        """dashboard.md stays dashboard.md."""
        from milanon.adapters.repositories.sqlite_repository import SqliteMappingRepository
        from milanon.domain.mapping_service import MappingService
        from milanon.domain.deanonymizer import DeAnonymizer
        from milanon.usecases.deanonymize import DeAnonymizeUseCase

        repo = SqliteMappingRepository(":memory:")
        service = MappingService(repo)
        da = DeAnonymizer(service)
        uc = DeAnonymizeUseCase(da, repo)

        input_dir = tmp_path / "input"
        input_dir.mkdir()
        (input_dir / "dashboard.md").write_text("# Dashboard", encoding="utf-8")

        output_dir = tmp_path / "output"
        result = uc.execute(input_dir, output_dir)

        assert (output_dir / "dashboard.md").exists()
