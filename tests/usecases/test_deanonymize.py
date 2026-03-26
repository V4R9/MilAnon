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
        from milanon.domain.deanonymizer import DeAnonymizer
        from milanon.domain.entities import EntityType
        from milanon.domain.mapping_service import MappingService
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
        uc.execute(input_dir, output_dir)

        assert (output_dir / "Wegmüller_Thomas.md").exists()
        assert not (output_dir / "[PERSON_001].md").exists()

        content = (output_dir / "Wegmüller_Thomas.md").read_text(encoding="utf-8")
        assert "Thomas WEGMÜLLER" in content

    def test_normal_filename_unchanged(self, tmp_path):
        """dashboard.md stays dashboard.md."""
        from milanon.adapters.repositories.sqlite_repository import SqliteMappingRepository
        from milanon.domain.deanonymizer import DeAnonymizer
        from milanon.domain.mapping_service import MappingService
        from milanon.usecases.deanonymize import DeAnonymizeUseCase

        repo = SqliteMappingRepository(":memory:")
        service = MappingService(repo)
        da = DeAnonymizer(service)
        uc = DeAnonymizeUseCase(da, repo)

        input_dir = tmp_path / "input"
        input_dir.mkdir()
        (input_dir / "dashboard.md").write_text("# Dashboard", encoding="utf-8")

        output_dir = tmp_path / "output"
        uc.execute(input_dir, output_dir)

        assert (output_dir / "dashboard.md").exists()


# ---------------------------------------------------------------------------
# B-025: In-place de-anonymization
# ---------------------------------------------------------------------------

class TestInPlaceDeanonymization:
    """B-025: In-place de-anonymization modifies files directly."""

    def _make_uc(self, repo):
        service = MappingService(repo)
        da = DeAnonymizer(service)
        return DeAnonymizeUseCase(da, repo)

    def test_in_place_overwrites_original(self, tmp_path):
        """Content is de-anonymized in the original file location."""
        from milanon.domain.entities import EntityType

        repo = SqliteMappingRepository(":memory:")
        repo.create_mapping(EntityType.PERSON, "Thomas WEGMÜLLER")
        uc = self._make_uc(repo)

        input_dir = tmp_path / "vault"
        input_dir.mkdir()
        test_file = input_dir / "note.md"
        test_file.write_text("# [PERSON_001]\nContent about [PERSON_001].", encoding="utf-8")

        uc.execute(input_dir, in_place=True)

        content = test_file.read_text(encoding="utf-8")
        assert "Thomas WEGMÜLLER" in content
        assert "[PERSON_001]" not in content

    def test_in_place_creates_backup(self, tmp_path):
        """Original files are backed up to .milanon_backup/."""
        from milanon.domain.entities import EntityType

        repo = SqliteMappingRepository(":memory:")
        repo.create_mapping(EntityType.PERSON, "Thomas WEGMÜLLER")
        uc = self._make_uc(repo)

        input_dir = tmp_path / "vault"
        input_dir.mkdir()
        original_content = "# [PERSON_001]\nOriginal content."
        (input_dir / "note.md").write_text(original_content, encoding="utf-8")

        uc.execute(input_dir, in_place=True)

        backup = input_dir / ".milanon_backup" / "note.md"
        assert backup.exists()
        assert backup.read_text(encoding="utf-8") == original_content

    def test_in_place_renames_placeholder_filenames(self, tmp_path):
        """Placeholder filenames are resolved in-place."""
        from milanon.domain.entities import EntityType

        repo = SqliteMappingRepository(":memory:")
        repo.create_mapping(EntityType.PERSON, "Thomas WEGMÜLLER")
        uc = self._make_uc(repo)

        input_dir = tmp_path / "vault"
        input_dir.mkdir()
        (input_dir / "[PERSON_001].md").write_text("# [PERSON_001]", encoding="utf-8")

        uc.execute(input_dir, in_place=True)

        assert (input_dir / "Wegmüller_Thomas.md").exists()
        assert not (input_dir / "[PERSON_001].md").exists()
        content = (input_dir / "Wegmüller_Thomas.md").read_text(encoding="utf-8")
        assert "Thomas WEGMÜLLER" in content

    def test_in_place_no_output_dir_needed(self, tmp_path):
        """In-place mode works without output_dir parameter."""
        repo = SqliteMappingRepository(":memory:")
        uc = self._make_uc(repo)

        input_dir = tmp_path / "vault"
        input_dir.mkdir()
        (input_dir / "test.md").write_text("No placeholders here.", encoding="utf-8")

        result = uc.execute(input_dir, output_dir=None, in_place=True)
        assert result.files_scanned == 1

    def test_without_in_place_requires_output(self, tmp_path):
        """Without --in-place, output_dir is used for writing."""
        repo = SqliteMappingRepository(":memory:")
        uc = self._make_uc(repo)

        input_dir = tmp_path / "vault"
        input_dir.mkdir()
        (input_dir / "test.md").write_text("test", encoding="utf-8")

        output_dir = tmp_path / "output"
        result = uc.execute(input_dir, output_dir)
        assert result.files_scanned == 1

    def test_in_place_backup_not_reprocessed(self, tmp_path):
        """Files in .milanon_backup/ are excluded from processing."""
        from milanon.domain.entities import EntityType

        repo = SqliteMappingRepository(":memory:")
        repo.create_mapping(EntityType.PERSON, "Thomas WEGMÜLLER")
        uc = self._make_uc(repo)

        input_dir = tmp_path / "vault"
        input_dir.mkdir()
        (input_dir / "note.md").write_text("[PERSON_001] here.", encoding="utf-8")

        # First run
        uc.execute(input_dir, in_place=True)
        backup_count_before = len(list((input_dir / ".milanon_backup").rglob("*")))

        # Second run — backup dir must not be scanned
        uc.execute(input_dir, in_place=True, force=True)
        backup_count_after = len(list((input_dir / ".milanon_backup").rglob("*")))

        # Backup count must not have grown from second run
        assert backup_count_after == backup_count_before
