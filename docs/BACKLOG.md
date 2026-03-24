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

## Iteration 4 — Output Quality (from MD Analysis 2026-03-24)

## B-013: Organigramm/Gliederung Pages — Mega-Cell Visual Detection (P1) 🔴

**Discovered in:** Real-world test MD analysis (2026-03-24)

**Problem:** The Organigramm Stab (page ~68) and Gliederung (page ~67) are visual layouts (org charts with boxes and connection lines), but the current visual detection heuristic does NOT flag them because:
- The extracted table has only **3 columns** (below the >20 threshold)
- However, one cell contains **1000+ characters** of garbled content — all the org chart boxes mashed into a single cell

The result is an unreadable wall of placeholders:
```
[GRAD_FUNKTION_008] [GRAD_FUNKTION_009] A CIARDO [PERSON_176] KdtL InfBat 11 
[FUNKTION_001] (a i) (1.1.2026) [GRAD_FUNKTION_009] [GRAD_FUNKTION_008]...
```

**Root Cause:** The heuristic only checks column count + empty cell percentage. It doesn't detect "mega-cells" — single cells with hundreds of characters of garbled content from visual layouts.

**Required Fix:**

Add a third condition to `_is_visual_layout()` in `pdf_parser.py`:
```
A page is visual layout when ANY of:
  (a) >20 columns AND >70% empty cells (existing — catches WAP/Picasso)
  (b) ANY single cell contains >500 characters (new — catches Organigramm)
```

When condition (b) triggers:
- Same behavior as existing visual detection: skip table extraction, insert marker, optionally embed as PNG.

**Acceptance Criteria:**
- Given a PDF page with an org chart where one cell contains >500 chars of garbled content, when parsed, then it is detected as visual layout.
- Given a normal data table where the longest cell has <200 chars, when parsed, then it is NOT detected as visual layout.
- Given the Organigramm Stab page, when --embed-images is used, then the page is rasterized as PNG instead of producing garbled text.

**Commit:** `fix(parser): detect mega-cell visual layouts (organigramm, gliederung)`

---

## B-014: Remove Empty Columns from PDF Tables (P1) 🔴

**Discovered in:** Real-world test MD analysis (2026-03-24)

**Problem:** The Dokumentenbudget table has 5 actual columns (Dok, Titel, Dokument, Wer, Status), but pdfplumber extracts 15 columns because of merged cells and invisible column separators. The extra columns are completely empty in every row:
```
| | Dok | | | Titel | | | Dokument | | | Wer | | | Status | |
```

This is readable but unnecessarily wide and noisy.

**Required Fix:**

Post-processing step in `_table_to_markdown()` or `_extract_with_tables()` in `pdf_parser.py`:
1. After extracting a table, check each column index.
2. If a column is empty (or only whitespace) in EVERY row including header → remove it.
3. Apply before rendering to Markdown.

```python
def _remove_empty_columns(table: list[list[str]]) -> list[list[str]]:
    if not table:
        return table
    num_cols = max(len(row) for row in table)
    keep = [
        col_idx for col_idx in range(num_cols)
        if any(
            col_idx < len(row) and (row[col_idx] or "").strip()
            for row in table
        )
    ]
    return [[row[i] if i < len(row) else "" for i in keep] for row in table]
```

**Acceptance Criteria:**
- Given a table with 15 columns where 10 are empty in all rows, when processed, then the Markdown table has only 5 columns.
- Given a table where all columns have at least one non-empty cell, when processed, then no columns are removed.
- Given a table with a header row where a column header is empty but data cells below are not, when processed, then the column is preserved.

**Commit:** `feat(parser): strip empty columns from PDF table extraction`

---

## B-015: International Phone Numbers (P2) 🔴

**Discovered in:** Real-world test MD analysis (2026-03-24)

**Problem:** The current TELEFON patterns only match Swiss phone numbers (+41 and 0xx prefixes). International numbers are not caught:
```
+49 157 86 08 12 32    ← German number, not anonymized
+4915786081232          ← Same number compact, not anonymized
```

In the Befehlsdossier Adressliste, at least one person has a German mobile number.

**Required Fix:**

Add international phone patterns to `config/military_patterns.py`:

Option A — Generic international pattern:
```python
PHONE_INTL_GENERIC_PATTERN = re.compile(
    r"\+\d{2}[\s\-]?\d{2,3}[\s\-]?\d{2,3}[\s\-]?\d{2}[\s\-]?\d{2}[\s\-]?\d{0,2}\b"
)
```

Option B — Specific patterns for common countries (DE, AT, FR, IT):
```python
PHONE_DE_PATTERN = re.compile(r"\+49[\s\-]?\d{2,4}[\s\-]?\d{2,}[\s\-]?\d{2}[\s\-]?\d{2}\b")
```

Recommend Option A — generic catch-all for any international number starting with +.

**Acceptance Criteria:**
- Given text containing "+49 157 86 08 12 32", when recognition runs, then it is detected as TELEFON.
- Given text containing "+4915786081232" (compact), when recognition runs, then it is detected as TELEFON.
- Given existing Swiss numbers (+41, 079), when recognition runs, then they are still correctly detected (no regression).
- Given text containing "+1 800 555 1234" (US toll-free), when recognition runs, then it is detected as TELEFON.

**Commit:** `feat(recognition): detect international phone numbers beyond Swiss +41`

---

## B-016: c/o Name Detection in Address Fields (P2) 🔴

**Discovered in:** Real-world test MD analysis (2026-03-24)

**Problem:** When a person's address contains "c/o [Name]", the name inside the address is not anonymized:
```
c/o Walter Fanger / [ADRESSE_016]
```

"Walter Fanger" is a person's name embedded in an address field. The Adressliste parser correctly anonymized the street address but not the c/o recipient.

**Root Cause:** The PatternRecognizer has no pattern for c/o names, and the ListRecognizer only matches names that are in the DB. "Walter Fanger" might not be in the DB if he's not in the PISA export (he could be a relative at the same address).

**Required Fix:**

New pattern in `PatternRecognizer` or as a post-processing step:
```python
# c/o + Titlecase Firstname + Titlecase/ALLCAPS Lastname
CO_NAME_PATTERN = re.compile(
    r"(?:c/o|p\.A\.|bei)\s+([A-ZÄÖÜ][a-zäöüé]+\s+[A-ZÄÖÜ][a-zäöüÄÖÜé]+)"
)
```

Detected names are flagged as PERSON entities with confidence 0.8.

**Acceptance Criteria:**
- Given text "c/o Walter Fanger", when recognition runs, then "Walter Fanger" is detected as PERSON.
- Given text "p.A. Maria Schmidt", when recognition runs, then "Maria Schmidt" is detected as PERSON.
- Given text "c/o Firma XY AG", when recognition runs, then "Firma XY AG" is NOT detected as PERSON (company names don't match Firstname Lastname pattern).

**Commit:** `feat(recognition): detect person names in c/o address prefixes`

---

## B-017: Near-AHV Warning for Transposed Digits (P3) 🔴

**Discovered in:** Real-world test MD analysis (2026-03-24)

**Problem:** One AHV number in the Adressliste was extracted as `765.4056.6550.18` — this starts with `765` instead of the correct `756`. It could be a typo in the original document or an OCR error. The AHV pattern only matches `756.xxxx.xxxx.xx` and correctly ignores this.

However, a transposed `765` is very likely a real AHV number with a data entry error. It would be useful to warn the user.

**Required Fix:**

In `PatternRecognizer._match_birthdates` or as a separate scan, add a "near-AHV" detector:
```python
NEAR_AHV_PATTERN = re.compile(r"\b(?:756|765|675)\.\d{4}\.\d{4}\.\d{2}\b")
```

When a near-AHV is found that doesn't match the strict `756.` prefix:
- Do NOT anonymize it (it might be something else)
- Add a warning: "Possible AHV with transposed digits: 765.4056.6550.18 on page X"

**Acceptance Criteria:**
- Given text "765.4056.6550.18", when recognition runs, then a warning is emitted but the number is NOT anonymized.
- Given text "756.1234.5678.97" (correct), when recognition runs, then it IS anonymized as AHV_NR.
- Given text "123.4567.8901.23" (clearly not AHV), when recognition runs, then no warning is emitted.

**Commit:** `feat(recognition): warn on possible AHV numbers with transposed digits`

---

## Iteration 3 — Self-Improving Recognition

## B-010: Post-Anonymization Review — Learn Unknown Names (P2) 🔴

**As a** commander, **I want** the tool to show me suspicious words that might be names after anonymization, **so that** I can confirm them and the tool learns for next time.

**Problem:** The Adressliste Stab contains 20+ names not in any import list. After anonymization, these leak in cleartext:
- Ciardo, Adrian — not in CSV import
- Koch, Fanger, Müller, Tribelhorn, Merisi, Schneeberger, Sarasin, Storrer, Greco, Dürst, Megevand — all Bat Stab personnel not covered by the 21-person CSV

The tool currently has no way to flag these. The user must manually read the entire output to find leaks.

**Solution:** After anonymization, scan the output for candidate names:
1. ALLCAPS words (≥3 chars) not in known exclusion lists (military abbreviations, Ortschaften)
2. Title-case words near rank abbreviations that weren't caught
3. Title-case words in personnel-context sections (near phone numbers, email addresses)

Present candidates to user. Confirmed → added to DB. Rejected → exclusion list.

**GUI interaction:**
```
⚠ Possible names found (not anonymized):
☐ DÜRST (appears 2x, near rank abbreviations)
☐ Ciardo (appears 2x, in organigramm context)  
☐ Koch (appears 1x, in adressliste)
☐ Fanger (appears 3x, in adressliste + address field)
☐ Tribelhorn (appears 1x)
```

**CLI interaction:** `milanon anonymize --review` flag → interactive prompts after processing.

**Why this matters:** Every run makes the tool smarter. After 2-3 runs with review, the DB covers virtually all personnel. This is the most sustainable path to high recall.

**Commit:** `feat(review): add post-anonymization review for unknown name candidates`

---

## Iteration 5 — EINHEIT Alias System

## B-018: Military Unit Alias Table (P2) 🔴

**Discovered in:** EINHEIT analysis (2026-03-24)

**Problem:** Multiple placeholders map to the same real unit due to different writing styles in the document:
- EINHEIT_006 = "Inf Ustü Kp 56/4" and EINHEIT_013 = "Inf Ustü Kp 56" → same unit
- EINHEIT_009 = "Inf Stabskp 56" and EINHEIT_012 = "Inf Kp 56/0" → same unit (Stabskp = 56/0)
- EINHEIT_016 = "Inf Kp 56" → doesn't exist, likely a parsing artefact or abbreviation for the battalion's organic units

These are not whitespace/newline duplicates (those were fixed). These are **military naming aliases** — different valid names for the same organizational unit.

**Required Fix:**

New table `unit_aliases` in SQLite schema:
```sql
CREATE TABLE IF NOT EXISTS unit_aliases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    canonical_mapping_id INTEGER REFERENCES entity_mappings(id),
    alias_value TEXT NOT NULL,
    normalized_alias TEXT NOT NULL,
    UNIQUE(normalized_alias)
);
```

Domain knowledge rules (configurable in `config/military_patterns.py`):
- "Ustü Kp XX/4" = "Ustü Kp XX" (with or without /4)
- "Stabskp XX" = "Kp XX/0" (Stabskompanie = /0)
- When creating a new EINHEIT mapping, check if an alias exists → use canonical placeholder

**Acceptance Criteria:**
- Given "Inf Ustü Kp 56/4" already in DB, when "Inf Ustü Kp 56" is encountered, then it maps to the same placeholder.
- Given "Inf Stabskp 56" already in DB, when "Inf Kp 56/0" is encountered, then it maps to the same placeholder.
- Given "Inf Kp 56/1" and "Inf Kp 56/2", when both encountered, then they remain separate (different sub-units).

**Commit:** `feat(mapping): military unit alias table for duplicate EINHEIT resolution`

---

## Future Ideas (P3)

- **B-100**: NLP-based entity recognition (spaCy) for unknown names
- **B-101**: Fuzzy matching for typos
- **B-102**: Image OCR in DOCX/PDF for embedded text
- **B-103**: Manual entity management — edit/delete via GUI
- **B-104**: Reporting & Audit trail
- **B-105**: Import summary with delta info
- **B-106**: GUI Finder dialog for folder/file selection (tkinter.filedialog) — replace manual path copy-paste
- **B-107**: --exclude pattern for anonymize (e.g. `--exclude "Personel Lists"`) — skip folders/files matching pattern
- **B-108**: CLI UX polish — Kali-Linux-style terminal output (ASCII banner, colored sections, icons, clear summary blocks via click.style)
