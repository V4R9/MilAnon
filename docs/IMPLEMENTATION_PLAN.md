# Implementation Plan — MilAnon

> Phase 3 Output
> Last updated: 2026-03-23

## Implementation Order

Build from inside out (Clean Architecture): Domain first, then Use Cases, then Adapters, then CLI.
Each step produces testable, commitable code. No step depends on a later step.

---

## Step 1: Project Skeleton

**Goal:** Working Python package with CLI entry point, all dependencies declared.

**Produces:**
- `pyproject.toml` with all dependencies
- `src/milanon/__init__.py` and `__main__.py`
- `src/milanon/cli/main.py` with `milanon --version`
- Empty package structure for all modules
- `conftest.py` with basic fixtures

**Verification:** `pip install -e .` then `milanon --version` prints version.

**Commit:** `feat: project skeleton with CLI entry point and dependencies`

---

## Step 2: Domain Layer — Entities & Protocols

**Goal:** All data structures and interfaces defined. Zero external dependencies.

**Produces:**
- `domain/entities.py` — EntityType enum, DetectedEntity, EntityMapping, ExtractedDocument, AnonymizedDocument, DocumentFormat
- `domain/protocols.py` — DocumentParser, EntityRecognizer, MappingRepository protocols

**Verification:** `pytest tests/domain/test_entities.py` — tests for entity creation, validation, serialization.

**Commit:** `feat(domain): add entity models and protocol definitions`

---

## Step 3: Domain Layer — Mapping Service + SQLite Repository

**Goal:** Persistent entity-to-placeholder mapping with full CRUD.

**Produces:**
- `domain/mapping_service.py` — MappingService (business logic)
- `adapters/repositories/sqlite_repository.py` — SqliteMappingRepository
- `config/settings.py` — DB path, defaults
- Database schema auto-creation on first run

**Verification:**
- `pytest tests/domain/test_mapping_service.py` — get_or_create, consistency, statistics
- `pytest tests/adapters/repositories/test_sqlite_repository.py` — CRUD, persistence, aliases

**Commit:** `feat(mapping): add MappingService and SQLite repository`

---

## Step 4: Parsers — Document Ingestion

**Goal:** Parse all four file formats into ExtractedDocument.

**Sub-steps (one commit each):**

### 4a: EML Parser
- `adapters/parsers/eml_parser.py`
- Handles: quoted-printable, base64, multipart/alternative, header extraction
- Test with synthetic .eml files in `tests/e2e/fixtures/`
- **Commit:** `feat(parser): add EML parser with MIME encoding support`

### 4b: DOCX Parser
- `adapters/parsers/docx_parser.py`
- Handles: paragraphs, tables, headers/footers, embedded image detection
- **Commit:** `feat(parser): add DOCX parser with table and image detection`

### 4c: PDF Parser
- `adapters/parsers/pdf_parser.py`
- Handles: text extraction (pdfplumber), OCR fallback (pytesseract), mixed pages
- **Commit:** `feat(parser): add PDF parser with OCR fallback`

### 4d: XLSX/CSV Parser
- `adapters/parsers/xlsx_csv_parser.py`
- Handles: multi-sheet XLSX, CSV delimiter detection, header row preservation
- **Commit:** `feat(parser): add XLSX and CSV parser`

### 4e: Parser Registry
- `adapters/parsers/__init__.py` — auto-select parser by file extension
- **Commit:** `feat(parser): add parser registry with auto-detection`

---

## Step 5: Recognizers — Entity Detection

**Sub-steps (one commit each):**

### 5a: Pattern Recognizer
- `adapters/recognizers/pattern_recognizer.py`
- Regex patterns: AHV_NR, TELEFON, EMAIL, ADRESSE, GEBURTSDATUM
- `config/military_patterns.py` — centralized pattern definitions
- **Commit:** `feat(recognition): add pattern recognizer for structured entities`

### 5b: Military Recognizer
- `adapters/recognizers/military_recognizer.py`
- Rank+Name compounds, unit designations (EINHEIT), FUNKTION, GRAD_FUNKTION
- **Commit:** `feat(recognition): add military recognizer for ranks and units`

### 5c: List Recognizer
- `adapters/recognizers/list_recognizer.py`
- Lookup against mapping DB + reference data (municipalities)
- `data/swiss_municipalities.csv` — BFS open data
- **Commit:** `feat(recognition): add list recognizer with municipality database`

### 5d: Recognition Pipeline
- `domain/recognition.py` — orchestrates all three, merge & deduplicate, conflict resolution
- **Commit:** `feat(recognition): add recognition pipeline with priority-based conflict resolution`

---

## Step 6: Anonymizer

**Goal:** Replace detected entities with placeholders, generate legend.

**Produces:**
- `domain/anonymizer.py` — entity replacement, legend generation
- Tests with known input/output pairs

**Commit:** `feat(anonymize): add anonymizer with placeholder replacement and legend generation`

---

## Step 7: De-Anonymizer

**Goal:** Restore placeholders to original values from mapping DB.

**Produces:**
- `domain/deanonymizer.py` — placeholder detection, DB lookup, replacement
- Tests for: successful restoration, missing placeholders, partial matches

**Commit:** `feat(deanonymize): add de-anonymizer with placeholder restoration`

---

## Step 8: Output Writers

**Sub-steps:**

### 8a: Markdown Writer
- For anonymized PDFs and general text output
- **Commit:** `feat(writer): add Markdown writer for anonymized output`

### 8b: DOCX Writer
- Preserves basic formatting during anonymization/de-anonymization
- **Commit:** `feat(writer): add DOCX writer with formatting preservation`

### 8c: CSV Writer + EML Writer
- **Commit:** `feat(writer): add CSV and EML output writers`

---

## Step 9: Use Cases + File Tracking

**Goal:** Orchestrate full flows with incremental processing.

**Produces:**
- `usecases/anonymize.py` — AnonymizeUseCase (single file + batch + incremental)
- `usecases/deanonymize.py` — DeAnonymizeUseCase (single + batch + incremental)
- `usecases/import_entities.py` — ImportEntitiesUseCase (MilOffice CSV)
- `usecases/validate_output.py` — ValidateOutputUseCase (placeholder integrity check)
- File tracking table + SHA-256 delta detection

**Commit:** `feat(usecases): add use case orchestration with incremental processing`

---

## Step 10: CLI Commands

**Goal:** Wire everything together via click CLI.

**Produces:**
- `cli/main.py` — click group
- `cli/anonymize_cmd.py` — `milanon anonymize` with --output, --recursive, --force, --dry-run
- `cli/deanonymize_cmd.py` — `milanon deanonymize` with --output, --force, --dry-run
- `cli/db_cmd.py` — `milanon db import|list|stats`
- `cli/validate_cmd.py` — `milanon validate`

**Commit:** `feat(cli): add CLI commands for anonymize, deanonymize, db, and validate`

---

## Step 11: End-to-End Tests

**Goal:** Full pipeline test with synthetic documents.

**Produces:**
- `tests/e2e/test_full_pipeline.py` — folder in → anonymize → validate → deanonymize → verify
- Synthetic test fixtures for all formats

**Commit:** `test(e2e): add full pipeline end-to-end tests`

---

## Step 12: Reference Data + README

**Goal:** Ship with pre-loaded data and user documentation.

**Produces:**
- `data/swiss_municipalities.csv` populated from BFS open data
- `data/military_units.csv` with common patterns
- `README.md` — installation, usage, examples

**Commit:** `docs: add README with setup instructions and reference data`

---

## Step 13: Streamlit GUI

**Goal:** Simple browser-based local GUI for non-CLI users.

**Produces:**
- `src/milanon/gui/app.py` — Streamlit app
- `cli/main.py` updated with `milanon gui` command
- Streamlit added as dependency in `pyproject.toml`

**Features:**
- Input folder picker (browse or paste path)
- Output folder picker
- Mode selection: Anonymize / De-Anonymize
- Options: --recursive, --force
- "Start" button
- Live progress bar per file
- Summary table: files processed, entities found, warnings
- DB stats view (entity counts by type)
- DB import (upload PISA CSV)

**Usage:** `milanon gui` → opens browser at http://localhost:8501

**Verification:** Manual testing — launch GUI, process test documents, verify output.

**Commit:** `feat(gui): add Streamlit GUI for anonymize and deanonymize`

---

## Step 14: Reference Data Initialization (US-6.3)

**Goal:** Auto-load Swiss municipalities and military patterns into DB on first run.

**Traces to:** US-6.3

**Produces:**
- `usecases/init_reference_data.py` or extension of import_entities.py
- `milanon db init` CLI command
- Auto-detection: if DB has no ref data, load automatically
- data/military_units.csv (generated from data/swiss_military_ranks.md)

**Commit:** `feat(db): add reference data initialization from CSV files`

---

## Step 15: PISA 410 Import with Cross-Source Consistency (US-5.2, US-5.4)

**Goal:** Full PISA 410 import with guaranteed entity consistency across sources.

**Traces to:** US-5.2, US-5.4

**Produces:**
- Complete PISA 410 import in usecases/import_entities.py
- Row 1 skip, Row 2 headers, * prefix strip, i_Gst combination
- Consistency test: Basel from PISA = Basel from municipalities = same placeholder
- Tests in tests/usecases/test_import_entities.py

**Commit:** `feat(import): add PISA 410 import with cross-source consistency`

---

## Step 16: Documentation Update

**Goal:** All project docs reflect the final MVP state.

**Produces:**
- Updated CHANGELOG.md, CLAUDE.md, README.md

**Commit:** `docs: update all project documentation for MVP`
