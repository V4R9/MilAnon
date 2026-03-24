"""Markdown writer — writes anonymized content as a Markdown file."""

from __future__ import annotations

from pathlib import Path

from milanon.domain.entities import AnonymizedDocument


class MarkdownWriter:
    """Writes an AnonymizedDocument to a Markdown (.md) file.

    The legend block (if present) is already embedded in doc.content
    by the Anonymizer. Page-break separators (---) from PDF parsing
    are preserved as-is.
    """

    def write(self, document: AnonymizedDocument, output_path: Path) -> Path:
        """Write anonymized content to a Markdown file.

        Args:
            document: The anonymized document to write.
            output_path: Destination file path (created if needed).

        Returns:
            The path to the written file.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(document.content, encoding="utf-8")
        return output_path

    def default_extension(self) -> str:
        return ".md"
