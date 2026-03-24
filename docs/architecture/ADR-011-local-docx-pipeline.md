# ADR-011: Local DOCX Generation Pipeline

## Status: Accepted
## Date: 2026-03-25

## Context

Commanders need to distribute Befehle as formatted DOCX files (for printing, filing, and presenting to the Bat Kdt). The question: who generates the DOCX?

Options evaluated:
- **A: LLM generates DOCX** — Claude writes directly into a DOCX template. Requires cloud, complex prompting, unreliable formatting.
- **B: Manual formatting** — Commander copy-pastes from Markdown into Word. Time-consuming, error-prone.
- **C: Local code generates DOCX** — MilAnon converts structured Markdown to DOCX using python-docx, applying the official Armee-Vorlage styles. Completely offline, deterministic, de-anonymizes in the same step.

## Decision

**Option C: Local DOCX generation from structured Markdown with simultaneous de-anonymization.** The LLM produces content (with placeholders). Code produces the document.

## Rationale

1. **Separation of concerns** — The LLM is good at THINKING (content, doctrine, structure). Code is good at FORMATTING (styles, tables, page layout). Use each for what it does best.
2. **Deterministic** — DOCX generation is a mapping problem, not a creative one. `### 3 Aufträge` → Style "1. Main title" is always the same. No LLM needed.
3. **Security** — De-anonymization happens locally. `[PERSON_001]` → "Hptm Degen" never touches the cloud.
4. **Official template compliance** — python-docx uses the actual Armee-Vorlage (`befehl_vorlage.docx`) as base template. All styles, fonts, margins, headers/footers are correct by construction.
5. **One command** — `milanon export vault/befehl.md --docx --deanonymize` does everything.

## Technical Design

```
Input:  Structured Markdown (from Claude, stored in Vault)
        + Armee-Vorlage DOCX (template with correct styles)
        + Mapping DB (SQLite with entity → cleartext mappings)

Process:
  1. Parse Markdown → identify structure (headings, bullets, tables)
  2. Open DOCX template as base document (preserves styles, headers, footers)
  3. Map Markdown elements to DOCX styles:
     - ### → "1. Main title"
     - #### → "1.1 Title"
     - ##### → "1.1.1 Title"
     - Text → "Text Indent"
     - - Bullet → "Bullet List 1"
     - | Table | → DOCX Table (Aufträge: Nx2 with Einheit links, Bullets rechts)
  4. Replace all [PLACEHOLDER] tokens with cleartext from DB
  5. Save as new DOCX

Output: Druckfertiges DOCX mit echten Namen, korrekten Styles, Armee-konform
```

## DOCX Style Mapping (from template analysis)

| Markdown | DOCX Style | Font/Size |
|---|---|---|
| `# Grundlagen` | Heading 1 | Bold, indented |
| `## "DECKNAME"` | Subject heading | Bold, 13pt |
| `### 1 Orientierung` | 1. Main title | Auto-numbered |
| `#### 1.1 Bedrohung` | 1.1 Title | Auto-numbered |
| `##### 1.1.1 Bestimmend` | 1.1.1 Title | Auto-numbered |
| Paragraph text | Text Indent | Normal, indented |
| `- Bullet item` | Bullet List 1 | With bullet char |
| Aufträge-Tabelle | Table Nx2 | Col1=~4cm (Einheit), Col2=~4.3cm (Bullets) |

## Consequences

- python-docx is a dependency (already available, no network needed)
- DOCX templates stored in `data/templates/docx/` (binary files, committed to repo)
- The Markdown output from Claude MUST be consistently structured (enforced by skeleton + Layer 5 rules)
- De-anonymization in DOCX = text replacement across all paragraphs, table cells, headers, footers
- Taktische Symbole (left column in Aufträge table) remain as placeholder for manual insertion (images can't be auto-generated)
