# MEGA-PROMPT: Paket J — README Rewrite + Final Documentation
# MODEL: Opus

## Context
Read CLAUDE.md, docs/ROADMAP.md, docs/SESSION_HANDOVER.md, docs/PRODUCT_DESIGN_COMMAND_ASSISTANT.md, docs/STRATEGIC_ANALYSIS.md.
Read the current README.md to understand what exists.
Read pyproject.toml for the current version and dependencies.

## Branch
```bash
git checkout -b docs/readme-rewrite
```

## Your Task
Complete rewrite of README.md as a professional open source project landing page. This is what people see first on GitHub. It must be clear, compelling, and complete.

## README.md Structure

```markdown
# MilAnon — Secure AI Command Assistant for the Swiss Army

> Local anonymization + doctrine-aware AI workflows + DOCX generation.
> From 70-page battalion dossier to print-ready company order in hours, not weeks.

[Badges: Python 3.11+ | License: MIT | Tests: 649 passing | Version: 0.5.0]

## The Problem

Swiss Army company commanders (Miliz) receive a 70-page battalion dossier and must
create a complete company command dossier — 16 interconnected documents, all doctrine-
compliant — in their spare time. No staff, no templates, no prior experience.

Public LLMs (ChatGPT, Claude) could help, but classified military documents cannot
be uploaded to cloud services.

## The Solution

MilAnon solves this with three steps:
1. **Anonymize** — Replace all names, units, locations with [PLACEHOLDER] tokens locally
2. **AI-Assisted Creation** — Claude writes doctrine-compliant orders using the 5+2 process
3. **De-anonymize + Export** — Restore real names and generate print-ready DOCX

No classified data ever leaves your machine.

## Quick Start

### Installation
```bash
pip install milanon  # or: git clone + pip install -e .
```

### Basic Flow
```bash
# 1. Import your personnel data
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

## Features

### Core Engine (v0.3.0)
- **Document parsing:** PDF, DOCX, EML, XLSX/CSV
- **Entity recognition:** Names, AHV numbers, phone, email, addresses, military units
- **Bidirectional mapping:** Anonymize ↔ De-anonymize with consistent placeholders
- **Round-trip workflow:** Edit in Obsidian → Re-anonymize → Update via LLM → De-anonymize

### 5+2 Command Workflows (v0.5.0)
- **Doctrine Knowledge Base:** 11 Swiss Army regulations indexed with chapter-level extraction
- **5-Layer Prompt Assembly:** Role + Context + Doctrine + Task + Rules
- **Mode Support:** Bereitschaftsraum (Berrm) and classical ADF
- **3 Workflows:** Analyse (Problemerfassung), Einsatzbefehl, Wachtdienstbefehl
- **DOCX Export:** Markdown → Armee-formatted DOCX with de-anonymization
- **Claude Project Generator:** One-click setup for non-technical commanders

## Supported Workflows

| Workflow | What it does | 5+2 Step |
|---|---|---|
| `analyse` | 4-color marking + problem decomposition + SOMA + timeline | Step 1 |
| `ei-bf` | Complete 5-point order from all planning products | Step 5 |
| `wachtdienst` | WAT-compliant guard duty order | Full cycle |
| `bdl` | AUGEZ factor analysis with AEK method | Step 2 |
| `entschluss` | Variant generation + evaluation + decision | Step 3 |

## Architecture

```
┌──────────────────────────────────────────────────────┐
│  Your Machine (100% local)                           │
│                                                      │
│  PDF/DOCX ──→ Anonymize ──→ [PLACEHOLDER] text       │
│                                    │                  │
│                                    ▼                  │
│                          ┌─────────────────┐          │
│                          │  Claude.ai      │  Cloud   │
│                          │  (sees only     │          │
│                          │  placeholders)  │          │
│                          └────────┬────────┘          │
│                                   │                   │
│                                   ▼                   │
│  Vault ◄── De-anonymize ◄── [PLACEHOLDER] response   │
│    │                                                  │
│    ▼                                                  │
│  DOCX Export (real names, Armee formatting)           │
└──────────────────────────────────────────────────────┘
```

## CLI Reference

[Full table of all commands with flags — from CLAUDE.md]

## Doctrine Knowledge Base

MilAnon includes 11 Swiss Army regulations:
- BFE 52.080 (Führung Einheit — Einsatz) — THE core: 5+2 Aktionsplanungsprozess
- BFE 52.081 (Führung Einheit — Ausbildung)
- WAT 51.301 (Wachtdienst aller Truppen)
- TF 50.030 (Taktische Führung 17)
- [... rest of the list]

## Development

```bash
git clone https://github.com/V4R9/MilAnon.git
cd MilAnon
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
python -m pytest tests/ -x
```

### Architecture: Clean Architecture with 4 layers
[Brief description from CLAUDE.md]

### Contributing
[Standard section: fork, branch, PR, tests must pass]

## License

MIT — see [LICENSE](LICENSE)

## Acknowledgments

- Swiss Army doctrine: BFE, FSO, TF, WAT
- IMD Strategic Thinking (strategic analysis framework)
- Built with Claude (Anthropic) as AI pair-programming partner
```

## Also update: docs/SESSION_HANDOVER.md

Add a "Final State" section at the top:
- Version: 0.5.0
- Tests: [current count]
- CLI commands: [current count]
- GUI pages: [current count]
- Doctrine files: 11 + 14 extracts
- Workflows: 5
- ADRs: 13
- Design decisions: 10/10 resolved

## Files to modify:
- `README.md` — Complete rewrite
- `docs/SESSION_HANDOVER.md` — Final state update

## Files NOT to touch:
- ALL Python source code
- ALL test files
- `CLAUDE.md` (already updated)
- `data/` (any data file)

## Commit
```bash
git add -A
git commit -m "docs: comprehensive README rewrite + session handover final state

- README: problem statement, solution, quick start, architecture, CLI reference
- README: doctrine knowledge base, development guide, contributing
- SESSION_HANDOVER: final v0.5.0 state with all metrics"
```
