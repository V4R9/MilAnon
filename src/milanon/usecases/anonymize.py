"""AnonymizeUseCase — orchestrates parsing, recognition, anonymization, and writing."""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass, field
from pathlib import Path

from milanon.adapters.repositories.sqlite_repository import SqliteMappingRepository

from milanon.adapters.parsers import get_parser
from milanon.adapters.parsers.pdf_parser import VISUAL_PAGE_EMBED_MARKER, VISUAL_PAGE_SKIP_MARKER
from milanon.adapters.writers.csv_writer import CsvWriter
from milanon.adapters.writers.docx_writer import DocxWriter
from milanon.adapters.writers.eml_writer import EmlWriter
from milanon.adapters.writers.markdown_writer import MarkdownWriter
from milanon.domain.anonymizer import Anonymizer
from milanon.domain.entities import DocumentFormat
from milanon.domain.recognition import RecognitionPipeline

logger = logging.getLogger(__name__)

_EMBED_DPI = 200

_SUPPORTED_EXTENSIONS = {".eml", ".docx", ".pdf"}
_SPREADSHEET_EXTENSIONS = {".xlsx", ".csv"}

_WRITERS = {
    DocumentFormat.EML: EmlWriter(),
    DocumentFormat.DOCX: DocxWriter(),
    DocumentFormat.PDF: MarkdownWriter(),
    DocumentFormat.XLSX: CsvWriter(),
    DocumentFormat.CSV: CsvWriter(),
    DocumentFormat.MARKDOWN: MarkdownWriter(),
}


@dataclass(frozen=True)
class ProcessingOptions:
    force: bool = False
    dry_run: bool = False
    embed_images: bool = False
    include_spreadsheets: bool = False


@dataclass
class AnonymizeResult:
    files_scanned: int = 0
    files_new: int = 0
    files_changed: int = 0
    files_skipped: int = 0
    files_error: int = 0
    files_cleaned: int = 0
    entities_found: int = 0
    entities_total: int = 0
    visual_page_count: int = 0
    warnings: list[str] = field(default_factory=list)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _output_path(source: Path, input_root: Path, output_dir: Path, ext: str) -> Path:
    rel = source.relative_to(input_root)
    return output_dir / rel.with_suffix(ext)


def _embed_visual_pages(source_pdf: Path, visual_pages: list[int], out_md: Path) -> None:
    """Rasterize visual PDF pages and replace their skip markers with image embeds.

    For each page number in visual_pages:
    - Converts the page to a PNG at 200 DPI next to out_md.
    - Replaces the ⚠ skip marker in out_md with an image embed marker.

    Silently skips pages that fail to rasterize (e.g. poppler not installed).
    """
    try:
        import pdf2image as _pdf2image
    except ImportError:
        logger.warning("pdf2image not installed — cannot embed visual pages as images")
        return

    content = out_md.read_text(encoding="utf-8")
    changed = False

    for page_num in visual_pages:
        png_name = f"{out_md.stem}_page_{page_num}.png"
        png_path = out_md.parent / png_name
        try:
            images = _pdf2image.convert_from_path(
                str(source_pdf),
                first_page=page_num,
                last_page=page_num,
                dpi=_EMBED_DPI,
            )
            if images:
                images[0].save(str(png_path))
                logger.info("Embedded page %d as %s", page_num, png_name)
        except Exception as exc:
            logger.warning("Could not rasterize page %d of %s: %s", page_num, source_pdf.name, exc)
            continue

        skip = VISUAL_PAGE_SKIP_MARKER.format(page_num=page_num)
        embed = VISUAL_PAGE_EMBED_MARKER.format(page_num=page_num, png_name=png_name)
        if skip in content:
            content = content.replace(skip, embed)
            changed = True

    if changed:
        out_md.write_text(content, encoding="utf-8")


class AnonymizeUseCase:
    """Anonymizes all supported documents in a directory (incremental by default).

    Uses SHA-256 content hashing to skip unchanged files (ADR-008).
    """

    def __init__(
        self,
        pipeline: RecognitionPipeline,
        anonymizer: Anonymizer,
        repository: SqliteMappingRepository,
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
        embed_images: bool = False,
        clean: bool = False,
        include_spreadsheets: bool = False,
    ) -> AnonymizeResult:
        """Anonymize documents in input_path.

        Args:
            input_path: File or directory to process.
            output_dir: Directory where anonymized files are written.
            recursive: If True, recurse into subdirectories.
            force: If True, reprocess all files regardless of hash.
            dry_run: If True, report what would be done without writing.
            embed_images: If True, rasterize visual PDF pages and embed as PNG.
            clean: If True, remove output files with no corresponding input file.
            include_spreadsheets: If True, also process .csv and .xlsx files.

        Returns:
            AnonymizeResult with processing statistics.
        """
        options = ProcessingOptions(
            force=force, dry_run=dry_run, embed_images=embed_images,
            include_spreadsheets=include_spreadsheets,
        )
        result = AnonymizeResult()

        allowed_extensions = _SUPPORTED_EXTENSIONS | (_SPREADSHEET_EXTENSIONS if include_spreadsheets else set())

        if input_path.is_file():
            files = [input_path]
            input_root = input_path.parent
        else:
            pattern = "**/*" if recursive else "*"
            files = [
                f for f in input_path.glob(pattern)
                if f.is_file() and f.suffix.lower() in allowed_extensions
            ]
            input_root = input_path

        result.files_scanned = len(files)

        for file_path in files:
            try:
                self._process_file(file_path, input_root, output_dir, options, result)
            except Exception as exc:
                logger.error("Error processing %s: %s", file_path, exc)
                result.files_error += 1
                result.warnings.append(f"{file_path.name}: {exc}")

        # B-019: Remove orphaned output files
        if clean and not dry_run:
            result.files_cleaned = self._clean_orphaned_outputs(
                input_path, output_dir, files, input_root
            )

        # B-020: Total entity count across all tracked files
        try:
            tracked_counts = []
            for f in files:
                rel_path = str(f.relative_to(input_root))
                tracking = self._repository.get_file_tracking(rel_path, "anonymize")
                if tracking:
                    tracked_counts.append(tracking.get("entity_count", 0))
            result.entities_total = sum(tracked_counts)
        except Exception:
            result.entities_total = result.entities_found

        return result

    def _process_file(
        self,
        file_path: Path,
        input_root: Path,
        output_dir: Path,
        options: ProcessingOptions,
        result: AnonymizeResult,
    ) -> None:
        current_hash = _sha256(file_path)
        rel_path = str(file_path.relative_to(input_root))

        if not options.force:
            tracking = self._repository.get_file_tracking(rel_path, "anonymize")
            if tracking and tracking["content_hash"] == current_hash:
                result.files_skipped += 1
                logger.info("Skipping %s (unchanged)", file_path.name)
                return

            # B-021: Renamed file detection — same hash, different path
            existing_by_hash = self._find_tracking_by_hash(current_hash, "anonymize")
            if existing_by_hash and existing_by_hash["file_path"] != rel_path:
                logger.info(
                    "Detected renamed file: %s → %s (same content hash)",
                    existing_by_hash["file_path"],
                    rel_path,
                )
                # TECH DEBT: Accesses repository._conn directly. Should be a proper
                # repository method (get_tracking_by_hash). Deferred to avoid parallel
                # session conflict. See Code Review.
                self._repository.upsert_file_tracking(
                    rel_path,
                    current_hash,
                    "anonymize",
                    output_path=existing_by_hash.get("output_path", ""),
                    entity_count=existing_by_hash.get("entity_count", 0),
                )
                result.files_skipped += 1
                return

        is_new = self._repository.get_file_tracking(rel_path, "anonymize") is None
        if is_new:
            result.files_new += 1
        else:
            result.files_changed += 1

        if options.dry_run:
            logger.info("[dry-run] Would process: %s", file_path.name)
            return

        logger.info("Processing %s…", file_path.name)

        # Parse
        parser = get_parser(file_path)
        document = parser.parse(file_path)

        # Track visual pages (PDF WAP/schedule grids)
        result.visual_page_count += len(getattr(document, "visual_pages", []))

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

        # Embed visual pages as PNG if requested (PDFs only)
        if options.embed_images and getattr(document, "visual_pages", []):
            _embed_visual_pages(file_path, document.visual_pages, out_path)

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

    def _find_tracking_by_hash(self, content_hash: str, operation: str) -> dict | None:
        """Find a file tracking record by content hash (for rename detection).

        Returns the first matching record dict, or None.
        """
        try:
            # TECH DEBT: Accesses repository._conn directly. Should be a proper
            # repository method (get_tracking_by_hash). Deferred to avoid parallel
            # session conflict. See Code Review.
            conn = self._repository._conn
            row = conn.execute(
                "SELECT * FROM file_tracking WHERE content_hash = ? AND operation = ? LIMIT 1",
                (content_hash, operation),
            ).fetchone()
            return dict(row) if row else None
        except Exception:
            return None

    def _clean_orphaned_outputs(
        self,
        input_path: Path,
        output_dir: Path,
        processed_files: list[Path],
        input_root: Path,
    ) -> int:
        """Remove output files that no longer have a corresponding input file.

        Compares output directory contents against input file list.
        Only removes files with extensions that MilAnon produces (.md, .eml, .csv, .docx, .txt).
        Returns count of removed files.
        """
        if not output_dir.exists():
            return 0

        _ext_map = {
            ".eml": ".eml",
            ".pdf": ".md",
            ".docx": ".docx",
            ".xlsx": ".csv",
            ".csv": ".csv",
            ".md": ".md",
            ".txt": ".txt",
        }

        expected_outputs: set[str] = set()
        for f in processed_files:
            rel = f.relative_to(input_root)
            out_ext = _ext_map.get(f.suffix.lower(), ".md")
            expected_outputs.add(str(rel.with_suffix(out_ext)))

        _output_extensions = {".md", ".eml", ".csv", ".docx", ".txt"}
        removed = 0
        for out_file in output_dir.glob("**/*"):
            if not out_file.is_file():
                continue
            if out_file.suffix.lower() not in _output_extensions:
                continue
            if out_file.name == "CONTEXT.md":
                continue
            rel_out = str(out_file.relative_to(output_dir))
            if rel_out not in expected_outputs:
                out_file.unlink()
                logger.info("Cleaned orphaned output: %s", rel_out)
                removed += 1

        return removed
