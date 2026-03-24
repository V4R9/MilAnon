# MilAnon — Product Vision v2.0

> From Anonymizer to Secure AI Command Assistant
> Last updated: 2026-03-25

---

## Product Vision Statement

**For** Swiss Army unit commanders (Stufe Einheit)
**who** must prepare and execute WK cycles with limited time and no dedicated staff,
**MilAnon** is a local AI command assistant
**that** enables secure, doctrine-aware document creation using public LLMs
**unlike** manual document creation or unsecured ChatGPT usage,
**our product** guarantees that classified data never leaves the commander's machine
while providing structured, BFE-conform workflows for every standard task.

---

## Two Product Layers

### Layer 1: MilAnon Core (Anonymization Engine) — BUILT ✅

The security layer. Enables safe use of public LLMs with classified military documents.

- Document parsing (EML, PDF, DOCX, XLSX/CSV)
- Entity recognition (names, AHV, phone, email, units, functions, municipalities)
- Bidirectional anonymization (anonymize ↔ de-anonymize)
- Persistent mapping database (round-trip safe)
- Obsidian integration (wiki-links, filename resolution, in-place)
- Self-improving recognition (review loop)

### Layer 2: Command Workflows (Doctrine-Aware AI Assistant) — PLANNED

The productivity layer. Turns raw documents into finished command products.

- Doctrine knowledge base (BFE, Wachtdienst, Taktik, FSO)
- Structured workflows (Kp Befehl, WAP, Ausbildungsplanung, etc.)
- Claude Project templates (system prompts + project knowledge + instructions)
- Output in multiple formats (Markdown → Obsidian, DOCX → official, XLSX → planning)
- Shareable across commanders (Open Source, transferable knowledge)

---

## User Personas

### Primary: Erstlings-Kp Kdt "Sandro"
- First WK as unit commander
- No previous templates or Vorjahresbefehl
- Tech-savvy (uses Obsidian, Claude, GitHub)
- Needs guidance on WHAT to produce and HOW to structure it
- Time is the #1 constraint

### Secondary: Erfahrener Kp Kdt "Thomas"
- Has done 2-3 WKs as Kp Kdt
- Has Vorjahres-Dokumente but wants to improve quality
- Less tech-savvy — needs a simple GUI workflow
- Values completeness and doctrine conformity

### Tertiary: Bat Kdt / S3
- Wants consistent quality across all Kp in the Bat
- Could mandate the tool for all Kp Kdt
- Cares about standardization and Befehlskonformität

---

## Epic Overview

### Completed Epics (v0.3.0)
| Epic | Name | Status |
|---|---|---|
| E1 | Document Ingestion | ✅ |
| E2 | Entity Recognition (incl. Review Loop) | ✅ |
| E3 | Anonymization Engine | ✅ |
| E4 | De-Anonymization (incl. Obsidian, in-place) | ✅ |
| E5 | Mapping Database | ✅ |
| E6 | Reference Data (incl. Swiss Army Hierarchy) | ✅ |
| E7 | User Interface (CLI + GUI) | ✅ |
| E8 | LLM Output Optimization (Context, Validation) | ✅ |
| E10 | LLM Workflow (Pack, Templates, Unpack) | ✅ |
| E13 | Military Reference Data (Single Source of Truth) | ✅ |

### New Epics (v1.0 — Command Assistant)

#### Epic E14: Doctrine Knowledge Base
**Goal:** MilAnon knows Swiss Army doctrine and can reference the right regulations for each task.

**User Stories:**

US-14.1: As a Kp Kdt, I want the tool to know the BFE (52.080/52.081) structure, so that every document it helps me create follows the correct doctrine format.

US-14.2: As a Kp Kdt, I want to add reglemente as Markdown files, so that the tool can reference them when building prompts.

US-14.3: As a Kp Kdt, I want the system to include only the RELEVANT chapters of a reglement in the prompt (not the whole 200-page document), so that token usage is efficient and Claude's context isn't wasted.

**Implementation:**
```
data/doctrine/
  52_080_bfe_einsatz.md           # Full BFE Part 1
  52_081_bfe_ausbildung.md        # Full BFE Part 2
  wachtdienst_aller_truppen.md    # Wachtdienst Reglement
  51_030_taktische_fuehrung.md    # Auszug Taktische Führung
  50_040_fso_17.md                # Auszug FSO 17
  militaerische_begriffe.md       # Begriffslexikon

data/doctrine/index.yaml          # Maps workflow → relevant chapters
```

The index.yaml maps each workflow to the specific chapters it needs:
```yaml
kp-befehl:
  - source: 52_080_bfe_einsatz.md
    sections: ["5 Befehlsgebung", "5.2 Beurteilung der Lage", "5.3 Befehlsschema"]
  - source: 50_040_fso_17.md
    sections: ["Befehlstechnik Stufe Einheit"]

wachtdienst:
  - source: wachtdienst_aller_truppen.md
    sections: ["Wachtdienstbefehl", "Pflichten", "Ablösung"]

ausbildungsplan:
  - source: 52_081_bfe_ausbildung.md
    sections: ["3 Ausbildungsplanung", "4 Ausbildungsdurchführung"]
```

**Acceptance Criteria:**
- Given a doctrine file in data/doctrine/, when `milanon pack --workflow kp-befehl` runs, then only the relevant BFE chapters are included in the prompt.
- Given a new reglement added as .md to data/doctrine/ + entry in index.yaml, when pack runs, then it is available.
- Given no doctrine files exist, when pack runs, then it falls back to basic templates (existing behavior).

---

#### Epic E15: Command Workflows
**Goal:** Pre-built, doctrine-aware workflows for every standard command task.

**User Stories:**

US-15.1 — Kompaniebefehl:
As a Kp Kdt, I want to generate a BFE-conform Kompaniebefehl from the Bat Dossier, so that I have a complete, structured command order without starting from scratch.

Workflow:
1. Input: Anonymized Bat Dossier
2. Claude extracts all tasks relevant to my Kp
3. Claude structures the Kp Befehl according to BFE 52.080 Kap 5.3:
   - Allgemeines (Grundlagen, Beilagen)
   - Lage (Allgemein, Eigene, Feind)
   - Auftrag (Bat Auftrag → eigener Auftrag)
   - Durchführung (Absicht, Phasen, Aufträge an Züge)
   - Logistik (Vpf, San, Mun, Transport)
   - Führung (KP, Verbindungen, Stellvertretung)
4. Claude flags: Widersprüche, offene Fragen, fehlende Info
5. Output: Markdown (Obsidian) + DOCX (offiziell)

US-15.2 — Wochenarbeitsplan (WAP):
As a Kp Kdt, I want to derive my company WAP from the Bat WAP, so that my weekly schedule is complete and conflict-free.

US-15.3 — Wachtdienstbefehl:
As a Kp Kdt, I want to generate a Wachtdienstbefehl from the Bat Sicherheitsbefehl, so that it follows the Wachtdienst-Reglement structure exactly.

US-15.4 — Ausbildungsplanung:
As a Kp Kdt, I want to create a structured Ausbildungsplanung based on the Bat Ausbildungsbefehl, so that Lernziele, Lektionen, and Übungen are BFE-konform planned.

US-15.5 — Schiessbefehl / Übungsanlage:
As a Kp Kdt, I want to generate a Schiessbefehl or Übungsanlage from a template, so that safety and structure requirements are met.

US-15.6 — Rapport-Vorbereitung:
As a Kp Kdt, I want to prepare my Frontrapport and Bat Rap input from my current Kp data, so that I don't forget any reporting items.

US-15.7 — Aktionsplanung (Führungsprozess):
As a Kp Kdt, I want a guided Aktionsplanung workflow that walks me through the Führungsprozess (Erfassen → Beurteilen → Entschliessen → Befehlen), so that I don't skip steps and my BdL is complete.

**CLI:**
```bash
milanon pack --workflow kp-befehl --input anon/ --unit "Inf Kp 56/1"
milanon pack --workflow wachtdienst --input anon/ --unit "Inf Kp 56/1"
milanon pack --workflow ausbildungsplan --input anon/ --unit "Inf Kp 56/1"
milanon pack --workflow aktionsplanung --input anon/ --unit "Inf Kp 56/1"
```

**GUI:** Workflow dropdown on the LLM Workflow page replaces the template dropdown.

---

#### Epic E16: Claude Project Generator
**Goal:** MilAnon can generate a complete Claude Project setup (system prompt + project knowledge files + instructions) that other Kdt can import and use immediately.

**User Stories:**

US-16.1: As a Kp Kdt, I want MilAnon to generate Claude Project instructions for my unit, so that I can create a Claude Project that knows my Kp, my Bat, and Swiss doctrine.

US-16.2: As a Bat Kdt, I want to share a pre-configured Claude Project template with all my Kp Kdt, so that everyone has the same quality baseline.

US-16.3: As a Kp Kdt, I want to export my MilAnon configuration as a "Starter Kit" that another Kdt can import, so that onboarding a new Kdt takes minutes, not days.

**What a Claude Project contains:**
```
project/
  system_prompt.md          # Role, doctrine, rules, unit context
  knowledge/
    CONTEXT.md              # Unit hierarchy (auto-generated by MilAnon)
    bfe_auszug.md           # Relevant BFE chapters
    wachtdienst_auszug.md   # Relevant Wachtdienst chapters
    taktik_auszug.md        # Relevant Taktik chapters
    begriffe.md             # Military terminology glossary
  instructions.md           # How to use the project (for the Kdt)
```

**CLI:**
```bash
milanon project generate --unit "Inf Kp 56/1" --output ~/claude_project/
# → Generates all files ready to upload as Claude Project Knowledge
```

---

#### Epic E17: Multi-Format Output
**Goal:** Generate finished documents in the format the commander needs — not just Markdown.

**User Stories:**

US-17.1: As a Kp Kdt, I want my Kompaniebefehl as a formatted DOCX with correct headers, page numbers, and Swiss Army letterhead, so that I can print and distribute it directly.

US-17.2: As a Kp Kdt, I want my WAP as an Excel sheet with the correct weekly grid layout, so that I can share it with my Kp Stab.

US-17.3: As a Kp Kdt, I want templates for standard military document formats (Befehl, Wachdienstbefehl, Übungsanlage, Marschbefehl), so that the output looks professional.

**Implementation:**
```bash
milanon export --input vault/kp_befehl.md --format docx --template armee-befehl
milanon export --input vault/wap.md --format xlsx --template wochenplan
```

---

#### Epic E18: Shared Knowledge & Onboarding
**Goal:** Knowledge transfer between commanders. A new Kp Kdt gets a complete starter kit.

**User Stories:**

US-18.1: As a Kp Kdt, I want to export my complete MilAnon setup (DB, templates, doctrine, vault structure) as a portable package, so that my successor can start where I left off.

US-18.2: As a Bat Kdt, I want a standardized "Bat Starter Kit" that all Kp Kdt import, so that naming conventions, unit hierarchy, and doctrine references are consistent across the battalion.

US-18.3: As a Kp Kdt, I want to import my predecessor's MilAnon package, so that I have all previous year's data, person mappings, and document templates from day one.

---

## Roadmap — The Path to v1.0

### Phase 1: Foundation (v0.3.0 — DONE ✅)
MilAnon Core: Anonymize → Claude → De-Anonymize → Vault
- All recognition, Pack/Unpack, Review Loop, Military Hierarchy
- 520+ tests, CLI + GUI, Open Source

### Phase 2: Doctrine Integration (v0.5.0 — April 2026)
**Epic E14: Doctrine Knowledge Base**
- Upload BFE + Wachtdienst + FSO as doctrine files
- Chapter-level indexing (only include relevant sections in prompts)
- `milanon pack --workflow kp-befehl` uses BFE structure

**Epic E15.1-15.3: Core Workflows**
- Kompaniebefehl workflow (highest value, most complex)
- Wachtdienstbefehl workflow
- Ausbildungsplanung workflow

### Phase 3: Project Generator (v0.7.0 — May 2026)
**Epic E16: Claude Project Generator**
- Generate complete Claude Project setups
- Sharable between commanders
- Pre-configured with unit context + doctrine

**Epic E15.4-15.7: Additional Workflows**
- WAP, Schiessbefehl, Rapport, Aktionsplanung

### Phase 4: Professional Output (v0.8.0 — June 2026)
**Epic E17: Multi-Format Output**
- DOCX export with Swiss Army formatting
- XLSX export for planning documents
- Print-ready templates

### Phase 5: Sharing & Onboarding (v1.0 — Q3 2026)
**Epic E18: Shared Knowledge**
- Export/Import of complete MilAnon setups
- Bat Starter Kits
- Predecessor → Successor handover

---

## Success Metrics

| Metric | Today | With v1.0 |
|---|---|---|
| Time to create Kp Befehl | 2-3 days (or never for new Kdt) | 2-3 hours |
| Time for WAP creation | 2-3 hours per week | 20 minutes |
| Time for Wachtdienstbefehl | 3-4 hours | 15 minutes |
| Onboarding new Kp Kdt | Weeks (find templates, learn formats) | 1 hour (import starter kit) |
| Doctrine conformity | Depends on Kdt experience | Guaranteed (BFE-based) |
| Data security | Risk (ChatGPT with real data) | Guaranteed (local anonymization) |
| Knowledge transfer | Lost when Kdt changes | Preserved in exportable package |

---

## Technical Architecture for v1.0

```
┌─────────────────────────────────────────────────────┐
│                    MilAnon v1.0                      │
├──────────────┬──────────────────┬───────────────────┤
│  Layer 1:    │  Layer 2:        │  Layer 3:         │
│  Core Engine │  Workflows       │  Output & Share   │
│              │                  │                   │
│  Parsers     │  Doctrine KB     │  DOCX Generator   │
│  Recognizers │  Workflow Engine  │  XLSX Generator   │
│  Anonymizer  │  Pack Builder    │  Project Generator │
│  DeAnonymizer│  Prompt Templates│  Export/Import     │
│  Mapping DB  │  Claude Projects │  Starter Kits      │
└──────────────┴──────────────────┴───────────────────┘
         ↕              ↕                ↕
    Local SQLite    data/doctrine/    Obsidian Vault
                    data/templates/   DOCX / XLSX
                                      Claude.ai
```

---

## Competitive Landscape

| Solution | Security | Doctrine | Workflows | Sharing |
|---|---|---|---|---|
| Manual (Word/Excel) | ✅ Local | ❌ Manual | ❌ None | ❌ Copy-paste |
| ChatGPT Custom GPT | ❌ Cloud | ⚠️ User-provided | ⚠️ Basic | ❌ Per-user |
| Claude Project | ❌ Cloud | ⚠️ User-provided | ⚠️ Basic | ⚠️ Shared |
| **MilAnon v1.0** | **✅ Local** | **✅ Built-in** | **✅ BFE-based** | **✅ Starter Kits** |
