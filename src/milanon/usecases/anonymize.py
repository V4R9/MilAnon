"""AnonymizeUseCase — orchestrates parsing, recognition, anonymization, and writing."""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass, field
from pathlib import Path

from milanon.adapters.parsers import get_parser
from milanon.adapters.writers.csv_writer import CsvWriter
from milanon.adapters.writers.docx_writer import DocxWriter
from milanon.adapters.writers.eml_writer import EmlWriter
from milanon.adapters.writers.markdown_writer import MarkdownWriter
from milanon.domain.anonymizer import Anonymizer
from milanon.domain.entities import DocumentFormat
from milanon.domain.recognition import RecognitionPipeline

logger = logging.getLogger(__name__)

_SUPPORTED_EXTENSIONS = {".eml", ".docx", ".pdf", ".xlsx", ".csv"}

_WRITERS = {
    DocumentFormat.EML: EmlWriter(),
    DocumentFormat.DOCX: DocxWriter(),
    DocumentFormat.PDF: MarkdownWriter(),
    DocumentFormat.XLSX: CsvWriter(),
    DocumentFormat.CSV: CsvWriter(),
    DocumentFormat.MARKDOWN: MarkdownWriter(),
}


@dataclass
class AnonymizeResult:
    files_scanned: int = 0
    files_new: int = 0
    files_changed: int = 0
    files_skipped: int = 0
    files_error: int = 0
    entities_found: int = 0
    warnings: list[str] = field(default_factory=list)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _output_path(source: Path, input_root: Path, output_dir: Path, ext: str) -> Path:
    rel = source.relative_to(input_root)
    return output_dir / rel.with_suffix(ext)


class AnonymizeUseCase:
    """Anonymizes all supported documents in a directory (incremental by default).

    Uses SHA-256 content hashing to skip unchanged files (ADR-008).
    """

    def __init__(
        self,
        pipeline: RecognitionPipeline,
        anonymizer: Anonymizer,
        repository,  # SqliteMappingRepository (has file tracking methods)
    ) -> None:
        self._pipeline = pipeline
        self._anonymizer = anonymizer
        self._repository = repository

    def execute(
        self,
        input_path: Path,
        output_dir: Path,
        recursive: bool = False,
        force: bool = False,
        dry_run: bool = False,
    ) -> AnonymizeResult:
        """Anonymize documents in input_path.

        Args:
            input_path: File or directory to process.
            output_dir: Directory where anonymized files are written.
            recursive: If True, recurse into subdirectories.
            force: If True, reprocess all files regardless of hash.
            dry_run: If True, report what would be done without writing.

        Returns:
            AnonymizeResult with processing statistics.
        """
        result = AnonymizeResult()

        if input_path.is_file():
            files = [input_path]
            input_root = input_path.parent
        else:
            pattern = "**/*" if recursive else "*"
            files = [
                f for f in input_path.glob(pattern)
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
        self,
        file_path: Path,
        input_root: Path,
        output_dir: Path,
        force: bool,
        dry_run: bool,
        result: AnonymizeResult,
    ) -> None:
        current_hash = _sha256(file_path)
        rel_path = str(file_path.relative_to(input_root))

        if not force:
            tracking = self._repository.get_file_tracking(rel_path, "anonymize")
            if tracking and tracking["content_hash"] == current_hash:
                result.files_skipped += 1
                logger.info("Skipping %s (unchanged)", file_path.name)
                return

        is_new = self._repository.get_file_tracking(rel_path, "anonymize") is None
        if is_new:
            result.files_new += 1
        else:
            result.files_changed += 1

        if dry_run:
            logger.info("[dry-run] Would process: %s", file_path.name)
            return

        # Parse
        parser = get_parser(file_path)
        document = parser.parse(file_path)

        # Recognize
        entities = self._pipeline.recognize(document)
        result.entities_found += len(entities)

        # Anonymize
        anon_doc = self._anonymizer.anonymize(
            document, entities, source_document=file_path.name
        )
        result.warnings.extend(anon_doc.warnings)

        # Write
        writer = _WRITERS.get(document.format, MarkdownWriter())
        ext = writer.default_extension()
        out_path = _output_path(file_path, input_root, output_dir, ext)
        writer.write(anon_doc, out_path)

        # Track
        self._repository.upsert_file_tracking(
            rel_path,
            current_hash,
            "anonymize",
            output_path=str(out_path),
            entity_count=len(entities),
        )

        logger.info(
            "Anonymized %s → %s (%d entities)",
            file_path.name,
            out_path.name,
            len(entities),
        )
