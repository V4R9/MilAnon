"""Doctrine CLI commands — manage the doctrine knowledge base.

NOTE: This command group is NOT yet wired into main.py.
To use standalone:
    python -c "from milanon.cli.doctrine_commands import doctrine; doctrine()" -- list
"""

from __future__ import annotations

import logging
from pathlib import Path

import click

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
        click.echo("No doctrine files found. Check data/doctrine/INDEX.yaml.")
        return

    click.echo(f"{'Filename':<45} {'Regulation':<12} Title")
    click.echo("-" * 100)
    for f in files:
        click.echo(
            f"  {f['filename']:<43} {f.get('regulation', ''):<12} {f.get('title', '')}"
        )
        for ch in f.get("key_chapters", []):
            click.echo(f"      - {ch}")


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
        click.echo(f"Workflow-specific filtering not yet implemented: {workflow}", err=True)
        click.echo("Use --all to extract all chapters.")
        return

    results = uc.extract_all(out_dir)
    succeeded = sum(1 for v in results.values() if v)
    failed = sum(1 for v in results.values() if not v)

    for name, success in results.items():
        icon = click.style("✓", fg="green") if success else click.style("✗", fg="red")
        click.echo(f"  {icon} {name}")

    click.echo("")
    click.echo(click.style(f"Extracted: {succeeded}", fg="green"))
    if failed:
        click.echo(click.style(f"Failed:    {failed}", fg="red"))
    click.echo(f"Output:    {out_dir}")
