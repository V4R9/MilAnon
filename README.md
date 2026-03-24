# MilAnon — Secure AI Command Assistant for the Swiss Army

> Local anonymization + doctrine-aware AI workflows + DOCX generation.
> From 70-page battalion dossier to print-ready company order in hours, not weeks.

![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-green)
![Tests: 672 passing](https://img.shields.io/badge/tests-672%20passing-brightgreen)
![Version: 0.5.0](https://img.shields.io/badge/version-0.5.0-orange)

---

## The Problem

Swiss Army company commanders (Miliz) receive a 70-page battalion dossier and must create a complete company command dossier — 16 interconnected documents, all doctrine-compliant — in their spare time. No staff, no templates, no prior experience.

Public LLMs (ChatGPT, Claude) could help, but classified military documents cannot be uploaded to cloud services.

## The Solution

MilAnon solves this with three steps:

1. **Anonymize** — Replace all names, units, locations with `[PLACEHOLDER]` tokens locally
2. **AI-Assisted Creation** — Claude writes doctrine-compliant orders using the 5+2 process
3. **De-anonymize + Export** — Restore real names and generate print-ready DOCX

No classified data ever leaves your machine.

---

## Quick Start

### Installation

```bash
git clone https://github.com/V4R9/MilAnon.git
cd Anonymizer_Tool_Army
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
milanon --version
```

**System dependencies** (macOS):
```bash
brew install tesseract tesseract-lang poppler
```

### Basic Flow

```bash
# 1. Import your personnel data
milanon db init
milanon db import pisa_410.csv

# 2. Anonymize the battalion dossier
milanon anonymize bat_dossier/ --output anon/ --recursive

# 3. Generate a doctrine-aware prompt (copies to clipboard)
milanon pack --workflow analyse --mode berrm --input anon/ --unit "Inf Kp 56/1"

# 4. Paste in Claude.ai → Get your analysis → Copy Claude's response

# 5. De-anonymize and save to your vault
milanon unpack --clipboard --output vault/Planung/ --split

# 6. Export as print-ready DOCX with real names
milanon export vault/befehl.md --docx --deanonymize
```

### For Non-Technical Users: Claude Project

```bash
# Generate a ready-to-use Claude.ai Project
milanon project generate --unit "Inf Kp 56/1" --output ~/claude_project/
# → Upload to Claude.ai → Done. No terminal needed after this.
```

---

## Features

### Core Engine (v0.3.0)

- **Document parsing:** PDF (with OCR fallback), DOCX, EML, XLSX/CSV
- **Entity recognition:** Names, AHV numbers, phone, email, addresses, military units
- **Bidirectional mapping:** Anonymize <-> De-anonymize with consistent placeholders
- **Round-trip workflow:** Edit in Obsidian -> Re-anonymize -> Update via LLM -> De-anonymize
- **Incremental processing:** SHA-256 hashing, only new/changed files are processed
- **Cross-source consistency:** "Basel" from PISA import, municipality DB, and documents = same placeholder

### 5+2 Command Workflows (v0.5.0)

- **Doctrine Knowledge Base:** 11 Swiss Army regulations indexed with chapter-level extraction
- **5-Layer Prompt Assembly:** Role + Context + Doctrine + Task + Rules
- **Mode Support:** Bereitschaftsraum (Berrm) and classical ADF
- **3 Workflows:** Analyse (Problemerfassung), Einsatzbefehl, Wachtdienstbefehl
- **DOCX Export:** Markdown -> Armee-formatted DOCX with de-anonymization
- **Claude Project Generator:** One-click setup for non-technical commanders

---

## Supported Workflows

| Workflow | What it does | 5+2 Step |
|---|---|---|
| `analyse` | 4-color marking + problem decomposition + SOMA + timeline | Step 1 |
| `ei-bf` | Complete 5-point order from all planning products | Step 5 |
| `wachtdienst` | WAT-compliant guard duty order | Full cycle |
| `bdl` | AUGEZ factor analysis with AEK method | Step 2 |
| `entschluss` | Variant generation + evaluation + decision | Step 3 |

---

## Architecture

```
┌──────────────────────────────────────────────────────┐
│  Your Machine (100% local)                           │
│                                                      │
│  PDF/DOCX ──> Anonymize ──> [PLACEHOLDER] text       │
│                                    │                  │
│                                    v                  │
│                          ┌─────────────────┐          │
│                          │  Claude.ai      │  Cloud   │
│                          │  (sees only     │          │
│                          │  placeholders)  │          │
│                          └────────┬────────┘          │
│                                   │                   │
│                                   v                   │
│  Vault <── De-anonymize <── [PLACEHOLDER] response   │
│    │                                                  │
│    v                                                  │
│  DOCX Export (real names, Armee formatting)           │
└──────────────────────────────────────────────────────┘
```

### Clean Architecture (4 Layers)

```
Layer 1 (Domain):    entities, protocols, mapping_service, recognition, anonymizer, deanonymizer
Layer 2 (Use Cases): anonymize, deanonymize, import, validate, context, pack, doctrine, export
Layer 3 (Adapters):  parsers/, recognizers/, writers/, repositories/, cli/
Layer 4 (Infra):     SQLite, Tesseract, File System, Streamlit
```

Dependencies point inward only. The domain layer has zero external dependencies.

---

## CLI Reference

| Command | Description |
|---|---|
| `milanon anonymize <input> -o <dir>` | Anonymize documents (`--recursive`, `--force`, `--dry-run`, `--embed-images`) |
| `milanon deanonymize <input> -o <dir>` | De-anonymize LLM outputs |
| `milanon validate <file>` | Check placeholder integrity in LLM output |
| `milanon pack` | Assemble 5-layer workflow prompt (`--workflow`, `--mode`, `--step`, `--context`) |
| `milanon unpack` | De-anonymize clipboard/file, optionally split into files (`--split`) |
| `milanon export <file> --docx` | Export Markdown to DOCX (`--deanonymize` for real names) |
| `milanon context` | Generate LLM context file (`--unit`, `--output`) |
| `milanon doctrine list` | List available doctrine files from INDEX.yaml |
| `milanon doctrine extract` | Extract doctrine chapters for token-efficient prompting |
| `milanon project generate` | Generate Claude.ai Project folder (`--unit`, `--output`) |
| `milanon config set/get` | Read/write project configuration (mode, unit) |
| `milanon review <dir>` | Review anonymization quality, learn unrecognized names |
| `milanon db init` | Initialize reference data (municipalities + military units) |
| `milanon db import <csv>` | Import from CSV (`--format pisa\|names`) |
| `milanon db list` | List known entities (`--type`, `--limit`) |
| `milanon db stats` | Show database statistics |
| `milanon db reset` | Reset mapping database (`--include-ref-data`) |
| `milanon gui` | Launch Streamlit web interface (`--port`) |

---

## Doctrine Knowledge Base

MilAnon includes 11 Swiss Army regulations as Markdown with chapter-level extraction:

| Regulation | Content |
|---|---|
| BFE 52.080 (Einsatz) | **THE core:** 5+2 Aktionsplanungsprozess, all 5 steps |
| BFE 52.081 (Ausbildung) | Training planning and execution |
| TF 50.030 | Taktische Fuehrung 17 — Einsatzgrundsaetze, Raumordnung, Taktische Aufgaben |
| FSO 50.040 | Fuehrung und Stabsorganisation 17 — Aktionsplanung on staff level |
| WAT 51.301 | Wachtdienst aller Truppen — 10-point guard duty order structure |
| Reglement 51.019 | Checkpoints |
| Reglement 51.020 | Strassenkontrollen |
| Reglement 51.025 | Beobachtung |
| Reglement 51.050 | Sperren |
| Paradigmenwechsel | Bereitschaftsraum paradigm reference |

14 chapter-level extracts in `data/doctrine/extracts/` for token-efficient prompting (~5-30 KB each instead of ~3 MB total).

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

## Streamlit GUI

```bash
milanon gui              # Opens http://localhost:8501
milanon gui --port 8502  # Custom port
```

5 pages: Anonymize, De-Anonymize, LLM Workflow (Pack/Work/Unpack), DB Import, DB Stats.

---

## Development

```bash
git clone https://github.com/V4R9/MilAnon.git
cd Anonymizer_Tool_Army
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
python -m pytest tests/ -x    # 672 tests
ruff check src/ tests/        # Linting
```

### Project Structure

```
src/milanon/
  domain/           # Core business logic (no external deps)
  usecases/         # Anonymize, deanonymize, pack, doctrine, export, context
  adapters/         # Parsers, recognizers, writers, repositories, CLI
  gui/              # Streamlit app
  config/           # Settings, military patterns
  utils/            # CSV helpers
data/
  military_units.csv          # Single source of truth: ranks, branches, units, functions
  swiss_municipalities.csv    # 4059 Swiss municipalities with PLZ and canton
  doctrine/                   # 11 regulations + 14 extracts + 5 skeletons
  templates/                  # 5-layer prompt templates + DOCX base templates
```

### Standards

- Clean Code + SOLID principles
- Tests: Arrange-Act-Assert, naming `test_<what>_<when>_<then>`
- Commits: Conventional Commits (`feat:`, `fix:`, `refactor:`, `test:`)
- All code, docs, tests, comments in English

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feat/your-feature`)
3. Write tests for your changes
4. Ensure all tests pass (`python -m pytest tests/ -x`)
5. Commit with conventional commits
6. Open a Pull Request

---

## Documentation

| Document | Description |
|---|---|
| [Product Design](docs/PRODUCT_DESIGN_COMMAND_ASSISTANT.md) | 5+2 process design, workflow architecture |
| [Roadmap](docs/ROADMAP.md) | Epics, user stories, delivery phases |
| [Architecture](docs/architecture/ARCHITECTURE.md) | Clean Architecture overview + 13 ADRs |
| [Strategic Analysis](docs/STRATEGIC_ANALYSIS.md) | IMD frameworks (Rumelt, PESTEL, VRIO) applied |
| [Changelog](CHANGELOG.md) | Release history |

---

## Security & Privacy

- **No network access** — all processing is 100% local
- **No telemetry** — nothing is logged or transmitted externally
- Database stored at `~/.milanon/milanon.db` (override via `MILANON_DB_PATH`)
- Streamlit GUI runs on `localhost` only
- To wipe all mappings: `milanon db reset` or `rm ~/.milanon/milanon.db`

---

## License

MIT — see [LICENSE](LICENSE)

---

## Acknowledgments

- Swiss Army doctrine: BFE, FSO, TF, WAT
- IMD Strategic Thinking (strategic analysis framework)
- Built with Claude (Anthropic) as AI pair-programming partner
