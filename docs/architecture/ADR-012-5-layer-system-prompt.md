# ADR-012: 5-Layer System Prompt Architecture

## Status: Accepted
## Date: 2026-03-25

## Context

The `milanon pack` command assembles a prompt for Claude. Currently it uses simple Markdown templates. For the 5+2 Command Assistant, prompts need to be context-aware, doctrine-informed, and step-specific.

## Decision

Every prompt is assembled from 5 layers, each with a distinct responsibility:

```
┌──────────────────────────────────────────────┐
│ Layer 1: ROLE (static)                       │
│ "Du bist der Stabsassistent eines Kp Kdt..." │
│ Includes: 5+2 process, taktische Kompetenz,  │
│ Einsatzgrundsätze, Auftragstaktik-Regeln     │
├──────────────────────────────────────────────┤
│ Layer 2: UNIT CONTEXT (from milanon context) │
│ "Deine Einheit: [EINHEIT_001] = Inf Kp 56/1 │
│  Bat: Inf Bat 56 → Ter Div 2..."            │
├──────────────────────────────────────────────┤
│ Layer 3: DOCTRINE (workflow+mode specific)   │
│ Extracted chapters from BFE/FSO/TF/WAT       │
│ Only the chapters relevant to current step   │
├──────────────────────────────────────────────┤
│ Layer 4: TASK (step-specific instructions)   │
│ "Du bist in Schritt 2: BdL. Führe durch     │
│  AUGEZ mit AEK-Methode. Produziere:..."     │
│ Includes: Skeleton (if Befehlsgebung step)   │
├──────────────────────────────────────────────┤
│ Layer 5: RULES (static)                      │
│ "Preserve [PLACEHOLDER] tokens, mark         │
│  decisions with <!-- KDT ENTSCHEID -->,      │
│  use Obsidian wiki-links, flag open Qs..."   │
└──────────────────────────────────────────────┘
```

## Rationale

1. **Separation of concerns** — Each layer changes at a different rate. Layer 1 is stable. Layer 3 changes per workflow. Layer 4 changes per step.
2. **Token efficiency** — Only include the doctrine chapters needed for the current step. BFE Kap 5.1 for Problemerfassung, BFE Kap 5.4 for BdL, etc.
3. **Reusability** — Layers 1, 2, 5 are shared across all workflows. Only Layer 3+4 vary.
4. **Claude Project compatibility** — For the Project Generator (E16), Layers 1+2+5 become the System Prompt, Layer 3 becomes Project Knowledge, Layer 4 becomes the user's instructions.

## Assembly

The Pack builder reads INDEX.yaml to determine which doctrine chapters to extract for Layer 3, and which task template to use for Layer 4. The `--mode` flag (berrm/adf) influences which mode-specific content is included.

```bash
milanon pack --workflow ei-bf --mode berrm --step 3 --unit "Inf Kp 56/1"
# Layer 1: templates/role.md (static)
# Layer 2: auto-generated from milanon context
# Layer 3: extracts/bfe_entschlussfassung.md + extracts/tf_kap5_einsatzgrundsaetze.md
# Layer 4: templates/entschlussfassung.md + skeletons/5_punkte_befehl_universal.md (Berrm markers only)
# Layer 5: templates/rules.md (static)
```

## Consequences

- `data/templates/` directory for Layer 1, 4, 5 templates
- `data/doctrine/extracts/` for Layer 3 chapter extracts
- INDEX.yaml maps: workflow × step × mode → (doctrine chapters, task template, skeleton)
- `--context` flag allows adding Vault files (previous step outputs) as additional input between Layer 4 and the user documents
