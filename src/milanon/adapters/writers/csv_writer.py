"""CSV writer — writes anonymized spreadsheet content as a .csv file."""

from __future__ import annotations

import csv
import io
from pathlib import Path

from milanon.domain.entities import AnonymizedDocument


class CsvWriter:
    """Writes anonymized CSV content back to a .csv file.

    If the AnonymizedDocument has structured_content["tables"], the first
    table is written as properly quoted CSV. Otherwise, the plain text
    content (pipe-separated) is written as-is.
    """

    def write(self, document: AnonymizedDocument, output_path: Path) -> Path:
        """Write anonymized content to a CSV file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if document.structured_content and "tables" in document.structured_content:
            tables = document.structured_content["tables"]
            rows = tables[0] if tables else []
            self._write_rows(rows, output_path)
        else:
            output_path.write_text(document.content, encoding="utf-8")

        return output_path

    def _write_rows(self, rows: list[list[str]], output_path: Path) -> None:
        buf = io.StringIO()
        writer = csv.writer(buf, delimiter=";")
        for row in rows:
            writer.writerow(row)
        output_path.write_text(buf.getvalue(), encoding="utf-8")

    def default_extension(self) -> str:
        return ".csv"
