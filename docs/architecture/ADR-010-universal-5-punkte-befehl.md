# ADR-010: Universal 5-Punkte-Befehl with Mode Markers

## Status: Accepted
## Date: 2026-03-25

## Context

The Swiss Army has two operational modes for WK planning in 2026:
- **ADF (Ausbildungsdienst der Formationen)** — classical WK with Bf Dienstbetrieb as primary order
- **Berrm (Bereitschaftsraum)** — new paradigm where Ei Bf Berrm (5-Punkte-Befehl) is the primary order

We evaluated whether to create separate skeletons and workflows for each mode or a unified approach.

## Decision

**One universal 5-Punkte-Befehl skeleton with mode markers.** The structure is identical in both modes — only the content changes. Mode markers (`<!-- ADF: ... -->`, `<!-- BERRM: ... -->`) indicate mode-specific content.

A `--mode` flag on the CLI selects the mode. The Pack builder strips irrelevant markers before assembling the prompt.

## Rationale

1. **Verified against official DOCX template** — The CH Armee Befehl Vorlage (Einsatz vs Übung) is structurally identical. Same styles, same hierarchy. Only a header table differs.
2. **5-Punkte-Befehl = 5-Punkte-Befehl** — Points 1-5 exist in both modes. The content under each point differs (e.g. Absicht covers 3 Berrm-Phasen vs WK-Phasen), but the structure is fixed.
3. **Reduces maintenance** — One skeleton to maintain, not two divergent copies.
4. **Flexibility** — The Bat Dossier may arrive in a hybrid format. The universal skeleton handles both.

## Consequences

- `data/doctrine/skeletons/5_punkte_befehl_universal.md` is the PRIMARY skeleton
- Old mode-specific skeletons (500_einsatzbefehl.md, 500_einsatzbefehl_berrm.md) are kept as reference but superseded
- CLI: `milanon pack --workflow ei-bf --mode berrm` or `--mode adf`
- Default mode can be set per project: `milanon config set mode berrm`
- The INDEX.yaml maps workflows to mode-specific doctrine chapters
