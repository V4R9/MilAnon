"""Workflow configuration domain model — parsed from INDEX.yaml."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class DoctrineRef:
    """Reference to a doctrine source and its optional extract file."""

    source: str             # Full doctrine file in data/doctrine/
    extract: str | None     # Extract file in data/doctrine/extracts/ (or None)


@dataclass
class WorkflowConfig:
    """Configuration for one workflow, parsed from INDEX.yaml."""

    name: str
    description: str
    system_prompt: str              # Layer 4 template filename (e.g. "templates/analyse.md")
    doctrine: list[DoctrineRef]     # Layer 3 sources
    skeleton: str | None            # Skeleton filename (if Befehlsgebung)
    output_format: list[str]        # ["markdown", "docx"]
    maps_to_5plus2: str             # Which 5+2 step this maps to (from "maps_to_5+2")
    depends_on: list[str] = field(default_factory=list)


def load_workflows(index_path: Path) -> dict[str, WorkflowConfig]:
    """Parse INDEX.yaml and return workflow configs keyed by workflow name.

    Raises FileNotFoundError if the index file does not exist.
    Raises KeyError for unknown workflow names when accessed on the result dict.
    """
    if not index_path.exists():
        raise FileNotFoundError(f"INDEX.yaml not found: {index_path}")

    with index_path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)

    raw_workflows: dict = data.get("workflows", {}) or {}
    result: dict[str, WorkflowConfig] = {}

    for key, wf in raw_workflows.items():
        doctrine_entries: list[DoctrineRef] = []
        for entry in wf.get("doctrine", []) or []:
            doctrine_entries.append(
                DoctrineRef(
                    source=entry.get("source", ""),
                    extract=entry.get("extract"),  # may be None
                )
            )

        result[str(key)] = WorkflowConfig(
            name=wf.get("name", str(key)),
            description=wf.get("description", ""),
            system_prompt=wf.get("system_prompt", ""),
            doctrine=doctrine_entries,
            skeleton=wf.get("skeleton"),
            output_format=list(wf.get("output_format", ["markdown"])),
            # YAML key is "maps_to_5+2" — Python attribute is maps_to_5plus2
            maps_to_5plus2=wf.get("maps_to_5+2", ""),
            depends_on=list(wf.get("depends_on", []) or []),
        )

    return result
