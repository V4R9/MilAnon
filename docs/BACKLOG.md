# MilAnon — Post-MVP Backlog

> Items for iteration after MVP completion.
> Priority: P0 (critical), P1 (next), P2 (soon), P3 (later)
> Status: 🔴 Open, 🟡 In Progress, ✅ Done

---

## Iteration 1 — Done ✅

- B-007: PDF Tables as Markdown ✅
- B-004: Initial.NACHNAME Pattern ✅
- B-005: Municipality Stopwords ✅
- B-006: GEBURTSDATUM context-only ✅
- B-001: GUI Database Reset ✅
- B-002: Documentation Cleanup ✅
- B-003: Real-World Verification ✅

---

## Iteration 2 — Done ✅

- B-008: Generic Name CSV Import ✅
- B-009: Quick-Add Names in GUI ✅

---

## Iteration 2b — Done ✅

- B-008-fix: Combined "Name / Vorname" column format ✅
- B-011: Visual PDF page detection + optional image embed ✅
- "Alle" municipality completely excluded from matching ✅
- "Adj" added as standalone rank ✅
- Per-file progress output in CLI ✅
- Version number in GUI sidebar ✅
- CSV delimiter auto-detection (csv.Sniffer) ✅

---

## Iteration 2c — Done ✅

- B-011-fix: --embed-images rendering PNGs ✅
- B-012: LLM Context Generator with interactive unit selection ✅
- B-012-fix: EINHEIT duplicate normalization + Context output path ✅
- B-011-fix2: Visual page heuristic tightened (AND logic) ✅
- Code Review: All 14 findings addressed (refactoring) ✅

---

## Iteration 4 — Output Quality — Done ✅ (2026-03-25)

- B-013: Mega-Cell Visual Detection (Organigramm/Gliederung >500 chars) ✅
- B-014: Remove Empty Columns from PDF Tables (15→5 cols) ✅
- B-022: EML Display Names anonymized (From/To/Cc/Bcc headers) ✅

---

## Iteration 7 — De-Anonymization Quality — Done ✅ (2026-03-25)

- B-023: De-Anonymize Filenames ([PERSON_005].md → Brüngger_Xenia.md) ✅
- B-024: Obsidian Wiki-Link Compatibility ([[PERSON_005]] → [[Brüngger_Xenia|Xenia BRÜNGGER]]) ✅
- B-025: In-Place De-Anonymization (--in-place flag with .milanon_backup/) ✅

---

## Iteration 8 — GUI Enhancements — Done ✅ (2026-03-25)

- B-026: Embed Images Checkbox on Anonymize Page ✅
- B-027: LLM Workflow Page (3 tabs: Pack, Work with LLM, Unpack) ✅

---

## Iteration 9 — Military Reference Data (Epic E13) — Done ✅ (2026-03-25)

- B-028: Consolidate Redundant Data Files (swiss_military_ranks.md deprecated, CSV extended with parent/level) ✅
- B-029: CSV as Source of Truth (military_patterns.py reads from CSV, fallback to hardcoded) ✅
- B-030: Concrete Swiss Army Formations (~100 units with hierarchy: Kdo Op → Ter Div → Bat → Kp) ✅
- B-031: Hierarchy-Aware Context Generator (full command chain, siblings, children from DB) ✅

---

## Iteration 10 — Self-Improving Recognition — Done ✅ (2026-03-25)

- B-010: Post-Anonymization Review Loop (scan for ALLCAPS/Titlecase candidates, interactive confirmation, auto-add to DB) ✅
- CLI: `milanon review` command with --auto-add and --dry-run flags ✅

---

## Iteration 11 — LLM Workflow Automation (Epic E10) — Done ✅ (2026-03-25)

- E10.1: Pack CLI (`milanon pack --template obsidian-notes --input anon/ --unit "Inf Kp 56/1"`) ✅
- E10.2: Templates (4 built-in: obsidian-notes, befehl-entwurf, analyse, frei + custom ~/.milanon/templates/) ✅
- E10.3: Unpack CLI (`milanon unpack --clipboard --output vault/` with split support) ✅
- E10.4: GUI Integration (Pack Builder + Unpack in LLM Workflow page) ✅

---

## Documentation & Polish — Done ✅ (2026-03-25)

- Version bump 0.1.0 → 0.3.0 ✅
- CHANGELOG.md v0.3.0 section ✅
- README.md updated (all CLI commands, features, Git URL) ✅
- CLAUDE.md updated ✅
- SESSION_HANDOVER.md created ✅
- CLI colored output + ref data in db stats ✅
- Stale files cleaned up ✅

---

## Still Open 🔴

## Iteration 5 — EINHEIT Alias System

## B-018: Military Unit Alias Table (P2) 🔴

**Problem:** Multiple placeholders for same unit due to naming variants ("Inf Ustü Kp 56/4" vs "Inf Ustü Kp 56"). With E13 hierarchy data now in the DB, this could leverage the parent-child relationships for automatic alias resolution.

**Commit:** `feat(mapping): military unit alias table for duplicate EINHEIT resolution`

---

## Iteration 6 — Incremental Processing Improvements

## B-019: Clean Up Orphaned Output Files (P2) 🔴

`--clean` flag to remove output files whose source input was deleted/renamed.

## B-020: Entity Count Total Across All Outputs (P3) 🔴

Show total entity count across all tracked files, not just current batch.

## B-021: Detect Renamed Files via Content Hash (P3) 🔴

Reuse existing output when a file is renamed but content is identical.

---

## Iteration 4b — Recognition Gaps

## B-015: International Phone Numbers (P2) 🔴

Generic pattern for +49, +33, +43 etc. At least one German number found in real-world test.

## B-016: c/o Name Detection in Address Fields (P2) 🔴

"c/o Walter Fanger" pattern → PERSON entity with confidence 0.8.

## B-017: Near-AHV Warning for Transposed Digits (P3) 🔴

Detect 765.xxxx.xxxx.xx (transposed 756) and emit warning without anonymizing.

---

## Epic E10 — Remaining Items

## E10.5: Update Template — Preserve User Edits (P2) 🔴

Template that instructs Claude to merge updated data with existing vault content without losing manual edits. Critical for the Round-Trip workflow.

---

## Future Ideas (P3)

- **B-100**: NLP-based entity recognition (spaCy) for unknown names
- **B-101**: Fuzzy matching for typos
- **B-102**: Image OCR in DOCX/PDF for embedded text
- **B-103**: Manual entity management — edit/delete via GUI
- **B-104**: Reporting & Audit trail
- **B-105**: Import summary with delta info
- **B-106**: GUI Finder dialog for folder/file selection (tkinter.filedialog)
- **B-107**: --exclude pattern for anonymize
- **B-108**: CLI UX polish — ASCII banner, Kali-style terminal
