"""GenerateProjectUseCase — generate a ready-to-import Claude.ai Project folder."""

from __future__ import annotations

import logging
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

_INSTRUCTIONS_MD = """\
# MilAnon Command Assistant — Anleitung

## Was ist dieses Projekt?

Dieses Claude-Projekt ist dein persönlicher **Stabsassistent auf Stufe Einheit**.
Es enthält das gesamte doktrinelle Wissen (BFE, TF, FSO, WAT) und führt dich
durch den 5+2 Aktionsplanungsprozess — von der Problemerfassung bis zum
druckfertigen 5-Punkte-Befehl.

Alle Daten bleiben anonym: Personen, Orte und Einheiten erscheinen als
Platzhalter (z.B. [PERSON_001], [ORT_003]). Die Rück-Anonymisierung erfolgt
lokal mit MilAnon.

## Wie richte ich es ein?

1. **Claude-Projekt erstellen**: Gehe auf claude.ai → Projects → «Create Project»
2. **System Prompt einfügen**: Öffne `SYSTEM_PROMPT.md`, kopiere den gesamten Inhalt und füge ihn unter «Project Instructions» ein
3. **Knowledge hochladen**: Lade alle Dateien aus dem Ordner `knowledge/` hoch (Drag & Drop)
4. **Workflows lesen**: Öffne `WORKFLOWS.md` für die verfügbaren Befehle

## Wie benutze ich es?

1. **Dossier anonymisieren**: `milanon anonymize <dossier-ordner> --output <output> --recursive`
2. **Dossier hochladen**: Lade die anonymisierten Dateien als Konversations-Anhang hoch
3. **Workflow starten**: Schreibe z.B. «Analysiere mein Bat Dossier» (siehe WORKFLOWS.md)
4. **Iterieren**: Claude führt dich Schritt für Schritt durch den 5+2
5. **Ergebnis de-anonymisieren**: `milanon unpack --clipboard --output <output>`
6. **DOCX exportieren**: `milanon export <befehl.md> --docx --deanonymize`

## Was muss ICH als Kdt entscheiden?

Überall wo Claude `<!-- KDT ENTSCHEID: ... -->` markiert, musst DU entscheiden.
Claude kann vorschlagen, aber die folgenden Entscheide sind immer Kommandantensache:

- **Absicht** — «Ich will...» ist DEIN Entschluss
- **Schwergewichtsbildung** — Wo setzt du den Schwerpunkt?
- **Reserveeinsatz** — Wann und wie wird die Reserve eingesetzt?
- **Risikotragbarkeit** — Welche Risiken akzeptierst du?
- **Aufträge an Unterstellte** — Wer macht was?

Claude liefert die Analyse. Du triffst den Entschluss.
"""

_WORKFLOWS_MD = """\
# Verfügbare Workflows

## Dossier-Analyse
**Befehl:** «Analysiere mein Bat Dossier»

Claude liest dein hochgeladenes Bat Dossier und extrahiert:
- Alle Aufträge und Auflagen für deine Einheit
- Zeitplan (extern und intern)
- Widersprüche und offene Fragen
- Erste Problemerfassungs-Matrix

Dies ist Schritt 1 des 5+2: Problemerfassung.

---

## Beurteilung der Lage (BdL)
**Befehl:** «Führe mich durch die BdL»

Claude führt dich durch die vernetzte Faktorenanalyse:
- AUGEZ-Faktoren (Auftrag, Umwelt, Gegner, Eigene, Zeit)
- AEK-Methode (Aussage → Erkenntnis → Konsequenz)
- Schlüsselbereiche ROT und BLAU
- Konsequenzen für eigene Möglichkeiten

Dies ist Schritt 2 des 5+2: Beurteilung der Lage.

---

## Einsatzbefehl
**Befehl:** «Erstelle den Einsatzbefehl»

Claude erstellt einen vollständigen 5-Punkte-Befehl:
- Orientierung (Lage, Bedrohung, eigene Lage)
- Absicht (basierend auf deinem Entschluss)
- Aufträge (Element × Auftrag Tabelle)
- Durchführung (Phasenplan, Feuerplan)
- Logistik und Führungsunterstützung

Dies ist Schritt 5 des 5+2: Befehlsgebung.

---

## Wachtdienstbefehl
**Befehl:** «Erstelle den Wachtdienstbefehl»

Claude erstellt einen Wachtdienstbefehl nach WAT 51.301:
- Wachtpflichten und Befugnisse
- Postenorganisation und Ablösung
- ROE/ROB
- Alarmorganisation

Dies ist ein spezialisierter 5+2-Zyklus mit Fokus Sicherung.
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
      SYSTEM_PROMPT.md     — Layers 1+2+5 combined
      knowledge/           — Doctrine extracts merged by topic
      INSTRUCTIONS.md      — How to use (German)
      WORKFLOWS.md         — Available commands
    """

    def __init__(self, data_dir: Path):
        self._data_dir = data_dir
        self._doctrine_dir = data_dir / "doctrine"
        self._templates_dir = data_dir / "templates"

    def execute(self, unit: str, output_dir: Path) -> GenerateProjectResult:
        """Generate the project folder.

        Args:
            unit: The unit designation, e.g. "Inf Kp 56/1".
            output_dir: Where to create the project folder.

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

        # 4. INSTRUCTIONS.md
        (output_dir / "INSTRUCTIONS.md").write_text(_INSTRUCTIONS_MD, encoding="utf-8")
        files_created.append("INSTRUCTIONS.md")

        # 5. WORKFLOWS.md
        (output_dir / "WORKFLOWS.md").write_text(_WORKFLOWS_MD, encoding="utf-8")
        files_created.append("WORKFLOWS.md")

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
