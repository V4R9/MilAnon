"""Rich output helpers for MilAnon CLI."""

from __future__ import annotations

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()


def print_header(title: str, subtitle: str = "") -> None:
    """Print a styled header panel."""
    text = Text(title, style="bold cyan")
    if subtitle:
        text.append(f"\n{subtitle}", style="dim")
    console.print(Panel(text, box=box.ROUNDED, border_style="cyan"))


def print_result_table(rows: list[tuple[str, str]], title: str = "") -> None:
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


def print_success(msg: str) -> None:
    console.print(f"  [green bold]✅ {msg}[/green bold]")


def print_warning(msg: str) -> None:
    console.print(f"  [yellow]⚠️  {msg}[/yellow]")


def print_error(msg: str) -> None:
    console.print(f"  [red bold]❌ {msg}[/red bold]")


def print_file_list(files: list[str], title: str = "Files") -> None:
    for f in files:
        console.print(f"  [dim]→ {f}[/dim]")
