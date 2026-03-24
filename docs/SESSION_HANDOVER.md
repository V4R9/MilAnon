# MilAnon — Session Handover / Project Status

> Last updated: 2026-03-23
> Purpose: Complete context for continuing development in a new chat session.

---

## 1. Project Summary

**MilAnon** is a local-only Python CLI + GUI tool for Swiss Army company commanders to anonymize sensitive documents before using public LLMs, and de-anonymize the LLM outputs afterward. All PII stays local.

**Repo:** `/Users/<username>/Documents/GitHub/Anonymizer_Tool_Army`
**User:** macOS, Python 3.11, VS Code, Claude Max, GitHub

---

## 2. What's Been Completed

### Phase 0 — Intake ✅
- Stakeholder interview, knowledge onboarding
- Analyzed: Befehlsdossier (70p PDF), 21 EML files, Obsidian vault, MilOffice sample
- 16 entity types defined, project summary confirmed

### Phase 1 — Requirements ✅
- PRD v1.1 with 9 Epics, 26 User Stories (docs/PRD.md)
- MVP boundary defined, MoSCoW prioritization

### Phase 2 — Architecture ✅
- Clean Architecture (4 layers), 8 ADRs (docs/architecture/)
- Component, Data Flow, Class diagrams (Mermaid)
- SQLite schema, module structure, technology stack

### Phase 3 — Implementation ✅ COMPLETE

| Step | What | Status | Tests |
|------|------|--------|-------|
| 1 | Project Skeleton | ✅ | 7 |
| 2 | Domain Layer (Entities, Protocols) | ✅ | 21 |
| 3 | Mapping Service + SQLite | ✅ | 35 (12+23) |
| 4a | EML Parser | ✅ | 25 |
| 4b | DOCX Parser | ✅ | 25 |
| 4c | PDF Parser (+ OCR fallback) | ✅ | 25 |
| 4d | XLSX/CSV Parser | ✅ | — |
| 4e | Parser Registry | ✅ | — |
| 5a | Pattern Recognizer | ✅ | — |
| 5b | Military Recognizer | ✅ | — |
| 5c | List Recognizer | ✅ | — |
| 5d | Recognition Pipeline | ✅ | — |
| 6 | Anonymizer | ✅ | — |
| 7 | De-Anonymizer | ✅ | — |
| 8 | Output Writers (MD, DOCX, CSV, EML) | ✅ | — |
| 9 | Use Cases + File Tracking | ✅ | — |
| 10 | CLI Commands | ✅ | — |
| 11 | E2E Tests | ✅ | — |
| 12 | Reference Data + README | ✅ | — |
| 13 | Streamlit GUI | ✅ | — |
| **BUG FIX** | **Word boundary enforcement** | ✅ | **17 regression tests** |
| 14 | Reference Data Init (`milanon db init`) | ✅ | 12 |
| 15 | Cross-Source Entity Consistency | ✅ | 10 |
| 16 | Documentation Update | ✅ | — |
| **Total** | | **393 tests passing** | |

---

## 3. ✅ CRITICAL BUG — Word Boundary in Anonymizer — FIXED

**Discovered during first real-world test on the Befehlsdossier Inf Bat 56.**

### Problem (was)
Short entity values were matched INSIDE normal German words:
- "Au" (municipality) → "Ausbildung" became "[ORT_093]sbildung" (474 occurrences!)
- "Lt" → "Gewalt" became "Gewa[GRAD_FUNKTION_002]" (163 occurrences)
- "Inf" → "Einführungen" became "E[FUNKTION_009]ührungen" (112 occurrences)
- "Ins" → "Einsatz" became "E[ORT_034]atz" (81 occurrences)
- "Bern" → "Arbeitgebern" became "[ORT_084]" (40 occurrences)
- "Urs" → "Kurse" became "K[VORNAME_024]e"
- **Total: 917 destroyed words** in a 70-page document

### Fix Applied
1. **`list_recognizer.py`**: `_word_boundary_pattern()` helper using `(?<!\w)`/`(?!\w)` applied to all DB entity lookups (`_match_known_mappings`) and municipality lookups (`_match_municipalities`). `_MIN_MUNICIPALITY_LEN = 4` skips "Au" (2), "Ins" (3), "Egg" (3) entirely.
2. **`military_recognizer.py`**: `_FUNCTION_PATTERNS` and `_RANK_PATTERNS` switched from `\b` to `(?<!\w)`/`(?!\w)`.
3. **`military_patterns.py`**: `UNIT_PATTERN`, `TER_DIV_PATTERN`, `RANK_NAME_PATTERN` switched from `\b` to `(?<!\w)`/`(?!\w)`.
4. **17 regression tests** added in `TestWordBoundaryProtection` classes in both `test_list_recognizer.py` and `test_military_recognizer.py`, covering all 6 reported cases.

> Note: The Anonymizer itself already used offset-based replacement (start_offset/end_offset), so no change was needed there.

---

## 4. ✅ Completed Prompts

All implementation steps and bug fixes are complete. No pending prompts.

---

## 5. Key Files & Locations

| What | Where |
|------|-------|
| Repo | `/Users/<username>/Documents/GitHub/Anonymizer_Tool_Army` |
| PRD (v1.1) | `docs/PRD.md` |
| Architecture | `docs/architecture/ARCHITECTURE.md` |
| ADRs | `docs/architecture/ADR-001..008` |
| Implementation Plan | `docs/IMPLEMENTATION_PLAN.md` |
| PISA 410 Mapping | `docs/PISA_410_COLUMN_MAPPING.md` |
| Project Summary | `docs/PROJECT_SUMMARY.md` |
| Swiss PLZ data | `data/swiss_municipalities.csv` (4'059 entries) |
| Military ranks | `data/swiss_military_ranks.md` |
| Military units CSV | `data/military_units.csv` |
| CLAUDE.md | Root — context for Claude Code |
| Source code | `src/milanon/` |
| Tests | `tests/` |
| GUI | `src/milanon/gui/app.py` (Streamlit) |
| Mails (real) | `/Users/<username>/Library/CloudStorage/OneDrive-Armee2030/Inf Kp 56_1/WK 2026/Personelles` |
| Obsidian vault | `/Users/<username>/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal Vault/10_Projects/WK 2026` |
| Befehlsdossier | In Claude Project Knowledge (PDF, 70 pages) |

## 6. Tech Stack

- Python 3.11+, pyproject.toml, pip
- click (CLI), Streamlit (GUI)
- pdfplumber + pytesseract + pdf2image (PDF/OCR)
- python-docx, openpyxl, email stdlib
- SQLite (mapping DB at ~/.milanon/milanon.db)
- pytest, ruff, mypy
- System deps: `brew install tesseract tesseract-lang poppler`

## 7. CLI Commands (current)

```bash
milanon anonymize <input> --output <o> [--recursive] [--force] [--dry-run]
milanon deanonymize <input> --output <o> [--force] [--dry-run]
milanon validate <file>
milanon db import <csv_path>
milanon db list [--type PERSON]
milanon db init [--force]      # Load reference data (Swiss municipalities + military units)
milanon db stats
milanon gui [--port 8501]      # Opens Streamlit in browser
```

## 8. Development Workflow

- **This chat (claude.ai):** Project management, architecture, reviews, documentation
- **Claude Code (Terminal):** Implementation, testing, committing
- **Model:** Opus for complex architecture decisions, Sonnet for implementation steps
- After every Claude Code step: `pytest tests/ -v`, then commit with Conventional Commits

## 9. Key Decisions Made

| # | Decision |
|---|----------|
| D1 | PDF → Markdown output for LLM |
| D2 | Embedded images: detect & warn (MVP), OCR (post-MVP) |
| D3 | Streamlit GUI promoted to MVP |
| D4 | Cross-source entity consistency is Must |
| D5 | Auto reference data init on first run |
| D6 | Dienstbemerkungen NOT anonymized |

## 10. User Context

- Swiss Army Kp Kdt (Inf Kp 56/1), 4-year command cycle
- ~150 personnel, documents: Befehlsdossier, Mails, PISA exports
- Uses: Claude Max, VS Code, GitHub, macOS, Obsidian
- Conversation language: German (Swiss, ss not ß)
- All technical artifacts: English
