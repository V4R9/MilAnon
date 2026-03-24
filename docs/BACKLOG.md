# MilAnon — Post-MVP Backlog

> Items for iteration after MVP completion.
> Priority: P0 (critical), P1 (next), P2 (soon), P3 (later)
> Status: 🔴 Open, 🟡 In Progress, ✅ Done

---

## Iteration 1 — Done ✅

## B-007: PDF Tables Must Render as Markdown Tables (P0) ✅

**Commit:** `feat(parser): extract PDF tables as Markdown table syntax`

## B-004: Name Leaks — Initial.NACHNAME Pattern (P0) ✅

**Commit:** `fix(recognition): detect initial+surname patterns like D. MUFFLER`

## B-005: Municipality "Alle" False Positive (P1) ✅

**Commit:** `fix(recognition): add municipality stopword list to prevent false positives`

## B-006: All Dates Flagged as GEBURTSDATUM (P1) ✅

**Commit:** `fix(recognition): restrict GEBURTSDATUM to personnel context only`

## B-001: GUI Database Reset (P1) ✅

**Commit:** `feat(db): add database reset with GUI and CLI support`

## B-002: Documentation Cleanup (P1) ✅

**Commit:** `docs: update all documentation for current state`

## B-003: Real-World Verification Test ✅

Tested 2026-03-24. Results: 22 files, 0 errors, 1457 entities. Markdown tables working (665 rows). "Alle" FP: 0. GEBURTSDATUM FP: 0. Name leaks: 3 (DÜRST, CIARDO, Schegg — all Bat Stab, not in PISA). EML anonymization clean.

---

## Iteration 2 — Next (by end of March)

## B-008: Generic Name CSV Import for Bat Stab / External Personnel (P1) 🔴

**As a** commander, **I want to** import a simple name list (Grad, Vorname, Nachname) from a CSV, **so that** I can pre-load Bat Stab, Div Stab, and other external personnel not covered by my PISA 410 export.

**Problem:** PISA 410 only covers the commander's own unit (~150 people). The Befehlsdossier contains names from the entire battalion staff, division staff, and attached units — people NOT in the PISA export. These names leak through anonymization.

**Format:** Simple 3-column CSV (semicolon-separated, UTF-8):
```
Grad;Vorname;Nachname
Oberstlt i Gst;Thomas;Wegmüller
Hptm;Simon;Kohler
Maj;Roger;Siegrist
Stabsadj;Thomas;Uhlmann
```

### Acceptance Criteria

- Given a 3-column CSV with Grad/Vorname/Nachname, when imported via `milanon db import --format names`, then each row creates PERSON, VORNAME, NACHNAME, and GRAD_FUNKTION mappings.
- Given the GUI "DB Import" page, when "Simple Name List" format is selected and a CSV uploaded, then the import runs and shows a summary.
- Given a name already in the DB (from PISA), when the same name appears in the name CSV, then no duplicate is created.
- Given the Bat Stab Organigramm names imported via this CSV, when the Befehlsdossier is anonymized, then those names are caught by ListRecognizer.

### Implementation Notes

- Extend ImportEntitiesUseCase or create a new ImportNamesUseCase.
- CLI: `milanon db import <csv> --format names` (vs existing `--format miloffice`).
- GUI: Dropdown on DB Import page to select format (PISA 410 / Simple Name List).

**Commit:** `feat(import): add simple name CSV import for external personnel`

---

## B-009: Quick-Add Names in GUI (P2) 🔴

**As a** commander, **I want to** add individual names directly in the GUI, **so that** I can quickly add a person without creating a CSV file.

### Acceptance Criteria

- Given the GUI, when I enter Grad + Vorname + Nachname in input fields and click "Add", then PERSON, VORNAME, NACHNAME, and GRAD_FUNKTION mappings are created.
- Given a name already in the DB, when I try to add it again, then a message shows "already exists" and no duplicate is created.
- Given the Quick-Add form, when I add 5 names, then all 5 are immediately available for the next anonymize run.

### Implementation Notes

- New section on GUI "DB Import" page or separate "Manage Entities" page.
- Simple form: st.text_input for Grad, Vorname, Nachname + st.button("Add").
- Uses MappingService.get_or_create_placeholder() for each entity.

**Commit:** `feat(gui): add quick-add name form for individual entity entry`

---

## Iteration 3 — Self-Improving Recognition

## B-010: Post-Anonymization Review — Learn Unknown Names (P2) 🔴

**As a** commander, **I want** the tool to show me suspicious words that might be names after anonymization, **so that** I can confirm them and the tool learns for next time.

### Problem

The tool can only anonymize names it already knows (from PISA import, CSV import, or pattern matching). Names that are not in the DB and don't match any pattern (e.g. standalone title-case surnames like "Schegg", or foreign names) slip through silently. The user has no way to know what was missed without manually reading the entire output.

### Concept: Feedback Loop

After anonymization, the tool scans the output for **candidate names** — words that look like they might be names but were not matched by any recognizer. The user reviews these candidates and confirms or rejects each one. Confirmed names are added to the DB and used in all future runs.

### Candidate Detection Heuristics

1. **ALLCAPS words (≥3 chars) not in a known exclusion list**: Words like "STORRER", "CIARDO" that are not military abbreviations (FGG, KVK, etc.), not municipality names, and not common German/French words. Show these as "possibly a surname."
2. **Title-case words after rank abbreviations that weren't caught**: If "Adj Stefan Schegg" wasn't matched because "Schegg" is title-case, flag "Schegg" as candidate.
3. **Title-case words in personnel-context sections**: Words appearing near phone numbers, email addresses, rank abbreviations — likely names.
4. **Words that appear in the same position as known anonymized names**: If line format is "Rank Firstname LASTNAME" and some are anonymized but one isn't, flag the unanonymized one.

### User Interaction (GUI)

After anonymize completes, a new "Review" section shows:
```
⚠ Possible names found (not anonymized):
☐ DÜRST (appears 2x, near rank abbreviations)
☐ CIARDO (appears 2x, in organigramm context)
☐ Schegg (appears 2x, after "Adj Stefan")
☐ TSAW (appears 16x) — probably not a name
```
User checks the boxes → confirmed names are added to DB as NACHNAME (and PERSON if firstname is adjacent). Next anonymize run catches them automatically.

### User Interaction (CLI)

```bash
milanon anonymize ./input/ --output ./output/ --review
# After processing:
# Found 4 possible unrecognized names:
# [1] DÜRST (2x) — Confirm as name? [y/N]
# [2] CIARDO (2x) — Confirm as name? [y/N]
# [3] Schegg (2x) — Confirm as name? [y/N]
# [4] TSAW (16x) — Confirm as name? [y/N]
# Added 3 names to database. Re-run anonymize to apply.
```

### Acceptance Criteria

- Given an anonymized document with unknown ALLCAPS words, when review runs, then candidates are presented to the user sorted by likelihood.
- Given a user confirms "DÜRST" as a name, when confirmed, then NACHNAME "Dürst" is added to the DB.
- Given a confirmed name in the DB, when the next anonymize runs, then the name is caught by ListRecognizer.
- Given a user rejects "TSAW", when rejected, then it is added to an exclusion list and never shown again.
- Given the GUI, when review is shown, then checkboxes allow batch confirmation/rejection.
- Given the CLI with --review flag, when processing completes, then interactive prompts allow confirmation.

### Implementation Notes

- New use case: `ReviewUnmatchedUseCase` — scans anonymized output for candidate names.
- New DB table: `review_exclusions` — words the user has rejected (never show again).
- Heuristics module: `adapters/recognizers/candidate_detector.py` — identifies suspicious unmatched words.
- GUI integration: New section on Anonymize results page.
- CLI integration: `--review` flag on anonymize command.

### Why This Matters

Every document the user processes makes the tool smarter. After 3-4 runs with review, the DB covers virtually all personnel in the user's operational scope. This is the most sustainable path to high recall without NLP dependencies.

**Commit:** `feat(review): add post-anonymization review for unknown name candidates`

---

## Future Ideas (P3)

- **B-100**: NLP-based entity recognition (spaCy) for unknown names (US-2.3)
- **B-101**: Fuzzy matching for typos (US-2.4)
- **B-102**: Image OCR in DOCX/PDF for embedded text (US-3.5 post-MVP)
- **B-103**: Manual entity management — edit/delete via GUI (US-5.3)
- **B-104**: Reporting & Audit trail (Epic E9)
- **B-105**: Import summary with delta info (new/existing/only-in-DB comparison)
