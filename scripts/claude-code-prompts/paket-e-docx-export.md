# MEGA-PROMPT: Paket E — Local DOCX Export Pipeline

## Context
Read CLAUDE.md. You're building the DOCX generation feature described in `docs/architecture/ADR-011-local-docx-pipeline.md`.
Read `data/doctrine/skeletons/README.md` for the DOCX style mapping.
The DOCX template is at `data/templates/docx/befehl_vorlage.docx` — analyze its styles with python-docx before writing code.

## Branch
```bash
git checkout -b feat/e17-docx-export
```

## What to Build

### 1. `src/milanon/adapters/writers/docx_befehl_writer.py`

A writer that converts structured Markdown into a properly formatted DOCX using the Armee-Vorlage as template.

**Style mapping (from template analysis):**
| Markdown | DOCX Style Name | Notes |
|---|---|---|
| `# Grundlagen` | "Heading 1" | Only for "Grundlagen" header |
| `## "DECKNAME"` | "Subject heading" | Bold, 13pt |
| `### 1 Orientierung` | "1. Main title" | Auto-numbered main points |
| `#### 1.1 Bedrohung` | "1.1 Title" | Sub-points |
| `##### 1.1.1 Bestimmend` | "1.1.1 Title" | Sub-sub-points |
| Body text | "Text Indent" | Regular paragraphs |
| `- Bullet item` | "Bullet List 1" | Bullet lists |
| `1. Item` | "Numbered List 2" | For Beilagen |

**Special handling for Aufträge (Punkt 3):**
When encountering a Markdown table under ### 3 Aufträge:
```markdown
| Element | Auftrag |
|---|---|
| Z Ambos | - NIMMT und SICHERT Ags WEST; |
| Z Canale | - SPERRT auf Höhe CHUR. |
```
Convert to DOCX Table(Nx2) where:
- Left column: ~4cm width, Einheitsbezeichnung (no style or Normal)
- Right column: ~4.3cm width, "Bullet List 1" style for each auftrag line

**Steps:**
1. Open template DOCX as base (`python-docx` Document)
2. Clear template placeholder content (keep styles, headers, footers)
3. Parse Markdown line by line
4. For each line, determine the correct DOCX style based on prefix (###, ####, -, etc.)
5. Add paragraph with correct style
6. For tables: create DOCX table with correct column widths
7. Replace header/footer placeholders if present

### 2. `src/milanon/usecases/export_docx.py`

```python
class ExportDocxUseCase:
    """Export a Markdown Befehl to DOCX with optional de-anonymization."""
    
    def __init__(self, repository, writer):
        self._repo = repository
        self._writer = writer  # DocxBefehlWriter
    
    def execute(
        self,
        input_path: Path,      # Markdown file
        output_path: Path,     # Output .docx
        template_path: Path,   # befehl_vorlage.docx
        deanonymize: bool = False,
    ) -> Path:
        # 1. Read markdown
        # 2. If deanonymize: replace [PLACEHOLDER] → cleartext from DB
        # 3. Convert to DOCX using writer
        # 4. If deanonymize: also replace in DOCX tables and headers
        # 5. Save and return path
```

**De-anonymization in DOCX:**
After generating the DOCX, iterate over ALL paragraphs and ALL table cells.
For each text run, search for `[TYPE_NNN]` patterns and replace with the cleartext value from the mapping database.

```python
import re
PLACEHOLDER_PATTERN = re.compile(r'\[([A-Z_]+)_(\d{3})\]')

def _deanonymize_docx(doc: Document, repository) -> None:
    """Replace all placeholders in the DOCX with cleartext values."""
    for paragraph in doc.paragraphs:
        _replace_in_paragraph(paragraph, repository)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    _replace_in_paragraph(paragraph, repository)
```

### 3. Tests

`tests/usecases/test_export_docx.py`:
- test_export_creates_docx_file
- test_heading_styles_applied_correctly
- test_auftraege_table_created_with_correct_columns
- test_bullet_lists_use_correct_style
- test_deanonymize_replaces_person_placeholder
- test_deanonymize_replaces_ort_placeholder
- test_deanonymize_in_table_cells
- test_template_header_footer_preserved

`tests/adapters/writers/test_docx_befehl_writer.py`:
- test_markdown_to_docx_basic_structure
- test_heading_level_detection
- test_table_detection_and_conversion

## Files you MUST NOT touch
- `src/milanon/domain/` (any file)
- `src/milanon/cli/main.py`
- `src/milanon/adapters/writers/markdown_writer.py`
- `src/milanon/adapters/writers/docx_writer.py` (existing, for anonymized output — yours is DIFFERENT)
- `src/milanon/usecases/pack.py`

## Dependencies
- python-docx (already in pyproject.toml)

## Commit
```bash
git add -A
git commit -m "feat(e17): local DOCX export pipeline with de-anonymization

- DocxBefehlWriter: Markdown → DOCX with Armee-Vorlage style mapping
- ExportDocxUseCase: orchestrates conversion + optional de-anonymization
- Aufträge table: Nx2 DOCX table (Einheit left, Bullets right)
- Placeholder replacement across paragraphs and table cells
- Tests: 11 new tests for export, styles, de-anonymization"
```
