# MilAnon — Product Roadmap v2

> Central Concept: **5+2 Aktionsplanungsprozess** (BFE 52.080 Kap 5)
> Core Architecture: Cloud Intelligence + Local Security + Local DOCX Generation
> Last updated: 2026-03-25 (Session: Deep Doctrine + Berrm + Template Analysis)

---

## Architecture Decisions (this session)

| ADR | Decision | Impact |
|---|---|---|
| [ADR-009](architecture/ADR-009-5plus2-central-concept.md) | 5+2 is THE central product concept | Every workflow = specialized 5+2 |
| [ADR-010](architecture/ADR-010-universal-5-punkte-befehl.md) | Universal 5-Punkte-Befehl with mode markers | One skeleton, ADF+Berrm via `--mode` |
| [ADR-011](architecture/ADR-011-local-docx-pipeline.md) | Local DOCX generation from structured Markdown | LLM=content, Code=formatting, De-Anon=local |
| [ADR-012](architecture/ADR-012-5-layer-system-prompt.md) | 5-Layer System Prompt Architecture | Role+Context+Doctrine+Task+Rules |
| [ADR-013](architecture/ADR-013-doctrine-chapter-extraction.md) | Doctrine chapter extraction for token efficiency | ~3MB → 5-30KB per workflow step |

---

## Phase 1: Core Engine — DONE ✅ (v0.3.0)

520+ tests, 13 CLI commands, 5 GUI pages. See [BACKLOG.md](BACKLOG.md) for details.

---

## Phase 2: Doctrine + 5+2 Workflows (v0.5.0 — April 2026)

### Epic E14: Doctrine Knowledge Base

| ID | Story | Size | Prio | Status |
|---|---|---|---|---|
| US-14.1 | Store 11 doctrine files as .md in data/doctrine/ | S | P0 | ✅ Done |
| US-14.2 | INDEX.yaml with workflow→chapter→mode mapping | M | P0 | ✅ Done |
| US-14.3 | Chapter extraction engine (full .md → relevant sections) | L | P0 | ✅ Done |
| US-14.4 | `milanon doctrine list` CLI | S | P2 | ✅ Done |
| US-14.5 | `milanon doctrine extract --workflow analyse` preview | M | P2 | ✅ Done |
| US-14.6 | Paradigmenwechsel Berrm document in doctrine KB | S | P0 | ✅ Done |

### Epic E15: 5+2 Command Workflows

**Infrastructure (must-have for ANY workflow):**

| ID | Story | Size | Prio | Status |
|---|---|---|---|---|
| US-15.I1 | `--workflow` flag on `milanon pack` — reads INDEX.yaml, assembles 5-layer prompt | L | **P0** | ✅ Done |
| US-15.I2 | 5-Layer System Prompt assembly engine (Role+Context+Doctrine+Task+Rules) | L | **P0** | ✅ Done |
| US-15.I3 | `--context` flag — include Vault files from previous steps as additional input | M | **P0** | ✅ Done |
| US-15.I4 | `--mode berrm\|adf` flag — selects skeleton mode markers + doctrine chapters | M | **P0** | ✅ Done |
| US-15.I5 | `--step 1-5` flag — selects which 5+2 step to execute | S | **P0** | ✅ Done |
| US-15.I6 | Layer 1 template: `templates/role.md` (static, with TF 17 taktische Kompetenz) | M | **P0** | ✅ Done |
| US-15.I7 | Layer 5 template: `templates/rules.md` (static, placeholder + KDT ENTSCHEID rules) | S | **P0** | ✅ Done |

**Workflows (content — each is a Layer 4 template):**

| ID | Story | 5+2 Step | Size | Prio | Status |
|---|---|---|---|---|---|
| US-15.W1 | **Analyse** — 4-Farben-Initialisierung + Problemerfassung + SOMA + Zeitplan | Step 1 | L | **P0** | ✅ Done |
| US-15.W2 | **BdL** — AUGEZ-Analyse mit AEK, Konsequenzen ROT/BLAU | Step 2 | L | P1 | Open |
| US-15.W3 | **Entschluss** — Varianten (ROS), Einsatzgrundsätze-Bewertung, Absicht+Aufträge | Step 3 | L | P1 | Open |
| US-15.W4 | **Ei Bf** — 5-Punkte-Befehl aus allen Produkten (universal, mode-aware) | Step 5 | L | **P0** | ✅ Done |
| US-15.W5 | **Wachtdienst** — WAT-konformer Befehl (Berrm: taktische Sicherung) | Full cycle | L | **P0** | ✅ Done |
| US-15.W6 | **EP Halten** — Eventualplanung Halten Standort | Sub-product | M | P1 |
| US-15.W7 | **EP Interessenraum** — Eventualplanung Kampf im Interessenraum | Sub-product | M | P1 |
| US-15.W8 | Dienstbetrieb (Erg Bf im Berrm, Grundbefehl im ADF) | Full cycle | M | P2 |
| US-15.W9 | Ausbildung (Erg Bf im Berrm, eigener Bf im ADF) | Full cycle | M | P2 |

**Skeletons:**

| ID | Story | Size | Prio | Status |
|---|---|---|---|---|
| US-15.S1 | Universal 5-Punkte-Befehl skeleton with mode markers | L | P0 | ✅ Done |
| US-15.S2 | Allgemeiner Befehl skeleton (Dok 000) | M | P0 | ✅ Done |
| US-15.S3 | Wachtdienstbefehl skeleton (WAT structure) | M | P0 | ✅ Done |
| US-15.S4 | EP Halten Standort skeleton | S | P1 | Open |
| US-15.S5 | EP Kampf Interessenraum skeleton | S | P1 | Open |

---

## Phase 3: DOCX Pipeline + Claude Projects (v0.7.0 — May 2026)

### Epic E17: Local DOCX Generation (ADR-011)

| ID | Story | Size | Prio | Status |
|---|---|---|---|---|
| US-17.1 | `milanon export vault/befehl.md --docx --template befehl_vorlage.docx` | L | P1 | ✅ Done |
| US-17.2 | Markdown→DOCX style mapping engine (### → "1. Main title", etc.) | L | P1 | ✅ Done |
| US-17.3 | Aufträge-Tabelle: Nx2 DOCX table (links=Einheit, rechts=Bullet List) | M | P1 | ✅ Done |
| US-17.4 | `--deanonymize` flag on export — replace [PLACEHOLDER] → cleartext in DOCX | M | P1 | ✅ Done |
| US-17.5 | Combined: `milanon export --docx --deanonymize` in one step | S | P1 | ✅ Done |
| US-17.6 | XLSX export for WAP/Personalplanung/Synchronisationsmatrix | M | P2 |
| US-17.7 | Dossier assembly: `milanon dossier assemble` — all docs, numbered, as ZIP | L | P2 |

### Epic E16: Claude Project Generator

| ID | Story | Size | Prio |
|---|---|---|---|
| US-16.1 | `milanon project generate --unit "Inf Kp 56/1" --output ~/project/` | M | P2 |
| US-16.2 | System Prompt assembler (Layer 1+2+5 → SYSTEM_PROMPT.md) | M | P2 |
| US-16.3 | Knowledge file merger (doctrine → per-domain extracts for Project KB) | M | P2 |
| US-16.4 | INSTRUCTIONS.md + WORKFLOWS.md generator | S | P2 |

---

## Phase 4: Sharing + Community (v1.0 — Q3 2026)

### Epic E18: Starter Kit & Onboarding

| ID | Story | Size | Prio |
|---|---|---|---|
| US-18.1 | `milanon starter-kit export` (doctrine+templates+config, no PII) | M | P3 |
| US-18.2 | `milanon starter-kit import` | M | P3 |
| US-18.3 | Bat-level shared configuration | S | P3 |

---

## Critical Path for 31.03.2026 (Bat Dossier arrives)

**Must work on Day 1:**
1. ✅ Anonymization (works today)
2. ✅ Review Loop (works today)
3. E14.3 Chapter Extraction — doctrine extracts for prompts
4. E15.I1-I7 Workflow Infrastructure — `--workflow`, 5-layer prompt, `--mode`, `--context`
5. E15.W1 Workflow Analyse — first step of the 5+2

**Must work in Week 1-2:**
6. E15.W4 Workflow Ei Bf — the primary document
7. E15.W5 Workflow Wachtdienst — most time-consuming document
8. E17.1-5 DOCX Export + De-Anonymize — for distribution

**Can wait until WK (June):**
9. All other workflows (BdL, Entschluss, EP, Dienstbetrieb, Ausbildung)
10. Claude Project Generator
11. Starter Kit

---

## Delivery Channels (all use the same core)

| Channel | Zielgruppe | How it works |
|---|---|---|
| **CLI + Clipboard** | Any Kdt | `milanon pack` → paste in Claude.ai → `milanon unpack` |
| **Claude Code** | Tech-savvy Kdt | Claude Code calls milanon CLI directly, reads/writes Vault |
| **Claude Desktop + MCP** | Advanced | Claude Desktop accesses filesystem via MCP |
| **Claude Project** | Less technical Kdt | Pre-built Project with System Prompt + Knowledge |

The core flow is always: **Anonymize → LLM writes content → De-anonymize → Local DOCX generation.**
