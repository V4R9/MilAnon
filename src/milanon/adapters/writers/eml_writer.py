"""EML writer — writes anonymized content as a plain-text .eml file."""

from __future__ import annotations

from pathlib import Path

from milanon.domain.anonymizer import LEGEND_PATTERN
from milanon.domain.entities import AnonymizedDocument


class EmlWriter:
    """Writes anonymized EML content to a .eml file.

    The content field is expected to contain the anonymized email body
    (headers + body as extracted by EmlParser, with placeholders).
    A minimal EML envelope is generated.
    """

    def write(self, document: AnonymizedDocument, output_path: Path) -> Path:
        """Write anonymized content to a .eml file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Strip legend block
        body = LEGEND_PATTERN.sub("", document.content).strip()

        # Wrap in a minimal EML envelope if not already one
        if not body.startswith(("From:", "Return-Path:", "Received:")):
            eml_content = (
                "Content-Type: text/plain; charset=utf-8\r\n"
                "Content-Transfer-Encoding: 8bit\r\n"
                "\r\n"
                + body
            )
        else:
            eml_content = body

        output_path.write_text(eml_content, encoding="utf-8")
        return output_path

    def default_extension(self) -> str:
        return ".eml"
