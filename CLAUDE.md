# CLAUDE.md — MilAnon Project Context

> This file provides context for Claude Code sessions.
> Last updated: 2026-03-25 (v0.5.0 — Code complete: Doctrine KB, 5+2 Workflows, DOCX Export, Claude Project Generator)

## What is this project?

MilAnon is a local-only Python CLI tool (+ Streamlit GUI) for Swiss Army company commanders to anonymize sensitive documents before using public LLMs, and de-anonymize the LLM outputs afterward. All PII stays on the local machine — nothing sensitive is ever transmitted.

The primary flow is: **anonymize → project generate → Claude.ai → export --docx**

## Tech Stack

- **Language:** Python 3.11+
- **Packaging:** pyproject.toml + pip
- **CLI:** click 8.x + rich 13.x (terminal output)
- **GUI:** Streamlit 1.35+
- **Database:** SQLite (persistent entity mapping, `~/.milanon/milanon.db`)
- **OCR:** Tesseract via pytesseract (for scanned PDFs)
- **PDF:** pdfplumber (text extraction) + pdf2image (rasterization for OCR)
- **DOCX:** python-docx
- **XLSX:** openpyxl
- **EML:** email (stdlib)
- **Testing:** pytest (648+ tests)
- **Linting:** ruff

## Architecture

**Clean Architecture** with 4 layers. Dependencies point inward only.

```
Layer 1 (Domain):    entities, protocols, mapping_service, recognition, anonymizer, deanonymizer
Layer 2 (Use Cases): anonymize, deanonymize, import_entities, validate_output, init_reference_data,
                     generate_context, workflow_pack, generate_project, export_docx
Layer 3 (Adapters):  parsers/, recognizers/, writers/, repositories/, cli/
Layer 4 (Infra):     SQLite, Tesseract, File System, Streamlit
```

### Key protocols (interfaces)
- `DocumentParser` — `parse(path) -> ExtractedDocument`
- `EntityRecognizer` — `recognize(document) -> list[DetectedEntity]`
- `MappingRepository` — `get_mapping()`, `create_mapping()`, `get_placeholder()`

### Recognition pipeline (priority order)
1. **PatternRecognizer** — regex for AHV, phone, email, address (highest priority)
2. **MilitaryRecognizer** — rank+name compounds, unit designations
3. **ListRecognizer** — known entities from DB + municipalities from ref table (lowest priority)

Overlapping detections: higher priority wins. Longer match wins at same priority.

### Placeholder format
`[ENTITY_TYPE_NNN]` — e.g. `[PERSON_001]`, `[ORT_003]`
Regex: `\[([A-Z_]+)_(\d{3})\]`

### Incremental processing
- Files tracked via SHA-256 content hash in `file_tracking` table
- Unchanged files are skipped automatically on re-runs
- `--force` flag reprocesses everything
- `--dry-run` flag shows what would be processed without doing it

### CSV/XLSX handling (Paket K)
- `.csv` and `.xlsx` files are **excluded by default** from `milanon anonymize`
- Use `--include-spreadsheets` to explicitly include them
- `.csv` files are also excluded from `milanon pack` prompt assembly (token efficiency)

### Cross-source entity consistency (US-5.4, D4)
- `MappingService.get_or_create_placeholder()` normalizes via `value.strip().lower()`
- "Basel", "BASEL", "basel" all map to the same `[ORT_NNN]` placeholder
- Entities from PISA import, municipality DB, and document processing are consistent

### Reference data (Single Source of Truth)
- **`data/military_units.csv`** is the ONLY place to edit military reference data
- Contains row types: `rank`, `branch`, `unit_pattern`, `function`, `concrete_unit`
- `concrete_unit` rows have `parent` and `level` columns for hierarchical context
- `config/military_patterns.py` loads abbreviation lists from CSV at import time
- `InitReferenceDataUseCase` loads CSV into SQLite (including hierarchy)
- `GenerateContextUseCase` uses DB hierarchy for full ancestor/sibling resolution
- Schema migration: new columns (`full_name`, `level`, `category`) added automatically
- Auto-triggered on first anonymize/deanonymize run if DB is empty
- `milanon db init` for manual initialization; `--force` to reload
- Idempotent: second call skips if tables already populated

## Project Structure

```
src/milanon/
├── domain/           # Core business logic (no external deps)
│   ├── entities.py   # EntityType, DetectedEntity, EntityMapping, ExtractedDocument, AnonymizedDocument
│   ├── protocols.py  # DocumentParser, EntityRecognizer, MappingRepository
│   ├── mapping_service.py
│   ├── recognition.py
│   ├── anonymizer.py  # also exports LEGEND_PATTERN (used by writers + deanonymizer)
│   └── deanonymizer.py
├── adapters/
│   ├── parsers/      # eml, docx, pdf, xlsx_csv + __init__.py (registry)
│   ├── recognizers/  # pattern, list, military
│   ├── writers/      # markdown, docx, csv, eml
│   └── repositories/ # sqlite_repository
├── usecases/         # anonymize, deanonymize, import_entities, validate_output,
│                     # init_reference_data, generate_context, workflow_pack,
│                     # generate_project, export_docx
├── cli/
│   ├── main.py       # All click commands + Rich output
│   └── output.py     # Rich helpers (console, print_header, print_result_table, etc.)
├── gui/              # Streamlit app (app.py) — 5 pages
├── utils/            # Shared helpers: csv_helpers.py (detect_delimiter)
└── config/           # settings, military_patterns
data/
├── swiss_municipalities.csv  # ~4000 Swiss municipalities
├── military_units.csv        # SINGLE SOURCE OF TRUTH: ranks, branches, unit patterns,
│                             # functions, AND concrete units with parent-child hierarchy
│                             # (Aufbauorganisation der Schweizer Armee)
├── swiss_military_ranks.md   # DEPRECATED — redirects to military_units.csv
├── doctrine/                 # Swiss Army regulations as Markdown
│   ├── INDEX.yaml            # Workflow → chapter → mode mapping (machine-readable)
│   ├── INDEX.md              # Human-readable overview of all doctrine files
│   ├── *.md                  # 11 regulation files (~3 MB total, BFE/TF/FSO/WAT etc.)
│   ├── paradigmenwechsel_berrm.md  # Bereitschaftsraum paradigm reference
│   ├── extracts/             # 14 chapter-level extracts for token-efficient prompting (E14.3)
│   │   ├── bfe_initialisierung.md, bfe_problemerfassung.md, bfe_sofortmassnahmen.md
│   │   ├── bfe_zeitplanung.md, bfe_bdl.md, bfe_entschlussfassung.md
│   │   ├── bfe_planentwicklung.md, bfe_befehlsgebung.md
│   │   ├── tf_einsatzgrundsaetze.md, tf_taktische_grundsaetze.md
│   │   ├── tf_raumordnung.md, tf_taktische_aufgaben.md
│   │   ├── fso_aktionsplanung.md, wat_wachtdienstbefehl.md
│   └── skeletons/            # Document templates with ADF/Berrm mode markers
│       ├── 5_punkte_befehl_universal.md  # THE primary skeleton
│       ├── 000_allgemeiner_befehl.md
│       └── 300_wachtdienstbefehl.md
└── templates/
    ├── role.md               # Layer 1: LLM role definition (static, Swiss Army expert)
    ├── rules.md              # Layer 5: Output rules (placeholder preservation, KDT ENTSCHEID)
    ├── CHEAT_SHEET.md        # Quick reference for Kdt (print out)
    ├── workflows/            # Layer 4 templates
    │   ├── analyse.md        # Schritt 1: 4-Farben + Problemerfassung + SOMA + Zeitplan
    │   ├── ei-bf.md          # Schritt 5: Universal 5-Punkte-Befehl
    │   ├── wachtdienst.md    # Wachtdienstbefehl (WAT-konform, Berrm: taktische Sicherung)
    │   └── dossier-check.md  # Pre-flight Dossier Quality Check (FR-001, not yet in INDEX.yaml)
    └── docx/                 # DOCX base templates
        ├── befehl_vorlage.docx        # CH Armee Befehl template
        └── befehl_vorlage_uebung.docx # CH Armee Übungsbefehl template
```

## Entity Types

PERSON, VORNAME, NACHNAME, EMAIL, TELEFON, AHV_NR, GEBURTSDATUM, ORT, ADRESSE, ARBEITGEBER, EINHEIT, FUNKTION, GRAD_FUNKTION, MEDIZINISCH, FAMILIAER, STANDORT_MIL

## Military Domain Context

- Documents in German (Swiss High German, no ß, always ss)
- Ranks precede names: "Hptm Marco BERNASCONI"
- Multi-word ranks: "Oberstlt i Gst" is ONE rank
- Units: "Inf Bat 56", "Inf Kp 56/1", "Ter Div 2"
- AHV: `756.XXXX.XXXX.XX`
- Phone formats: `079 535 80 46`, `+41 79 535 80 46`, `0795358046`

## Workflow System

MilAnon v0.5.0 adds a **5-Layer System Prompt architecture** that assembles context-aware prompts for each step of the Swiss Army 5+2 Aktionsplanungsprozess.

### 5-Layer Architecture (ADR-012)

| Layer | File | Language | Content |
|---|---|---|---|
| Layer 1 | `data/templates/role.md` | English | LLM role definition — Swiss Army Kp Kdt expert |
| Layer 2 | Generated at runtime | German | Context: unit, Vault files, placeholder map |
| Layer 3 | `data/doctrine/extracts/<chapter>.md` | German | Relevant doctrine chapters (token-efficient) |
| Layer 4 | `data/templates/workflows/<workflow>.md` | German | Task definition + skeleton for this step |
| Layer 5 | `data/templates/rules.md` | English | Output rules: placeholder preservation, KDT ENTSCHEID |

### `milanon pack` Workflow Flags

```bash
milanon pack <input_path> --workflow <name> [--mode berrm|adf] [--unit "Inf Kp 56/1"]
             [--context <path>] [--step 1-5] [--output <path>] [--no-clipboard]
```

| Flag | Description |
|---|---|
| `--workflow <name>` | Reads INDEX.yaml, loads doctrine + skeleton for this workflow |
| `--mode berrm\|adf` | Selects mode markers in skeleton (Bereitschaftsraum vs. ADF) |
| `--unit "..."` | Overrides the unit name in Layer 2 context |
| `--context <path>` | Includes Vault files from previous steps as Layer 2 input |
| `--step 1-5` | Selects which 5+2 step to execute (adds skeleton when step=5) |
| `--output <path>` | Write assembled prompt to file (in addition to clipboard) |
| `--no-clipboard` | Skip clipboard copy |

### Available Workflows

| Workflow | Maps to 5+2 | Status |
|---|---|---|
| `analyse` | Schritt 1: Problemerfassung | ✅ Done |
| `ei-bf` | Schritt 5: Befehlsgebung | ✅ Done |
| `wachtdienst` | Vollständiger Zyklus Wachtdienst | ✅ Done |
| `dossier-check` | Schritt 0: Pre-flight Validation | Template only — not in INDEX.yaml |

### INDEX.yaml Structure

`data/doctrine/INDEX.yaml` maps each workflow to its doctrine chapters, skeleton, and output format:

```yaml
workflows:
  analyse:
    name: "Bat Dossier Analyse"
    system_prompt: templates/workflows/analyse.md
    doctrine:
      - source: 52_080_bfe_einsatz.md
        extract: extracts/bfe_initialisierung.md
      - source: 52_080_bfe_einsatz.md
        extract: extracts/bfe_problemerfassung.md
    skeleton: null
    output_format: [markdown]
    maps_to_5+2: "Schritt 1: Problemerfassung"
```

### Mode Markers (ADF vs. Berrm)

Templates contain HTML-style markers that are stripped at prompt assembly time:
- `<!-- ADF: content -->` — shown in ADF mode, stripped in Berrm
- `<!-- BERRM: content -->` — shown in Berrm mode, stripped in ADF
- `<!-- BOTH: content -->` — always shown
- `<!-- FILL: placeholder -->` — always shown (user fills in)
- `<!-- KDT ENTSCHEID: ... -->` — always shown (mandatory commander decision)

## Doctrine Knowledge Base

11 Swiss Army regulation files in `data/doctrine/`:

| File | Content |
|---|---|
| `52_080_bfe_einsatz.md` | BFE 52.080 — Befehlsgebung Einsatz (5+2 Hauptreferenz) |
| `50_030_tf_taktik.md` | TF 50.030 — Taktik Grundlagen |
| `50_305_fso_sicherungsoperationen.md` | FSO 50.305 — Sicherungsoperationen |
| `51_301_wat_wachtdienst.md` | WAT 51.301 — Wachtdienst |
| `paradigmenwechsel_berrm.md` | Bereitschaftsraum-Paradigma (internes Dokument) |
| + 6 weitere | BABS, BLAS, KBT, etc. |

14 extracts in `data/doctrine/extracts/` — 5-30 KB each, pre-cut to relevant sections.

## DOCX Export

MilAnon generates local DOCX files from anonymized Markdown output — de-anonymization happens locally, never in the cloud (ADR-011).

### Command

```bash
milanon export <file> --docx [--deanonymize] [--template <path>] [--output <path>]
```

### Pipeline

```
Markdown (anonymized) → python-docx → DOCX (anonymized) → de-anonymize → DOCX (cleartext)
```

### Style Mapping (Markdown → DOCX)

Uses `befehl_vorlage.docx` as base template (official CH Armee styles).

| Markdown | DOCX Style |
|---|---|
| `# Heading` | `Heading 1` |
| `## Subject` | `Subject heading` |
| `### 1 Main` | `1. Main title` |
| `#### 1.1 Sub` | `1.1 Title` |
| `##### 1.1.1 Sub` | `1.1.1 Title` |
| `- item` | `Bullet List 1` |
| `1. item` | `Numbered List 2` |
| `**bold**` / `*italic*` | Bold/Italic Runs |
| `> blockquote` | `Text Indent` (italic) |
| `| table |` | DOCX Table (any column count) |
| `---` | Page break |
| `<!-- comment -->` | Stripped |
| Other text | `Text Indent` |

## Claude Project Generator

Generates a ready-to-import Claude.ai Project folder from the anonymized Bat Dossier.

### Command

```bash
milanon project generate --unit "Inf Kp 56/1" --input test_output/anon/ \
    [--include-images] --output test_output/claude_project/
```

### Output Structure

```
claude_project/
├── README.md              — 4-step setup guide (German)
├── SYSTEM_PROMPT.md       — Paste into Claude.ai "Project Instructions"
├── CHEAT_SHEET.md         — Quick reference (print out)
└── knowledge/
    ├── *.md               — Anonymized Bat Dossier files (from --input)
    ├── *.png              — Visual pages / WAP (from --include-images)
    ├── bfe_aktionsplanung.md
    ├── tf_taktik.md
    ├── fso_aktionsplanung.md
    ├── wat_wachtdienst.md
    └── skeletons.md
```

## Development Standards

- Clean Code (meaningful names, small functions, SRP, DRY)
- SOLID principles
- Tests: Arrange-Act-Assert, naming: `test_<what>_<when>_<then>`
- Commits: Conventional Commits (feat:, fix:, refactor:, test:)
- All code, docs, tests, comments in English
- Conversation language: German (Swiss, no ß)

## CLI Commands

```bash
# Initialize reference data (first run or after reset)
milanon db init [--force]

# Anonymize (incremental by default — .csv/.xlsx excluded unless --include-spreadsheets)
milanon anonymize <input> --output <o> [--level dsg|full] [--recursive] [--force]
                  [--dry-run] [--embed-images] [--include-spreadsheets]

# De-anonymize (incremental by default)
milanon deanonymize <input> --output <o> [--force] [--dry-run]

# Validate LLM output placeholders
milanon validate <file>

# Generate LLM context file (unit hierarchy + placeholder map)
milanon context [--unit "Inf Kp 56/1"] [--output CONTEXT.md]

# Assemble 5-layer prompt for a workflow step
milanon pack <input_path> --workflow analyse|ei-bf|wachtdienst|dossier-check
             [--mode berrm|adf] [--level dsg|full] [--unit "Inf Kp 56/1"]
             [--context <path>] [--step 1-5] [--output <path>] [--no-clipboard]

# Doctrine management
milanon doctrine list
milanon doctrine extract [--all] [--workflow <name>]

# Export Markdown to DOCX (with optional in-place de-anonymization)
milanon export <file> --docx [--deanonymize] [--template <path>] [--output <path>]

# Generate Claude.ai Project folder
milanon project generate --unit "Inf Kp 56/1" [--input <anon_path>]
                         --output <output_path> [--include-images]

# Project configuration
milanon config set <key> <value>
milanon config get <key>

# Database management
milanon db import <csv_path> [--format pisa|names]
milanon db list [--type PERSON] [--limit N]
milanon db reset [--include-ref-data] [--yes]
milanon db stats

# Streamlit GUI (opens browser at http://localhost:8501)
milanon gui [--port 8501]
```

## Current Phase

v0.6.3 — GUI Alignment Sprint complete. All CLI features available in GUI.

**Phase 1 (Core Engine) — DONE** (v0.3.0): Anonymization, de-anonymization, GUI, round-trip.
**Phase 2 (Doctrine + 5+2 Workflows) — DONE** (v0.5.0-v0.6.2): E14, E15 (5 workflows + 6 BFE skeletons), E16 complete.
**Phase 3 (DOCX Pipeline) — DONE** (v0.6.1): FR-004 Writer Rewrite with official CH Armee styles.
**Phase 4 (Quality) — ~90% DONE**: FR-017, CI/CD, FR-001, FR-004, BUG-018, GUI Alignment all done. Open: BUG-012/013.

See docs/BACKLOG.md for known bugs and feature requests.
See docs/ROADMAP.md for full epic planning.
See docs/CHANGELOG.md for version history.

## Known Issues

See `docs/BACKLOG.md` for the complete bug and feature request list.

| ID | Description | Severity | Status |
|---|---|---|---|
| BUG-012 | PII: single names without rank not detected | 🟡 | Open (FR-013) |
| BUG-013 | PII: street names without suffix missed | 🟡 | Open (FR-012) |

### Key directories

```
src/milanon/config/     — military_patterns.py (regex patterns, PII + military)
src/milanon/utils/      — csv_helpers.py (shared CSV utilities)
src/milanon/cli/output.py — Rich terminal output helpers
data/                   — military_units.csv (single source of truth for military ref data)
                          swiss_municipalities.csv (4059 municipalities)
```
