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
- Streamlit GUI for non-CLI users (`milanon gui`)

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

The GUI offers 4 pages:
- **Anonymize** — folder pickers, options, progress bar, entity count summary; warns on visual PDF pages
- **De-Anonymize** — restore LLM output files
- **DB Import** — upload PISA 410 or simple name list CSV; format selector; Quick-Add single person form
- **DB Stats** — entity counts per type with bar chart; Reset Mappings / Reset Everything buttons

> **Tip:** When entering paths in the GUI, quotes are stripped automatically. You can paste paths from Finder (with or without quotes).

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

| File | Contents |
|---|---|
| `data/swiss_municipalities.csv` | 3958 Swiss municipalities (BFS open data) |
| `data/military_units.csv` | Ranks, branches, unit patterns, functions (57 entries) |
| `data/swiss_military_ranks.md` | Complete rank reference (human-readable) |

---

## Development

```bash
# Run all tests
pytest tests/ -v         # 438 tests

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
