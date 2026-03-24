# ADR-013: Doctrine Chapter Extraction

## Status: Accepted
## Date: 2026-03-25

## Context

The doctrine Knowledge Base contains 11 reglemente totaling ~3 MB of Markdown. Claude's context window cannot fit all of them. We need to extract only the relevant chapters per workflow step.

## Decision

**Chapter-level extraction from full reglemente into compact extract files.** Each extract contains only the chapters needed for a specific workflow step. Extraction is semi-automated: a script identifies chapter boundaries by heading patterns, a human verifies the result.

## Extract Files

| Extract | Source | Chapters | Used in Step |
|---|---|---|---|
| `bfe_initialisierung.md` | 52_080 | Kap 5.1.1 | 1: Problemerfassung |
| `bfe_problemerfassung.md` | 52_080 | Kap 5.1.2 | 1: Problemerfassung |
| `bfe_sofortmassnahmen.md` | 52_080 | Kap 5.2 | 1+: SOMA (all steps) |
| `bfe_zeitplanung.md` | 52_080 | Kap 5.3 | 1+: Zeitplanung (all steps) |
| `bfe_bdl.md` | 52_080 | Kap 5.4 | 2: BdL |
| `bfe_entschlussfassung.md` | 52_080 | Kap 5.5 | 3: Entschlussfassung |
| `bfe_planentwicklung.md` | 52_080 | Kap 5.6 | 4: Planentwicklung |
| `bfe_befehlsgebung.md` | 52_080 | Kap 5.7 | 5: Befehlsgebung |
| `fso_aktionsplanung.md` | 50_040 | Kap 4.2 (Zif 110-245) | All steps (reference) |
| `tf_einsatzgrundsaetze.md` | 50_030 | Kap 5.2.1 (Zif 5007-5038) | 3: Variant evaluation |
| `tf_taktische_grundsaetze.md` | 50_030 | Kap 5.2.3 (Zif 5045-5070) | 2+3: BdL + Varianten |
| `tf_raumordnung.md` | 50_030 | Kap 5.4 (Zif 5114-5178) | 4: Planentwicklung |
| `tf_taktische_aufgaben.md` | 50_030 | Kap 5.5 (Zif 5179-5182) | 3+5: Absicht + Aufträge |
| `wat_wachtdienstbefehl.md` | 51_301 | Wachtdienst-Befehlsstruktur | Workflow: Wachtdienst |

## Consequences

- `data/doctrine/extracts/` holds all extract files
- INDEX.yaml references extracts, not full doctrine files, in workflow definitions
- A `milanon doctrine extract` CLI command can regenerate extracts from full files
- Extracts are committed to the repo (not generated at runtime) — they are curated, not just sliced
