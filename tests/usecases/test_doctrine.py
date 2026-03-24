"""Tests for DoctrineExtractUseCase — chapter extraction from doctrine files."""

from __future__ import annotations

from pathlib import Path

import pytest

from milanon.usecases.doctrine import (
    EXTRACTS,
    DoctrineExtractUseCase,
    extract_chapter,
)

# Path to the real doctrine source files (read-only)
_DOCTRINE_DIR = Path(__file__).parent.parent.parent / "data" / "doctrine"
_BFE_FILE = _DOCTRINE_DIR / "52_080_bfe_einsatz.md"
_TF_FILE = _DOCTRINE_DIR / "50_030_taktische_fuehrung.md"
_FSO_FILE = _DOCTRINE_DIR / "50_040_fso_17.md"
_WAT_FILE = _DOCTRINE_DIR / "51_301_wachtdienst_aller_truppen.md"


@pytest.fixture
def use_case() -> DoctrineExtractUseCase:
    return DoctrineExtractUseCase(_DOCTRINE_DIR)


@pytest.fixture
def bfe_lines() -> list[str]:
    return _BFE_FILE.read_text(encoding="utf-8").splitlines(keepends=True)


@pytest.fixture
def tf_lines() -> list[str]:
    return _TF_FILE.read_text(encoding="utf-8").splitlines(keepends=True)


@pytest.fixture
def fso_lines() -> list[str]:
    return _FSO_FILE.read_text(encoding="utf-8").splitlines(keepends=True)


# ---------------------------------------------------------------------------
# Chapter extraction — BFE
# ---------------------------------------------------------------------------

class TestExtractBfeChapter511:
    def test_extract_bfe_chapter_5_1_1_returns_content_with_initialisierung(
        self, bfe_lines
    ):
        content = extract_chapter(bfe_lines, "5.1.1")
        assert content is not None
        assert "5.1.1" in content
        assert "Initialisierung" in content

    def test_extract_bfe_5_1_1_does_not_include_5_1_2(self, bfe_lines):
        content = extract_chapter(bfe_lines, "5.1.1")
        assert content is not None
        # The heading "5.1.2" should NOT appear in 5.1.1 extract
        assert "### 5.1.2" not in content
        assert "# 5.1.2" not in content

    def test_extract_bfe_5_1_1_starts_with_heading(self, bfe_lines):
        content = extract_chapter(bfe_lines, "5.1.1")
        assert content is not None
        assert content.lstrip().startswith("#")


class TestExtractBfeChapter54:
    def test_extract_bfe_chapter_5_4_returns_full_bdl_section(self, bfe_lines):
        content = extract_chapter(bfe_lines, "5.4")
        assert content is not None
        assert "5.4" in content
        assert "Beurteilung der Lage" in content

    def test_extract_bfe_5_4_includes_subsections(self, bfe_lines):
        """5.4 extract must include 5.4.1, 5.4.2, 5.4.3 (all of BdL)."""
        content = extract_chapter(bfe_lines, "5.4")
        assert content is not None
        assert "5.4.1" in content
        assert "5.4.2" in content
        assert "5.4.3" in content

    def test_extract_bfe_5_4_does_not_include_5_5(self, bfe_lines):
        content = extract_chapter(bfe_lines, "5.4")
        assert content is not None
        assert "## 5.5" not in content
        assert "Entschlussfassung" not in content


# ---------------------------------------------------------------------------
# Chapter extraction — FSO
# ---------------------------------------------------------------------------

class TestExtractFso42:
    def test_extract_fso_4_2_returns_aktionsplanung(self, fso_lines):
        content = extract_chapter(fso_lines, "4.2")
        assert content is not None
        assert "4.2" in content
        assert "Aktionsplanung" in content

    def test_extract_fso_4_2_includes_all_subsections(self, fso_lines):
        """FSO 4.2 includes 4.2.1 through 4.2.7."""
        content = extract_chapter(fso_lines, "4.2")
        assert content is not None
        for sub in ["4.2.1", "4.2.2", "4.2.3", "4.2.4", "4.2.5", "4.2.6", "4.2.7"]:
            assert sub in content, f"Expected subsection {sub} in FSO 4.2 extract"

    def test_extract_fso_4_2_does_not_include_chapter_5(self, fso_lines):
        content = extract_chapter(fso_lines, "4.2")
        assert content is not None
        assert "# 5 " not in content


# ---------------------------------------------------------------------------
# Chapter extraction — TF
# ---------------------------------------------------------------------------

class TestExtractTf521:
    def test_extract_tf_5_2_1_returns_einsatzgrundsaetze(self, tf_lines):
        content = extract_chapter(tf_lines, "5.2.1")
        assert content is not None
        assert "5.2.1" in content
        assert "Einsatzgrundsätze" in content

    def test_extract_tf_5_2_1_does_not_include_5_2_2(self, tf_lines):
        content = extract_chapter(tf_lines, "5.2.1")
        assert content is not None
        assert "5.2.2" not in content


# ---------------------------------------------------------------------------
# Nonexistent chapter
# ---------------------------------------------------------------------------

class TestExtractNonexistentChapter:
    def test_extract_nonexistent_chapter_logs_warning(
        self, use_case: DoctrineExtractUseCase, tmp_path: Path, caplog
    ):
        """Requesting a chapter that doesn't exist logs a warning and returns False."""
        import logging
        with caplog.at_level(logging.WARNING):
            success = use_case.extract_chapter(
                "52_080_bfe_einsatz.md",
                "99.99",
                tmp_path / "nonexistent.md",
            )
        assert success is False
        assert any("99.99" in record.message for record in caplog.records)

    def test_extract_nonexistent_chapter_does_not_create_file(
        self, use_case: DoctrineExtractUseCase, tmp_path: Path
    ):
        use_case.extract_chapter("52_080_bfe_einsatz.md", "99.99", tmp_path / "out.md")
        assert not (tmp_path / "out.md").exists()


# ---------------------------------------------------------------------------
# list_doctrine_files
# ---------------------------------------------------------------------------

class TestListDoctrine:
    def test_list_doctrine_returns_11_source_files(self, use_case: DoctrineExtractUseCase):
        files = use_case.list_doctrine_files()
        assert len(files) == 11

    def test_list_doctrine_entries_have_filename(self, use_case: DoctrineExtractUseCase):
        files = use_case.list_doctrine_files()
        for f in files:
            assert "filename" in f
            assert f["filename"].endswith(".md")

    def test_list_doctrine_entries_have_title(self, use_case: DoctrineExtractUseCase):
        files = use_case.list_doctrine_files()
        bfe = next((f for f in files if "52_080" in f["filename"]), None)
        assert bfe is not None
        assert "BFE" in bfe.get("title", "") or "Behelf" in bfe.get("title", "")


# ---------------------------------------------------------------------------
# extract_all
# ---------------------------------------------------------------------------

class TestExtractAll:
    def test_extract_all_creates_14_files(
        self, use_case: DoctrineExtractUseCase, tmp_path: Path
    ):
        results = use_case.extract_all(tmp_path)
        assert len(results) == 14
        succeeded = [name for name, ok in results.items() if ok]
        assert len(succeeded) == 14, (
            f"Expected all 14 extracts to succeed. Failed: "
            f"{[name for name, ok in results.items() if not ok]}"
        )
        for name in EXTRACTS:
            assert (tmp_path / name).exists(), f"Expected file {name} to exist"

    def test_extract_all_files_have_content(
        self, use_case: DoctrineExtractUseCase, tmp_path: Path
    ):
        use_case.extract_all(tmp_path)
        for name in EXTRACTS:
            path = tmp_path / name
            assert path.exists()
            assert path.stat().st_size > 100, f"{name} is suspiciously small"
