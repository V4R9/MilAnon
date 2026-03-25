# Changelog

All notable changes to MilAnon are documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.6.0] — 2026-03-25

### Added
- **FR-017: Two-Tier Anonymization** — `--level dsg|full` flag on `milanon anonymize` and `milanon pack`
  - DSG mode (default): anonymizes only personal data (names, AHV, phone, email, address, medical, family)
  - Full mode: anonymizes all entities including units, locations, functions (previous behavior)
  - Domain: `AnonymizationLevel` enum, `DSG_ENTITY_TYPES`/`ISG_ENTITY_TYPES` frozensets, `filter_entities_by_level()`
  - Config: `milanon config set level dsg|full` for persistent default
- **FR-001: Dossier Quality Check** — wired `dossier-check` workflow into INDEX.yaml
- **BUG-018: Rich output** for `milanon pack --workflow` command
- **CI/CD: GitHub Actions pipeline** — pytest + ruff on Python 3.11/3.12
- Templates updated with anonymization level awareness (rules.md, CHEAT_SHEET.md, generate_context.py)
- 13 new tests for two-tier anonymization (705 total)

---

## [0.5.0-stable] — 2026-03-25

### Added
- Rich terminal output with panels, tables, and colors (click + rich)
- Complete Streamlit GUI overhaul (8 pages: anonymize, deanonymize, workflows, export, doctrine, project, db, config)
- E2E bug fixes: {user_unit} replacement, doctrine layer, CSV exclusion
- README rewrite with problem/solution narrative
- Repository context manager support (`__enter__`/`__exit__`)
- Thread safety in mapping creation (`BEGIN IMMEDIATE`)
- CSV encoding fallback (UTF-8 + Latin-1)
- HTML entity handling via `html.unescape()` in EML parser
- Regex pattern caching in ListRecognizer
- New protocols: `FileTrackingRepository`, `ReferenceDataRepository`
- FR-017 specification committed (`docs/specs/FR-017_two_tier_anonymization.md`)

### Fixed
- CR-001: Placeholder collision — `COUNT(*)` replaced with `MAX()` to avoid collisions on concurrent inserts
- CR-002: Bare `except Exception` in migrations narrowed to `sqlite3.OperationalError`
- CR-003: DB connection leak — connections now properly closed via context manager
- CR-004: PII leaked in anonymizer warning strings — strings sanitized
- CR-005: PII leaked in review_candidates log messages — log output sanitized
- CR-008: Private attribute access (`_attr`) replaced with public methods
- CR-009: `domain/workflow.py` imported yaml (external dep in domain) — moved to `config/`
- CR-011: Entity normalization moved from repository to MappingService (correct Clean Architecture layer)
- CR-012: Placeholder regex deduplicated into single `PLACEHOLDER_PATTERN` constant
- CR-017: `EntityMapping` now immutable (`frozen=True`)
- Narrow exception handling in DOCX parser and PDF parser (CR-013)

### Removed
- Deprecated `data/swiss_military_ranks.md` (superseded by `military_units.csv`)
- Stale documentation moved to `docs/archive/`

---

## [0.5.0] — 2026-03-25

### Added
- **E14: Doctrine Knowledge Base** — 11 regulations, 14 chapter extracts, INDEX.yaml
- **E15: 5+2 Workflow Infrastructure** — `--workflow`, `--mode`, `--context`, `--step` flags
- **E15.W1/W4/W5: Workflows** — Analyse, Einsatzbefehl, Wachtdienstbefehl
- **E16: Claude Project Generator** — `milanon project generate` with `--input`, `--include-images`
- **E17: DOCX Export** — `milanon export --docx --deanonymize` (functional, formatting issues pending)
- 5-Layer System Prompt architecture (Role + Context + Doctrine + Task + Rules)
- 3 document skeletons (5-Punkte-Befehl, Allgemeiner Befehl, Wachtdienstbefehl)
- CHEAT_SHEET.md quick reference for commanders
- Incremental processing improvements (orphan cleanup, rename detection)

### Known Issues
- BUG-005 to BUG-011: DOCX Writer formatting issues (planned: FR-004 Writer Rewrite)
- BUG-012/013: PII detection gaps for names without rank, addresses without suffix

---

## [0.3.0] — 2026-03-22

### Added
- Core anonymization engine (pattern, military, list recognizers)
- De-anonymization with placeholder mapping
- SQLite persistent entity mapping
- PDF, DOCX, EML, XLSX/CSV parsers
- Streamlit GUI (5 pages)
- 17 CLI commands
- 520+ tests
