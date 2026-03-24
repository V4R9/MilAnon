"""GenerateProjectUseCase — generate a ready-to-import Claude.ai Project folder."""

from __future__ import annotations

import logging
import shutil
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

# Doctrine extracts grouped by knowledge file
_KNOWLEDGE_MAP: dict[str, list[str]] = {
    "bfe_aktionsplanung.md": [
        "extracts/bfe_initialisierung.md",
        "extracts/bfe_problemerfassung.md",
        "extracts/bfe_sofortmassnahmen.md",
        "extracts/bfe_zeitplanung.md",
        "extracts/bfe_bdl.md",
        "extracts/bfe_entschlussfassung.md",
        "extracts/bfe_planentwicklung.md",
        "extracts/bfe_befehlsgebung.md",
    ],
    "tf_taktik.md": [
        "extracts/tf_einsatzgrundsaetze.md",
        "extracts/tf_taktische_grundsaetze.md",
        "extracts/tf_raumordnung.md",
        "extracts/tf_taktische_aufgaben.md",
    ],
    "wat_wachtdienst.md": [
        "extracts/wat_wachtdienstbefehl.md",
    ],
    "fso_aktionsplanung.md": [
        "extracts/fso_aktionsplanung.md",
    ],
}

_LAYER_2_TEMPLATE = """\
## Deine Einheit

Du arbeitest für den Kommandanten der **{unit}**.

Alle Personen, Orte, Einheiten und andere sensible Angaben sind anonymisiert.
Wenn du Platzhalter wie [PERSON_001], [ORT_003], [EINHEIT_002] siehst,
verwende sie GENAU SO weiter — ersetze sie NIEMALS durch echte Werte.

Der Kdt wird dir sein Bat Dossier (Einsatzbefehl, Beilagen, Karten) als
anonymisierte Dokumente hochladen. Arbeite damit.
"""

_README_MD = """\
# MilAnon Command Assistant — Setup-Anleitung

## Schritt 1: Projekt erstellen
Gehe auf claude.ai → Projects → «Neues Projekt erstellen»

## Schritt 2: Projektanweisung einfügen
Öffne die Datei `SYSTEM_PROMPT.md`, kopiere den GESAMTEN Inhalt (Cmd+A, Cmd+C)
und füge ihn in das Feld «Custom Instructions» ein.

## Schritt 3: Knowledge Files hochladen
Öffne den Ordner `knowledge/` und ziehe ALLE Dateien per Drag & Drop
in den Bereich «Project Knowledge».

Folgende Dateien sollten hochgeladen werden:
- Anonymisiertes Bat Dossier (*.md Dateien)
- bfe_aktionsplanung.md — Doktrin: BFE Aktionsplanung
- tf_taktik.md — Doktrin: TF Taktische Grundsätze
- fso_aktionsplanung.md — Doktrin: FSO Aktionsplanung
- wat_wachtdienst.md — Doktrin: WAT Wachtdienst
- skeletons.md — Befehlsvorlagen
- (optional) *.png — Visuelle Seiten (WAP, Karten)

## Schritt 4: Los gehts
Öffne `CHEAT_SHEET.md` (oder drucke es aus).
Starte einen neuen Chat und sage: «Analysiere mein Bat Dossier»

## Nach Abschluss
Wenn du den fertigen Befehl hast, kopiere Claude's Output und führe auf deinem Mac aus:
```
milanon unpack --clipboard --output vault/Dossier/ --split
milanon export vault/Dossier/ei_bf.md --docx --deanonymize
```
"""


@dataclass
class GenerateProjectResult:
    output_dir: Path
    files_created: list[str]
    unit: str


class GenerateProjectUseCase:
    """Generate a ready-to-import Claude.ai Project folder.

    Output structure:
    project/
      README.md            — Setup guide (German, 4-step)
      SYSTEM_PROMPT.md     — Layers 1+2+5 combined (paste into Claude.ai)
      CHEAT_SHEET.md       — Quick reference (print out)
      knowledge/           — Doctrine extracts merged by topic
                             + anonymized input documents (if --input given)
    """

    def __init__(self, data_dir: Path):
        self._data_dir = data_dir
        self._doctrine_dir = data_dir / "doctrine"
        self._templates_dir = data_dir / "templates"

    def execute(
        self,
        unit: str,
        output_dir: Path,
        input_path: Path | None = None,
        include_images: bool = False,
    ) -> GenerateProjectResult:
        """Generate the project folder.

        Args:
            unit: The unit designation, e.g. "Inf Kp 56/1".
            output_dir: Where to create the project folder.
            input_path: Optional path to anonymized documents to copy into knowledge/.
            include_images: If True, also copy PNG files from input_path.

        Returns:
            Result with list of created files.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        knowledge_dir = output_dir / "knowledge"
        knowledge_dir.mkdir(parents=True, exist_ok=True)

        files_created: list[str] = []

        # 1. SYSTEM_PROMPT.md — Layers 1 + 2 + 5
        system_prompt = self._build_system_prompt(unit)
        (output_dir / "SYSTEM_PROMPT.md").write_text(system_prompt, encoding="utf-8")
        files_created.append("SYSTEM_PROMPT.md")

        # 2. Knowledge files — merged doctrine extracts
        for knowledge_file, extract_paths in _KNOWLEDGE_MAP.items():
            merged = self._merge_extracts(extract_paths)
            if merged:
                (knowledge_dir / knowledge_file).write_text(merged, encoding="utf-8")
                files_created.append(f"knowledge/{knowledge_file}")

        # 3. Skeletons — all in one file
        skeletons_content = self._merge_skeletons()
        if skeletons_content:
            (knowledge_dir / "skeletons.md").write_text(skeletons_content, encoding="utf-8")
            files_created.append("knowledge/skeletons.md")

        # 4. Copy anonymized documents into knowledge/
        if input_path:
            for f in sorted(input_path.glob("*.md")):
                shutil.copy2(f, knowledge_dir / f.name)
                files_created.append(f"knowledge/{f.name}")
            if include_images:
                for f in sorted(input_path.glob("*.png")):
                    shutil.copy2(f, knowledge_dir / f.name)
                    files_created.append(f"knowledge/{f.name}")

        # 5. README.md — setup guide (replaces INSTRUCTIONS.md)
        (output_dir / "README.md").write_text(_README_MD, encoding="utf-8")
        files_created.append("README.md")

        # 6. CHEAT_SHEET.md — copy from templates (replaces WORKFLOWS.md)
        cheat_sheet_src = self._templates_dir / "CHEAT_SHEET.md"
        if cheat_sheet_src.exists():
            shutil.copy2(cheat_sheet_src, output_dir / "CHEAT_SHEET.md")
            files_created.append("CHEAT_SHEET.md")

        logger.info("Project generated at %s with %d files", output_dir, len(files_created))
        return GenerateProjectResult(
            output_dir=output_dir,
            files_created=files_created,
            unit=unit,
        )

    def _build_system_prompt(self, unit: str) -> str:
        """Combine Layer 1 (role) + Layer 2 (unit context) + Layer 5 (rules)."""
        parts: list[str] = []

        # Layer 1: role.md
        role_path = self._templates_dir / "role.md"
        if role_path.exists():
            parts.append(role_path.read_text(encoding="utf-8").strip())

        # Layer 2: unit context (template with {unit} replaced)
        layer2 = _LAYER_2_TEMPLATE.format(unit=unit)
        parts.append(layer2.strip())

        # Layer 5: rules.md
        rules_path = self._templates_dir / "rules.md"
        if rules_path.exists():
            parts.append(rules_path.read_text(encoding="utf-8").strip())

        return "\n\n---\n\n".join(parts) + "\n"

    def _merge_extracts(self, extract_paths: list[str]) -> str:
        """Merge multiple doctrine extract files into one."""
        parts: list[str] = []
        for rel_path in extract_paths:
            full_path = self._doctrine_dir / rel_path
            if full_path.exists():
                content = full_path.read_text(encoding="utf-8").strip()
                if content:
                    parts.append(content)
            else:
                logger.warning("Doctrine extract not found: %s", full_path)
        return "\n\n---\n\n".join(parts) + "\n" if parts else ""

    def _merge_skeletons(self) -> str:
        """Merge all active skeleton files into one knowledge file."""
        skeletons_dir = self._doctrine_dir / "skeletons"
        if not skeletons_dir.exists():
            return ""

        parts: list[str] = []
        # Only active skeletons (not superseded ones, not README)
        active_names = [
            "5_punkte_befehl_universal.md",
            "000_allgemeiner_befehl.md",
            "300_wachtdienstbefehl.md",
        ]
        for name in active_names:
            path = skeletons_dir / name
            if path.exists():
                content = path.read_text(encoding="utf-8").strip()
                if content:
                    parts.append(f"# Skeleton: {name}\n\n{content}")

        return "\n\n---\n\n".join(parts) + "\n" if parts else ""
