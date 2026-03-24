"""DoctrineExtractUseCase — extracts chapters from doctrine Markdown files."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

# Matches headings: "### 5.2.1 Einsatzgrundsätze", "# 5 Aktionsplanung", etc.
# Group 1 = hashes, group 2 = chapter number (digits/dots), group 3 = title text
_HEADING_RE: re.Pattern[str] = re.compile(r"^(#{1,6})\s+\*{0,2}(\d+(?:\.\d+)*)\*{0,2}\s+(.+)$")

# Minimal YAML key-value extractor — used for INDEX.yaml (no pyyaml dependency)
_YAML_KEY_RE: re.Pattern[str] = re.compile(r"^(\s{2})(\S[^:]+\.md):\s*$")
_YAML_TITLE_RE: re.Pattern[str] = re.compile(r'^\s+title:\s*"?(.+?)"?\s*$')
_YAML_REGULATION_RE: re.Pattern[str] = re.compile(r'^\s+regulation:\s*"?(.+?)"?\s*$')
_YAML_LIST_ITEM_RE: re.Pattern[str] = re.compile(r'^\s+- "?(.+?)"?\s*$')


# ---------------------------------------------------------------------------
# Extract definitions — maps output filename → (source file, chapter number)
# ---------------------------------------------------------------------------

EXTRACTS: dict[str, tuple[str, str]] = {
    "bfe_initialisierung.md":      ("52_080_bfe_einsatz.md",              "5.1.1"),
    "bfe_problemerfassung.md":     ("52_080_bfe_einsatz.md",              "5.1.2"),
    "bfe_sofortmassnahmen.md":     ("52_080_bfe_einsatz.md",              "5.2"),
    "bfe_zeitplanung.md":          ("52_080_bfe_einsatz.md",              "5.3"),
    "bfe_bdl.md":                  ("52_080_bfe_einsatz.md",              "5.4"),
    "bfe_entschlussfassung.md":    ("52_080_bfe_einsatz.md",              "5.5"),
    "bfe_planentwicklung.md":      ("52_080_bfe_einsatz.md",              "5.6"),
    "bfe_befehlsgebung.md":        ("52_080_bfe_einsatz.md",              "5.7"),
    "fso_aktionsplanung.md":       ("50_040_fso_17.md",                   "4.2"),
    "tf_einsatzgrundsaetze.md":    ("50_030_taktische_fuehrung.md",       "5.2.1"),
    "tf_taktische_grundsaetze.md": ("50_030_taktische_fuehrung.md",       "5.2.3"),
    "tf_raumordnung.md":           ("50_030_taktische_fuehrung.md",       "5.4"),
    "tf_taktische_aufgaben.md":    ("50_030_taktische_fuehrung.md",       "5.5"),
    "wat_wachtdienstbefehl.md":    ("51_301_wachtdienst_aller_truppen.md", "10"),
}


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------

@dataclass
class ExtractResult:
    """Summary of a bulk extract_all() run."""

    extracts_attempted: int = 0
    extracts_succeeded: int = 0
    extracts_failed: int = 0
    failed_names: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Chapter extraction helpers
# ---------------------------------------------------------------------------

def _is_child_chapter(parent: str, candidate: str) -> bool:
    """Return True if candidate is the same as or a descendant of parent.

    Examples:
        _is_child_chapter("5.4", "5.4")    → True
        _is_child_chapter("5.4", "5.4.1")  → True
        _is_child_chapter("5.4", "5.5")    → False
        _is_child_chapter("5.4", "6")      → False
    """
    return candidate == parent or candidate.startswith(parent + ".")


def extract_chapter(lines: list[str], chapter_num: str) -> str | None:
    """Extract the content block for a given chapter number from document lines.

    Finds the first heading matching chapter_num exactly, then collects
    everything up to (but not including) the next heading that is not a
    descendant of chapter_num.

    Returns None if the chapter heading is not found.
    """
    start_idx = -1
    for i, line in enumerate(lines):
        m = _HEADING_RE.match(line)
        if m and m.group(2) == chapter_num:
            start_idx = i
            break

    if start_idx < 0:
        return None

    end_idx = len(lines)
    for i in range(start_idx + 1, len(lines)):
        m = _HEADING_RE.match(lines[i])
        if m and not _is_child_chapter(chapter_num, m.group(2)):
            end_idx = i
            break

    content = "".join(lines[start_idx:end_idx])
    return content.rstrip("\n") + "\n"


# ---------------------------------------------------------------------------
# INDEX.yaml parser (no pyyaml dependency)
# ---------------------------------------------------------------------------

def _parse_index_yaml(path: Path) -> list[dict]:
    """Parse the doctrine_files section from INDEX.yaml without pyyaml.

    Reads only the `doctrine_files:` block, extracting filename, title,
    regulation, and key_chapters for each entry.
    """
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    entries: list[dict] = []
    in_doctrine_files = False
    in_key_chapters = False
    current: dict | None = None

    for line in lines:
        # Detect section start
        if line.strip() == "doctrine_files:":
            in_doctrine_files = True
            continue

        # Detect section end: top-level non-blank, non-comment line after our section
        if in_doctrine_files and line and not line.startswith(" ") and not line.startswith("#"):
            if current:
                entries.append(current)
                current = None
            in_doctrine_files = False
            continue

        if not in_doctrine_files:
            continue

        # 2-space-indented .md filename key
        m_key = _YAML_KEY_RE.match(line)
        if m_key:
            if current:
                entries.append(current)
            current = {
                "filename": m_key.group(2),
                "title": "",
                "regulation": "",
                "key_chapters": [],
            }
            in_key_chapters = False
            continue

        if current is None:
            continue

        # key_chapters list block
        if "key_chapters:" in line:
            in_key_chapters = True
            continue

        # Other nested keys reset the list block
        if re.match(r"^\s{4}\w+:", line) and "key_chapters" not in line:
            in_key_chapters = False

        if in_key_chapters:
            m_item = _YAML_LIST_ITEM_RE.match(line)
            if m_item:
                current["key_chapters"].append(m_item.group(1))
            continue

        m_title = _YAML_TITLE_RE.match(line)
        if m_title and not current["title"]:
            current["title"] = m_title.group(1)
            continue

        m_reg = _YAML_REGULATION_RE.match(line)
        if m_reg and not current["regulation"]:
            current["regulation"] = m_reg.group(1)

    if current:
        entries.append(current)

    return entries


# ---------------------------------------------------------------------------
# Use case
# ---------------------------------------------------------------------------

class DoctrineExtractUseCase:
    """Extracts doctrine chapters into compact Markdown files for LLM prompts.

    Source files are in doctrine_dir/*.md.
    Extracted chapters are written to doctrine_dir/extracts/ by default,
    or to a caller-supplied output directory.
    """

    def __init__(self, doctrine_dir: Path) -> None:
        self._doctrine_dir = doctrine_dir

    def list_doctrine_files(self) -> list[dict]:
        """Return metadata for all doctrine source files defined in INDEX.yaml.

        Returns a list of dicts with keys: filename, title, regulation,
        key_chapters.  Returns an empty list if INDEX.yaml is not found.
        """
        index_path = self._doctrine_dir / "INDEX.yaml"
        if not index_path.exists():
            logger.warning("INDEX.yaml not found at %s", index_path)
            return []
        return _parse_index_yaml(index_path)

    def extract_chapter(
        self,
        source_filename: str,
        chapter_num: str,
        output_path: Path,
    ) -> bool:
        """Extract one chapter from a source file and write to output_path.

        Returns True on success, False if the source file is missing or the
        chapter number is not found.
        """
        source_path = self._doctrine_dir / source_filename
        if not source_path.exists():
            logger.warning("Source file not found: %s", source_path)
            return False

        lines = source_path.read_text(encoding="utf-8").splitlines(keepends=True)
        content = extract_chapter(lines, chapter_num)

        if content is None:
            logger.warning("Chapter %s not found in %s", chapter_num, source_filename)
            return False

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")
        logger.info(
            "Extracted %s § %s → %s (%d chars)",
            source_filename, chapter_num, output_path.name, len(content),
        )
        return True

    def extract_all(self, output_dir: Path) -> dict[str, bool]:
        """Extract all configured chapters to output_dir.

        Returns a mapping of {extract_filename: success}.
        """
        results: dict[str, bool] = {}
        for name, (source, chapter) in EXTRACTS.items():
            success = self.extract_chapter(source, chapter, output_dir / name)
            results[name] = success
        return results
