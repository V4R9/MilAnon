"""Doctrine CLI commands — manage the doctrine knowledge base.

NOTE: This command group is NOT yet wired into main.py.
To use standalone:
    python -c "from milanon.cli.doctrine_commands import doctrine; doctrine()" -- list
"""

from __future__ import annotations

import logging
from pathlib import Path

import click
from rich import box
from rich.table import Table

from milanon.cli.output import console, print_warning

_DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"
_DOCTRINE_DIR = _DATA_DIR / "doctrine"


@click.group()
def doctrine() -> None:
    """Manage doctrine knowledge base."""


@doctrine.command("list")
def doctrine_list() -> None:
    """List all available doctrine files and their key chapters."""
    from milanon.usecases.doctrine import DoctrineExtractUseCase

    uc = DoctrineExtractUseCase(_DOCTRINE_DIR)
    files = uc.list_doctrine_files()

    if not files:
        print_warning("No doctrine files found. Check data/doctrine/INDEX.yaml.")
        return

    table = Table(title="Doctrine Knowledge Base", box=box.ROUNDED, border_style="cyan")
    table.add_column("#", style="dim", width=3)
    table.add_column("File", style="cyan")
    table.add_column("Regulation", style="green", width=14)
    table.add_column("Title", style="white")
    for i, doc in enumerate(files, 1):
        table.add_row(str(i), doc["filename"], doc.get("regulation", ""), doc.get("title", ""))
    console.print(table)


@doctrine.command("extract")
@click.option("--workflow", default=None, help="Extract chapters for a specific workflow (not yet implemented).")
@click.option("--all", "extract_all", is_flag=True, help="Extract all defined chapters.")
@click.option(
    "--output", "-o", default=None, type=click.Path(),
    help="Output directory (default: data/doctrine/extracts/).",
)
def doctrine_extract(workflow: str | None, extract_all: bool, output: str | None) -> None:
    """Extract doctrine chapters into compact files for prompts."""
    from milanon.usecases.doctrine import DoctrineExtractUseCase

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    uc = DoctrineExtractUseCase(_DOCTRINE_DIR)
    out_dir = Path(output) if output else _DOCTRINE_DIR / "extracts"

    if workflow and not extract_all:
        print_warning(f"Workflow-specific filtering not yet implemented: {workflow}")
        console.print("  Use [cyan]--all[/cyan] to extract all chapters.")
        return

    results = uc.extract_all(out_dir)
    succeeded = sum(1 for v in results.values() if v)
    failed = sum(1 for v in results.values() if not v)

    for name, success in results.items():
        if success:
            console.print(f"  [green]✓[/green] {name}")
        else:
            console.print(f"  [red]✗[/red] {name}")

    console.print("")
    console.print(f"  [green bold]Extracted: {succeeded}[/green bold]")
    if failed:
        console.print(f"  [red bold]Failed:    {failed}[/red bold]")
    console.print(f"  [dim]Output:    {out_dir}[/dim]")
