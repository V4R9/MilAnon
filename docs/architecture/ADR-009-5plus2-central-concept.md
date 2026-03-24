# ADR-009: 5+2 Aktionsplanungsprozess as Central Product Concept

## Status: Accepted
## Date: 2026-03-25

## Context

MilAnon started as an anonymization tool. As we designed the Command Assistant layer, we evaluated multiple approaches for how to help commanders create documents:

- **Option A: Template Filling** — Simple Markdown templates per document type. Claude fills in the blanks.
- **Option B: 5+2 Guided Process** — Claude leads the commander through the complete Aktionsplanungsprozess (BFE 52.080 Kap 5), producing all intermediate products on the way to a final Befehl.
- **Option C: Free-form Chat** — Commander asks Claude anything, Claude answers.

## Decision

We choose **Option B: The 5+2 Aktionsplanungsprozess is THE central concept.** Every workflow in MilAnon is a specialized application of the 5+2. The tool does not just fill templates — it guides the thinking process.

## Rationale

1. **The 5+2 is universal** — whether ADF or Bereitschaftsraum, Einsatzbefehl or Wachtdienstbefehl, the process is always: Problemerfassung → Sofortmassnahmen → Zeitplanung → BdL (AUGEZ+AEK) → Entschlussfassung → Planentwicklung → Befehlsgebung.
2. **Intermediate products have value** — The Problemerfassungs-Matrix, SOMA-Liste, AUGEZ-Analyse, Varianten are useful outputs on their own, not just steps toward a Befehl.
3. **It creates sustainable competitive advantage (VRIO)** — Deep doctrine integration requires domain knowledge that competitors cannot easily replicate.
4. **It teaches** — A new Kdt who uses MilAnon learns the 5+2 by doing it.
5. **It catches errors** — The structured process enforces completeness.
6. **The Berrm paradigm validates this** — In the Bereitschaftsraum mode, the 5+2 is not academic (only for Übungsanlage) but real (for the actual Raum). This makes the 5+2 assistant MORE valuable, not less.

## Consequences

- Every workflow MUST map to one or more steps of the 5+2
- The INDEX.yaml documents the mapping (workflow → 5+2 step)
- System prompts reference doctrine (BFE, FSO) for each step
- Claude must produce ALL intermediate products, not just the final Befehl
- `<!-- KDT ENTSCHEID -->` markers separate Claude's proposals from commander decisions
