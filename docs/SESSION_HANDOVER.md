# MilAnon — Session Handover / Project Status

> Last updated: 2026-03-24
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

### Post-MVP Iterations ✅

#### Iteration 1 (v0.2.0)

| Item | What | Tests |
|------|------|-------|
| B-007 | PDF tables rendered as Markdown pipe-syntax | 4 |
| B-004 | Initial.NACHNAME pattern (`D. MUFFLER`) | 6 |
| B-005 | Municipality stopword list (context signal) | 5 |
| B-006 | GEBURTSDATUM restricted to personnel context | 6 |
| B-001 | GUI + CLI database reset | 4 |
| Quick Fix | "Alle" fully excluded from municipality matching | — |
| Quick Fix | "Adj" added as standalone rank | 2 |
| **Total** | | **418 tests passing** |

#### Iteration 2 + 2b (v0.3.0 — partial)

| Item | What | Tests |
|------|------|-------|
| B-008 | Generic name CSV import (`Grad;Vorname;Nachname`) | 11 |
| B-008-fix | Auto-detect combined `Name / Vorname` column + `Grad Kurzform` alias | (included above) |
| B-009 | Quick-Add single person via GUI form | — |
| B-011 | Visual PDF page detection (WAP/schedules), warning marker | 5 |
| B-011-fix | `--embed-images` renders visual pages as PNG (200 DPI) | 5 |
| B-011-fix2 | Visual heuristic tightened to AND logic (fixes false positives) | 2 |
| Quick Fix | Per-file progress output in CLI (anonymize + deanonymize) | — |
| Quick Fix | Version number in GUI sidebar | — |
| Quick Fix | CSV delimiter auto-detection via `csv.Sniffer` (`;`, `,`, tab) | 6 |

#### Iteration 2c (v0.3.0 — complete)

| Item | What | Tests |
|------|------|-------|
| B-012 | LLM Context Generator (`milanon context --unit "Inf Kp 56/1"`) | 24 |
| B-012-fix | EINHEIT whitespace normalization (newlines → spaces), single-word rejection, `--output` flag | 6 |
| B-012-fix2 | Battalion filtering uses correct parent unit (not first in list) | 2 |

#### Phase 5 — Code Review Refactoring ✅ (14 findings, all addressed)

| Finding | Priority | What |
|---------|----------|------|
| F1 | P0 | `has_mapping()` on `MappingService` — Use Cases no longer access `_repository` directly |
| F2 | P0 | `clear_reference_data()` on repo — CLI no longer accesses `_conn` directly |
| F3 | P1 | Extracted `detect_delimiter()` into `utils/csv_helpers.py` (DRY) |
| F4 | P1 | Consolidated `LEGEND_PATTERN` into `anonymizer.py` — imported by writers and deanonymizer |
| F5 | P1 | Consolidated `VISUAL_PAGE_SKIP_MARKER` / `_EMBED_MARKER` into `pdf_parser.py` |
| F6 | P1 | Removed duplicate `import re` from `pattern_recognizer.py` |
| F7 | P1 | `ProcessingOptions` frozen dataclass replaces 3 bool params in `_process_file` |
| F8 | P2 | `DeAnonymizer.resolve_placeholder()` public method; `ValidateOutputUseCase` no longer reaches into `_mapping_service` |
| F9 | P2 | SRP NOTE added to `SqliteMappingRepository` docstring |
| F10 | P2 | PERFORMANCE NOTE added to `ListRecognizer._match_known_mappings` |
| F11 | P2 | Explicit type hints — `SqliteMappingRepository` in `AnonymizeUseCase` + `InitReferenceDataUseCase`; `MappingRepository` in `GenerateContextUseCase` |
| F12 | P2 | Promoted lazy `docx` imports to module level in `DocxWriter` |
| F13 | P3 | NOTE added to `_parent_number()` about Swiss Army `/` naming convention |
| F14 | P3 | `__all__` added to `domain/`, `adapters/parsers/`, `adapters/recognizers/`, `adapters/writers/` |

**Current total: 480 tests passing.**

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
1. **`list_recognizer.py`**: `_word_boundary_pattern()` helper using `(?<!\w)`/`(?!\w)` applied to all DB entity lookups and municipality lookups. `_MIN_MUNICIPALITY_LEN = 4` skips "Au" (2), "Ins" (3), "Egg" (3) entirely.
2. **`military_recognizer.py`**: `_FUNCTION_PATTERNS` and `_RANK_PATTERNS` switched from `\b` to `(?<!\w)`/`(?!\w)`.
3. **`military_patterns.py`**: `UNIT_PATTERN`, `TER_DIV_PATTERN`, `RANK_NAME_PATTERN` switched from `\b` to `(?<!\w)`/`(?!\w)`.
4. **17 regression tests** covering all 6 reported cases.

---

## 4. Real-World Test Results

**Test document:** Befehlsdossier Inf Bat 56 (23 files: 1 PDF 70p, 21 EML, 1 DOCX)

| Metric | Value |
|--------|-------|
| Files processed | 23 |
| Errors | 0 |
| Visual pages detected | 4 (WAP/Picasso schedules) |
| Total entities anonymized | ~1232 |
| Known leaks | DÜRST (2×), Schegg (2×) — not in any import list |
| Partially covered | 20+ names in Adressliste Stab not in CSV import |

**Root causes of known leaks:**
- Soldiers with no PISA export entry and not in Bat Stab CSV
- Fix path: B-010 (Post-Anonymization Review) or manual `milanon db import` with their names

---

## 5. Pending (next session)

- **Phase 4 — Abnahmetest** (user acceptance) — real-world full run with current v0.3.0
- **Iteration 4** — Output Quality: B-013 (Organigramm mega-cell), B-014 (empty column stripping)
- **Iteration 3** — B-010 Post-Anonymization Review (learn unknown names)

See `docs/BACKLOG.md` for the full backlog (21 open items across 6 planned iterations).

---

## 6. Key Files & Locations

| What | Where |
|------|-------|
| Repo | `/Users/<username>/Documents/GitHub/Anonymizer_Tool_Army` |
| PRD (v1.1) | `docs/PRD.md` |
| Architecture | `docs/architecture/ARCHITECTURE.md` |
| ADRs | `docs/architecture/ADR-001..008` |
| Implementation Plan | `docs/IMPLEMENTATION_PLAN.md` |
| PISA 410 Mapping | `docs/PISA_410_COLUMN_MAPPING.md` |
| Project Summary | `docs/PROJECT_SUMMARY.md` |
| Backlog | `docs/BACKLOG.md` |
| Swiss PLZ data | `data/swiss_municipalities.csv` (3958 entries) |
| Military ranks | `data/swiss_military_ranks.md` |
| Military units CSV | `data/military_units.csv` |
| CLAUDE.md | Root — context for Claude Code |
| Source code | `src/milanon/` |
| Tests | `tests/` |
| GUI | `src/milanon/gui/app.py` (Streamlit) |
| Shared utilities | `src/milanon/utils/csv_helpers.py` |

## 7. Tech Stack

- Python 3.11+, pyproject.toml, pip
- click (CLI), Streamlit (GUI)
- pdfplumber + pytesseract + pdf2image (PDF/OCR)
- python-docx, openpyxl, email stdlib
- SQLite (mapping DB at ~/.milanon/milanon.db)
- pytest, ruff
- System deps: `brew install tesseract tesseract-lang poppler`

## 8. CLI Commands (current)

```bash
milanon anonymize <input> --output <o> [--recursive] [--force] [--dry-run] [--embed-images]
milanon deanonymize <input> --output <o> [--force] [--dry-run]
milanon validate <file>
milanon context [--unit "Inf Kp 56/1"] [--output CONTEXT.md]
milanon db import <csv_path> [--format pisa|names]
milanon db list [--type PERSON] [--limit N]
milanon db init [--force]                          # Load reference data
milanon db reset [--include-ref-data] [--yes]      # Delete mappings
milanon db stats
milanon gui [--port 8501]                          # Opens Streamlit in browser
```

## 9. Development Workflow

- **This chat (claude.ai):** Project management, architecture, reviews, documentation
- **Claude Code (Terminal):** Implementation, testing, committing
- **Model:** Opus for complex architecture decisions, Sonnet for implementation steps
- After every Claude Code step: `pytest tests/ -v`, then commit with Conventional Commits

## 10. Key Decisions Made

| # | Decision |
|---|----------|
| D1 | PDF → Markdown output for LLM |
| D2 | Embedded images: detect & warn (MVP), OCR (post-MVP) |
| D3 | Streamlit GUI promoted to MVP |
| D4 | Cross-source entity consistency is Must |
| D5 | Auto reference data init on first run |
| D6 | Dienstbemerkungen NOT anonymized |

## 11. User Context

- Swiss Army Kp Kdt (Inf Kp 56/1), 4-year command cycle
- ~150 personnel, documents: Befehlsdossier, Mails, PISA exports
- Uses: Claude Max, VS Code, GitHub, macOS, Obsidian
- Conversation language: German (Swiss, ss not ß)
- All technical artifacts: English
