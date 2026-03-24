# MilAnon — Swiss Military Document Anonymizer

Local-only CLI + GUI tool for Swiss Army company commanders to anonymize sensitive documents before using public LLMs, and de-anonymize the LLM outputs afterward. **No data ever leaves your machine.**

---

## Features

- Detects and replaces: AHV numbers, phone numbers, email addresses, names, ranks, units, addresses, dates of birth
- Bundled reference data: 3958 Swiss municipalities + complete rank/unit taxonomy
- Incremental processing — unchanged files are skipped automatically (SHA-256 hashing)
- Full round-trip: anonymize → send to LLM → de-anonymize → restore originals
- Supports: CSV, XLSX, DOCX, PDF (with OCR fallback), EML
- Cross-source consistency: "Basel" from PISA import, municipality DB, and documents = same placeholder
- Persistent mapping database (`~/.milanon/milanon.db`) — consistent placeholders across runs
- PDF table extraction as Markdown pipe-syntax tables
- Visual PDF page detection (WAP/Picasso schedules) — warns instead of producing garbled output
- Generic name CSV import (`Grad;Vorname;Nachname`) + combined `Name / Vorname` column auto-detection
- Quick-add single person via GUI
- LLM Context Generator (`milanon context`) — produces `CONTEXT.md` with unit hierarchy and filtering instructions
- GUI with LLM Workflow page (Pack → Work → Unpack)
- Optional PNG embedding for visual PDF pages (`--embed-images`)
- Word-boundary-safe entity matching (Unicode-aware, prevents substring false positives)
- Streamlit GUI for non-CLI users (`milanon gui`)
- **5+2 Workflow System** — doctrine-aware prompt assembly for Swiss Army Aktionsplanungsprozess
- **DOCX Export** — local Markdown→DOCX generation with de-anonymization (`milanon export --docx --deanonymize`)

---

## Prerequisites

| Requirement | Install |
|---|---|
| Python 3.11+ | [python.org](https://www.python.org/downloads/) |
| Tesseract OCR (for scanned PDFs) | `brew install tesseract tesseract-lang` |
| Poppler (for PDF rendering) | `brew install poppler` |

---

## Installation

```bash
# Clone the repository
git clone https://github.com/V4R9/MilAnon.git
cd Anonymizer_Tool_Army

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install (includes all dependencies including Streamlit)
pip install -e ".[dev]"

# Verify
milanon --version
```

---

## Quick Start

```bash
# 1. Initialize reference data (Swiss municipalities + military units)
milanon db init

# 2. Import personnel from MilOffice/PISA 410 export
milanon db import personalbestand.csv

# 3. Anonymize documents
milanon anonymize ./dossier/ --output ./anon/

# 4. (Send ./anon/ to your LLM — Claude, ChatGPT, etc.)

# 5. De-anonymize LLM output
milanon deanonymize ./llm_output/ --output ./restored/
```

---

## Usage

### Initialize reference data (first run)

```bash
milanon db init           # Load municipalities + military units
milanon db init --force   # Force reload (replaces existing data)
```

### Anonymize documents

```bash
# Single file
milanon anonymize report.docx --output ./anonymized/

# Folder (non-recursive)
milanon anonymize ./input/ --output ./anonymized/

# Recursive — include subfolders
milanon anonymize ./input/ --output ./anonymized/ --recursive

# Force reprocess all (ignore cache)
milanon anonymize ./input/ --output ./anonymized/ --force

# Dry run — show what would be processed without writing
milanon anonymize ./input/ --output ./anonymized/ --dry-run

# Embed visual PDF pages (WAP/schedules) as PNG — NOT anonymized
milanon anonymize ./input/ --output ./anonymized/ --embed-images
```

Output:
```
Scanned:   3
New:       2
Changed:   1
Skipped:   0
Errors:    0
Entities:  47
```

### De-anonymize LLM output

```bash
milanon deanonymize ./llm_output/ --output ./restored/
milanon deanonymize ./llm_output/ --output ./restored/ --force
milanon deanonymize ./llm_output/ --output ./restored/ --dry-run
```

### Validate placeholder integrity

```bash
milanon validate llm_output.md
```

Output:
```
File:         llm_output.md
Placeholders: 12
Resolved:     12
Unresolved:   0
OK
```

### Import external personnel (Bat Stab, Div Stab)

```bash
milanon db import bat_stab.csv --format names
```

### Generate LLM context

```bash
# For a specific unit
milanon context --unit "Inf Kp 56/1" --output CONTEXT.md

# Interactive unit selection (lists all known units)
milanon context --output CONTEXT.md
```

Generates a `CONTEXT.md` with the organizational hierarchy, filtering instructions, and all `[EINHEIT_NNN]` placeholders — paste it before your anonymized document when prompting an LLM.

### Database management

```bash
# Initialize reference data
milanon db init

# Import personnel from PISA 410 / MilOffice CSV
milanon db import personnel_export.csv

# Import from simple name list (Grad;Vorname;Nachname or combined Name/Vorname column)
milanon db import bat_stab.csv --format names

# List entities (optionally filtered)
milanon db list
milanon db list --type PERSON
milanon db list --type AHV_NR --limit 20

# Statistics
milanon db stats

# Reset mappings (keep reference data)
milanon db reset

# Full reset (includes municipalities, military units — re-run db init afterward)
milanon db reset --include-ref-data
```

Entity types: `PERSON`, `VORNAME`, `NACHNAME`, `EMAIL`, `TELEFON`, `AHV_NR`, `GEBURTSDATUM`, `ORT`, `ADRESSE`, `ARBEITGEBER`, `EINHEIT`, `FUNKTION`, `GRAD_FUNKTION`

### Streamlit GUI

```bash
milanon gui              # Opens http://localhost:8501
milanon gui --port 8502  # Custom port
```

The GUI offers 5 pages:
- **Anonymize** — folder pickers, options, progress bar, entity count summary; warns on visual PDF pages
- **De-Anonymize** — restore LLM output files; paste text area for direct LLM output
- **LLM Workflow** — 3-tab workflow: Pack for LLM, Work with LLM, Unpack Response; includes Context Generator with unit dropdown and preview
- **DB Import** — upload PISA 410 or simple name list CSV; format selector; Quick-Add single person form
- **DB Stats** — entity counts per type with bar chart; Reset Mappings / Reset Everything buttons; Initialize Reference Data button

> **Tip:** When entering paths in the GUI, quotes are stripped automatically. You can paste paths from Finder (with or without quotes).

---

## 5+2 Workflow System

MilAnon v0.5.0 adds doctrine-aware prompt assembly for the Swiss Army 5+2 Aktionsplanungsprozess (BFE 52.080 Kap 5).

```bash
# Assemble a prompt for Step 1 (Analyse) in Bereitschaftsraum mode
milanon pack --workflow analyse --mode berrm --context ./vault/ --step 1

# Assemble a prompt for Einsatzbefehl (Step 5), including prior products as context
milanon pack --workflow ei-bf --mode adf --context ./vault/ --step 5

# List available doctrine files
milanon doctrine list

# Extract chapter-level doctrine snippets for token-efficient prompting
milanon doctrine extract --all
```

The assembled prompt contains 5 layers: role definition, unit context + placeholders, relevant doctrine chapters, task template, and output rules. Paste the result into Claude.ai (or any LLM), then de-anonymize the response locally.

### DOCX Export

```bash
# Convert de-anonymized LLM output to CH Armee DOCX format
milanon export vault/befehl.md --docx --deanonymize
```

Produces a ready-to-distribute DOCX using the official CH Armee Befehl template. De-anonymization happens locally — no cleartext ever leaves your machine.

---

## Typical Workflow

```
1. Initialize (once):         milanon db init
2. Import personnel (once):   milanon db import personalbestand.csv
3. Anonymize:                 milanon anonymize ./vertraulich/ --output ./anon/
4. Work with LLM (Claude, ChatGPT, etc.) — use content from ./anon/
5. Validate LLM output:       milanon validate llm_response.md
6. De-anonymize:              milanon deanonymize ./llm_output/ --output ./restored/
```

---

## CLI Reference

| Command | Description |
|---|---|
| `milanon anonymize` | Anonymize documents |
| `milanon deanonymize` | De-anonymize LLM outputs |
| `milanon context` | Generate LLM context file |
| `milanon validate` | Check placeholder integrity |
| `milanon pack` | Assemble 5-layer workflow prompt (`--workflow`, `--mode`, `--context`, `--step`) |
| `milanon export` | Export Markdown to DOCX (`--docx`, `--deanonymize`) |
| `milanon doctrine list` | List available doctrine files |
| `milanon doctrine extract` | Extract doctrine chapters for prompting |
| `milanon config set/get` | Read/write project configuration |
| `milanon db init` | Initialize reference data |
| `milanon db import` | Import from CSV (PISA or name list) |
| `milanon db reset` | Reset mapping database |
| `milanon db list` | List known entities |
| `milanon db stats` | Show database statistics |
| `milanon gui` | Launch Streamlit web interface |

---

## Placeholder Format

| Original | Placeholder |
|---|---|
| `756.1234.5678.97` | `[AHV_NR_001]` |
| `Marco BERNASCONI` | `[PERSON_001]` |
| `Inf Kp 56/1` | `[EINHEIT_001]` |
| `marco.bernasconi@mil.ch` | `[EMAIL_001]` |
| `Hptm` | `[GRAD_FUNKTION_001]` |
| `Basel` | `[ORT_001]` |

The same entity always gets the same placeholder — consistent across files, runs, and sources.

---

## Reference Data

| File | Description |
|---|---|
| `data/swiss_municipalities.csv` | 4059 Swiss municipalities with PLZ and canton |
| `data/military_units.csv` | Ranks, branches, functions, unit patterns (single source of truth) |
| `data/doctrine/INDEX.yaml` | Workflow → doctrine chapter → mode mapping |
| `data/doctrine/*.md` | 11 Swiss Army regulations as Markdown (~3 MB) |
| `data/doctrine/extracts/` | Token-efficient chapter extracts for prompt assembly |
| `data/doctrine/skeletons/` | Document structure templates (5-Punkte-Befehl universal) |
| `data/templates/role.md` | Layer 1: LLM role definition |
| `data/templates/rules.md` | Layer 5: Output rules |
| `data/templates/workflows/` | Layer 4: Per-workflow task templates |
| `data/templates/docx/befehl_vorlage.docx` | CH Armee Befehl base template |

---

## Development

```bash
# Run all tests
pytest tests/ -v         # 520+ tests

# Specific test modules
pytest tests/domain/ -v
pytest tests/e2e/ -v

# Lint
ruff check src/ tests/

# Coverage
pytest tests/ --cov=src/milanon --cov-report=term-missing
```

---

## Documentation

| Document | Description |
|---|---|
| [Project Summary](docs/PROJECT_SUMMARY.md) | Goals, scope, non-goals |
| [Product Requirements](docs/PRD.md) | Full requirements specification (v1.1) |
| [Architecture Overview](docs/architecture/ARCHITECTURE.md) | Clean Architecture, ADRs, diagrams |
| [Implementation Plan](docs/IMPLEMENTATION_PLAN.md) | Step-by-step build plan |
| [PISA 410 Column Mapping](docs/PISA_410_COLUMN_MAPPING.md) | MilOffice CSV import spec |
| [Changelog](CHANGELOG.md) | Release history |

---

## Security & Privacy

- **No network access** — all processing is local
- **No telemetry** — nothing is logged or transmitted externally
- Database stored at `~/.milanon/milanon.db` (override via `MILANON_DB_PATH` env var)
- Streamlit GUI runs on `localhost` only
- To wipe all mappings: `milanon db reset` (or `rm ~/.milanon/milanon.db` then `milanon db init`)

---

## License

Internal use only — Swiss Army.
