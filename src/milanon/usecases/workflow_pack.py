"""WorkflowPackUseCase — builds doctrine-aware 5-layer prompts."""

from __future__ import annotations

import logging
import re
import tempfile
from pathlib import Path

from milanon.domain.workflow import load_workflows
from milanon.usecases.pack import PackResult, _copy_to_clipboard

logger = logging.getLogger(__name__)

_DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"
_TEMPLATES_DIR = _DATA_DIR / "templates"
_DOCTRINE_DIR = _DATA_DIR / "doctrine"

_SUPPORTED_INPUT_EXTENSIONS = {".md", ".eml", ".txt", ".csv"}


def _strip_mode_markers(text: str, mode: str) -> str:
    """Remove mode-specific HTML comments that don't apply.

    Keep:  <!-- BERRM: ... --> if mode is "berrm"
    Strip: <!-- ADF: ... -->   if mode is "berrm"
    Always keep: <!-- BOTH: -->, <!-- KDT ENTSCHEID: -->, <!-- FILL: -->
    """
    if mode == "berrm":
        text = re.sub(r"<!--\s*ADF:.*?-->", "", text)
    elif mode == "adf":
        text = re.sub(r"<!--\s*BERRM:.*?-->", "", text)
    return text


class WorkflowPackUseCase:
    """Assembles a 5-layer prompt for a given workflow, mode, and step.

    Layer 1: Role (static) — from data/templates/role.md
    Layer 2: Unit Context — from GenerateContextUseCase
    Layer 3: Doctrine — chapter extracts from data/doctrine/extracts/
    Layer 4: Task — workflow-specific template from data/templates/workflows/
    Layer 5: Rules (static) — from data/templates/rules.md

    Plus: Anonymized documents from --input
    Plus: Previous step outputs from --context
    """

    def __init__(
        self,
        repository,
        context_generator,
        templates_dir: Path | None = None,
        doctrine_dir: Path | None = None,
    ) -> None:
        self._repo = repository
        self._context_gen = context_generator
        self._templates_dir = templates_dir or _TEMPLATES_DIR
        self._doctrine_dir = doctrine_dir or _DOCTRINE_DIR
        self._workflows_dir = self._templates_dir / "workflows"
        self._index_path = self._doctrine_dir / "INDEX.yaml"

    def execute(
        self,
        workflow: str,
        mode: str = "berrm",
        step: int | None = None,
        input_path: Path | None = None,
        unit: str = "",
        context_path: Path | None = None,
        output_path: Path | None = None,
        copy_clipboard: bool = True,
    ) -> tuple[str, PackResult]:
        """Build a 5-layer doctrine-aware prompt pack.

        Args:
            workflow:      Workflow name from INDEX.yaml (e.g. "analyse", "wachtdienst").
            mode:          "berrm" or "adf" — strips irrelevant mode markers.
            step:          Current 5+2 step (1-5). Affects skeleton inclusion.
            input_path:    Directory or file with anonymized documents.
            unit:          Unit designator for context generation.
            context_path:  Directory with previous-step vault files (.md).
            output_path:   If set, write the assembled pack to this file.
            copy_clipboard: Copy result to system clipboard.

        Returns:
            Tuple of (pack_text, PackResult).
        """
        result = PackResult()

        # Load workflow config
        workflows = load_workflows(self._index_path)
        if workflow not in workflows:
            raise ValueError(
                f"Workflow '{workflow}' not found in INDEX.yaml. "
                f"Available: {list(workflows.keys())}"
            )
        wf_config = workflows[workflow]
        result.template_used = workflow

        # --- Layer 1: Role ---
        layer1 = self._load_static_layer(
            self._templates_dir / "role.md",
            placeholder="<!-- Layer 1: Role (role.md not found) -->",
        )

        # --- Layer 2: Unit Context ---
        layer2 = self._get_unit_context(unit)

        # --- Layer 3: Doctrine extracts ---
        layer3_parts: list[str] = []
        for ref in wf_config.doctrine:
            if not ref.extract:
                continue
            extract_path = self._doctrine_dir / ref.extract
            if not extract_path.exists():
                logger.warning(
                    "Doctrine extract not found (skipping): %s", extract_path
                )
                continue
            text = extract_path.read_text(encoding="utf-8")
            layer3_parts.append(text)
        layer3 = "\n\n".join(layer3_parts)

        # --- Layer 4: Workflow template ---
        template_filename = Path(wf_config.system_prompt).name
        template_path = self._workflows_dir / template_filename
        if not template_path.exists():
            raise ValueError(
                f"Workflow template not found: {template_path}. "
                f"Create data/templates/workflows/{template_filename} first."
            )
        layer4 = template_path.read_text(encoding="utf-8")

        # Append skeleton if step 5 (Befehlsgebung) and skeleton defined
        if step == 5 and wf_config.skeleton:
            skeleton_path = self._doctrine_dir / wf_config.skeleton
            if skeleton_path.exists():
                layer4 += "\n\n" + skeleton_path.read_text(encoding="utf-8")
            else:
                logger.warning("Skeleton not found (skipping): %s", skeleton_path)

        # --- Layer 5: Rules ---
        layer5 = self._load_static_layer(
            self._templates_dir / "rules.md",
            placeholder="<!-- Layer 5: Rules (rules.md not found) -->",
        )

        # Apply mode marker stripping to all content layers
        layer1 = _strip_mode_markers(layer1, mode)
        layer2 = _strip_mode_markers(layer2, mode)
        layer3 = _strip_mode_markers(layer3, mode)
        layer4 = _strip_mode_markers(layer4, mode)
        layer5 = _strip_mode_markers(layer5, mode)

        # --- Context files (previous step outputs) ---
        context_parts: list[str] = []
        if context_path and context_path.is_dir():
            for f in sorted(context_path.glob("*.md")):
                context_parts.append(
                    f"## Context: {f.name}\n\n" + f.read_text(encoding="utf-8")
                )
            if context_parts:
                result.context_included = True
        elif context_path and context_path.is_file():
            context_parts.append(context_path.read_text(encoding="utf-8"))
            result.context_included = True

        # --- Anonymized documents ---
        doc_texts: list[str] = []
        if input_path is not None:
            if input_path.is_file():
                doc_texts.append(
                    f"## Document: {input_path.name}\n\n"
                    + input_path.read_text(encoding="utf-8")
                )
                result.documents_included = 1
            elif input_path.is_dir():
                for f in sorted(input_path.glob("**/*")):
                    if f.is_file() and f.suffix.lower() in _SUPPORTED_INPUT_EXTENSIONS:
                        doc_texts.append(
                            f"## Document: {f.name}\n\n"
                            + f.read_text(encoding="utf-8")
                        )
                        result.documents_included += 1

        # --- Assemble ---
        sections: list[str] = []
        for layer in (layer1, layer2, layer3, layer4, layer5):
            if layer.strip():
                sections.append(layer)

        if context_parts:
            sections.append("---")
            sections.extend(context_parts)

        if doc_texts:
            sections.append("---")
            sections.append("# ANONYMIZED DOCUMENTS")
            sections.extend(doc_texts)

        pack_text = "\n\n".join(sections)
        result.total_chars = len(pack_text)

        # --- Output ---
        if copy_clipboard:
            result.copied_to_clipboard = _copy_to_clipboard(pack_text)

        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(pack_text, encoding="utf-8")
            result.output_path = str(output_path)

        return pack_text, result

    def _load_static_layer(self, path: Path, placeholder: str) -> str:
        """Read a static layer file; return placeholder text if file is missing."""
        if path.exists():
            return path.read_text(encoding="utf-8")
        logger.debug("Static layer file not found, using placeholder: %s", path)
        return placeholder

    def _get_unit_context(self, unit: str) -> str:
        """Generate unit context text via GenerateContextUseCase.

        Returns empty string if unit is empty or context generation fails.
        """
        if not unit or self._context_gen is None:
            return ""
        try:
            tmp_path = Path(tempfile.mktemp(suffix=".md"))
            self._context_gen.generate(unit, tmp_path)
            text = tmp_path.read_text(encoding="utf-8")
            tmp_path.unlink(missing_ok=True)
            return text
        except Exception as exc:
            logger.warning(
                "Could not generate unit context for '%s': %s", unit, exc
            )
            return ""
