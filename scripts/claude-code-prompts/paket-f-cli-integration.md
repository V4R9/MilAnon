# MEGA-PROMPT: Paket F — CLI Integration (wires everything together)

## Context
Read CLAUDE.md. This paket WIRES the new features (from Pakets A-E) into the existing CLI.
Read `src/milanon/cli/main.py` CAREFULLY before making changes — understand every existing command.

## IMPORTANT: This paket depends on A+B being merged into main first!
```bash
git checkout main
git pull
git checkout -b feat/e15-cli-integration
```

## What to Build

### Modify: `src/milanon/cli/main.py`

Add these new capabilities to the EXISTING CLI. Do NOT break existing commands.

#### 1. Extend `pack` command with `--workflow`, `--mode`, `--context`, `--step`

The existing `pack` command uses `PackUseCase`. When `--workflow` is provided, use `WorkflowPackUseCase` instead.

```python
@cli.command()
@click.argument("input_path", type=click.Path(exists=True))
@click.option("--template", default="frei", help="Template name (for non-workflow mode)")
@click.option("--workflow", default=None, help="Workflow name: analyse, ei-bf, wachtdienst, bdl, entschluss")
@click.option("--mode", default=None, help="Mode: berrm or adf (default from config)")
@click.option("--step", default=None, type=int, help="5+2 step number (1-5)")
@click.option("--unit", default="", help="Unit designation for context")
@click.option("--context", "context_path", default=None, type=click.Path(exists=True), help="Path to previous step outputs")
@click.option("--output", default=None, type=click.Path(), help="Write pack to file instead of clipboard")
@click.option("--prompt", default="", help="Custom prompt text (for frei template)")
@click.option("--no-clipboard", is_flag=True, help="Don't copy to clipboard")
def pack(input_path, template, workflow, mode, step, unit, context_path, output, prompt, no_clipboard):
    """Build a prompt pack for LLM interaction."""
    if workflow:
        # Use WorkflowPackUseCase
        from milanon.usecases.workflow_pack import WorkflowPackUseCase
        from milanon.usecases.generate_context import GenerateContextUseCase
        repo = _get_repository()
        ctx_gen = GenerateContextUseCase(repo)
        use_case = WorkflowPackUseCase(repo, ctx_gen)
        
        resolved_mode = mode or _get_config_mode()  # from project config or default "berrm"
        
        text, result = use_case.execute(
            workflow=workflow,
            mode=resolved_mode,
            step=step,
            input_path=Path(input_path),
            unit=unit,
            context_path=Path(context_path) if context_path else None,
            output_path=Path(output) if output else None,
            copy_clipboard=not no_clipboard,
        )
    else:
        # Existing PackUseCase (backward compatible)
        ...existing code...
```

#### 2. Add `doctrine` command group

```python
@cli.group()
def doctrine():
    """Manage doctrine knowledge base."""
    pass

@doctrine.command("list")
def doctrine_list():
    """List available doctrine files and chapters."""
    from milanon.usecases.doctrine import DoctrineExtractUseCase
    use_case = DoctrineExtractUseCase()
    ...

@doctrine.command("extract") 
@click.option("--workflow", help="Extract chapters for a specific workflow")
@click.option("--all", "extract_all", is_flag=True, help="Extract all defined chapters")
def doctrine_extract(workflow, extract_all):
    """Extract doctrine chapters into compact files."""
    ...
```

#### 3. Add `export` command

```python
@cli.command()
@click.argument("input_path", type=click.Path(exists=True))
@click.option("--docx", is_flag=True, help="Export as DOCX")
@click.option("--template", default=None, type=click.Path(), help="DOCX template file")
@click.option("--deanonymize", is_flag=True, help="Replace placeholders with real values")
@click.option("--output", default=None, type=click.Path(), help="Output file path")
def export(input_path, docx, template, deanonymize, output):
    """Export Markdown to DOCX with optional de-anonymization."""
    if docx:
        from milanon.usecases.export_docx import ExportDocxUseCase
        from milanon.adapters.writers.docx_befehl_writer import DocxBefehlWriter
        ...
```

#### 4. Add `config` command group

```python
@cli.group()
def config():
    """Manage project configuration."""
    pass

@config.command("set")
@click.argument("key")
@click.argument("value")
def config_set(key, value):
    """Set a config value (e.g. mode, unit)."""
    # Store in .milanon/config.yaml
    ...

@config.command("get")
@click.argument("key")
def config_get(key):
    """Get a config value."""
    ...
```

### Tests: `tests/cli/test_cli_integration.py`

- test_pack_with_workflow_flag_uses_workflow_pack
- test_pack_with_mode_flag_passes_through
- test_pack_with_context_flag_includes_path
- test_pack_without_workflow_uses_old_pack (backward compat!)
- test_doctrine_list_exits_zero
- test_doctrine_extract_all_exits_zero
- test_export_docx_creates_file
- test_export_docx_deanonymize_flag
- test_config_set_and_get_roundtrip

## CRITICAL: Backward Compatibility
ALL existing `milanon pack --template ...` commands MUST still work exactly as before.
ALL existing tests MUST still pass.

## Files you MUST NOT touch
- `src/milanon/domain/` (any file)
- `src/milanon/adapters/parsers/` (any file)
- `src/milanon/adapters/recognizers/` (any file)
- `src/milanon/usecases/anonymize.py`
- `src/milanon/usecases/deanonymize.py`

## Run tests
```bash
python -m pytest tests/ -x -v  # EVERYTHING must pass
python -m pytest tests/cli/ -v  # Focus on CLI tests
```

## Commit
```bash
git add -A
git commit -m "feat(e15): CLI integration — workflow, doctrine, export, config commands

- pack: --workflow, --mode, --context, --step flags (backward compatible)
- doctrine: list and extract subcommands
- export: --docx with --deanonymize flag
- config: set/get for project-level settings (mode, unit)
- Tests: 9 new CLI integration tests
- All 520+ existing tests still passing"
```
