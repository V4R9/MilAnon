# MEGA-PROMPT: Paket H — Terminal Pretty-Print with Rich
# MODEL: Sonnet

## Context
Read CLAUDE.md. Read `src/milanon/cli/main.py` completely — you'll modify the output formatting of EVERY command.

## Branch
```bash
git checkout -b feat/cli-rich-output
```

## Your Task
Replace plain click.echo() output with Rich panels, tables, and styled text for a professional CLI experience.

## Step 1: Add Rich dependency
In pyproject.toml, add `"rich>=13.0"` to dependencies.

## Step 2: Create a CLI output helper
Create `src/milanon/cli/output.py`:

```python
"""Rich output helpers for MilAnon CLI."""
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

console = Console()

def print_header(title: str, subtitle: str = ""):
    """Print a styled header panel."""
    text = Text(title, style="bold cyan")
    if subtitle:
        text.append(f"\n{subtitle}", style="dim")
    console.print(Panel(text, box=box.ROUNDED, border_style="cyan"))

def print_result_table(rows: list[tuple[str, str]], title: str = ""):
    """Print a key-value result table."""
    table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    table.add_column("Key", style="cyan", width=20)
    table.add_column("Value", style="white")
    for key, value in rows:
        table.add_row(key, value)
    if title:
        console.print(Panel(table, title=title, box=box.ROUNDED, border_style="cyan"))
    else:
        console.print(table)

def print_success(msg: str):
    console.print(f"  ✅ {msg}", style="green bold")

def print_warning(msg: str):
    console.print(f"  ⚠️  {msg}", style="yellow")

def print_error(msg: str):
    console.print(f"  ❌ {msg}", style="red bold")

def print_file_list(files: list[str], title: str = "Files"):
    for f in files:
        console.print(f"  → {f}", style="dim")
```

## Step 3: Update every command in main.py

Replace all click.echo() calls with Rich equivalents. Examples:

### `anonymize` command — before:
```python
click.echo(click.style(f"Scanned:   {result.files_scanned}", fg="cyan"))
click.echo(click.style(f"New:       {result.files_new}", fg="green"))
```

### `anonymize` command — after:
```python
from milanon.cli.output import print_header, print_result_table, print_success, print_warning

print_header("MilAnon Anonymize", str(input_path))
print_result_table([
    ("Scanned", str(result.files_scanned)),
    ("New", f"[green]{result.files_new}[/green]"),
    ("Changed", f"[yellow]{result.files_changed}[/yellow]"),
    ("Skipped", str(result.files_skipped)),
    ("Errors", f"[red]{result.files_error}[/red]" if result.files_error > 0 else f"[green]{result.files_error}[/green]"),
    ("Entities", f"[bold cyan]{result.entities_found}[/bold cyan]"),
], title="Anonymize Results")
```

### `pack` command — SPECIAL: Show token estimate
```python
token_estimate = result.total_chars // 4  # rough estimate
print_result_table([
    ("Workflow", workflow or template_name),
    ("Mode", mode or "classic"),
    ("Context", "✅ included" if result.context_included else "—"),
    ("Documents", str(result.documents_included)),
    ("Total chars", f"{result.total_chars:,}"),
    ("~Tokens", f"~{token_estimate:,} ({token_estimate * 100 // 200_000}% of 200K context)"),
], title="Pack Result")
if result.copied_to_clipboard:
    print_success("Copied to clipboard")
```

### `doctrine list` command — use a Rich table:
```python
table = Table(title="Doctrine Knowledge Base", box=box.ROUNDED)
table.add_column("#", style="dim", width=3)
table.add_column("File", style="cyan")
table.add_column("Regulation", style="green")
table.add_column("Title", style="white")
for i, doc in enumerate(docs, 1):
    table.add_row(str(i), doc["filename"], doc["regulation"], doc["title"])
console.print(table)
```

### `db stats` command — use a Rich table:
```python
table = Table(title="Database Statistics", box=box.ROUNDED)
table.add_column("Type", style="cyan")
table.add_column("Count", justify="right", style="green")
# ...
```

### `export` command:
```python
print_header("MilAnon Export", f"{input_path} → DOCX")
# ...
print_success(f"Exported: {result_path}")
if deanonymize:
    print_success("De-anonymization applied")
```

## Step 4: Add a startup banner (optional but nice)

In the cli group callback:
```python
@cli.group(invoke_without_command=True)
@click.version_option(version=__version__, prog_name="milanon")
@click.pass_context
def cli(ctx) -> None:
    if ctx.invoked_subcommand is None:
        from milanon.cli.output import console
        console.print(Panel(
            "[bold cyan]MilAnon[/bold cyan] — Swiss Military Document Anonymizer\n"
            f"[dim]Version {__version__} • 5+2 Command Assistant[/dim]",
            box=box.DOUBLE,
            border_style="cyan",
        ))
        click.echo(ctx.get_help())
```

## Files to modify:
- `src/milanon/cli/main.py` — Replace all click.echo with Rich
- `pyproject.toml` — Add rich dependency

## Files to create:
- `src/milanon/cli/output.py` — Rich output helpers

## Files NOT to touch:
- `src/milanon/domain/` (any file)
- `src/milanon/usecases/` (any file)
- `src/milanon/adapters/` (any file)
- `src/milanon/gui/` (any file)

## Run and verify:
```bash
source .venv/bin/activate
pip install rich
milanon --version  # should show styled banner
milanon db stats   # should show Rich table
milanon pack --list-templates  # should show Rich table
python -m pytest tests/ -x --tb=short  # all tests must pass
```

## Commit
```bash
git add -A
git commit -m "feat(cli): Rich terminal output — panels, tables, colors, token estimates

- Add rich>=13.0 dependency
- cli/output.py: shared Rich helpers (header, table, success/warning/error)
- All CLI commands use Rich panels and tables
- Pack shows token estimate and context percentage
- Doctrine list shows formatted table
- Startup banner with version info"
```
