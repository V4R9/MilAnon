# MEGA-PROMPT: Paket A — Doctrine Chapter Extraction Engine

## Context
Read CLAUDE.md first. You're working on MilAnon, a Swiss Army anonymization + command assistant tool.

## Your Task
Build a doctrine chapter extraction engine. The project has 11 Swiss Army regulation files (~3MB total Markdown) in `data/doctrine/`. We need to extract specific chapters into smaller files in `data/doctrine/extracts/` for token-efficient LLM prompts.

## Branch
```bash
git checkout -b feat/e14-doctrine-extraction
```

## What to Build

### 1. `src/milanon/usecases/doctrine.py`

A `DoctrineExtractUseCase` that:
- Reads `data/doctrine/INDEX.yaml` (already exists — read it first to understand the structure)
- For each extract defined in INDEX.yaml under `workflows.*.doctrine.*.extract`:
  - Opens the source .md file from `data/doctrine/`
  - Finds chapter boundaries by heading patterns (see below)
  - Extracts the content between start heading and next same-level heading
  - Writes to `data/doctrine/extracts/{extract_name}.md`

Heading patterns vary by regulation:
- BFE (52_080): `## 5.4 Führungstätigkeit: Beurteilung der Lage` or `# 5.1.2 Problemerfassung`
- FSO (50_040): `### 4.2.4 Beurteilung der Lage` or `## 4.2 Aktionsplanung`  
- TF (50_030): `## 5.2 Grundsätze der Taktik` or `### 5.2.1 Einsatzgrundsätze`

Strategy: Use regex to find headings that match a chapter number pattern, then extract everything until the next heading at the same or higher level.

### 2. Extract Definitions

Create these 14 extract files:

| Extract filename | Source file | Chapter/Section |
|---|---|---|
| `bfe_initialisierung.md` | 52_080_bfe_einsatz.md | Kap 5.1.1 |
| `bfe_problemerfassung.md` | 52_080_bfe_einsatz.md | Kap 5.1.2 |
| `bfe_sofortmassnahmen.md` | 52_080_bfe_einsatz.md | Kap 5.2 |
| `bfe_zeitplanung.md` | 52_080_bfe_einsatz.md | Kap 5.3 |
| `bfe_bdl.md` | 52_080_bfe_einsatz.md | Kap 5.4 (all of 5.4.1, 5.4.2, 5.4.3) |
| `bfe_entschlussfassung.md` | 52_080_bfe_einsatz.md | Kap 5.5 (all of 5.5.1, 5.5.2, 5.5.3) |
| `bfe_planentwicklung.md` | 52_080_bfe_einsatz.md | Kap 5.6 |
| `bfe_befehlsgebung.md` | 52_080_bfe_einsatz.md | Kap 5.7 (all of 5.7.1, 5.7.2) |
| `fso_aktionsplanung.md` | 50_040_fso_17.md | Kap 4.2 (Zif 110 through end of 4.2.7) |
| `tf_einsatzgrundsaetze.md` | 50_030_taktische_fuehrung.md | Kap 5.2.1 (Zif 5007-5038) |
| `tf_taktische_grundsaetze.md` | 50_030_taktische_fuehrung.md | Kap 5.2.3 (Zif 5045-5070) |
| `tf_raumordnung.md` | 50_030_taktische_fuehrung.md | Kap 5.4 (Zif 5114-5178) |
| `tf_taktische_aufgaben.md` | 50_030_taktische_fuehrung.md | Kap 5.5 (Zif 5179-5182) |
| `wat_wachtdienstbefehl.md` | 51_301_wachtdienst_aller_truppen.md | Chapters about Wachtdienstbefehl structure |

### 3. CLI Commands: `src/milanon/cli/doctrine_commands.py`

Create a click command group (DO NOT modify cli/main.py — that's for a later integration paket):

```python
@click.group()
def doctrine():
    """Manage doctrine knowledge base."""
    pass

@doctrine.command()
def list():
    """List all available doctrine files and their key chapters."""
    
@doctrine.command()  
@click.option("--workflow", help="Extract chapters for a specific workflow")
@click.option("--all", is_flag=True, help="Extract all defined chapters")
def extract(workflow, all):
    """Extract doctrine chapters into compact files for prompts."""
```

### 4. Tests: `tests/usecases/test_doctrine.py`

Write tests that:
- test_extract_bfe_chapter_5_1_1_returns_content_with_initialisierung
- test_extract_bfe_chapter_5_4_returns_full_bdl_section  
- test_extract_fso_4_2_returns_aktionsplanung
- test_extract_tf_5_2_1_returns_einsatzgrundsaetze
- test_extract_all_creates_14_files
- test_list_doctrine_returns_11_source_files
- test_extract_nonexistent_chapter_logs_warning

## Files you MUST NOT touch
- `src/milanon/domain/` (any file)
- `src/milanon/adapters/` (any file)  
- `src/milanon/cli/main.py`
- `src/milanon/usecases/pack.py`
- `data/doctrine/*.md` (the source files — read only!)
- `data/doctrine/INDEX.yaml` (read only!)

## Run tests
```bash
cd /Users/sd/Documents/GitHub/Anonymizer_Tool_Army
python -m pytest tests/usecases/test_doctrine.py -v
python -m pytest tests/ -x  # full suite must still pass
```

## Commit
```bash
git add -A
git commit -m "feat(e14): doctrine chapter extraction engine with 14 extract files

- DoctrineExtractUseCase: semi-automatic chapter extraction from reglemente
- Heading-boundary detection for BFE, FSO, TF, WAT formats
- 14 extract files generated in data/doctrine/extracts/
- CLI: milanon doctrine list|extract commands (not yet wired to main CLI)
- Tests: 7 new tests covering extraction, listing, error cases"
```
