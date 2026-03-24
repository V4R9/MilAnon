"""CSV utility helpers shared across import use cases."""

from __future__ import annotations

import csv


def detect_delimiter(text: str) -> str:
    """Auto-detect CSV delimiter via Sniffer. Falls back to first-line counting.

    Handles semicolon (MilOffice/PISA), comma (Excel EN locale), and tab (TSV)
    delimiters. Uses the first 4096 characters as the Sniffer sample.
    """
    try:
        dialect = csv.Sniffer().sniff(text[:4096], delimiters=";,\t")
        return dialect.delimiter
    except csv.Error:
        first_line = text.split("\n")[0]
        if first_line.count(";") > first_line.count(","):
            return ";"
        return ","
