# MEGA-PROMPT: Paket B — 5-Layer Workflow Pack Engine

## Context
Read CLAUDE.md first. You're working on MilAnon, a Swiss Army anonymization + command assistant tool.

Read the existing `src/milanon/usecases/pack.py` to understand the current PackUseCase. You are building a NEW class `WorkflowPackUseCase` that extends the concept with doctrine-aware 5-layer prompt assembly.

## Branch
```bash
git checkout -b feat/e15-workflow-infrastructure
```

## What to Build

### 1. `src/milanon/domain/workflow.py` — Workflow Config

```python
"""Workflow configuration domain model — parsed from INDEX.yaml."""
from dataclasses import dataclass, field
from pathlib import Path
import yaml

@dataclass
class DoctrineRef:
    source: str           # Full doctrine file in data/doctrine/
    extract: str | None   # Extract file in data/doctrine/extracts/

@dataclass 
class WorkflowConfig:
    name: str
    description: str
    system_prompt: str              # Layer 4 template filename
    doctrine: list[DoctrineRef]     # Layer 3 sources
    skeleton: str | None            # Skeleton filename (if Befehlsgebung)
    output_format: list[str]        # ["markdown", "docx"]
    maps_to_5plus2: str             # Which 5+2 step this maps to
    depends_on: list[str] = field(default_factory=list)

def load_workflows(index_path: Path) -> dict[str, WorkflowConfig]:
    """Parse INDEX.yaml and return workflow configs keyed by workflow name."""
    ...
```

Read `data/doctrine/INDEX.yaml` (it exists already) to understand the exact YAML structure. Parse the `workflows:` section into WorkflowConfig objects.

### 2. `src/milanon/usecases/workflow_pack.py` — The Engine

```python
"""WorkflowPackUseCase — builds doctrine-aware 5-layer prompts."""

class WorkflowPackUseCase:
    """Assembles a 5-layer prompt for a given workflow, mode, and step.
    
    Layer 1: Role (static) — from data/templates/role.md
    Layer 2: Unit Context — from GenerateContextUseCase
    Layer 3: Doctrine — chapter extracts from data/doctrine/extracts/
    Layer 4: Task — workflow-specific template from data/templates/workflows/
    Layer 5: Rules (static) — from data/templates/rules.md
    
    Plus: Anonymized documents from --input
    Plus: Previous step outputs from --context
    """
    
    def __init__(self, repository, context_generator):
        self._repo = repository
        self._context_gen = context_generator  # GenerateContextUseCase
    
    def execute(
        self,
        workflow: str,           # "analyse", "ei-bf", "wachtdienst"
        mode: str = "berrm",    # "berrm" or "adf"
        step: int | None = None, # 1-5 for specific 5+2 step
        input_path: Path = ...,  # anonymized documents
        unit: str = "",          # "Inf Kp 56/1"
        context_path: Path | None = None,  # vault dir with previous outputs
        output_path: Path | None = None,
        copy_clipboard: bool = True,
    ) -> tuple[str, PackResult]:
        ...
```

**Assembly logic:**

1. Load WorkflowConfig from INDEX.yaml for the given workflow name
2. Load Layer 1: Read `data/templates/role.md`. If file doesn't exist, use a placeholder.
3. Load Layer 2: Call `self._context_gen.execute(unit=unit)` to get unit hierarchy text
4. Load Layer 3: For each `doctrine` entry in the workflow config, read the extract file from `data/doctrine/extracts/`. If extract file doesn't exist, log a warning and skip.
5. Load Layer 4: Read `data/templates/workflows/{workflow_config.system_prompt}`. If a skeleton is defined AND we're in step 5 (Befehlsgebung), append the skeleton content.
6. Load Layer 5: Read `data/templates/rules.md`. If doesn't exist, use placeholder.
7. **Mode filtering**: Strip `<!-- ADF: ... -->` blocks if mode is "berrm" and vice versa. Keep `<!-- BOTH: ... -->`, `<!-- KDT ENTSCHEID: ... -->`, `<!-- FILL: ... -->` blocks always.
8. Load anonymized documents from input_path (same logic as existing PackUseCase)
9. Load context files from context_path (if provided): read all .md files in the directory
10. Assemble in order: Layer 1, Layer 2, Layer 3, Layer 4, "---", Context files, "---", Documents
11. Copy to clipboard / write to file (reuse existing logic from PackUseCase)

**Mode marker stripping:**
```python
def _strip_mode_markers(text: str, mode: str) -> str:
    """Remove mode-specific HTML comments that don't apply.
    
    Keep: <!-- BERRM: ... --> if mode is "berrm"
    Strip: <!-- ADF: ... --> if mode is "berrm"
    Always keep: <!-- BOTH: -->, <!-- KDT ENTSCHEID: -->, <!-- FILL: -->
    """
    import re
    if mode == "berrm":
        # Remove ADF blocks (single-line comments)
        text = re.sub(r'<!--\s*ADF:.*?-->', '', text)
    elif mode == "adf":
        text = re.sub(r'<!--\s*BERRM:.*?-->', '', text)
    return text
```

### 3. Tests

`tests/domain/test_workflow.py`:
- test_load_workflows_parses_index_yaml
- test_workflow_config_has_required_fields
- test_unknown_workflow_raises_keyerror

`tests/usecases/test_workflow_pack.py`:
- test_assemble_includes_all_5_layers
- test_mode_berrm_strips_adf_markers
- test_mode_adf_strips_berrm_markers  
- test_kdt_entscheid_markers_always_kept
- test_context_path_includes_vault_files
- test_missing_extract_logs_warning_continues
- test_missing_template_raises_clear_error
- test_documents_appended_after_layers
- test_copy_clipboard_called_when_enabled

Use the existing `pack.py` test patterns and `conftest.py` fixtures.

## Important: Reuse existing infrastructure
- Import `PackResult` from `usecases/pack.py` (don't redefine)
- Import `_copy_to_clipboard` from `usecases/pack.py` (don't redefine)
- Import `GenerateContextUseCase` from `usecases/generate_context.py`

## Files you MUST NOT touch
- `src/milanon/domain/entities.py`
- `src/milanon/domain/protocols.py`
- `src/milanon/domain/anonymizer.py`
- `src/milanon/domain/deanonymizer.py`
- `src/milanon/adapters/` (any file)
- `src/milanon/cli/main.py`
- `src/milanon/usecases/pack.py` (read it for reference, but create NEW file)
- `data/doctrine/` (read only)
- `data/templates/` (read only — Paket C/D creates files there)

## Run tests
```bash
cd /Users/sd/Documents/GitHub/Anonymizer_Tool_Army
python -m pytest tests/domain/test_workflow.py tests/usecases/test_workflow_pack.py -v
python -m pytest tests/ -x  # full suite must still pass
```

## Commit
```bash
git add -A
git commit -m "feat(e15): workflow pack engine with 5-layer prompt assembly

- WorkflowConfig domain model with INDEX.yaml parser
- WorkflowPackUseCase: assembles Role+Context+Doctrine+Task+Rules
- Mode marker stripping (ADF/Berrm)
- Context chaining (--context for previous step outputs)
- Reuses PackResult and clipboard from existing pack module
- Tests: 12 new tests covering assembly, mode filtering, error handling"
```
