"""UnpackUseCase — de-anonymizes LLM output from clipboard or file."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path

from milanon.domain.deanonymizer import DeAnonymizer

logger = logging.getLogger(__name__)

_SECTION_SEPARATOR_RE = re.compile(r"\n---\n")

# Detect Markdown H1 headers that could be filenames
_FILENAME_HEADER_RE = re.compile(r"^#\s+(.+\.md)\s*$", re.MULTILINE)

# Characters not allowed in filenames
_UNSAFE_CHARS_RE = re.compile(r'[<>:"/\\|?*]')


@dataclass
class UnpackResult:
    """Result of unpacking LLM output."""

    source: str = ""  # "clipboard", "file:<name>", or "text"
    placeholders_resolved: int = 0
    files_written: int = 0
    output_files: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class UnpackUseCase:
    """De-anonymizes LLM output and writes to target directory.

    Supports input from: clipboard, file, or raw text.
    Supports output modes: single file, split on --- separators, or in-place.
    """

    def __init__(self, deanonymizer: DeAnonymizer) -> None:
        self._deanonymizer = deanonymizer

    def execute(
        self,
        output_dir: Path,
        input_text: str | None = None,
        input_file: Path | None = None,
        from_clipboard: bool = False,
        split_sections: bool = False,
        in_place: bool = False,
    ) -> UnpackResult:
        """De-anonymize LLM output and write to output_dir.

        Exactly one of input_text, input_file, or from_clipboard must be set.

        Args:
            output_dir: Directory to write de-anonymized files.
            input_text: Raw LLM output text.
            input_file: Path to a file containing LLM output.
            from_clipboard: If True, read from system clipboard.
            split_sections: If True, split on --- and write separate files.
            in_place: If True and input_file is set, overwrite the input file.

        Returns:
            UnpackResult with statistics and file paths.
        """
        result = UnpackResult()

        # Read input — exactly one source must be provided
        if from_clipboard:
            from milanon.usecases.pack import _read_from_clipboard
            raw_text = _read_from_clipboard()
            result.source = "clipboard"
            if not raw_text.strip():
                result.warnings.append("Clipboard is empty")
                return result
        elif input_file is not None:
            raw_text = input_file.read_text(encoding="utf-8")
            result.source = f"file:{input_file.name}"
        elif input_text is not None:
            raw_text = input_text
            result.source = "text"
        else:
            raise ValueError("One of input_text, input_file, or from_clipboard must be set")

        # De-anonymize
        restored, warnings = self._deanonymizer.deanonymize(raw_text)
        result.warnings.extend(warnings)

        # Count resolved placeholders
        original_count = len(self._deanonymizer.find_placeholders(raw_text))
        result.placeholders_resolved = original_count - len(warnings)

        # Write output
        if in_place and input_file is not None:
            input_file.write_text(restored, encoding="utf-8")
            result.files_written = 1
            result.output_files.append(str(input_file))
        elif split_sections:
            sections = self._split_into_sections(restored)
            output_dir.mkdir(parents=True, exist_ok=True)
            for filename, content in sections:
                out_path = output_dir / filename
                out_path.write_text(content, encoding="utf-8")
                result.output_files.append(str(out_path))
                result.files_written += 1
                logger.info("Wrote %s", out_path)
        else:
            output_dir.mkdir(parents=True, exist_ok=True)
            out_path = output_dir / "llm_output.md"
            out_path.write_text(restored, encoding="utf-8")
            result.files_written = 1
            result.output_files.append(str(out_path))

        return result

    def _split_into_sections(self, text: str) -> list[tuple[str, str]]:
        """Split text on --- separators. Extract filenames from H1 headers.

        Returns list of (filename, content) tuples.
        """
        raw_sections = _SECTION_SEPARATOR_RE.split(text)
        named_sections: list[tuple[str, str]] = []

        for i, section in enumerate(raw_sections):
            section = section.strip()
            if not section:
                continue

            header_match = _FILENAME_HEADER_RE.search(section)
            if header_match:
                filename = _UNSAFE_CHARS_RE.sub("_", header_match.group(1).strip())
            else:
                filename = f"section_{i + 1:03d}.md"

            named_sections.append((filename, section))

        return named_sections
