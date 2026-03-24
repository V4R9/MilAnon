# MilAnon — Session Handover

Last updated: 2026-03-25
Version: 0.3.0

## Project Status

MilAnon is a local Python CLI+GUI tool for Swiss Army commanders to anonymize documents before sending them to public LLMs. All processing is local — no data leaves the machine.

**Repository:** https://github.com/V4R9/MilAnon (public, branch protection enabled)

### What's Built

- CLI + Streamlit GUI (5 pages: Anonymize, De-Anonymize, LLM Workflow, DB Import, DB Stats)
- Parsers: EML, DOCX, PDF (with table extraction + OCR fallback), XLSX/CSV
- Recognizers: PatternRecognizer (AHV, phone, email, dates, addresses), MilitaryRecognizer (rank+name, units, functions), ListRecognizer (DB lookup + municipalities)
- Anonymizer with legend generation + De-Anonymizer with placeholder resolution
- SQLite mapping database with incremental file tracking (SHA-256)
- Reference data: 4059 Swiss municipalities, military unit patterns (single source of truth in `data/military_units.csv`)
- LLM Context Generator with unit hierarchy (`milanon context`)
- 505 tests across all layers

### What's In Progress (parallel Claude Code sessions)

- Epic E13: Military Reference Data Consolidation (B-028 to B-031)
- Content Sprint: PDF Output Quality (B-013, B-014), Obsidian De-Anonymize (B-023, B-024), EML Display Names (B-022)

### Real-World Test Results (last full run)

- Input: 1 PDF (70 pages) + 21 EML files
- PISA import: 132 persons, 1059 entities
- Bat Stab CSV: 21 persons, 56 entities
- Total DB: 1115 entities
- Output: 22 files, 0 errors
- Visual pages: 4 detected (WAP/Picasso schedules)
- Known leaks: Names not in any import list (Adressliste Stab ~20 persons)

### Sprint Plan

| When | What |
|---|---|
| Mi 25. | Demo |
| Do 26. | Output Quality + De-Anonymize Quality |
| Fr 27. | GUI Polish + Round-Trip Testing |
| Sa-So 28.-30. | Full Acceptance Test → Produktiv-ready |

### Key Files

- Repo: /Users/sd/Documents/GitHub/Anonymizer_Tool_Army
- DB: ~/.milanon/milanon.db
- Test input: test_input/ (PDF + EML + CSV)
- Test output: test_output/
- Docs: docs/BACKLOG.md (27 items), docs/ROADMAP.md (Epics E1-E13)
- GUI: src/milanon/gui/app.py
- App launcher: scripts/launch_gui.command

### Pending Documentation Tasks

- CHANGELOG: v0.3.0 section updated (this session)
- pyproject.toml: version bumped to 0.3.0

## Architecture Overview

Clean Architecture with Dependency Inversion:

- **Domain Layer:** entities, protocols, mapping_service, anonymizer, deanonymizer, recognition
- **Adapters:** parsers (eml, docx, pdf, xlsx_csv), recognizers (pattern, military, list), repositories (sqlite), writers (markdown, eml, csv, docx)
- **Use Cases:** anonymize, deanonymize, generate_context, import_entities, import_names, init_reference_data, validate_output
- **UI:** cli/main.py (Click), gui/app.py (Streamlit)

### Key directories

```
src/milanon/config/     — military_patterns.py (regex patterns, PII + military)
src/milanon/utils/      — csv_helpers.py (shared CSV utilities)
data/                   — military_units.csv (single source of truth for military ref data)
                          swiss_municipalities.csv (4059 municipalities)
```

## Obsidian Round-Trip Workflow (Vision)

The core innovation: MilAnon enables a continuous round-trip between a local Obsidian vault and Claude.ai, preserving user edits across iterations.

1. Source docs → anonymize → Claude → de-anonymize → Vault
2. User edits in Vault (status changes, notes, tasks)
3. Re-anonymize Vault → + new mails → Claude "update" → de-anonymize --in-place → Vault

See docs/ROADMAP.md Epic E10 for the Pack/Unpack automation.

## CLI Quick Reference

```bash
milanon db init                                          # Initialize reference data (first run)
milanon db import personalbestand.csv                    # PISA 410 / MilOffice export
milanon db import bat_stab.csv --format names            # Simple Grad;Vorname;Nachname list
milanon anonymize ./input/ --output ./anon/ --recursive
milanon anonymize ./input/ --output ./anon/ --embed-images  # PNG for visual pages
milanon context --unit "Inf Kp 56/1" --output test_output/CONTEXT.md
milanon deanonymize ./llm_output/ --output ./restored/
milanon validate llm_response.md
milanon db stats
milanon db reset [--include-ref-data]
milanon gui
```

## User Context

- Swiss Army Kp Kdt (Inf Kp 56/1), 4-year command cycle
- ~150 personnel, documents: Befehlsdossier, Mails, PISA exports
- Uses: Claude Max, VS Code, GitHub, macOS, Obsidian
- Conversation language: German (Swiss, ss not ß)
- All technical artifacts: English
