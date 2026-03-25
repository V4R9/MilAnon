# MilAnon — Product Roadmap v3

> Central Concept: **5+2 Aktionsplanungsprozess** (BFE 52.080 Kap 5)
> Core Architecture: Cloud Intelligence + Local Security + Local DOCX Generation
> Last updated: 2026-03-25 (v0.5.0-stable — code review complete)

---

## Architecture Decisions

| ADR | Decision | Impact |
|---|---|---|
| [ADR-009](architecture/ADR-009-5plus2-central-concept.md) | 5+2 is THE central product concept | Every workflow = specialized 5+2 |
| [ADR-010](architecture/ADR-010-universal-5-punkte-befehl.md) | Universal 5-Punkte-Befehl with mode markers | One skeleton, ADF+Berrm via `--mode` |
| [ADR-011](architecture/ADR-011-local-docx-pipeline.md) | Local DOCX generation from structured Markdown | LLM=content, Code=formatting, De-Anon=local |
| [ADR-012](architecture/ADR-012-5-layer-system-prompt.md) | 5-Layer System Prompt Architecture | Role+Context+Doctrine+Task+Rules |
| [ADR-013](architecture/ADR-013-doctrine-chapter-extraction.md) | Doctrine chapter extraction for token efficiency | ~3MB → 5-30KB per workflow step |

---

## Phase 1: Core Engine — DONE ✅ (v0.3.0)

685 tests, 17 CLI commands, 8 GUI pages. Full anonymize→validate→deanonymize round-trip.

---

## Phase 2: Doctrine + 5+2 Workflows — DONE ✅ (v0.5.0-stable)

> Code review complete (2026-03-25): 19 findings resolved (CR-001 to CR-019). See docs/BACKLOG.md.

### Epic E14: Doctrine Knowledge Base ✅

| ID | Story | Status |
|---|---|---|
| US-14.1 | Store 11 doctrine files as .md in data/doctrine/ | ✅ Done |
| US-14.2 | INDEX.yaml with workflow→chapter→mode mapping | ✅ Done |
| US-14.3 | Chapter extraction engine (14 extract files in data/doctrine/extracts/) | ✅ Done |
| US-14.4 | `milanon doctrine list` CLI | ✅ Done |
| US-14.5 | `milanon doctrine extract --all|--workflow <name>` | ✅ Done |
| US-14.6 | Paradigmenwechsel Berrm document in doctrine KB | ✅ Done |

### Epic E15: 5+2 Command Workflows ✅

**Infrastructure:**

| ID | Story | Status |
|---|---|---|
| US-15.I1 | `--workflow` flag on `milanon pack` — reads INDEX.yaml, assembles 5-layer prompt | ✅ Done |
| US-15.I2 | 5-Layer System Prompt assembly engine (Role+Context+Doctrine+Task+Rules) | ✅ Done |
| US-15.I3 | `--context` flag — include Vault files from previous steps | ✅ Done |
| US-15.I4 | `--mode berrm\|adf` flag — mode marker stripping | ✅ Done |
| US-15.I5 | `--step 1-5` flag — selects 5+2 step (skeleton at step 5) | ✅ Done |
| US-15.I6 | Layer 1 template: `templates/role.md` (with TF 17 taktische Kompetenz) | ✅ Done |
| US-15.I7 | Layer 5 template: `templates/rules.md` (placeholder + KDT ENTSCHEID + A/B/C options) | ✅ Done |

**Workflows:**

| ID | Story | 5+2 Step | Status |
|---|---|---|---|
| US-15.W1 | **Analyse** — Problemerfassung + 4-Farben + SOMA + Auftragsanalyse + Zeitplan | Step 1 | ✅ Done |
| US-15.W2 | **BdL** — AUGEZ-Analyse mit AEK, Konsequenzen ROT/BLAU | Step 2 | ❌ Open |
| US-15.W3 | **Entschluss** — Varianten (ROS), Absicht+Aufträge | Step 3 | ❌ Open |
| US-15.W4 | **Ei Bf** — Universal 5-Punkte-Befehl (mode-aware) | Step 5 | ✅ Done |
| US-15.W5 | **Wachtdienst** — WAT-konformer Befehl (Berrm: taktische Sicherung) | Full cycle | ✅ Done |
| US-15.W6 | **EP Halten** — Eventualplanung Halten Standort | Sub-product | ❌ Open |
| US-15.W7 | **EP Interessenraum** — Eventualplanung Kampf im Interessenraum | Sub-product | ❌ Open |
| FR-001 | **Dossier Check** — Pre-flight Validation (Schritt 0) | Pre-analysis | Template ✅, INDEX.yaml ❌ |

**Skeletons:**

| ID | Story | Status |
|---|---|---|
| US-15.S1 | Universal 5-Punkte-Befehl skeleton with ADF/Berrm mode markers | ✅ Done |
| US-15.S2 | Allgemeiner Befehl skeleton (Dok 000) | ✅ Done |
| US-15.S3 | Wachtdienstbefehl skeleton (WAT structure) | ✅ Done |
| US-15.S4 | EP Halten Standort skeleton | ❌ Open |
| US-15.S5 | EP Kampf Interessenraum skeleton | ❌ Open |

### Epic E16: Claude Project Generator ✅

| ID | Story | Status |
|---|---|---|
| US-16.1 | `milanon project generate --unit --output` — basic project folder | ✅ Done |
| US-16.2 | System Prompt assembler (Layer 1+2+5 → SYSTEM_PROMPT.md) | ✅ Done |
| US-16.3 | Knowledge file merger (doctrine extracts → per-domain files) | ✅ Done |
| US-16.4 | README.md + CHEAT_SHEET.md (replaced INSTRUCTIONS.md + WORKFLOWS.md) | ✅ Done (Paket L) |
| US-16.5 | `--input` flag — copy anonymized docs into knowledge/ | ✅ Done (Paket L) |
| US-16.6 | `--include-images` flag — copy PNG files into knowledge/ | ✅ Done (Paket L) |

---

## Phase 3: DOCX Pipeline (v0.7.0 — May 2026)

### Epic E17: Local DOCX Generation (ADR-011)

| ID | Story | Status | Known Bugs |
|---|---|---|---|
| US-17.1 | `milanon export <file> --docx` | ✅ Done | BUG-005 to BUG-011 |
| US-17.2 | Markdown→DOCX style mapping engine | ✅ Done | BUG-005, BUG-008, BUG-010 |
| US-17.3 | Aufträge-Tabelle: Nx2 DOCX table | ✅ Done | BUG-011 |
| US-17.4 | `--deanonymize` flag on export | ✅ Done | — |
| US-17.5 | Combined: `--docx --deanonymize` in one step | ✅ Done | — |
| FR-004 | **DOCX Writer Rewrite** — fix BUG-005 to BUG-011 | ❌ Open (P1, Opus session) | — |
| US-17.6 | XLSX export for WAP/Personalplanung | ❌ Open | — |
| US-17.7 | Dossier assembly: all docs numbered as ZIP | ❌ Open | — |

---

## Phase 4: Quality + Polish (v0.8.0)

| Feature | Prio | Status |
|---|---|---|
| FR-001: Dossier Quality Check — wire into INDEX.yaml | P0 | Template done, not wired |
| FR-004: DOCX Writer Rewrite | P1 | Open |
| BUG-012: Einzelnamen ohne Rang erkennen | P2 | Open |
| BUG-013: Strassennamen ohne Suffix erkennen | P2 | Open |
| BUG-018: Rich Output für `pack --workflow` | P2 | Open |
| FR-003: Interactive A/B/C Optionen | P1 | ✅ Done (in rules.md) |
| FR-017: Two-Tier Anonymization (DSG/Full) | P0 | ✅ Done (v0.6.0) |
| Code Review (19 findings) | P0 | ✅ Done (2026-03-25) |
| CI/CD Pipeline (GitHub Actions) | P1 | ✅ Done (v0.6.0) |
| GUI Overhaul | P1 | ✅ Done (Paket G) |

---

## Phase 5: Distribution (v1.0 — Q3 2026)

| Feature | Prio | Status |
|---|---|---|
| FR-008: Dossier Assembly ZIP | P2 | Open |
| FR-009: Starter Kit export/import | P3 | Open |
| FR-010: Claude Desktop MCP Integration | P3 | Open |
| FR-011: Desktop App (Electron/Tauri) | P3 | Open |

---

## Critical Path for 31.03.2026 (Bat Dossier arrives)

**Code review complete** — all 19 CR findings resolved (2026-03-25). Codebase is stable.

**Must work on Day 1 — ALL DONE ✅:**
1. ✅ Anonymization (tested with real 70-page dossier, 2795 entities)
2. ✅ Project Generate (--input, --include-images, README, CHEAT_SHEET)
3. ✅ Claude.ai Project (Knowledge uploaded, System Prompt working)
4. ✅ 5+2 Analysis in Claude.ai (4 prompts → 12 documents)
5. ⚠️ DOCX Export (functional, formatting rough — acceptable for Day 1)

**Must improve in Week 1-2:**
- FR-004: DOCX Writer Rewrite
- FR-001: Dossier Check wired into CLI

---

## Delivery Channels

| Channel | Zielgruppe | How it works |
|---|---|---|
| **CLI + Clipboard** | Tech-savvy Kdt | `milanon pack --workflow` → paste in Claude.ai |
| **Claude Project** | Any Kdt | `project generate` → Upload Knowledge → Claude.ai |
| **Claude Code** | Developer | Claude Code calls milanon CLI directly via shell |
| **Claude Desktop + MCP** | Advanced | Claude Desktop accesses filesystem via MCP (future) |

The core flow is always: **anonymize → project generate → Claude.ai → export --docx**
