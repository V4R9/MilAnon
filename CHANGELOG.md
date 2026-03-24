# Changelog

All notable changes to this project will be documented in this file.

## [0.3.0] — 2026-03-25 — Iterations 2-2c + Code Review + GUI Overhaul

### Iteration 2: External Personnel Import
- B-008: Generic name CSV import (`milanon db import <csv> --format names`) for Bat Stab and external personnel.
  - New `ImportNamesUseCase` for simple 3-column CSV (`Grad;Vorname;Nachname`).
  - Auto-detects "Name / Vorname" combined column format (splits on first comma).
  - Auto-detects "Grad Kurzform" as alias for "Grad".
  - GUI: Format radio on DB Import page (PISA 410 / Simple Name List).
  - 11 new tests.
- B-009: Quick-Add single person form in GUI (Grad + Vorname + Nachname).
  - Immediate feedback: "Added: Hptm Thomas WEGMÜLLER (4 entities)".
  - Duplicate detection: "Already exists in database".
  - Fields cleared after successful add via session_state.

### Iteration 2b: Format Compatibility + Visual Pages
- B-008-fix: Auto-detect "Name / Vorname" combined column format (split on comma).
- B-011: Visual PDF page detection (WAP/Picasso heuristic: >20 cols AND >70% empty → skip with warning).
  - `ExtractedDocument` gains `visual_pages: list[int]` field.
  - `AnonymizeResult` gains `visual_page_count`; CLI prints warning and accepts `--embed-images` flag.
  - GUI: Warning shown after anonymization.
  - 5 new tests.
- B-011-fix: `--embed-images` flag renders visual pages as PNG (200 DPI) alongside the `.md` output.
- B-011-fix2: Tightened visual heuristic to require BOTH conditions (AND logic) — fixes false positives on normal data tables (e.g. Dokumentenbudget).
- "Alle" (PLZ 2942, JU) completely excluded from municipality matching — 20 false positives in real-world test.
- "Adj" added as standalone rank (catches "Adj Stefan SCHEGG" pattern).
- CSV delimiter auto-detection via `csv.Sniffer` (handles `;`, `,` and tab) — new shared `utils/csv_helpers.py`.
- Per-file progress output during anonymization (CLI).
- Version number displayed in GUI sidebar.

### Iteration 2c: LLM Context + EINHEIT Quality
- B-012: LLM Context Generator — `milanon context --unit "Inf Kp 56/1"` generates `CONTEXT.md` with unit hierarchy, filtering instructions, and placeholder mapping. Interactive unit selection when `--unit` is omitted.
- B-012-fix: EINHEIT whitespace normalization (newlines → spaces) prevents duplicate placeholders from PDF extraction. Single-word fragments ("Ter", "Inf") rejected. Context file output path configurable via `--output`.
- B-012-fix2: Battalion filtering in `CONTEXT.md` now correctly uses the identified parent unit (not a random battalion).

### GUI Enhancements
- New "LLM Workflow" page with 3 tabs: Pack for LLM, Work with LLM, Unpack Response
- Context Generator integrated in GUI with unit dropdown and preview
- Embed Images checkbox on Anonymize page
- "Initialize Reference Data" button on DB Stats page (appears when ref data missing)
- Auto-initialize reference data after "Reset Everything"
- De-Anonymize page with paste text area for LLM output

### Code Review Refactoring (14 Findings)
- **P0 — Encapsulation:** Use Cases no longer access private `_repository` attribute directly — new `MappingService.has_mapping()` method added. CLI no longer accesses private `_conn` — new `clear_reference_data()` method.
- **P1 — DRY:** Extracted shared `detect_delimiter()` into `utils/csv_helpers.py`. Consolidated `LEGEND_PATTERN` into single definition in `anonymizer.py` (imported by writers and deanonymizer). Consolidated `VISUAL_PAGE_SKIP_MARKER` / `VISUAL_PAGE_EMBED_MARKER` into `pdf_parser.py`. Introduced `ProcessingOptions` frozen dataclass for `AnonymizeUseCase`.
- **P2 — Encapsulation + Types:** Added `DeAnonymizer.resolve_placeholder()` public method; `ValidateOutputUseCase` no longer accesses `_mapping_service` directly. Added explicit type hints to all use case constructors. Added performance and SRP notes in code comments.
- **P3 — Polish:** Fixed duplicate `import re`, promoted lazy imports to module level, added `__all__` to `domain/`, `adapters/parsers/`, `adapters/recognizers/`, `adapters/writers/` `__init__.py` files. Added NOTE to `_parent_number()` documenting Swiss Army `/` naming convention assumption.

### Test Coverage
- **505 tests** passing (up from 418 at v0.2.0).

---

## [0.2.0] — 2026-03-24 — Post-MVP Improvements (Iteration 1)

### B-007: PDF Tables Rendered as Markdown Tables
- `PdfParser` now detects tables via `pdfplumber.find_tables()` and renders them as pipe-syntax Markdown (`| col | col |`) with a `| --- | --- |` separator row.
- Text above/below tables is cropped to avoid duplicate content.
- OCR fallback path unchanged; tables interleaved in reading order (y-coordinate).
- 4 new tests.

### B-004: Initial.NACHNAME Pattern Detection
- New `INITIAL_SURNAME_PATTERN` in `PatternRecognizer` detects names of the form `D. MUFFLER`, `M. KOCH`, `L. STORRER` (uppercase initial, dot, ALLCAPS surname).
- These appear in Organigramm and Adressliste without a rank prefix and were previously missed.
- Word-boundary guards prevent substring false positives.
- 6 new tests.

### B-005: Municipality Stopword List
- `ListRecognizer` no longer matches municipalities whose names are also common German words (e.g. "Alle" — PLZ 2942, JU) without a context signal.
- Context signals: 4-digit PLZ or locative preposition (in/nach/bei/von/aus/via) within 40 characters before the match.
- Fixes 35 spurious `[ORT]` replacements of the word "alle" in real documents.
- 5 new tests.

### B-006: GEBURTSDATUM Detection Restricted to Personnel Context
- Dates in `dd.mm.yyyy` format are no longer matched as `GEBURTSDATUM` unconditionally.
- New `_match_birthdates()` in `PatternRecognizer` requires a personnel-context keyword (Geburtsdatum, geboren, geb., Jahrgang, JG, Geburtstag) within 80 characters before the date.
- Operational dates (mission dates, report dates, etc.) are no longer anonymized.
- Fixes 211 spurious GEBURTSDATUM matches in real documents.
- 6 new tests (+ 1 existing test updated to use context keyword).

### B-001: Database Reset (GUI + CLI)
- `SqliteMappingRepository` gains `reset_all_mappings()` (keeps reference data) and `reset_everything()` (clears all tables).
- CLI: `milanon db reset [--include-ref-data]` with `--yes`/confirmation prompt.
- GUI: "Database Management" section on DB Stats page with guarded Reset Mappings / Reset Everything buttons (checkbox confirmation required).
- 4 new tests.

### Test Coverage
- **418 tests** passing (up from 393 at MVP).

---

## [0.1.0] — 2026-03-23 — MVP Release

### Phase 3 — Implementation (2026-03-23)

#### Step 1-4: Project Skeleton + Parsers
- Project skeleton with click CLI, pyproject.toml, all dependencies
- EML parser (quoted-printable, base64, multipart/alternative, header extraction)
- DOCX parser (paragraphs, tables, headers/footers, image detection)
- PDF parser (pdfplumber text extraction + Tesseract OCR fallback)
- XLSX/CSV parser (multi-sheet XLSX, delimiter auto-detection, BOM handling)
- Parser registry `get_parser(path)` — auto-selects parser by extension

#### Step 5: Entity Recognition
- **PatternRecognizer**: regex for AHV_NR, TELEFON (3 formats), EMAIL, ADRESSE, GEBURTSDATUM
- **MilitaryRecognizer**: rank+name compounds → GRAD_FUNKTION + PERSON; unit designations → EINHEIT; FUNKTION
  - Longest-first rank alternation (e.g. "Oberstlt i Gst" before "Oberstlt")
- **ListRecognizer**: DB entity lookup (case-insensitive) + municipality lookup from DB
- **RecognitionPipeline**: priority-based conflict resolution (Pattern > Military > List)
  - Sort by (source_priority, -span_length, start_offset); greedy accept

#### Step 6-7: Anonymizer + De-Anonymizer
- **Anonymizer**: reverse-offset substitution, embedded legend header (`<!-- MILANON LEGEND START...END -->`)
- **DeAnonymizer**: strips legend, resolves placeholders, warns on unresolved

#### Step 8: Output Writers
- MarkdownWriter (pass-through, for PDF and plain text output)
- DocxWriter (strips legend, preserves DOCX structure)
- CsvWriter (uses structured_content for tabular preservation)
- EmlWriter (strips legend, preserves email headers)

#### Step 9: Use Cases + File Tracking
- **AnonymizeUseCase**: batch + incremental via SHA-256 (ADR-008), force/dry-run
- **DeAnonymizeUseCase**: same incremental pattern for LLM output files
- **ImportEntitiesUseCase**: PISA 410 format (skip title+header rows, strip `*` prefix, `i Gst` combining)
- **ValidateOutputUseCase**: placeholder integrity check with resolved/unresolved counts
- File tracking in `file_tracking` table (`UNIQUE(file_path, operation)`, upsert on conflict)

#### Step 10: CLI
- All commands wired to use cases with progress output and exit codes (0/1/2):
  - `milanon anonymize` / `deanonymize` / `validate`
  - `milanon db import` / `list` / `stats`

#### Step 11: End-to-End Tests
- Full pipeline test: folder of mixed files → anonymize → validate → deanonymize → verify
- 12 E2E tests covering CSV round-trip, mixed folder, incremental skipping, fixture files

#### Step 12: Reference Data + README
- `data/military_units.csv`: 57 entries (ranks, branches, unit patterns, functions)
- `data/swiss_municipalities.csv` (3958 names) wired into ListRecognizer
- README.md: complete installation guide, all CLI commands, workflow, reference table

#### Step 13: Streamlit GUI
- `src/milanon/gui/app.py`: 4-page Streamlit app
  - Anonymize page: folder pickers, recursive/force/dry-run, progress bar, metrics
  - De-Anonymize page: same pattern for LLM output restoration
  - DB Import page: upload PISA CSV, stores locally, shows import summary
  - DB Stats page: entity counts per type with bar chart
- `milanon gui [--port 8501]` — launches Streamlit in browser
- `streamlit>=1.35` added to dependencies

#### Critical Bug Fix: Word Boundary Enforcement

**Problem discovered during first real-world test (Befehlsdossier Inf Bat 56, 70 pages):**
Naive substring matching without word boundaries destroyed 917 words:
- "Au" (municipality, len 2) matched inside "Ausbildung" → "[ORT_093]sbildung" (474×)
- "Lt" (rank) matched inside "Gewalt" → "Gewa[GRAD_FUNKTION_002]" (163×)
- "Inf" matched inside "Einführungen" → "E[FUNKTION_009]ührungen" (112×)
- "Ins" (municipality, len 3) matched inside "Einsatz" → "E[ORT_034]atz" (81×)
- "Bern" matched inside "Arbeitgebern" → "[ORT_084]" (40×)
- "Urs" (first name) matched inside "Kurse" → "K[VORNAME_024]e"

**Root cause:** `_match_known_mappings` in `ListRecognizer` used bare `re.escape(value)` with zero word-boundary protection. `\b` in `MilitaryRecognizer` and `military_patterns.py` is unreliable with non-ASCII characters (umlauts).

**Fix:**
- `list_recognizer.py`: Added `_word_boundary_pattern()` helper using `(?<!\w)`/`(?!\w)` lookbehind/lookahead applied to all DB lookups and municipality matching. Added `_MIN_MUNICIPALITY_LEN = 4` — names shorter than 4 chars ("Au", "Ins", "Egg") are skipped entirely.
- `military_recognizer.py`: `_FUNCTION_PATTERNS` and `_RANK_PATTERNS` switched from `\b` to `(?<!\w)`/`(?!\w)`.
- `military_patterns.py`: `UNIT_PATTERN`, `TER_DIV_PATTERN`, `RANK_NAME_PATTERN` switched from `\b` to `(?<!\w)`/`(?!\w)`.
- 17 regression tests added (`TestWordBoundaryProtection` in both recognizer test files) covering all 6 reported cases.

Commit: `fix(recognition): word-boundary protection prevents substring false positives`

#### Step 14: Reference Data Initialization (US-6.3)
- **InitReferenceDataUseCase**: loads municipalities + military units from CSV into SQLite ref tables
- `milanon db init [--force]` CLI command
- Auto-init: first anonymize/deanonymize run triggers init if DB is empty (D5)
- ListRecognizer now fetches municipality names from `ref_municipalities` table (not in-memory)
- SqliteMappingRepository: added `import_municipalities_full`, `import_military_units`,
  `get_ref_municipality_count`, `get_ref_military_unit_count`
- 12 new tests: loading, idempotency, DB lookup

#### Step 15: Cross-Source Entity Consistency (US-5.4)
- MappingService uses `normalized_value = value.strip().lower()` for case-insensitive deduplication
- 10 consistency tests verifying: "Basel" from municipality DB + PISA import + document = same `[ORT_NNN]`
- Case variants verified: "BASEL"/"Basel"/"basel" → identical placeholder
- Whitespace trimming verified: "Müller" and "  Müller  " → same placeholder

#### Step 16: Bug Fix + Documentation
- GUI: strip surrounding quotes (single and double) from path inputs
- CHANGELOG.md, CLAUDE.md, README.md updated for MVP

### Test Coverage
- **393 tests** passing across all layers
- Domain: entities, mapping service, recognition pipeline, anonymizer, de-anonymizer
- Adapters: all parsers, all recognizers, SQLite repository, all writers
- Use Cases: anonymize, deanonymize, import entities, validate output, init reference data
- Cross-source consistency: 10 tests verifying entity deduplication across sources
- E2E: 12 full pipeline tests with fixture files
- Word boundary regression: 17 tests covering all reported substring false-positive cases

---

## [Unreleased — pre-0.1.0]

### Phase 2 — Architecture & Design (2026-03-23)

- ADR-008: Incremental Processing via content-hash delta detection
- Architecture Overview with Clean Architecture layer model
- 8 Architecture Decision Records (ADR-001 through ADR-008)
- PRD version 1.1 with 9 Epics, 23 User Stories

### Phase 1 — Requirements & Specification (2026-03-23)

- PRD v1.0 with 9 Epics, 23 User Stories
- Decisions D1-D6 documented
- 6 risks identified with mitigations

### Phase 0 — Intake & Knowledge Onboarding (2026-03-23)

- Stakeholder interview completed
- Analyzed reference documents (Befehlsdossier, EML files, MilOffice export)
- Repository initialized
