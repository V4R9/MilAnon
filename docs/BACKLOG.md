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

## B-008-fix: Handle "Name / Vorname" Combined Column Format (P0) ✅

**Problem:** Military system exports (MilOffice, PISA custom) often use a single column "Name / Vorname" with values like "von Gunten, Jürg" (Nachname, Vorname separated by comma). The current B-008 import expects separate "Vorname" and "Nachname" columns and won't work with this common format.

**Required Fix:**

The ImportNamesUseCase must auto-detect and handle both formats:
- **Format A (separate columns):** "Grad;Vorname;Nachname" → already works
- **Format B (combined column):** "Name / Vorname;Grad Kurzform" → needs to split on comma

Detection: If header contains "Name / Vorname" or "Name, Vorname" or "Name/Vorname" → use Format B logic.

**Acceptance Criteria:**
- Given a CSV with "Name / Vorname" header and values like "von Gunten, Jürg", when imported, then Nachname="von Gunten" and Vorname="Jürg" are correctly split.
- Given a CSV with "Grad Kurzform" header, when imported, then it maps to GRAD_FUNKTION.
- Given a CSV with separate "Vorname" and "Nachname" columns, when imported, then existing behavior is unchanged.
- Given a value without comma (e.g. just "Müller"), when imported, then it is treated as Nachname only.

**Commit:** `fix(import): handle combined Name/Vorname column format from military exports`

---

## B-011: Visual PDF Pages — Detect, Warn, Optional Image Embed (P1) ✅

**Problem:** WAP/Picasso pages in PDFs are visual Gantt charts, not data tables. pdfplumber produces unreadable garbage (85+ columns, fragmented text). These pages need special handling.

**Solution:** Detect "fake table" pages via heuristic. Show user a warning and let them decide whether to embed the page as an image (with clear warning that images are NOT anonymized).

### Detection Heuristic

A PDF page is "visual layout" when:
- `extract_tables()` returns a table with **>20 columns**, OR
- A table has **>70% empty/None cells**, OR
- The extracted text contains heavily fragmented words (average word length < 2 chars after stripping)

### Behavior

**CLI:** When visual pages are detected, print a warning per page:
```
⚠ Page 3: Visual layout detected (WAP/schedule) — text not extractable.
⚠ Page 4: Visual layout detected (WAP/schedule) — text not extractable.
Use --embed-images to include these pages as PNG images (NOT anonymized).
```
With `--embed-images` flag: rasterize as PNG (200 DPI), save alongside .md, embed in Markdown.

**GUI:** After anonymization, show detected visual pages with checkboxes:
```
⚠ Visual pages detected (not extractable as text):
☐ Page 3 — embed as image (NOT anonymized)
☐ Page 4 — embed as image (NOT anonymized)
☐ Page 5 — embed as image (NOT anonymized)
[Embed selected] [Skip all]
```

### Markdown Output (when embedded)

```markdown
⚠ **Page 3: Visual layout (WAP/schedule) — embedded as image. NOT ANONYMIZED.**

![Page 3](WK25_InfBat56_Bf_Dossier_56_page_3.png)
```

### Markdown Output (when skipped)

```markdown
⚠ **Page 3: Visual layout (WAP/schedule) — not extractable as text. See original PDF.**
```

### Acceptance Criteria

- Given a PDF with WAP/Picasso pages (>20 cols, >70% empty), when parsed, then these pages are detected and a warning is emitted.
- Given --embed-images flag (CLI) or checkbox confirmation (GUI), when enabled, then the page is rasterized as PNG and embedded in Markdown with warning.
- Given NO embed flag/confirmation, when visual pages exist, then a skip message is inserted in Markdown.
- Given a normal data table (5 columns, Dokumentenbudget), when parsed, then existing Markdown table behavior is unchanged.
- Given embedded images, when the output directory is checked, then PNG files exist alongside the .md file.

### Negative Criteria

- Must NOT embed images without user consent — always require explicit opt-in.
- Must NOT rasterize normal data table pages.
- Must NOT silently skip visual pages — always warn.

**Commit:** `feat(parser): detect visual PDF pages with optional image embedding`

---

## Iteration 3 — Self-Improving Recognition

## B-010: Post-Anonymization Review — Learn Unknown Names (P2) 🔴

Every document processed makes the tool smarter. After anonymization, scan output for candidate names (ALLCAPS words not in exclusion list, title-case words near rank abbreviations). User confirms/rejects → confirmed names added to DB automatically. See full spec in previous backlog version.

**Commit:** `feat(review): add post-anonymization review for unknown name candidates`

---

## Future Ideas (P3)

- **B-100**: NLP-based entity recognition (spaCy) for unknown names
- **B-101**: Fuzzy matching for typos
- **B-102**: Image OCR in DOCX/PDF for embedded text
- **B-103**: Manual entity management — edit/delete via GUI
- **B-104**: Reporting & Audit trail
- **B-105**: Import summary with delta info
- **B-106**: Progress bar / percentage display during anonymization
