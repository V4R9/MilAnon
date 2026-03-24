"""ValidateOutputUseCase — checks placeholder integrity in LLM output files."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from milanon.domain.deanonymizer import DeAnonymizer

_PLACEHOLDER_RE = re.compile(r"\[([A-Z_]+)_(\d{3})\]")


@dataclass
class ValidationResult:
    file_path: str
    total_placeholders: int = 0
    resolved: int = 0
    unresolved: int = 0
    unresolved_list: list[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return self.unresolved == 0


class ValidateOutputUseCase:
    """Validates that all placeholders in a file can be resolved from the DB."""

    def __init__(self, deanonymizer: DeAnonymizer) -> None:
        self._deanonymizer = deanonymizer

    def execute(self, file_path: Path) -> ValidationResult:
        """Check every placeholder in the file against the mapping DB.

        Args:
            file_path: Path to the (LLM-processed) anonymized file.

        Returns:
            ValidationResult with counts and list of unresolved placeholders.
        """
        content = file_path.read_text(encoding="utf-8")
        placeholders = self._deanonymizer.find_placeholders(content)

        result = ValidationResult(file_path=str(file_path))
        result.total_placeholders = len(placeholders)

        seen: set[str] = set()
        for ph in placeholders:
            if ph in seen:
                continue
            seen.add(ph)
            original = self._deanonymizer.resolve_placeholder(ph)
            if original is not None:
                result.resolved += 1
            else:
                result.unresolved += 1
                result.unresolved_list.append(ph)

        return result
