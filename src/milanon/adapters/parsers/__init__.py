"""Document parsers — one parser per file format."""

from __future__ import annotations

from pathlib import Path

from milanon.adapters.parsers.docx_parser import DocxParser
from milanon.adapters.parsers.eml_parser import EmlParser
from milanon.adapters.parsers.pdf_parser import PdfParser
from milanon.adapters.parsers.xlsx_csv_parser import XlsxCsvParser
from milanon.domain.protocols import DocumentParser

# Singleton instances — created once at import time
_PARSERS: list[DocumentParser] = [
    EmlParser(),
    DocxParser(),
    PdfParser(),
    XlsxCsvParser(),
]

# Extension → parser map built once
_EXTENSION_MAP: dict[str, DocumentParser] = {
    ext: parser
    for parser in _PARSERS
    for ext in parser.supported_extensions()
}


def get_parser(path: Path) -> DocumentParser:
    """Return the appropriate parser for the given file extension.

    Raises:
        ValueError: If no parser supports the file extension.
    """
    ext = path.suffix.lower()
    parser = _EXTENSION_MAP.get(ext)
    if parser is None:
        supported = sorted(_EXTENSION_MAP.keys())
        raise ValueError(
            f"No parser available for extension '{ext}'. "
            f"Supported extensions: {supported}"
        )
    return parser
