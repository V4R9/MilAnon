"""DeAnonymizeUseCase — batch de-anonymization with incremental processing."""

from __future__ import annotations

import hashlib
import logging
import shutil
from dataclasses import dataclass, field
from pathlib import Path

from milanon.domain.anonymizer import PLACEHOLDER_PATTERN
from milanon.domain.deanonymizer import DeAnonymizer, _to_obsidian_filename

_FILENAME_PLACEHOLDER_RE = PLACEHOLDER_PATTERN

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

    def _deanonymize_filename(self, filename: str) -> str:
        """Replace placeholders in a filename with resolved, filesystem-safe values.

        '[PERSON_005].md' → 'Brüngger_Xenia.md'
        'dashboard.md' → 'dashboard.md' (unchanged)
        """
        def _resolve_in_filename(match: re.Match[str]) -> str:
            placeholder = match.group(0)
            original = self._deanonymizer.resolve_placeholder(placeholder)
            if original:
                return _to_obsidian_filename(original)
            return match.group(0)

        return _FILENAME_PLACEHOLDER_RE.sub(_resolve_in_filename, filename)

    def execute(
        self,
        input_path: Path,
        output_dir: Path | None = None,
        force: bool = False,
        dry_run: bool = False,
        in_place: bool = False,
    ) -> DeAnonymizeResult:
        result = DeAnonymizeResult()

        if in_place:
            if input_path.is_file():
                files = [input_path]
                input_root = input_path.parent
            else:
                files = [
                    f for f in input_path.glob("**/*")
                    if f.is_file()
                    and f.suffix.lower() in _SUPPORTED_EXTENSIONS
                    and ".milanon_backup" not in f.parts
                ]
                input_root = input_path

            result.files_scanned = len(files)
            for file_path in files:
                try:
                    self._process_file(
                        file_path, input_root, None, force, dry_run, True, result
                    )
                except Exception as exc:
                    logger.error("Error processing %s: %s", file_path, exc)
                    result.files_error += 1
                    result.warnings.append(f"{file_path.name}: {exc}")
            return result

        # Non-in-place: output_dir is required
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
                    file_path, input_root, output_dir, force, dry_run, False, result
                )
            except Exception as exc:
                logger.error("Error processing %s: %s", file_path, exc)
                result.files_error += 1
                result.warnings.append(f"{file_path.name}: {exc}")

        return result

    def _process_file(
        self, file_path, input_root, output_dir, force, dry_run, in_place, result
    ) -> None:
        current_hash = _sha256(file_path)
        rel_path = str(file_path.relative_to(input_root))

        if not force:
            tracking = self._repository.get_file_tracking(rel_path, "deanonymize")
            if tracking and tracking["content_hash"] == current_hash:
                result.files_skipped += 1
                return

            # B-021: Renamed file detection — same hash, different path
            try:
                existing_by_hash = self._repository.get_file_tracking_by_hash(
                    current_hash, "deanonymize"
                )
                if existing_by_hash and existing_by_hash["file_path"] != rel_path:
                    logger.info(
                        "Detected renamed file: %s → %s",
                        existing_by_hash["file_path"],
                        rel_path,
                    )
                    out = existing_by_hash.get("output_path", "")
                    self._repository.upsert_file_tracking(
                        rel_path, current_hash, "deanonymize", output_path=out
                    )
                    result.files_skipped += 1
                    return
            except Exception:
                pass  # Fall through to normal processing

        is_new = self._repository.get_file_tracking(rel_path, "deanonymize") is None
        if is_new:
            result.files_new += 1
        else:
            result.files_changed += 1

        if dry_run:
            return

        logger.info("Processing %s…", file_path.name)

        content = file_path.read_text(encoding="utf-8")
        restored, warnings = self._deanonymizer.deanonymize(content)
        result.warnings.extend(warnings)

        placeholders_in_file = len(self._deanonymizer.find_placeholders(content))
        unresolved = len(warnings)
        result.placeholders_resolved += placeholders_in_file - unresolved

        if in_place:
            # Backup original before modifying
            backup_dir = input_root / ".milanon_backup"
            backup_dir.mkdir(parents=True, exist_ok=True)
            rel = file_path.relative_to(input_root)
            backup_path = backup_dir / rel
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, backup_path)

            # Overwrite original with restored content
            file_path.write_text(restored, encoding="utf-8")
            out_path = file_path

            # Rename file if filename contains placeholders
            original_name = out_path.name
            new_name = self._deanonymize_filename(original_name)
            if new_name != original_name:
                new_path = out_path.parent / new_name
                out_path.rename(new_path)
                out_path = new_path
                logger.debug("Renamed %s → %s", original_name, new_name)
        else:
            # Write to output directory
            out_path = output_dir / file_path.relative_to(input_root)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(restored, encoding="utf-8")

            # Rename in output dir if filename contains placeholders
            original_name = out_path.name
            new_name = self._deanonymize_filename(original_name)
            if new_name != original_name:
                new_path = out_path.parent / new_name
                if out_path.exists():
                    out_path.rename(new_path)
                out_path = new_path
                logger.debug("Renamed %s → %s", original_name, new_name)

        self._repository.upsert_file_tracking(
            rel_path, current_hash, "deanonymize", output_path=str(out_path)
        )
