"""Tests for AnonymizeUseCase — batch processing, incremental, file tracking."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from milanon.adapters.recognizers.list_recognizer import ListRecognizer
from milanon.adapters.recognizers.military_recognizer import MilitaryRecognizer
from milanon.adapters.recognizers.pattern_recognizer import PatternRecognizer
from milanon.adapters.repositories.sqlite_repository import SqliteMappingRepository
from milanon.domain.anonymizer import Anonymizer
from milanon.domain.mapping_service import MappingService
from milanon.domain.recognition import RecognitionPipeline
from milanon.usecases.anonymize import AnonymizeUseCase, _embed_visual_pages


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
        result = use_case.execute(src, out_dir, include_spreadsheets=True)
        assert result.files_scanned == 1
        assert result.files_new == 1
        assert result.files_error == 0

    def test_output_file_created(self, use_case, tmp_path):
        src = _write(tmp_path / "input" / "data.csv", "Name;AHV\nBERNASCONI;756.1234.5678.97\n")
        out_dir = tmp_path / "output"
        use_case.execute(src, out_dir, include_spreadsheets=True)
        assert any(out_dir.rglob("*.csv"))

    def test_ahv_replaced_in_output(self, use_case, tmp_path):
        src = _write(tmp_path / "in" / "doc.csv", "AHV;Name\n756.1234.5678.97;BERNASCONI\n")
        out_dir = tmp_path / "out"
        use_case.execute(src, out_dir, include_spreadsheets=True)
        out_file = next(out_dir.rglob("*.csv"))
        content = out_file.read_text(encoding="utf-8")
        assert "756.1234.5678.97" not in content
        assert "[AHV_NR_001]" in content


class TestIncrementalProcessing:
    def test_unchanged_file_skipped_on_second_run(self, use_case, tmp_path):
        src = _write(tmp_path / "in" / "data.csv", "AHV\n756.1234.5678.97\n")
        out_dir = tmp_path / "out"
        # First run
        r1 = use_case.execute(src, out_dir, include_spreadsheets=True)
        assert r1.files_new == 1
        assert r1.files_skipped == 0
        # Second run — same content
        r2 = use_case.execute(src, out_dir, include_spreadsheets=True)
        assert r2.files_skipped == 1
        assert r2.files_new == 0

    def test_changed_file_reprocessed(self, use_case, tmp_path):
        src = _write(tmp_path / "in" / "data.csv", "AHV\n756.1234.5678.97\n")
        out_dir = tmp_path / "out"
        use_case.execute(src, out_dir, include_spreadsheets=True)
        # Modify the file
        src.write_text("AHV\n756.9876.5432.10\n", encoding="utf-8")
        r2 = use_case.execute(src, out_dir, include_spreadsheets=True)
        assert r2.files_changed == 1
        assert r2.files_skipped == 0

    def test_force_flag_reprocesses_unchanged(self, use_case, tmp_path):
        src = _write(tmp_path / "in" / "data.csv", "AHV\n756.1234.5678.97\n")
        out_dir = tmp_path / "out"
        use_case.execute(src, out_dir, include_spreadsheets=True)
        r2 = use_case.execute(src, out_dir, force=True, include_spreadsheets=True)
        assert r2.files_skipped == 0
        assert r2.files_changed == 1

    def test_dry_run_does_not_write_files(self, use_case, tmp_path):
        src = _write(tmp_path / "in" / "data.csv", "AHV\n756.1234.5678.97\n")
        out_dir = tmp_path / "out"
        use_case.execute(src, out_dir, dry_run=True, include_spreadsheets=True)
        assert not any(out_dir.rglob("*"))


class TestEmbedVisualPages:
    """Unit tests for _embed_visual_pages — mocks convert_from_path to avoid poppler dep."""

    def _write_md_with_marker(self, path: Path, page_num: int) -> Path:
        marker = (
            f"\n\n⚠ **Page {page_num}: Visual layout (WAP/schedule) — "
            f"not extractable as text. See original PDF.**\n\n"
        )
        path.write_text(f"# Doc\n{marker}End.", encoding="utf-8")
        return path

    def test_embed_creates_png_file(self, tmp_path):
        md = self._write_md_with_marker(tmp_path / "doc.md", 3)
        fake_image = MagicMock()
        with patch("pdf2image.convert_from_path", return_value=[fake_image]):
            _embed_visual_pages(tmp_path / "source.pdf", [3], md)
        fake_image.save.assert_called_once_with(str(tmp_path / "doc_page_3.png"))

    def test_embed_replaces_skip_marker_with_image_embed(self, tmp_path):
        md = self._write_md_with_marker(tmp_path / "doc.md", 3)
        fake_image = MagicMock()
        with patch("pdf2image.convert_from_path", return_value=[fake_image]):
            _embed_visual_pages(tmp_path / "source.pdf", [3], md)
        content = md.read_text(encoding="utf-8")
        assert "not extractable as text" not in content
        assert "embedded as image. NOT ANONYMIZED." in content
        assert "![Page 3](doc_page_3.png)" in content

    def test_embed_handles_multiple_visual_pages(self, tmp_path):
        content = (
            "\n\n⚠ **Page 2: Visual layout (WAP/schedule) — "
            "not extractable as text. See original PDF.**\n\n"
            "\n\n⚠ **Page 5: Visual layout (WAP/schedule) — "
            "not extractable as text. See original PDF.**\n\n"
        )
        md = tmp_path / "doc.md"
        md.write_text(content, encoding="utf-8")
        fake_image = MagicMock()
        with patch("pdf2image.convert_from_path", return_value=[fake_image]):
            _embed_visual_pages(tmp_path / "source.pdf", [2, 5], md)
        result = md.read_text(encoding="utf-8")
        assert "![Page 2](doc_page_2.png)" in result
        assert "![Page 5](doc_page_5.png)" in result

    def test_embed_skips_page_when_rasterization_fails(self, tmp_path):
        md = self._write_md_with_marker(tmp_path / "doc.md", 3)
        with patch(
            "pdf2image.convert_from_path", side_effect=Exception("poppler missing")
        ):
            _embed_visual_pages(tmp_path / "source.pdf", [3], md)
        # Marker should remain unchanged — no crash
        content = md.read_text(encoding="utf-8")
        assert "not extractable as text" in content

    def test_no_embed_when_embed_images_false(self, use_case, tmp_path):
        # When embed_images=False, use case should NOT call convert_from_path
        src = _write(tmp_path / "in" / "data.csv", "AHV\n756.1234.5678.97\n")
        out_dir = tmp_path / "out"
        with patch("pdf2image.convert_from_path") as mock_conv:
            use_case.execute(src, out_dir, embed_images=False, include_spreadsheets=True)
        mock_conv.assert_not_called()


class TestCsvExclusion:
    """Bug 3 fix: CSV/XLSX excluded from anonymize by default."""

    def test_csv_excluded_by_default(self, use_case, tmp_path):
        """CSV files are skipped unless --include-spreadsheets is set."""
        in_dir = tmp_path / "in"
        _write(in_dir / "data.csv", "AHV\n756.1234.5678.97\n")
        out_dir = tmp_path / "out"
        result = use_case.execute(in_dir, out_dir)
        assert result.files_scanned == 0

    def test_xlsx_excluded_by_default(self, use_case, tmp_path):
        """XLSX files are skipped unless --include-spreadsheets is set."""
        in_dir = tmp_path / "in"
        _write(in_dir / "data.xlsx", "not a real xlsx")
        out_dir = tmp_path / "out"
        result = use_case.execute(in_dir, out_dir)
        assert result.files_scanned == 0

    def test_csv_included_with_flag(self, use_case, tmp_path):
        """CSV files are processed when include_spreadsheets=True."""
        in_dir = tmp_path / "in"
        _write(in_dir / "data.csv", "AHV\n756.1234.5678.97\n")
        out_dir = tmp_path / "out"
        result = use_case.execute(in_dir, out_dir, include_spreadsheets=True)
        assert result.files_scanned == 1
        assert result.files_new == 1


class TestDirectoryProcessing:
    def test_multiple_files_in_directory(self, use_case, tmp_path):
        in_dir = tmp_path / "in"
        _write(in_dir / "a.csv", "AHV\n756.1111.1111.11\n")
        _write(in_dir / "b.csv", "AHV\n756.2222.2222.22\n")
        out_dir = tmp_path / "out"
        result = use_case.execute(in_dir, out_dir, include_spreadsheets=True)
        assert result.files_scanned == 2
        assert result.files_new == 2

    def test_unsupported_files_ignored(self, use_case, tmp_path):
        """TXT files are not in _SUPPORTED_EXTENSIONS and are ignored."""
        in_dir = tmp_path / "in"
        _write(in_dir / "readme.txt", "Not a supported format")
        out_dir = tmp_path / "out"
        result = use_case.execute(in_dir, out_dir)
        assert result.files_scanned == 0  # .txt is not supported


class TestCleanOrphans:
    """B-019: --clean removes orphaned output files."""

    def test_orphaned_output_removed(self, use_case, tmp_path):
        """Output file without corresponding input is removed."""
        input_dir = tmp_path / "input"
        input_dir.mkdir()
        _write(input_dir / "file1.csv", "col\nvalue\n")

        output_dir = tmp_path / "output"
        output_dir.mkdir()
        (output_dir / "file1.csv").write_text("Anon 1", encoding="utf-8")
        (output_dir / "file2.md").write_text("Orphan", encoding="utf-8")

        result = use_case.execute(
            input_dir, output_dir, force=True, clean=True, include_spreadsheets=True
        )

        assert not (output_dir / "file2.md").exists()
        assert result.files_cleaned == 1

    def test_non_orphaned_output_kept(self, use_case, tmp_path):
        """Output file with matching input is not removed."""
        input_dir = tmp_path / "input"
        input_dir.mkdir()
        _write(input_dir / "file1.csv", "col\nvalue\n")

        output_dir = tmp_path / "output"
        output_dir.mkdir()
        (output_dir / "file1.csv").write_text("Anon 1", encoding="utf-8")

        result = use_case.execute(
            input_dir, output_dir, force=True, clean=True, include_spreadsheets=True
        )

        assert (output_dir / "file1.csv").exists()
        assert result.files_cleaned == 0

    def test_context_md_not_cleaned(self, use_case, tmp_path):
        """CONTEXT.md is never removed by --clean."""
        input_dir = tmp_path / "input"
        input_dir.mkdir()
        _write(input_dir / "file1.csv", "col\nvalue\n")

        output_dir = tmp_path / "output"
        output_dir.mkdir()
        (output_dir / "CONTEXT.md").write_text("Context file", encoding="utf-8")

        use_case.execute(
            input_dir, output_dir, force=True, clean=True, include_spreadsheets=True
        )

        assert (output_dir / "CONTEXT.md").exists()

    def test_clean_false_does_not_remove(self, use_case, tmp_path):
        """Without --clean, orphaned files are left in place."""
        input_dir = tmp_path / "input"
        input_dir.mkdir()
        _write(input_dir / "file1.csv", "col\nvalue\n")

        output_dir = tmp_path / "output"
        output_dir.mkdir()
        (output_dir / "orphan.md").write_text("Orphan", encoding="utf-8")

        result = use_case.execute(
            input_dir, output_dir, force=True, clean=False, include_spreadsheets=True
        )

        assert (output_dir / "orphan.md").exists()
        assert result.files_cleaned == 0


class TestEntityTotal:
    """B-020: Total entity count across all tracked files."""

    def test_entities_total_set(self, use_case, tmp_path):
        """entities_total is populated after processing."""
        input_dir = tmp_path / "input"
        input_dir.mkdir()
        _write(input_dir / "file1.csv", "col\nvalue\n")
        output_dir = tmp_path / "output"

        result = use_case.execute(input_dir, output_dir, force=True, include_spreadsheets=True)

        assert result.entities_total >= 0

    def test_entities_total_on_skip(self, use_case, tmp_path):
        """On second run (skipped file), entities_total still reflects tracked data."""
        input_dir = tmp_path / "input"
        input_dir.mkdir()
        _write(input_dir / "file1.csv", "col\nvalue\n")
        output_dir = tmp_path / "output"

        use_case.execute(input_dir, output_dir, force=True, include_spreadsheets=True)
        result = use_case.execute(input_dir, output_dir, include_spreadsheets=True)

        assert result.files_skipped == 1
        assert result.entities_total >= 0


class TestRenamedFileDetection:
    """B-021: Renamed files detected via content hash."""

    def test_renamed_file_skipped(self, use_case, tmp_path):
        """A renamed file with identical content is skipped on second run."""
        input_dir = tmp_path / "input"
        input_dir.mkdir()
        output_dir = tmp_path / "output"

        _write(input_dir / "original.csv", "col\nvalue\n")
        use_case.execute(input_dir, output_dir, force=True, include_spreadsheets=True)

        # Rename: same content, different name
        (input_dir / "original.csv").rename(input_dir / "renamed.csv")

        result = use_case.execute(input_dir, output_dir, include_spreadsheets=True)
        assert result.files_skipped >= 1

    def test_unchanged_file_not_renamed_detection(self, use_case, tmp_path):
        """Same file path with same content is skipped normally (not as rename)."""
        input_dir = tmp_path / "input"
        input_dir.mkdir()
        output_dir = tmp_path / "output"

        _write(input_dir / "file.csv", "col\nvalue\n")
        use_case.execute(input_dir, output_dir, force=True, include_spreadsheets=True)
        result = use_case.execute(input_dir, output_dir, include_spreadsheets=True)

        assert result.files_skipped == 1
        assert result.files_new == 0
