# MilAnon — Backlog

> Last updated: 2026-03-25 (post code review)
> Prioritization: P0 = Blocker for 31.03, P1 = Important for WK, P2 = Nice-to-have, P3 = Future
> Status: ✅ Done, 🔧 In Progress, ❌ Open

---

## BUGS

| ID | Bug | Severity | Status |
|---|---|---|---|
| BUG-001 | `{user_unit}` not replaced in workflow templates (Layer 4) | 🔴 | ✅ Fixed (Paket K) |
| BUG-002 | Layer 3 (Doctrine Extracts) missing from prompt output | 🔴 | ✅ Fixed (Paket K) |
| BUG-003 | CSVs (PISA, Hilfsliste) anonymized into output folder | 🟡 | ✅ Fixed (Paket K) |
| BUG-004 | CSVs packed into prompt (37% token waste) | 🟡 | ✅ Fixed (Paket K) |
| BUG-005 | DOCX Writer: `**bold**` not converted, stays as Markdown | 🔴 | ❌ Open |
| BUG-006 | DOCX Writer: `---` separators rendered as empty paragraphs | 🟡 | ❌ Open |
| BUG-007 | DOCX Writer: `<!-- FILL: -->` and `<!-- KDT ENTSCHEID: -->` appear as visible text | 🟡 | ❌ Open |
| BUG-008 | DOCX Writer: `> blockquotes` not recognized | 🟡 | ❌ Open |
| BUG-009 | DOCX Writer: Tables with >2 columns incorrectly parsed | 🔴 | ❌ Open |
| BUG-010 | DOCX Writer: No paragraph spacing — everything runs together | 🟡 | ❌ Open |
| BUG-011 | DOCX Writer: Aufträge-table (Pt 3) not differentiated from info tables | 🟡 | ❌ Open |
| BUG-012 | PII: Single first/last names without rank not detected (Ciardo, Megevand, Nicolas, Stéphane, Etienne) | 🟡 | ❌ Open |
| BUG-013 | PII: Street names without -strasse/-weg suffix not recognized (Fesenacker 3, Avenue D'Aire 73, Tumma 9) | 🟡 | ❌ Open |
| BUG-014 | Project Generator: Anonymized dossier missing from output | 🔴 | ✅ Fixed (Paket L) |
| BUG-015 | Project Generator: INSTRUCTIONS.md + SYSTEM_PROMPT.md confusing (2 files, only 1 field in Claude.ai) | 🟡 | ✅ Fixed (Paket L) |
| BUG-016 | Project Generator: CHEAT_SHEET.md missing from output | 🟡 | ✅ Fixed (Paket L) |
| BUG-017 | Project Generator: PNGs (WAP) missing from output | 🟡 | ✅ Fixed (Paket L) |
| BUG-018 | Rich CLI output missing on `pack --workflow` (shows old format instead of Rich panels) | 🟡 | ❌ Open |

---

## CODE REVIEW FIXES (2026-03-25)

All findings from the post-v0.5.0 code review session.

| ID | Finding | Status |
|---|---|---|
| CR-001 | Placeholder collision: COUNT(*) replaced with MAX() to avoid collisions on concurrent inserts | ✅ Done |
| CR-002 | Bare `except Exception` in repository migrations narrowed to `sqlite3.OperationalError` | ✅ Done |
| CR-003 | DB connection leak: connections now closed via context manager (`__enter__`/`__exit__`) | ✅ Done |
| CR-004 | PII leaked in anonymizer warning strings — strings sanitized | ✅ Done |
| CR-005 | PII leaked in review_candidates log messages — log output sanitized | ✅ Done |
| CR-006 | UseCase DIP violations: `FileTrackingRepository` and `ReferenceDataRepository` protocols added | ✅ Done |
| CR-007 | export_docx imports python-docx at module level — documented, deferred to FR-004 | ✅ Done |
| CR-008 | Private attribute access (`_attr`) replaced with public methods | ✅ Done |
| CR-009 | domain/workflow.py imported yaml (external dep in domain layer) — moved to config/ | ✅ Done |
| CR-010 | Thread safety in create_mapping: `BEGIN IMMEDIATE` transaction added | ✅ Done |
| CR-011 | Entity normalization logic was in repository layer — moved to MappingService (correct layer) | ✅ Done |
| CR-012 | Placeholder regex duplicated across files — deduplicated into single `PLACEHOLDER_PATTERN` constant | ✅ Done |
| CR-013 | Bare except in DOCX and PDF parsers — narrowed to specific exception types | ✅ Done |
| CR-014 | CSV encoding: UTF-8 only caused failures on Latin-1 files — Latin-1 fallback added | ✅ Done |
| CR-015 | HTML entities in EML not decoded — fixed via `html.unescape()` in EML parser | ✅ Done |
| CR-016 | Missing CLI integration tests | ❌ Open (documented) |
| CR-017 | EntityMapping was mutable — fixed with `frozen=True` (dataclass) | ✅ Done |
| CR-018 | Deprecated `data/swiss_military_ranks.md` still in repo — deleted | ✅ Done |
| CR-019 | Regex pattern not cached in ListRecognizer — `re.compile()` caching added | ✅ Done |

---

## FEATURE REQUESTS

### FR-001: Dossier Quality Check (Pre-Flight Validation) — P0

**Description:** Before Aktionsplanung, validate the Bat Dossier for logic errors, missing info, inconsistencies, and contradictions.
**Workflow:** `milanon pack --workflow dossier-check` or in Claude Project: "Prüfe mein Bat Dossier"
**Template:** `data/templates/workflows/dossier-check.md` — ✅ Created
**Check areas:**
- Timeline check (WAP vs. orders: overlaps, expired deadlines)
- Completeness check (referenced annexes present?)
- Consistency check (contradictions between orders)
- Logic check (physical feasibility: Kdt in 3 places simultaneously?)
- Information gaps (what does the unit need, where to request it?)
- Security-relevant checks (threat levels, ROE, alarm org)

**Output:** `00_dossier_check.md` with traffic-light rating (Red/Yellow/Green)
**Status:** Template created, not yet wired into INDEX.yaml

---

### FR-002: Auftragsanalyse as Fixed Product — P0

**Description:** The BFE 5.4.1 Auftragsanalyse (fixed 4-row table) must ALWAYS be produced.
**Table:** Bedeutung der Aufgabe | Erwartete Leistung | Handlungsspielraum | Unterstützung
**Columns:** Aussagen | Erkenntnisse | Konsequenzen (Mittel, Räume, Zeit, Info — must be drawable)
**Status:** ✅ Done — anchored in role.md, analyse.md, and CHEAT_SHEET.md. Output: `15_auftragsanalyse.md`

---

### FR-003: Interactive Options for KDT ENTSCHEID — P1

**Description:** Claude should present 2-3 concrete options (A, B, C) with a recommendation for each decision. Commander only says "A" or "B with adjustment X".
**Status:** ✅ Done — anchored in rules.md (with example). Included automatically in System Prompt on next `project generate`.

---

### FR-004: DOCX Writer Rewrite — P1

**Description:** The DOCX Writer is too simple for the complex Markdown Claude produces. Needs:
- Markdown Bold/Italic → DOCX runs with Bold/Italic
- HTML comments (`<!-- -->`) hidden or rendered as highlights
- Blockquotes → indented text or special style
- Multi-column tables (not just 2-column)
- Aufträge-table (Pt 3) as special Nx2 table with unit left + bullets right
- Correct paragraph spacing
- `---` as section break or ignored

**Effort:** L (Opus, 4-6h)
**Status:** ❌ Open (P1, planned for v0.7.0)

---

### FR-005: PNG/Images in Claude Project Knowledge — P2

**Description:** WAP pages and maps as PNG in Claude Project Knowledge files. Claude can read images and incorporate WAP timeline directly into analysis.
**Implementation:** `--include-images` flag on `project generate`
**Status:** ✅ Done (Paket L)

---

### FR-006: Dossier as Input for Project Generate — P0

**Description:** `milanon project generate --input test_output/anon/` should automatically copy anonymized dossier into `knowledge/` folder.
**Status:** ✅ Done (Paket L)

---

### FR-007: One-Shot Full 5+2 Prompt — P2

**Description:** A single mega-prompt that runs the entire 5+2 process in one shot (no interactive steps). Useful for batch processing or when the commander has no time for interactive review.
**Trade-off:** Less commander control, but faster.
**Status:** ❌ Open

---

### FR-008: Vault Export as ZIP — P2

**Description:** `milanon dossier assemble` collects all products (orders, annexes, EP) and creates a numbered ZIP dossier as the Bat Kdt expects.
**Structure:** 000_Allg_Bf.docx, 100_Ei_Bf.docx, 200_Wachtdienst_Bf.docx, etc.
**Status:** ❌ Open

---

### FR-009: Starter Kit for Other Commanders — P3

**Description:** `milanon starter-kit export` creates a PII-free package with doctrine, templates, and config that can be distributed to other commanders in the battalion. `milanon starter-kit import` imports it.
**Status:** ❌ Open

---

### FR-010: Claude Desktop MCP Integration — P3

**Description:** Claude Desktop can access the filesystem via MCP. MilAnon could act as an MCP server and let Claude Desktop execute commands directly (anonymize, pack, export) without a terminal.
**Status:** ❌ Open

---

### FR-011: Desktop App (Electron/Tauri) — P3

**Description:** Drag & Drop PDF → click through 5+2 → DOCX output. No terminal needed. The unicorn product.
**Status:** ❌ Open

---

### FR-012: Street Name Recognition Without Suffix — P2

**Description:** Addresses like "Fesenacker 3", "Tumma 9", "Falken 3" not recognized because they don't end with "-strasse", "-weg", etc. Pattern: `[A-Z][a-z]+\s+\d{1,3}` near personal data.
**Status:** ❌ Open (see BUG-013)

---

### FR-013: Single Name Recognition Without Rank — P2

**Description:** First/last names appearing without rank prefix (e.g., in address list tables) not recognized. Solution: context-based recognition — if a table contains AHV-Nr, phone, ZIP, words in certain columns are very likely names.
**Status:** ❌ Open (see BUG-012)

---

### FR-017: Two-Tier Anonymization (DSG/Full) — P0

**Description:** Implement two anonymization tiers:
- **DSG mode:** Anonymize only legally required PII (GDPR/DSG: names, AHV, phone, email, address)
- **Full mode:** Anonymize all military-sensitive data (current behavior: units, ranks, locations, etc.)

Commander selects mode based on use case: DSG for legal compliance, Full for operational security.
**Spec:** `docs/specs/FR-017_two_tier_anonymization.md` — approved
**Status:** ❌ Open (spec approved, implementation pending)

---

## EPICS — Status

### Phase 1: Core Engine (v0.3.0) — DONE

685 tests. All 17 CLI commands. 8 GUI pages.

### Phase 2: Doctrine + Workflows (v0.5.0) — CODE COMPLETE

| Epic | Status | Tests | Open Bugs |
|---|---|---|---|
| E14: Doctrine KB | ✅ Done | 14 extracts generated | — |
| E15: 5+2 Workflows | ✅ Done (3 workflows + infra) | 685 tests | BUG-018 (Rich output) |
| E16: Claude Project Generator | ✅ Done | — | — |

### Phase 3: DOCX Pipeline (v0.7.0) — PARTIAL

| Epic | Status | Open Bugs |
|---|---|---|
| E17: DOCX Export | Functional but not production-ready | BUG-005 to BUG-011 (Writer Rewrite needed) |

### Phase 4: Quality + Polish (v0.8.0) — OPEN

| Feature | Prio | Status |
|---|---|---|
| FR-001: Dossier Quality Check | P0 | Template created, not wired |
| FR-004: DOCX Writer Rewrite | P1 | Open |
| FR-017: Two-Tier Anonymization | P0 | Spec approved, implementation pending |
| BUG-012: Single names without rank | P2 | Open |
| BUG-013: Street names without suffix | P2 | Open |
| BUG-018: Rich output for `pack --workflow` | P2 | Open |
| CR-016: CLI integration tests | P2 | Open |
| GUI Overhaul | P1 | ✅ Done (Paket G) |

### Phase 5: Distribution (v1.0) — OPEN

| Feature | Prio | Status |
|---|---|---|
| FR-008: Dossier Assembly ZIP | P2 | Open |
| FR-009: Starter Kit | P3 | Open |
| FR-010: MCP Integration | P3 | Open |
| FR-011: Desktop App | P3 | Open |
