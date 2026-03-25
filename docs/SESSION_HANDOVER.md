# MilAnon — Session Handover

Last updated: 2026-03-25 (Marathon Session: v0.5.0 built in ~17 Claude Code sessions)
Version: 0.5.0 (code complete, branches to merge)

---

## Project Status

MilAnon is a local Python CLI+GUI tool for Swiss Army unit commanders to securely use public LLMs for command document creation — with local anonymization, doctrine-aware 5+2 workflows, and structured output following BFE/WAT/TF standards.

**Tests:** 648 passing
**CLI commands:** 17 (added: pack --workflow, doctrine, export --docx, project generate)
**GUI pages:** 6 (added: LLM Workflow page)
**Branches to merge:** feat/gui-overhaul, fix/e2e-bugs, fix/project-generator (docs/final-update-v050)

---

## What Was Built Today (~17 Claude Code Sessions)

### Marathon Structure (parallel + sequential sessions)

**Parallel Pakete (morning):**
- **Paket A** — Doctrine Extraction Engine (E14.3): 14 chapter-level extracts from 4 regulation files
- **Paket B** — Workflow Infrastructure (E15.I1-I7): `--workflow` flag, 5-layer assembly, `--mode`, `--context`, `--step`
- **Paket C** — First Workflows (E15.W1/W4/W5): analyse.md, ei-bf.md, wachtdienst.md Layer 4 templates
- **Paket D** — DOCX Export (E17.1-5): Markdown→DOCX pipeline, de-anonymize in-place
- **Paket E** — Skeletons (E15.S1-S3): 5-Punkte-Befehl universal, Allgemeiner Befehl, Wachtdienstbefehl
- **Paket F** — CLI Integration: All new commands integrated, test suite updated

**Sequential sessions (midday):**
- **Paket G** — GUI Overhaul: Streamlit LLM Workflow page, embed-images checkbox
- **Paket H** — Rich Terminal Output: All CLI output replaced with Rich panels/tables, token estimates in pack
- **Session 1** (earlier) — Doctrine extracts generated and committed
- **Paket I** (not explicitly named) — E2E testing with real 70-page Bat Dossier

**Bug Fix sessions (afternoon):**
- **Paket K** — E2E Bug Fixes:
  - BUG-001: `{user_unit}` not replaced in Layer 4 templates → fixed
  - BUG-002: Layer 3 (doctrine extracts) empty for `analyse` workflow → fixed (INDEX.yaml)
  - BUG-003: CSVs anonymized by default → excluded, `--include-spreadsheets` flag added
  - BUG-004: CSVs in pack prompts (37% token waste) → excluded from `_SUPPORTED_INPUT_EXTENSIONS`
- **Paket L** — Project Generator Fix:
  - BUG-014: Anonymized dossier missing from output → `--input` flag added
  - BUG-015: INSTRUCTIONS.md + SYSTEM_PROMPT.md confusing → replaced with README.md
  - BUG-016: CHEAT_SHEET.md not in output → CHEAT_SHEET.md included from templates
  - BUG-017: PNGs (WAP) not in output → `--include-images` flag added
- **Paket M** — Documentation Update (this session)

---

## E2E Test Results (with Real Bat Dossier — 25.03.2026)

**Input:** 70-page Bat Dossier PDF (WK 2026, real document)
**Anonymization:** 2795 entities detected, 1.2 MB → 450 KB anonymized
**Claude.ai Session:** Opus 4.6, Project with full Knowledge Base

### 5+2 Workflow Run (4 prompts):
1. **Analyse** (Schritt 1): Problemerfassung + 4-Farben-Bewertung + SOMA + Zeitplan → `00_analyse.md`
2. **BdL** (Schritt 2, manual): AUGEZ-Analyse mit AEK, Konsequenzen → `10_bdl.md`
3. **Entschluss** (Schritt 3, manual): Varianten A/B, Entschluss mit Begründung → `20_entschluss.md`
4. **Ei Bf** (Schritt 5): Vollständiger 5-Punkte-Befehl → `30_ei_bf.md`

**12 documents produced** in total (including Wachtdienstbefehl, EP-Entwürfe)

### Quality Assessment:
- ✅ Analysis: Production-ready (AUGEZ complete, AEK methodology correct)
- ✅ Entschluss: Proper variants with A/B comparison, commander decision preserved
- ✅ Anonymization: Zero PII leakage confirmed
- ⚠️ DOCX Export: Functional but formatting quality insufficient (BUG-005 to BUG-011)
- ⚠️ Token Budget: ~68% of 200K context at Step 5 (fine for today, monitor with longer dossiers)

---

## Key Insights from Session

### 1. The real product is the Claude Project, not the CLI
The `milanon project generate` command is the most important UX step. The flow:
```
anonymize → project generate --input anon/ → upload to Claude.ai → work → export --docx
```
The CLI Pack flow (`milanon pack --workflow`) works but is more complex for non-technical Kdt.

### 2. CHEAT_SHEET.md is the most valuable artifact
Print it out and lay it next to the laptop. It contains all commands, all workflow prompts,
and the KDT ENTSCHEID reminders. This is what makes the tool usable in a WK context.

### 3. Dossier Quality Check (FR-001) should be Schritt 0
Before any 5+2 analysis: check the Dossier for logical errors, timeline conflicts, missing
appendices, and inconsistencies. Template `dossier-check.md` created but not wired into INDEX.yaml.

### 4. Auftragsanalyse (BFE 5.4.1) was missing, now anchored
The 4-column table (Bedeutung | Erwartete Leistung | Handlungsspielraum | Unterstützung) with
AEK-Methode is now explicit in role.md, analyse.md, and CHEAT_SHEET.md.

### 5. Interactive options (A/B/C) beat plain KDT ENTSCHEID markers
Rules.md updated: Claude now presents 2-3 concrete options with recommendation at each
decision point. Kdt says "A" or "B mit Anpassung X". Much more efficient than free-form.

### 6. CSV exclusion was the right call
Before Paket K, anonymizing a folder with the PISA list would corrupt the CSV with placeholders.
Now CSV/XLSX are opt-in only. This also cleans up the pack output significantly.

---

## Files Created/Modified This Session

### New Source Files
| File | Content |
|---|---|
| `src/milanon/usecases/workflow_pack.py` | `WorkflowPackUseCase` — 5-layer prompt assembly engine |
| `src/milanon/usecases/generate_project.py` | `GenerateProjectUseCase` — Claude.ai Project folder generator |
| `src/milanon/usecases/export_docx.py` | `ExportDocxUseCase` — Markdown → DOCX pipeline |
| `src/milanon/cli/output.py` | Rich terminal output helpers (console, panels, tables) |
| `data/templates/role.md` | Layer 1: LLM role definition (TF 17 tactical competence) |
| `data/templates/rules.md` | Layer 5: Placeholder + KDT ENTSCHEID rules (with A/B/C options) |
| `data/templates/CHEAT_SHEET.md` | Quick reference for Kdt — most valuable artifact |
| `data/templates/workflows/analyse.md` | Layer 4: Schritt 1 Problemerfassung |
| `data/templates/workflows/ei-bf.md` | Layer 4: Schritt 5 Einsatzbefehl |
| `data/templates/workflows/wachtdienst.md` | Layer 4: Wachtdienstbefehl (WAT-konform) |
| `data/templates/workflows/dossier-check.md` | Layer 4: Pre-flight Dossier Check (not yet in INDEX.yaml) |
| `data/doctrine/extracts/*.md` | 14 chapter extracts (bfe_*, tf_*, fso_*, wat_*) |
| `data/doctrine/skeletons/5_punkte_befehl_universal.md` | Universal skeleton (ADF+Berrm mode markers) |
| `data/doctrine/skeletons/000_allgemeiner_befehl.md` | Allgemeiner Befehl skeleton |
| `data/doctrine/skeletons/300_wachtdienstbefehl.md` | Wachtdienstbefehl skeleton |

### Modified Source Files
| File | What changed |
|---|---|
| `src/milanon/cli/main.py` | All new commands: pack --workflow, doctrine, export --docx, project generate, config; Rich output throughout |
| `src/milanon/usecases/anonymize.py` | CSV/XLSX excluded by default; `--include-spreadsheets` flag; `--clean` flag |
| `data/doctrine/INDEX.yaml` | Added doctrine entries for analyse workflow (was empty, causing BUG-002) |
| `pyproject.toml` | Added `rich>=13.0` dependency |

### New Test Files
| File | Tests |
|---|---|
| `tests/usecases/test_workflow_pack.py` | 18 tests — 5-layer assembly, mode markers, error handling |
| `tests/usecases/test_generate_project.py` | 11 tests — project generation, --input, --include-images |
| `tests/e2e/test_workflow_e2e.py` | 16 slow E2E tests — full CLI subprocess integration |

---

## Critical Path to 31.03.2026

**What must work on Day 1 (Bat Dossier arrives):**
1. ✅ `milanon anonymize` — works, tested with real 70-page dossier
2. ✅ `milanon project generate --input anon/ --output claude_project/` — works
3. ✅ Upload to Claude.ai Project → 5+2 analysis — works
4. ⚠️ `milanon export --docx --deanonymize` — functional but formatting rough

**What to fix before WK:**
- FR-004: DOCX Writer Rewrite (BUG-005 to BUG-011)
- FR-001: Wire dossier-check.md into INDEX.yaml
- BUG-012/013: Better PII detection for names without rank, addresses without suffix

**Can wait:**
- BdL/Entschluss as dedicated workflows (currently done manually in Claude.ai)
- MCP integration
- Starter Kit

---

## Branch State

All code changes are on feature branches:
- `feat/gui-overhaul` — GUI changes (Paket G)
- `feat/cli-rich-output` — Rich terminal output (Paket H)
- `fix/e2e-bugs` — BUG-001 to BUG-004 fixes (Paket K)
- `fix/project-generator` — BUG-014 to BUG-017 fixes (Paket L)
- `docs/final-update-v050` — this docs update (Paket M)

Merge order: feat/* first, then fix/*, then docs/*. Main branch is the integration target.

```bash
git checkout main
git merge feat/cli-rich-output
git merge feat/gui-overhaul
git merge fix/e2e-bugs
git merge fix/project-generator
git merge docs/final-update-v050
git tag v0.5.0
git push origin main --tags
```
