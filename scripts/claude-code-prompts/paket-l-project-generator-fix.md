# MEGA-PROMPT: Paket L — Project Generator Bugfixes
# MODEL: Sonnet

## Context
Read CLAUDE.md. Read `src/milanon/usecases/generate_project.py` and `src/milanon/cli/main.py` (the `project generate` command).

## Branch
```bash
git checkout -b fix/project-generator
```

## The Problem
`milanon project generate` produces a Claude Project folder but:

1. **The anonymized Bat Dossier is NOT included** — the most important file is missing! The user has to manually copy it. That's a bug.
2. **INSTRUCTIONS.md and SYSTEM_PROMPT.md are confusing** — in Claude.ai there's only ONE field ("Project Instructions"). Having two files makes the user wonder which to use where.
3. **The CHEAT_SHEET is not included** — there's a `data/templates/CHEAT_SHEET.md` that should be in the output.
4. **PNGs (WAP pages) are not included** — visual pages from the Bat Dossier should optionally be included as Knowledge files.

## The Fix

### 1. Add `--input` flag to `project generate`

The command should accept the anonymized input folder:

```bash
milanon project generate --unit "Inf Kp 56/1" --input test_output/anon/ --output test_output/claude_project/
```

In `src/milanon/cli/main.py`, update the `project generate` command to accept `--input`:

```python
@project.command("generate")
@click.option("--unit", required=True, help='Unit designation, e.g. "Inf Kp 56/1"')
@click.option("--input", "input_path", default=None, type=click.Path(exists=True), help="Path to anonymized documents (from milanon anonymize)")
@click.option("--output", "-o", required=True, type=click.Path(), help="Output directory for the Claude Project")
@click.option("--include-images", is_flag=True, help="Include PNG images (WAP, maps) as Knowledge files")
def generate(unit, input_path, output, include_images):
```

### 2. Copy anonymized documents into knowledge/

In `src/milanon/usecases/generate_project.py`, add logic to copy anonymized files:

```python
# Copy anonymized documents into knowledge/
if input_path:
    for f in sorted(input_path.glob("*.md")):
        shutil.copy2(f, knowledge_dir / f.name)
    if include_images:
        for f in sorted(input_path.glob("*.png")):
            shutil.copy2(f, knowledge_dir / f.name)
```

### 3. Merge INSTRUCTIONS.md into a single README

Replace the confusing two-file setup with:

- **README.md** — Anleitung für den Kdt (was ist das, wie einrichten) — in German
- **SYSTEM_PROMPT.md** — Das was in Claude.ai "Project Instructions" eingefügt wird
- **CHEAT_SHEET.md** — Ausdrucken, neben Laptop legen

The README should clearly say:
```markdown
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
- bat_dossier_anon.md — Dein anonymisiertes Bat Dossier
- bfe_aktionsplanung.md — Doktrin: BFE Kap 5
- tf_taktik.md — Doktrin: TF Kap 5
- fso_aktionsplanung.md — Doktrin: FSO Kap 4.2
- wat_wachtdienst.md — Doktrin: WAT
- skeletons.md — Befehlsvorlagen
- (optional) *.png — Visuelle Seiten (WAP, Karten)

## Schritt 4: Los gehts
Öffne `CHEAT_SHEET.md` (oder drucke es aus).
Starte einen neuen Chat und sage: "Analysiere mein Bat Dossier"

## Nach Abschluss
Wenn du den fertigen Befehl hast, kopiere Claude's Output und führe auf deinem Mac aus:
\```
milanon unpack --clipboard --output vault/Dossier/ --split
milanon export vault/Dossier/ei_bf.md --docx --deanonymize
\```
```

### 4. Copy CHEAT_SHEET.md into output

```python
# Copy cheat sheet
cheat_sheet_src = data_dir / "templates" / "CHEAT_SHEET.md"
if cheat_sheet_src.exists():
    shutil.copy2(cheat_sheet_src, output_dir / "CHEAT_SHEET.md")
```

### 5. Expected output structure after fix

```
test_output/claude_project/
├── README.md                              ← Setup-Anleitung (für den Kdt)
├── SYSTEM_PROMPT.md                       ← In Claude.ai "Project Instructions" pasten
├── CHEAT_SHEET.md                         ← Ausdrucken, neben Laptop legen
├── knowledge/
│   ├── WK25_InfBat56_Bf Dossier 56.md    ← Anonymisiertes Bat Dossier ← NEU!
│   ├── WK25_InfBat56_Bf Dossier 56_page_10.png  ← WAP (optional) ← NEU!
│   ├── WK25_InfBat56_Bf Dossier 56_page_12.png  ← NEU!
│   ├── ... (weitere PNGs)
│   ├── bfe_aktionsplanung.md              ← Doktrin
│   ├── tf_taktik.md
│   ├── fso_aktionsplanung.md
│   ├── wat_wachtdienst.md
│   └── skeletons.md
└── (KEINE INSTRUCTIONS.md mehr — ersetzt durch README.md)
```

### 6. Delete old INSTRUCTIONS.md and WORKFLOWS.md generation

Remove the code that generates INSTRUCTIONS.md and WORKFLOWS.md separately. 
The README.md replaces INSTRUCTIONS.md, and the CHEAT_SHEET.md replaces WORKFLOWS.md.

## Tests

Update `tests/usecases/test_generate_project.py`:
- test_generate_copies_anonymized_documents_into_knowledge
- test_generate_copies_pngs_when_include_images_flag
- test_generate_includes_cheat_sheet
- test_generate_creates_readme_not_instructions
- test_generate_without_input_still_works (backward compat)

## Verify

```bash
rm -rf test_output/claude_project/
milanon project generate --unit "Inf Kp 56/1" --input test_output/anon/ --include-images --output test_output/claude_project/
ls -la test_output/claude_project/
ls -la test_output/claude_project/knowledge/
# Should show: README.md, SYSTEM_PROMPT.md, CHEAT_SHEET.md, knowledge/ with dossier + doctrine + PNGs
```

## Commit
```bash
git add -A
git commit -m "fix(e16): project generator includes anonymized dossier, cheat sheet, clear setup

- --input flag copies anonymized .md files into knowledge/
- --include-images flag copies PNG files (WAP, maps) into knowledge/
- README.md replaces confusing INSTRUCTIONS.md (clear 4-step setup guide)
- CHEAT_SHEET.md included from templates
- WORKFLOWS.md removed (replaced by CHEAT_SHEET.md)
- Updated tests for new structure"
```
