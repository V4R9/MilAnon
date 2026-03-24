# MilAnon — Session Handover

Last updated: 2026-03-25 (Design Session: 5+2 + Doctrine + Berrm + Template + Strategy)
Version: 0.3.0 (code unchanged this session — pure design + documentation)

**ALL 10 DESIGN DECISIONS RESOLVED. READY FOR IMPLEMENTATION.**

---

## Project Status

MilAnon is a local Python CLI+GUI tool for Swiss Army unit commanders to securely use public LLMs for command document creation — with local anonymization, doctrine-aware workflows, and structured output following BFE/WAT/TF standards.

**Repository:** https://github.com/V4R9/MilAnon
**Tests:** 520+ passing
**CLI commands:** 13
**GUI pages:** 5

---

## What Was Done This Session (Design, no code)

### 1. Deep Doctrine Reading
- Read BFE 52.080 Kap 5 (Aktionsplanung) in full — understood every sub-step
- Cross-referenced every BFE section with FSO 17 Kap 4.2 (Zif 110-245)
- Read TF 50.030 Kap 5 in full — Einsatzgrundsätze, Taktische Grundsätze, Raumordnung, Taktische Aufgaben
- Mapped: BFE 5.1→FSO 4.2.1, BFE 5.4→FSO 4.2.4 Zif 146-179, BFE 5.5→FSO 4.2.5 Zif 206, etc.

### 2. Product Design: 5+2 as Central Concept
- Designed the complete 5+2 workflow with all 5 steps + 2 begleitende Tätigkeiten
- Defined outputs per step (15+ intermediate products)
- Designed 5-Layer System Prompt architecture
- Created Product Design v3.1 with two parts:
  - `PRODUCT_DESIGN_COMMAND_ASSISTANT.md` — 5+2 process design, workflow architecture
  - `PRODUCT_DESIGN_TF17_APPENDIX.md` — Tactical knowledge base (Einsatzgrundsätze, Raumordnung, etc.)

### 3. Bereitschaftsraum Paradigm Integration
- Read and analyzed the Paradigmenwechsel document (472 lines)
- Understood: Berrm = Ei Bf as Grundbefehl, Dienstrad replaces WAP, 3 Phasen, 2 Pflicht-EP
- Key insight: Berrm makes the 5+2 MORE valuable (AP is real, not just for Übungsanlage)
- Decision: Universal skeleton with mode markers, not separate skeletons

### 4. CH Armee DOCX Template Analysis
- Extracted and analyzed both DOCX Vorlagen (Befehl + Übung)
- Verified: Structurally IDENTICAL (same styles, same hierarchy)
- Understood Punkt 3 Aufträge table pattern: Nx2 table (links=Einheit, rechts=Bullet List)
- Mapped all DOCX styles to Markdown equivalents
- Designed the local DOCX generation pipeline (ADR-011)

### 5. Strategic Analysis (IMD Frameworks)
- Applied Rumelt, PESTEL, VRIO, Sweet Spot to MilAnon
- Identified 3 sustainable competitive advantages (VRIO): 5+2 Workflows, Reglement KB, Round-Trip
- Mapped IMD Strategic Thinking ↔ Militärischer 5+2 (same structure)
- Created `STRATEGIC_ANALYSIS.md` with complete framework application

### 6. User Journey WK 2026
- Walkthrough: 13 steps from receiving Bat Dossier (31.03) through WK completion
- Identified all gaps per step (what works today vs what's missing)
- Prioritized: what must work Day 1, Week 1-2, and what can wait
- Updated with Berrm paradigm context

### 7. Architecture Decisions (5 ADRs)
- ADR-009: 5+2 as central concept
- ADR-010: Universal 5-Punkte-Befehl with mode markers
- ADR-011: Local DOCX generation pipeline
- ADR-012: 5-Layer System Prompt architecture
- ADR-013: Doctrine chapter extraction

### 8. Design Decisions Resolved (10/10)

| # | Decision | Choice |
|---|---|---|
| D-001 | Context Window Budget | ✅ Passt (25% bei vollem Dossier, 34% kumulativ) |
| D-002 | Kumulative Context-Kette | ✅ Passt (kein Summarization nötig) |
| D-003 | Prompt-Sprache | Layer 1+5 English, Layer 3+4 Deutsch, Output Deutsch |
| D-004 | Default Mode | Konfigurierbar pro Projekt via `milanon config` |
| D-005 | Vault-Struktur | Nach Dokumenttyp: Planung/, Dossier/, Personelles/ |
| D-006 | DOCX-Handling | Diff-Import: Änderungen erkennen + selektiv zurückspielen (P2) |
| D-007 | User ↔ Claude | Copy-Paste Default, API später optional |
| D-008 | Lizenz | MIT — Repo vorerst privat, bei Bedarf mit MIT öffnen |
| D-009 | Karten im PDF | Karten sind Sache des Kdt (manuell interpretieren) |
| D-010 | Doctrine Extracts | Semi-automatisch: Script + Human Review (~3-4h) |

Full documentation: [OPEN_DECISIONS.md](OPEN_DECISIONS.md)

---

## Files Created/Updated This Session

### New Files
| File | Content |
|---|---|
| `docs/PRODUCT_DESIGN_COMMAND_ASSISTANT.md` | Product Design v3.1 — 5+2 process design (735 lines) |
| `docs/PRODUCT_DESIGN_TF17_APPENDIX.md` | TF 17 Kap 5 integration — Einsatzgrundsätze, Taktik, Raumordnung |
| `docs/STRATEGIC_ANALYSIS.md` | IMD frameworks applied (Rumelt, PESTEL, VRIO, Sweet Spot) |
| `docs/USER_JOURNEY_WK2026.md` | 13-step walkthrough with gap analysis + Berrm |
| `docs/architecture/ADR-009-5plus2-central-concept.md` | 5+2 as central product concept |
| `docs/architecture/ADR-010-universal-5-punkte-befehl.md` | Universal skeleton with mode markers |
| `docs/architecture/ADR-011-local-docx-pipeline.md` | Local DOCX generation from Markdown |
| `docs/architecture/ADR-012-5-layer-system-prompt.md` | 5-Layer prompt assembly |
| `docs/architecture/ADR-013-doctrine-chapter-extraction.md` | Chapter extraction for token efficiency |
| `data/doctrine/skeletons/5_punkte_befehl_universal.md` | Universal 5-Punkte-Befehl skeleton (ADF+Berrm) |
| `data/doctrine/skeletons/500_einsatzbefehl_berrm.md` | Berrm-specific skeleton (superseded by universal) |
| `data/doctrine/skeletons/README.md` | Skeleton architecture + DOCX style mapping |
| `data/doctrine/paradigmenwechsel_berrm.md` | Bereitschaftsraum paradigm reference |
| `docs/OPEN_DECISIONS.md` | All 10 design decisions documented + 4 implicit assumptions |

### Updated Files
| File | What changed |
|---|---|
| `docs/ROADMAP.md` | Complete rewrite — v2 with ADR references, Berrm mode, DOCX pipeline, all user stories |
| `data/doctrine/INDEX.yaml` | Complete rewrite — 5+2 as core, ADF/Berrm mode support, 11 doctrine files mapped |
| `data/doctrine/INDEX.md` | Updated — 11 doctrine files documented |

### Doctrine Files (copied to repo)
All 11 .md files in `data/doctrine/` — totaling ~3 MB. See INDEX.md for full list.

### DOCX Templates (need manual copy)
```bash
cp "Unterlagen Review Product Design/Vorlagen CH Armee/Befehl Vorlage .docx" data/templates/docx/befehl_vorlage.docx
cp "Unterlagen Review Product Design/Vorlagen CH Armee/Befehl Vorlage übung.docx" data/templates/docx/befehl_vorlage_uebung.docx
```

---

## Critical Path to 31.03.2026

### What MUST be built (6 days, parallelizable):

**Paket A: Doctrine Extraction Engine (E14.3) — 2 days**
- Input: Full doctrine .md files (~3 MB)
- Output: Chapter-level extracts in `data/doctrine/extracts/` (~5-30 KB each)
- 14 extract files needed (see ADR-013 for list)
- Semi-automated: script finds heading boundaries, human verifies

**Paket B: Workflow Infrastructure (E15.I1-I7) — 2 days**
- `--workflow` flag reads INDEX.yaml, loads 5 layers, assembles prompt
- `--mode berrm|adf` strips irrelevant mode markers
- `--context` flag includes previous Vault files
- `--step 1-5` selects which 5+2 step
- Layer 1 (role.md) and Layer 5 (rules.md) templates
- Integration with existing `milanon pack` architecture

**Paket C: First Workflows (E15.W1 + W4 + W5) — 2 days**
- Analyse workflow (4-Farben + Problemerfassung + SOMA + Zeitplan)
- Ei Bf workflow (5-Punkte-Befehl from all products, mode-aware)
- Wachtdienst workflow (WAT-conform, Berrm: taktische Sicherung)
- Each = 1 Layer 4 template file

### What SHOULD be built (Week 1-2 after 31.03):
- E17.1-5: DOCX export + de-anonymize (the "sexy" feature)
- E15.W2-W3: BdL and Entschluss workflows
- E15.W6-W7: EP templates (Berrm-Pflicht)

---

## Key Insights for Next Developer

1. **The 5-Punkte-Befehl is the 5-Punkte-Befehl** — ADF and Berrm use the SAME structure. Only content differs. One skeleton, mode markers.

2. **LLM = Content, Code = Formatting** — Claude writes the Befehl (anonymized). python-docx generates the DOCX (locally). De-anonymization happens in the DOCX, not in the cloud. This is the core value proposition.

3. **The Aufträge table (Punkt 3) has a specific DOCX pattern** — Nx2 table, left column ~4cm for Einheitsbezeichnung, right column for Bullet List 1 with Aufträge. Every element (Kdt, Z Ambos, Z Canale, etc.) gets its own row.

4. **The Berrm paradigm is POSITIVE for the product** — It makes the 5+2 real (not just for Übungsanlage). BFE Teil 1 (which we've deeply integrated) becomes the primary reference.

5. **The IMD ↔ Military parallel is real** — PESTEL ≈ AUGEZ, AEK ≈ Facts→Interpretation→"So what?", Varianten ≈ Strategic Options. This validates the 5+2 as a universal decision-making framework.

---

## Repo Structure (relevant parts)

```
data/
  doctrine/
    INDEX.yaml                          # Workflow → chapter → mode mapping
    INDEX.md                            # Human-readable overview
    *.md                                # 11 reglement files (~3 MB)
    paradigmenwechsel_berrm.md          # Berrm context document
    extracts/                           # 🔴 EMPTY — needs E14.3
    skeletons/
      5_punkte_befehl_universal.md      # THE primary skeleton
      000_allgemeiner_befehl.md
      300_wachtdienstbefehl.md
      README.md                         # Architecture + DOCX style mapping
  templates/
    docx/                               # 🔴 NEEDS manual copy of DOCX templates
docs/
  ROADMAP.md                            # v2 — complete with ADRs + all stories
  PRODUCT_DESIGN_COMMAND_ASSISTANT.md   # 5+2 process design
  PRODUCT_DESIGN_TF17_APPENDIX.md      # Tactical knowledge base
  STRATEGIC_ANALYSIS.md                 # IMD frameworks applied
  USER_JOURNEY_WK2026.md               # 13-step walkthrough + gaps
  architecture/
    ADR-009 through ADR-013             # This session's decisions
```
