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

## Iteration 4 — Output Quality

## B-013: Mega-Cell Visual Detection (P1) 🔴

**Commit:** `fix(parser): detect mega-cell visual layouts (organigramm, gliederung)`

## B-014: Remove Empty Columns from PDF Tables (P1) 🔴

**Commit:** `feat(parser): strip empty columns from PDF table extraction`

## B-022: EML Display Names Not Anonymized (P1) 🔴

**Commit:** `feat(recognition): anonymize display names in EML From/To/Cc/Bcc headers`

---

## Iteration 7 — De-Anonymization Quality

## B-023: De-Anonymize Filenames (P1) 🔴

**Commit:** `feat(deanonymize): resolve placeholders in output filenames`

## B-024: Obsidian Wiki-Link Compatibility (P1) 🔴

**Commit:** `feat(deanonymize): handle Obsidian wiki-links with proper alias format`

## B-025: In-Place De-Anonymization (P2) 🔴

**Commit:** `feat(deanonymize): add --in-place flag for direct vault de-anonymization`

---

## Iteration 8 — GUI Enhancements

## B-026: Embed Images Checkbox on Anonymize Page (P1) 🔴

**Commit:** `feat(gui): add embed-images checkbox to Anonymize page`

## B-027: LLM Workflow Page (P1) 🔴

**Commit:** `feat(gui): add LLM Workflow page with context generator, instructions, and unpack`

---

## Iteration 9 — Military Reference Data Consolidation (Epic E13)

## B-028: Consolidate Redundant Data Files (P1) 🔴

**Discovered in:** Data audit (2026-03-25)

**Problem:** Three redundant data sources exist, two of which are dead:

| Source | Lines of code | Used by | Status |
|---|---|---|---|
| `data/military_units.csv` | 59 rows | `init_reference_data.py` → SQLite | **Dead data** — loaded into `ref_military_units` but NEVER queried |
| `data/swiss_military_ranks.md` | 120 lines | Nobody | **Dead data** — pure Markdown documentation |
| `src/milanon/config/military_patterns.py` | Hardcoded lists | `PatternRecognizer` + `MilitaryRecognizer` | **Actual source of truth** |

The same ranks, branches, and functions are maintained in 3 places with no sync mechanism.

**Required Fix:**

1. **Delete** `data/swiss_military_ranks.md` — replace with a one-line deprecation notice pointing to the CSV.

2. **Extend** `data/military_units.csv` with two new columns:
   - `parent` — full_name of the parent unit (empty for non-concrete entries)
   - `level` — organizational level: `command`, `division`, `brigade`, `battalion`, `company`, `platoon` (empty for rank/branch/function/unit_pattern entries)

3. **Verify** that all entries in `military_patterns.py` hardcoded lists are also present in the CSV:
   - All RANK_ABBREVIATIONS → type=rank rows in CSV
   - All BRANCH_ABBREVIATIONS → type=branch rows in CSV
   - All FUNCTION_ABBREVIATIONS → type=function rows in CSV
   - Add any missing entries to the CSV

4. **Ensure backward compatibility:** `military_patterns.py` hardcoded lists stay untouched in this phase. The CSV is extended but the Python code doesn't read from it yet.

5. **Update** `init_reference_data.py` to parse the new `parent` and `level` columns when loading into SQLite.

6. **Extend** SQLite schema for `ref_military_units`:
   ```sql
   -- Add columns (migration-safe: ALTER TABLE ADD COLUMN)
   ALTER TABLE ref_military_units ADD COLUMN full_name TEXT DEFAULT '';
   ALTER TABLE ref_military_units ADD COLUMN abbreviation TEXT DEFAULT '';
   ALTER TABLE ref_military_units ADD COLUMN level TEXT DEFAULT '';
   ALTER TABLE ref_military_units ADD COLUMN parent_unit_name TEXT DEFAULT '';
   ALTER TABLE ref_military_units ADD COLUMN category TEXT DEFAULT '';
   ```

**Acceptance Criteria:**
- Given the repo, when `data/swiss_military_ranks.md` is checked, then it contains only a deprecation notice.
- Given the CSV, when opened, then it has `parent` and `level` columns (may be empty for non-concrete entries).
- Given all entries in `military_patterns.py` RANK_ABBREVIATIONS, when compared to CSV type=rank rows, then every abbreviation is present in both.
- Given `milanon db init`, when run, then `ref_military_units` table contains all CSV rows including the new columns.
- Given existing tests, when `pytest tests/` runs, then all 480+ tests pass (backward compatible).

**Commit:** `refactor(data): consolidate military reference files, extend CSV schema with parent/level`

---

## B-029: Load Recognizer Lists from DB Instead of Hardcoded (P1) 🔴

**Discovered in:** Data audit (2026-03-25)

**Problem:** `military_patterns.py` contains hardcoded Python lists (RANK_ABBREVIATIONS, BRANCH_ABBREVIATIONS, FUNCTION_ABBREVIATIONS) that duplicate the CSV data. When a new rank or branch is added to the CSV, the Python file must also be manually updated — they will inevitably drift.

**Required Fix:**

1. **New function** in `military_patterns.py`:
   ```python
   def _load_from_csv() -> tuple[list[str], list[str], list[str]]:
       """Load rank, branch, function abbreviations from military_units.csv.
       Returns (ranks, branches, functions) sorted longest-first."""
   ```

2. **Replace** the hardcoded RANK_ABBREVIATIONS, BRANCH_ABBREVIATIONS, FUNCTION_ABBREVIATIONS with calls to `_load_from_csv()`. Fall back to hardcoded defaults if CSV is not found (for test isolation).

3. **Keep PII patterns hardcoded** — AHV_PATTERN, PHONE_*, EMAIL_PATTERN, ADRESSE_PATTERN, INITIAL_SURNAME_PATTERN are structural patterns, not reference data. They stay in Python.

4. **Rebuild compiled patterns** from the loaded lists: UNIT_PATTERN, TER_DIV_PATTERN, RANK_NAME_PATTERN must be re-compiled from the CSV-sourced lists.

5. **Performance:** Load once at module import time (same as today). No per-document DB queries.

**Key constraint:** The CSV is the source, not the DB. This keeps the module self-contained and testable without a DB connection. The DB is for runtime queries (generate_context, etc.), the CSV is for pattern compilation.

**Acceptance Criteria:**
- Given a new rank "Oberstbrigadier" added to CSV but NOT to the Python file, when the module loads, then the new rank is included in RANK_ABBREVIATIONS and RANK_NAME_PATTERN.
- Given the CSV does not exist (e.g. in unit tests), when the module loads, then it falls back to hardcoded defaults and all existing tests pass.
- Given the module loads, when RANK_ABBREVIATIONS is inspected, then it is sorted longest-first (for longest-match-first regex).
- Given all 480+ existing tests, when run, then they all pass.

**Commit:** `refactor(patterns): load rank/branch/function lists from CSV instead of hardcoded`

---

## B-030: Add Concrete Swiss Army Formations to CSV (P1) 🔴

**Discovered in:** Wikipedia analysis + WK25 Dossier (2026-03-25)

**Problem:** The tool has no knowledge of actual Swiss Army formations. It recognizes "Inf Bat 56" only via generic regex pattern (`Inf + Bat + Number`), not as a known entity. It doesn't know that Inf Bat 56 belongs to Ter Div 2, or that it has 5 companies (Stabskp 56, Kp 56/1-3, Ustü Kp 56/4).

**Data source:** [Wikipedia: Gliederung der Schweizer Armee](https://de.wikipedia.org/wiki/Gliederung_der_Schweizer_Armee) — public information, 2026 structure.

**Required Fix:**

Add `type=concrete_unit` rows to `military_units.csv` with `parent` and `level` columns:

**Top-level commands:**
```csv
concrete_unit,Kommando Operationen,Kdo Op,Kommando,,_root,command
concrete_unit,Kommando Ausbildung,Kdo Ausb,Kommando,,_root,command
concrete_unit,Logistikbasis der Armee,LBA,Kommando,,_root,command
concrete_unit,Kommando Cyber,Kdo Cyber,Kommando,,_root,command
```

**Heer + Mechanisierte Brigaden:**
```csv
concrete_unit,Heer,Heer,Kommando,,Kommando Operationen,command
concrete_unit,Mechanisierte Brigade 1,Mech Br 1,Brigade,,Heer,brigade
concrete_unit,Mechanisierte Brigade 4,Mech Br 4,Brigade,,Heer,brigade
concrete_unit,Mechanisierte Brigade 11,Mech Br 11,Brigade,,Heer,brigade
```

**All 4 Territorialdivisionen + their Bataillone:**
```csv
concrete_unit,Territorialdivision 2,Ter Div 2,Division,,Kommando Operationen,division
concrete_unit,Infanteriebataillon 56,Inf Bat 56,Bataillon,,Territorialdivision 2,battalion
```

**All 8 Inf Bat with standard 5er-structure (0-4):**
Each Inf Bat gets: Stabskp (=0), Kp 1, Kp 2, Kp 3, Ustü Kp (=4).
Inf Bat: 11, 13, 19, 20, 56, 61, 65, 97.

```csv
concrete_unit,Infanterie Stabskompanie 56,Inf Stabskp 56,Kompanie,Stabskp 56,Infanteriebataillon 56,company
concrete_unit,Infanteriekompanie 56/1,Inf Kp 56/1,Kompanie,,Infanteriebataillon 56,company
concrete_unit,Infanteriekompanie 56/2,Inf Kp 56/2,Kompanie,,Infanteriebataillon 56,company
concrete_unit,Infanteriekompanie 56/3,Inf Kp 56/3,Kompanie,,Infanteriebataillon 56,company
concrete_unit,Infanterie Unterstützungskompanie 56/4,Inf Ustü Kp 56/4,Kompanie,,Infanteriebataillon 56,company
```

**Luftwaffe, LBA, Kdo Cyber:**
Key brigades and battalions.

**Target: ~100-120 rows** of concrete_unit entries covering the complete Swiss Army structure at brigade level and below for the Heer, plus all Inf Bat companies.

**Acceptance Criteria:**
- Given the CSV, when all concrete_unit rows are counted, then there are 100+ entries.
- Given "Inf Bat 56" in the CSV, when its children are queried, then 5 companies are returned (Stabskp 56, Kp 56/1-3, Ustü Kp 56/4).
- Given "Ter Div 2", when its children are queried, then Inf Bat 11, 20, 56, 97 + Genie Bat 6 + Rttg Bat 2 are returned.
- Given `milanon db init --force`, when run, then all concrete_unit entries are in the DB with correct parent references.
- Given existing tests, when run, then they all pass.

**Commit:** `feat(data): add ~100 concrete Swiss Army formations with hierarchy to reference CSV`

---

## B-031: Hierarchy-Aware Context Generator + Improved Recognition (P1) 🔴

**Discovered in:** Data audit + LLM Context analysis (2026-03-25)

**Problem:** Two systems need upgrading to use the new hierarchy data:

**A) Context Generator (`generate_context.py`):**
Currently uses `_parent_number()` heuristic (slash-notation: "56/1" → parent "56"). This breaks for:
- Formations without slash (Ter Div 2 → parent is Kdo Op, not guessable from the name)
- Stabskp (56/0 pattern not used in all documents)
- Cross-level references (what Bat belongs to which Div)

With DB hierarchy: Full chain resolution `Kdo Op → Ter Div 2 → Inf Bat 56 → Inf Kp 56/1` directly from the `ref_military_units` table.

**B) Military Recognizer (`military_recognizer.py`):**
Currently only matches generic patterns. With concrete_unit data in the DB, it could:
- Match known unit names with higher confidence (1.0 vs 0.9 for pattern match)
- Recognize units that don't follow standard patterns (e.g. "Geb Inf Bat 29")
- Provide richer metadata in DetectedEntity

**Required Fix:**

**Part A — Context Generator:**
1. New method in `SqliteMappingRepository`:
   ```python
   def get_unit_hierarchy(self, unit_abbreviation: str) -> list[dict]:
       """Return the parent chain from the given unit up to root.
       Returns list of dicts with keys: full_name, abbreviation, level, parent."""
   
   def get_unit_children(self, parent_full_name: str) -> list[dict]:
       """Return direct children of a unit."""
   
   def get_unit_siblings(self, unit_full_name: str) -> list[dict]:
       """Return sibling units (same parent)."""
   ```

2. `generate_context.py` uses these methods to build a rich hierarchy section:
   ```markdown
   ## Organizational Hierarchy
   
   Command chain: Kdo Op → Ter Div 2 → Inf Bat 56 → **Inf Kp 56/1** (YOUR UNIT)
   
   Sibling companies (same Bat):
   | Placeholder | Unit | Type |
   |---|---|---|
   | [EINHEIT_009] | Stabskp 56 | Staff Company |
   | **[EINHEIT_001]** | **Inf Kp 56/1** | **← YOUR UNIT** |
   | [EINHEIT_008] | Inf Kp 56/2 | Company |
   | [EINHEIT_007] | Inf Kp 56/3 | Company |
   | [EINHEIT_006] | Ustü Kp 56/4 | Support Company |
   
   Sister battalions (same Ter Div):
   Inf Bat 11, Inf Bat 20, Inf Bat 97, G Bat 6, Rttg Bat 2
   ```

3. Falls back gracefully: If no hierarchy data in DB (old DB without B-030), use existing slash-heuristic.

**Part B — Enhanced Recognition (optional, can be deferred):**
1. After pattern-based recognition, check matched unit text against `ref_military_units` concrete entries.
2. If exact match found: boost confidence to 1.0 and add metadata (level, parent).
3. If no match but pattern matches: keep existing confidence (0.9).
4. New recognizer: scan for concrete unit abbreviations not caught by generic patterns.

**Acceptance Criteria:**
- Given "Inf Kp 56/1" as the user's unit and hierarchy data in DB, when context is generated, then the output includes the full command chain and sibling companies.
- Given a unit with no hierarchy data in DB, when context is generated, then it falls back to slash-heuristic (backward compatible).
- Given "Ter Div 2" in document text, when recognition runs, then it is detected with confidence 1.0 (exact match) instead of 0.9 (pattern).
- Given all existing tests, when run, then they pass.

**Commit:** `feat(context): hierarchy-aware context generation from DB + enhanced unit recognition`

---

## Iteration 3 — Self-Improving Recognition

## B-010: Post-Anonymization Review (P2) 🔴

**Commit:** `feat(review): add post-anonymization review for unknown name candidates`

---

## Iteration 5 — EINHEIT Alias System

## B-018: Military Unit Alias Table (P2) 🔴

**Commit:** `feat(mapping): military unit alias table for duplicate EINHEIT resolution`

---

## Iteration 6 — Incremental Processing Improvements

## B-019: Clean Up Orphaned Output Files (P2) 🔴
## B-020: Entity Count Total Across All Outputs (P3) 🔴
## B-021: Detect Renamed Files via Content Hash (P3) 🔴

---

## Iteration 4b — Recognition Gaps

## B-015: International Phone Numbers (P2) 🔴
## B-016: c/o Name Detection in Address Fields (P2) 🔴
## B-017: Near-AHV Warning for Transposed Digits (P3) 🔴

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
- **B-108**: CLI UX polish — Kali-Linux-style terminal output
