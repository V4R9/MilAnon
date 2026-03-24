# MilAnon — Product Roadmap

> Strategic feature planning. For tactical sprint items see [BACKLOG.md](BACKLOG.md).
> For original MVP requirements see [PRD.md](PRD.md).
> Last updated: 2026-03-25

---

## Completed Epics (MVP)

| Epic | Name | Status |
|---|---|---|
| E1 | Document Ingestion (EML, DOCX, PDF, XLSX/CSV) | ✅ |
| E2 | Entity Recognition (Pattern, Military, List) | ✅ |
| E3 | Anonymization Engine | ✅ |
| E4 | De-Anonymization Engine | ✅ |
| E5 | Mapping Database (SQLite, persistent) | ✅ |
| E6 | Reference Data & Bootstrapping (Municipalities, Ranks) | ✅ |
| E7 | User Interface (CLI + Streamlit GUI) | ✅ |
| E8 | LLM Output Optimization (Legend, Validation, Context) | ✅ |

---

## Current: Hardening & Quality (March 2026)

**Goal:** Produktiv-ready bis Ende März. Fokus auf Output-Qualität und Robustheit.

| Item | Epic | Priority | Status |
|---|---|---|---|
| Visual PDF page detection (WAP/Picasso) | E1 | P1 | ✅ |
| LLM Context Generator (`milanon context`) | E8 | P1 | ✅ |
| Generic name CSV import (Bat Stab) | E5 | P1 | ✅ |
| Quick-Add names in GUI | E7 | P2 | ✅ |
| Code Review — 14 findings refactored | — | P1 | ✅ |
| Mega-cell visual detection (Organigramm) | E1 | P1 | 🔴 B-013 |
| Empty column stripping in PDF tables | E1 | P1 | 🔴 B-014 |
| Post-anonymization review loop | E2 | P2 | 🔴 B-010 |
| EINHEIT alias system | E5 | P2 | 🔴 B-018 |
| De-anonymize filenames (B-023) | E4 | P1 | 🔴 |
| Obsidian wiki-link compatibility (B-024) | E4 | P1 | 🔴 |
| In-place de-anonymization (B-025) | E4 | P2 | 🔴 |

---

## Core Innovation: The Round-Trip Workflow

**Key insight (2026-03-24):** MilAnon is not a one-way anonymizer. It enables a **continuous round-trip** between the user's local vault and public LLMs — preserving the user's manual edits across iterations.

### The Problem

```
Week 1: Mails → Anonymize → Claude → Dashboard v1 → De-Anonymize → Vault
         User edits vault: status changes, notes, checked-off tasks ✏️
Week 2: 3 new mails arrive. How to update without losing edits?
         Option A: Regenerate everything → edits LOST ❌
         Option B: Only send new mails → Claude doesn't know current state ❌
```

### The Solution: Round-Trip via Re-Anonymize

```
INITIAL (once):
  Source docs (Mails/PDF) → anonymize → Claude → De-anonymize → Vault

UPDATE (repeatable, preserves edits):
  1. RE-ANONYMIZE: Vault files (with edits) → anonymize → Placeholders
  2. COMBINE: Re-anonymized vault + new anonymized mails
  3. PACK: Combined content + template → clipboard
  4. CLAUDE: "Here is the current state + 3 new mails. Update the dashboard."
  5. UNPACK: Claude's output → de-anonymize --in-place → Vault
```

**Why this works:** The mapping DB is persistent. "Müller Hans" is ALWAYS `[PERSON_042]` — whether from a mail, from the vault, or from any future document. The round-trip is lossless.

**Re-Anonymize is already built.** `milanon anonymize` takes text with real names and replaces them with placeholders. Just point it at vault files instead of source documents. No new code needed for the basic case.

---

## Next: LLM Workflow Automation — Epic E10 (Q2 2026)

**Goal:** MilAnon becomes the secure workspace between classified documents and public LLMs. The full round-trip in 3 commands.

### E10.1: Pack — Prompt Package Builder (P1) 🔴
### E10.2: Templates — Reusable Prompt Templates (P1) 🔴
### E10.3: Unpack — De-Anonymize from Clipboard (P1) 🔴
### E10.4: GUI Integration — Pack & Unpack in Streamlit (P2) 🔴
### E10.5: Update Template — Preserve User Edits (P2) 🔴

See [BACKLOG.md](BACKLOG.md) for full specifications.

---

## Epic E13: Military Reference Data Consolidation (Q2 2026)

**Goal:** Single Source of Truth for all Swiss Army reference data. Eliminate triple-redundancy, add real organizational hierarchy, enable smarter recognition and richer LLM context.

### Problem Statement

Today there are three redundant data sources that are out of sync:

| Source | Used by | Actual value |
|---|---|---|
| `data/military_units.csv` | `init_reference_data.py` → SQLite `ref_military_units` | **Dead data** — loaded into DB but never queried by any recognizer |
| `data/swiss_military_ranks.md` | Nobody | **Dead data** — pure documentation, read by no code |
| `src/milanon/config/military_patterns.py` | `PatternRecognizer` + `MilitaryRecognizer` | **Actual source of truth** — hardcoded Python lists |

All three contain the same ranks, branches, and functions — maintained in three places with no synchronization.

Additionally, the tool has no knowledge of:
- **Concrete formations** (Inf Bat 56, Ter Div 2, Mech Br 1)
- **Organizational hierarchy** (Kdo Op → Ter Div 2 → Inf Bat 56 → Inf Kp 56/1)
- **Standard battalion structure** (Stabskp=56/0, Kp 1-3, Ustü Kp=56/4)
- **Unit type long forms** ("Ustü Kp" = "Unterstützungskompanie")

### Value Created

| Area | Today | With E13 |
|---|---|---|
| **Recognition** | Generic regex only: `Inf + Bat + Number` | Exact lookup for known units (Confidence 1.0) + regex fallback |
| **LLM Context** | Flat list: `[EINHEIT_010] = Battalion` | Full hierarchy: `Kdo Op → Ter Div 2 → Inf Bat 56 → YOUR UNIT` |
| **Alias Resolution** | None — "Ustü Kp 56/4" and "Ustü Kp 56" = 2 placeholders | Auto-alias via standard Bat structure |
| **Pack Templates** | Generic: "Company under Battalion" | Rich: "Inf Kp 56/1, one of 5 companies of Inf Bat 56, under Ter Div 2" |
| **Maintainability** | Edit 3 files, hope they're in sync | Edit 1 CSV, everything updates |

### Implementation Phases

**Phase 1 — Consolidate (B-028):** Delete dead files, extend CSV with `parent` + `level` columns, keep `military_patterns.py` hardcoded lists as-is for backward compat.

**Phase 2 — CSV as Source of Truth for Recognizer (B-029):** `military_patterns.py` reads rank/branch/function lists from DB (loaded from CSV) instead of hardcoded. PII patterns (AHV, phone, email) stay hardcoded.

**Phase 3 — Concrete Units + Hierarchy (B-030):** ~80 real formations from Wikipedia (all Ter Div, Inf Bat, Mech Br), 5er-structure for all 8 Inf Bat, parent column for hierarchy chain.

**Phase 4 — Hierarchy in Context + Alias Resolution (B-031):** `generate_context.py` uses DB hierarchy instead of slash-heuristic. Automatic alias detection for Stabskp/Ustü Kp patterns.

### Data Source

Swiss Army organizational structure from [Wikipedia: Gliederung der Schweizer Armee](https://de.wikipedia.org/wiki/Gliederung_der_Schweizer_Armee) (public information, updated for 2026 structure).

---

## Future Epics (Q3+ 2026)

### Epic E9: Reporting & Audit (P3)
Processing history, entity statistics over time, audit trail for compliance.

### Epic E11: NLP Enhancement (P3)
spaCy-based recognition for unknown names, fuzzy matching for typos, image OCR for embedded text.

### Epic E12: Multi-User / Sharing (P3)
Shared mapping databases for battalion-level coordination. Export/import of mapping DBs.

---

## Backlog Cross-Reference

Tactical items (bug fixes, small improvements) are tracked in [BACKLOG.md](BACKLOG.md).

| Backlog Iteration | Mapped to Epic | Status |
|---|---|---|
| Iteration 1–2c | E1–E8 hardening | ✅ Done |
| Iteration 3 (B-010) | E2 — Self-improving recognition | 🔴 Next |
| Iteration 4 (B-013–B-017) | E1 — Output quality | 🔴 Next |
| Iteration 5 (B-018) | E5 — EINHEIT aliases | 🔴 Planned |
| Iteration 6 (B-019–B-021) | E3 — Incremental processing | 🔴 Planned |
| Iteration 7 (B-023–B-025) | E4 — De-anonymization quality | 🔴 Planned |
| Iteration 8 (B-026–B-027) | E7 — GUI enhancements | 🔴 Planned |
| Iteration 9 (B-028–B-031) | E13 — Military reference data | 🔴 Planned |
| Epic E10 | LLM Workflow Automation | 🔴 Q2 2026 |
