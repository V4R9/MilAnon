"""DeAnonymizeUseCase — batch de-anonymization with incremental processing."""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass, field
from pathlib import Path

from milanon.adapters.writers.markdown_writer import MarkdownWriter
from milanon.domain.deanonymizer import DeAnonymizer
from milanon.domain.entities import AnonymizedDocument, DocumentFormat

logger = logging.getLogger(__name__)

_SUPPORTED_EXTENSIONS = {".md", ".txt", ".docx", ".eml"}


@dataclass
class DeAnonymizeResult:
    files_scanned: int = 0
    files_new: int = 0
    files_changed: int = 0
    files_skipped: int = 0
    files_error: int = 0
    placeholders_resolved: int = 0
    warnings: list[str] = field(default_factory=list)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class DeAnonymizeUseCase:
    """Restores placeholders in LLM output files to their original values."""

    def __init__(self, deanonymizer: DeAnonymizer, repository) -> None:
        self._deanonymizer = deanonymizer
        self._repository = repository

    def execute(
        self,
        input_path: Path,
        output_dir: Path,
        force: bool = False,
        dry_run: bool = False,
    ) -> DeAnonymizeResult:
        result = DeAnonymizeResult()

        if input_path.is_file():
            files = [input_path]
            input_root = input_path.parent
        else:
            files = [
                f for f in input_path.glob("**/*")
                if f.is_file() and f.suffix.lower() in _SUPPORTED_EXTENSIONS
            ]
            input_root = input_path

        result.files_scanned = len(files)

        for file_path in files:
            try:
                self._process_file(
                    file_path, input_root, output_dir, force, dry_run, result
                )
            except Exception as exc:
                logger.error("Error processing %s: %s", file_path, exc)
                result.files_error += 1
                result.warnings.append(f"{file_path.name}: {exc}")

        return result

    def _process_file(
        self, file_path, input_root, output_dir, force, dry_run, result
    ) -> None:
        current_hash = _sha256(file_path)
        rel_path = str(file_path.relative_to(input_root))

        if not force:
            tracking = self._repository.get_file_tracking(rel_path, "deanonymize")
            if tracking and tracking["content_hash"] == current_hash:
                result.files_skipped += 1
                return

        is_new = self._repository.get_file_tracking(rel_path, "deanonymize") is None
        if is_new:
            result.files_new += 1
        else:
            result.files_changed += 1

        if dry_run:
            return

        content = file_path.read_text(encoding="utf-8")
        restored, warnings = self._deanonymizer.deanonymize(content)
        result.warnings.extend(warnings)

        placeholders_in_file = len(self._deanonymizer.find_placeholders(content))
        unresolved = len(warnings)
        result.placeholders_resolved += placeholders_in_file - unresolved

        out_path = output_dir / file_path.relative_to(input_root)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(restored, encoding="utf-8")

        self._repository.upsert_file_tracking(
            rel_path, current_hash, "deanonymize", output_path=str(out_path)
        )
