"""PackUseCase — builds a ready-to-paste prompt package for LLM interaction."""

from __future__ import annotations

import logging
import platform
import subprocess
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

_TEMPLATES_DIR = Path(__file__).parent.parent.parent.parent / "data" / "templates"
_USER_TEMPLATES_DIR = Path.home() / ".milanon" / "templates"

_SUPPORTED_INPUT_EXTENSIONS = {".md", ".eml", ".txt", ".csv"}


@dataclass
class PackResult:
    """Result of building a prompt pack."""

    template_used: str = ""
    context_included: bool = False
    documents_included: int = 0
    total_chars: int = 0
    copied_to_clipboard: bool = False
    output_path: str = ""


def list_templates() -> list[dict[str, str]]:
    """Return all available templates with name and description.

    Scans both built-in (data/templates/) and user templates (~/.milanon/templates/).
    Returns list of dicts with keys: name, path, source ("built-in" or "custom").
    """
    templates: list[dict[str, str]] = []

    for directory, source_label in [
        (_TEMPLATES_DIR, "built-in"),
        (_USER_TEMPLATES_DIR, "custom"),
    ]:
        if not directory.exists():
            continue
        for f in sorted(directory.glob("*.md")):
            desc = ""
            for line in f.read_text(encoding="utf-8").splitlines()[:3]:
                if line.startswith("# Template:"):
                    desc = line.replace("# Template:", "").strip()
                    break
            templates.append({
                "name": f.stem,
                "path": str(f),
                "source": source_label,
                "description": desc,
            })

    return templates


def _copy_to_clipboard(text: str) -> bool:
    """Copy text to system clipboard. Returns True on success."""
    system = platform.system()
    cmd: list[str] | None = None
    if system == "Darwin":
        cmd = ["pbcopy"]
    elif system == "Linux":
        cmd = ["xclip", "-selection", "clipboard"]

    if cmd is None:
        return False

    try:
        subprocess.run(
            cmd,
            input=text.encode("utf-8"),
            check=True,
            timeout=5,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        logger.warning("Could not copy to clipboard")
        return False


def _read_from_clipboard() -> str:
    """Read text from system clipboard. Returns empty string on failure."""
    system = platform.system()
    cmd: list[str] | None = None
    if system == "Darwin":
        cmd = ["pbpaste"]
    elif system == "Linux":
        cmd = ["xclip", "-selection", "clipboard", "-o"]

    if cmd is None:
        return ""

    try:
        proc = subprocess.run(cmd, capture_output=True, check=True, timeout=5)
        return proc.stdout.decode("utf-8")
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        logger.warning("Could not read from clipboard")
        return ""


class PackUseCase:
    """Builds a prompt package from context + template + anonymized documents.

    The pack is a single Markdown text that can be pasted into Claude.ai.
    It contains: LLM instructions, unit context, task template, and all
    anonymized document content.
    """

    def __init__(self, repository) -> None:
        self._repo = repository

    def execute(
        self,
        input_path: Path,
        template_name: str = "frei",
        user_prompt: str = "",
        user_unit: str = "",
        context_path: Path | None = None,
        output_path: Path | None = None,
        copy_clipboard: bool = True,
    ) -> tuple[str, PackResult]:
        """Build a prompt pack and optionally copy to clipboard.

        Args:
            input_path: Directory with anonymized .md files or single file.
            template_name: Name of the template to use (without .md extension).
            user_prompt: Custom prompt text (used when template is "frei").
            user_unit: Unit designation for template variable replacement.
            context_path: Path to CONTEXT.md (auto-detected if None).
            output_path: If set, write pack to this file.
            copy_clipboard: If True, copy pack to system clipboard.

        Returns:
            Tuple of (pack_text, PackResult).
        """
        result = PackResult()

        # 1. Load and fill template
        template_text = self._load_template(template_name)
        result.template_used = template_name
        if user_unit:
            template_text = template_text.replace("{user_unit}", user_unit)
        if user_prompt:
            template_text = template_text.replace("{user_prompt}", user_prompt)

        # 2. Load context (CONTEXT.md) — explicit path or auto-detect
        context_text = ""
        if context_path and context_path.exists():
            context_text = context_path.read_text(encoding="utf-8")
            result.context_included = True
        else:
            candidates = [
                input_path / "CONTEXT.md",
                input_path.parent / "CONTEXT.md",
            ]
            for candidate in candidates:
                if candidate.exists():
                    context_text = candidate.read_text(encoding="utf-8")
                    result.context_included = True
                    break

        # 3. Load anonymized documents
        doc_texts: list[str] = []
        if input_path.is_file():
            doc_texts.append(
                f"## Document: {input_path.name}\n\n"
                + input_path.read_text(encoding="utf-8")
            )
            result.documents_included = 1
        else:
            for f in sorted(input_path.glob("**/*")):
                if f.is_file() and f.suffix.lower() in _SUPPORTED_INPUT_EXTENSIONS:
                    if f.name == "CONTEXT.md":
                        continue
                    doc_texts.append(
                        f"## Document: {f.name}\n\n"
                        + f.read_text(encoding="utf-8")
                    )
                    result.documents_included += 1

        # 4. Assemble pack
        sections: list[str] = []
        if context_text:
            sections.append(context_text)
        sections.append("---\n")
        sections.append(template_text)
        sections.append("\n---\n")
        sections.append("# ANONYMIZED DOCUMENTS\n")
        for doc in doc_texts:
            sections.append(doc)
            sections.append("\n---\n")

        pack_text = "\n".join(sections)
        result.total_chars = len(pack_text)

        # 5. Copy to clipboard
        if copy_clipboard:
            result.copied_to_clipboard = _copy_to_clipboard(pack_text)

        # 6. Write to file
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(pack_text, encoding="utf-8")
            result.output_path = str(output_path)

        return pack_text, result

    def _load_template(self, name: str) -> str:
        """Load a template by name. Checks custom dir first, then built-in."""
        user_path = _USER_TEMPLATES_DIR / f"{name}.md"
        if user_path.exists():
            return user_path.read_text(encoding="utf-8")

        builtin_path = _TEMPLATES_DIR / f"{name}.md"
        if builtin_path.exists():
            return builtin_path.read_text(encoding="utf-8")

        raise ValueError(
            f"Template '{name}' not found. "
            f"Checked: {_USER_TEMPLATES_DIR} and {_TEMPLATES_DIR}"
        )
