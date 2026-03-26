# Changelog

All notable changes to MilAnon are documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.6.4] — 2026-03-26

### Fixed
- **BUG-019: Numbered heading recognition** — `DocxBefehlWriter` now detects numbered section patterns from PDF extraction (`1. Orientierung` → `1. Main title`, `1.1. Grundlagen` → `1.1 Title`, `1.2.1. Erhaltener Auftrag` → `1.1.1 Title`). Capital letter heuristic prevents false positives with ordered list items.
- **BUG-020: PDF artifact stripping** — Page footers, source `.docx` filenames, and standalone page numbers from PDF extraction are automatically filtered out before DOCX rendering.
- **BUG-021: Inline formatting** — `DocxBefehlWriter` now renders `**bold**`, `*italic*`, `***bold+italic***`, and `` `code` `` as proper DOCX runs (ported from `DocxWriter`).
- **Additional improvements** — `DocxBefehlWriter` now handles horizontal rules (`---` → page breaks), blockquotes (`>` → italic), HTML comment stripping, and MILANON legend block stripping.

---

## [0.6.3] — 2026-03-25

### Fixed
- **GUI Alignment Sprint** — all CLI features now available in Streamlit GUI:
  - `--level dsg|full` radio button on Anonymize page (FR-017)
  - `--include-spreadsheets` checkbox on Anonymize page
  - `--input` path field on Project Generator page
  - `--include-images` checkbox on Project Generator page
  - `dossier-check` workflow added to LLM Workflow dropdown
  - `level` setting on Config page (persistent default)
  - Workflows sorted by 5+2 step order (1→2→3→5→Wachtdienst→Dossier-Check)
  - Removed hardcoded `test_output/` default paths

---

## [0.6.2] — 2026-03-25

### Added
- **US-15.W2: BdL Workflow** — `milanon pack --workflow bdl` for AUGEZ factor analysis (Step 2 of 5+2)
- **US-15.W3: Entschluss Workflow** — `milanon pack --workflow entschluss` for variant generation + Absicht (Step 3 of 5+2)
- **6 BFE Skeleton Templates** from official Swiss Army forms:
  - `010_problemerfassung.md` — IST/SOLL problem analysis matrix (BFE 5.1.2)
  - `011_leistungsprofil_ppqqzd.md` — Priorität/Produkt/Quantität/Qualität/Zeitpunkt/Dauer (BFE 5.1)
  - `024_abspracherapport.md` — 33-point coordination meeting checklist (BFE 5.4)
  - `025_mittelbedarfsrechnung.md` — Resource request table for Bat (BFE 5.4/5.6)
  - `060_einh_rap_einsatz.md` — 32-point company rapport checklist (BFE Kap 4)
  - `505_rze.md` — Rasch zusammengestellter Einsatzbefehl / one-page emergency format (BFE 5.7)
- **Wachtdienst Skeleton enriched** with BFE Vorlage detail:
  - Posten-specific tables (Einsatzort/Einsatztätigkeit/Einsatzverhalten per post)
  - Schusswaffengebrauch section (WAT 51.301)
  - Bedrohungsstufen ALPHA/BRAVO/CHARLIE/DELTA
  - Wachtübergabe/-ablösung timing table

---

## [0.6.1] — 2026-03-25

### Fixed
- **FR-004: DOCX Writer Rewrite** — Complete rewrite using official CH Armee `befehl_vorlage.docx` as template
  - BUG-005: `**bold**` and `*italic*` now render as proper DOCX formatting runs
  - BUG-006: `---` horizontal rules become page breaks (no empty paragraphs)
  - BUG-007: HTML comments (`<!-- FILL: -->`, `<!-- KDT ENTSCHEID: -->`) fully stripped
  - BUG-008: `> blockquotes` rendered as italic Text Indent
  - BUG-009: Multi-column tables (2, 3, 4+ columns) fully supported
  - BUG-010: Paragraph spacing handled by template styles (no empty paragraphs)
  - BUG-011: All table types handled uniformly (Aufträge, Akteure, Standorte)
  - Style mapping: `#`→Heading 1, `##`→Subject heading, `###`→1. Main title, `####`→1.1 Title, `#####`→1.1.1 Title
  - Inline: bold/italic/code parsed into separate Runs
  - 25 new DOCX writer tests (730 total)

---

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
