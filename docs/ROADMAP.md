# MilAnon — Product Roadmap

> Strategic feature planning. For tactical sprint items see [BACKLOG.md](BACKLOG.md).
> For original MVP requirements see [PRD.md](PRD.md).
> Last updated: 2026-03-24

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

### Full Workflow with E10

```bash
# INITIAL SETUP (once per WK cycle)
milanon db init
milanon db import pisa_410.csv
milanon db import bat_stab.csv --format names
milanon anonymize source_docs/ --output anon/ --recursive
milanon pack --template obsidian-notes --input anon/ --unit "Inf Kp 56/1"
# → Paste in Claude.ai → Claude creates Dashboard + Notes → Copy output
milanon unpack --clipboard --output vault/Personelles/ --in-place

# WEEKLY UPDATE (repeatable)
milanon anonymize vault/Personelles/ --output anon/vault/        # Re-anonymize vault (with edits)
milanon anonymize new_mails/ --output anon/new/                   # Anonymize new mails
milanon pack --template update-dashboard --input anon/ --unit "Inf Kp 56/1"
# → Paste in Claude.ai → "Update with new mails, preserve existing data" → Copy output
milanon unpack --clipboard --output vault/Personelles/ --in-place
```

### E10.1: Pack — Prompt Package Builder (P1) 🔴

**As a** commander, **I want** to generate a ready-to-paste prompt package from my anonymized documents, **so that** I can start working with Claude.ai without manually assembling context, instructions, and document content.

**CLI:**
```bash
milanon pack --template obsidian-notes --input anon/ --unit "Inf Kp 56/1"
milanon pack --prompt "Update dashboard with new mails" --input anon/ --unit "Inf Kp 56/1"
```

Auto-copied to system clipboard (pbcopy on macOS).

### E10.2: Templates — Reusable Prompt Templates (P1) 🔴

Built-in templates (`data/templates/`):
- `obsidian-notes.md` — Create Obsidian notes with YAML frontmatter per person
- `befehl-entwurf.md` — Draft a company-level order from the Dossier
- `analyse.md` — Analyze document: decisions, timeline, open items, risks
- `update-dashboard.md` — Update existing dashboard with new information (preserves edits)
- `frei.md` — Minimal wrapper for custom prompts

Custom templates: `~/.milanon/templates/`

### E10.3: Unpack — De-Anonymize from Clipboard (P1) 🔴

```bash
milanon unpack --clipboard --output vault/Personelles/ --in-place
```

Features: clipboard reading, multi-file splitting, Obsidian wiki-link handling, filename de-anonymization.

### E10.4: GUI Integration — Pack & Unpack in Streamlit (P2) 🔴

Pack + Unpack pages in the GUI for non-CLI users.

### E10.5: Update Template — Preserve User Edits (P2) 🔴

**As a** commander, **I want** to tell Claude "here is my current vault state plus new mails — update without losing my edits", **so that** the round-trip preserves my work.

The `update-dashboard.md` template instructs Claude:
```
You are updating an existing set of personnel notes. 

CURRENT STATE (re-anonymized from user's vault — contains user's manual edits):
{vault_content}

NEW INFORMATION (newly anonymized mails):
{new_content}

Rules:
- PRESERVE all existing data, status changes, and notes from the current state
- ADD new information from the new mails
- UPDATE status fields if new mails indicate changes
- Do NOT delete or overwrite user's manual annotations
- Preserve all [PLACEHOLDER] tokens exactly
```

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
| Epic E10 | LLM Workflow Automation | 🔴 Q2 2026 |
