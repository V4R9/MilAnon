"""GenerateContextUseCase — produces an LLM context file for anonymized documents."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from milanon.domain.entities import EntityType


# Level definitions: keyword → (display name, sort order)
# Checked in order so "Stabskp" is tested before "Kp" (substring safety).
_LEVEL_RULES: list[tuple[str, str, int]] = [
    ("div",     "Division",       0),
    ("br",      "Brigade",        1),
    ("bat",     "Battalion",      2),
    ("stabskp", "Staff Company",  3),
    ("kp",      "Company",        4),
]
_LEVEL_OTHER = ("Other", 5)

_LEVEL_ORDER = {name: order for _, name, order in _LEVEL_RULES}
_LEVEL_ORDER[_LEVEL_OTHER[0]] = _LEVEL_OTHER[1]


def _parse_level(original_value: str) -> str:
    """Return the hierarchical level label for a unit name."""
    lower = original_value.lower()
    for keyword, label, _ in _LEVEL_RULES:
        if keyword in lower:
            return label
    return _LEVEL_OTHER[0]


def _parent_number(value: str) -> str | None:
    """Extract parent unit number from a sub-unit designator.

    e.g. "Inf Kp 56/1" → "56", "Inf Bat 56" → None (no slash).
    Returns the part before the slash if a 'number/number' pattern is found.
    """
    m = re.search(r"(\d+)/\d+", value)
    return m.group(1) if m else None


@dataclass
class UnitEntry:
    original_value: str
    placeholder: str
    level: str


class GenerateContextUseCase:
    """Generates a CONTEXT.md file that a commander can paste before an anonymized document.

    The output contains ONLY placeholders and level descriptions — no original values.
    """

    def __init__(self, repository) -> None:
        self._repo = repository

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_available_units(self) -> list[UnitEntry]:
        """Return all EINHEIT mappings sorted by hierarchy level."""
        mappings = [
            m for m in self._repo.get_all_mappings()
            if m.entity_type == EntityType.EINHEIT
        ]
        entries = [
            UnitEntry(m.original_value, m.placeholder, _parse_level(m.original_value))
            for m in mappings
        ]
        entries.sort(key=lambda e: (_LEVEL_ORDER.get(e.level, 99), e.original_value))
        return entries

    def generate(self, user_unit_value: str, output_path: Path) -> None:
        """Generate CONTEXT.md for *user_unit_value* and write it to *output_path*.

        Raises ValueError if the unit is not found in the database.
        """
        units = self.get_available_units()
        user_entry = next(
            (u for u in units if u.original_value.strip().lower() == user_unit_value.strip().lower()),
            None,
        )
        if user_entry is None:
            raise ValueError(f"Unit '{user_unit_value}' not found in database.")

        content = self._render(user_entry, units)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def _render(self, user_entry: UnitEntry, all_units: list[UnitEntry]) -> str:
        parent_number = _parent_number(user_entry.original_value)
        parent_entry: UnitEntry | None = None
        if parent_number:
            parent_entry = next(
                (
                    u for u in all_units
                    if parent_number in u.original_value
                    and "/" not in u.original_value
                    and u.placeholder != user_entry.placeholder
                ),
                None,
            )

        hierarchy_rows = self._build_hierarchy_rows(user_entry, all_units)
        company_placeholders = ", ".join(
            u.placeholder for u in all_units if u.level == "Company"
        )
        bat_entry = next((u for u in all_units if u.level == "Battalion"), None)

        lines: list[str] = []

        lines.append("# LLM Context — MilAnon Anonymized Document\n")
        lines.append(
            "> Paste this BEFORE your anonymized document when prompting an LLM.\n"
        )

        lines.append("\n## Your Unit\n")
        lines.append(
            f"You are assisting the commander of **{user_entry.placeholder}** "
            f"({user_entry.level}).\n"
        )
        if parent_entry:
            lines.append(
                f"Parent unit: **{parent_entry.placeholder}** ({parent_entry.level}).\n"
            )

        lines.append("\n## Organizational Hierarchy\n")
        lines.append("| Placeholder | Level | Notes |")
        lines.append("|---|---|---|")
        for row in hierarchy_rows:
            lines.append(row)

        lines.append("\n## Filtering Instructions\n")
        lines.append(
            "Use these when you want the LLM to focus on specific levels:\n"
        )
        lines.append(
            f"- **\"Information relevant to my unit only\"** → "
            f"Filter for {user_entry.placeholder}"
        )
        if company_placeholders:
            lines.append(
                f"- **\"All company-level units\"** → {company_placeholders}"
            )
        if bat_entry:
            lines.append(
                f"- **\"Battalion level only\"** → {bat_entry.placeholder}"
            )
        lines.append("- **\"All units\"** → All EINHEIT placeholders listed above")

        lines.append("\n## Rules\n")
        lines.append(
            "- Preserve all [PLACEHOLDER] tokens exactly as written in your responses."
        )
        lines.append(
            "- Do NOT attempt to guess or infer real names, locations, "
            "or unit designations."
        )
        lines.append(
            "- When referencing units, always use the exact placeholder."
        )

        return "\n".join(lines) + "\n"

    def _build_hierarchy_rows(
        self, user_entry: UnitEntry, all_units: list[UnitEntry]
    ) -> list[str]:
        rows: list[str] = []
        for unit in all_units:
            if unit.placeholder == user_entry.placeholder:
                row = (
                    f"| **{unit.placeholder}** | **{unit.level}** | **← YOUR UNIT** |"
                )
            else:
                row = f"| {unit.placeholder} | {unit.level} |  |"
            rows.append(row)
        return rows
