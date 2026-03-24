"""MilAnon CLI — main entry point."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import click
from rich import box
from rich.panel import Panel
from rich.table import Table

from milanon import __version__
from milanon.cli.output import console, print_error, print_file_list, print_header, print_result_table, print_success, print_warning
from milanon.config.settings import ensure_db_dir

# Path to bundled reference data
_DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"


def _make_repo():
    """Create and return a configured SqliteMappingRepository."""
    from milanon.adapters.repositories.sqlite_repository import SqliteMappingRepository

    db_path = ensure_db_dir()
    return SqliteMappingRepository(db_path)


def _auto_init_ref_data(repo) -> None:
    """Auto-initialize reference data if not yet loaded (D5: first-run init)."""
    if repo.get_ref_municipality_count() == 0 or repo.get_ref_military_unit_count() == 0:
        from milanon.usecases.init_reference_data import InitReferenceDataUseCase
        InitReferenceDataUseCase(repo, _DATA_DIR).execute()


def _make_anonymize_use_case(repo):
    from milanon.adapters.recognizers.list_recognizer import ListRecognizer
    from milanon.adapters.recognizers.military_recognizer import MilitaryRecognizer
    from milanon.adapters.recognizers.pattern_recognizer import PatternRecognizer
    from milanon.domain.anonymizer import Anonymizer
    from milanon.domain.mapping_service import MappingService
    from milanon.domain.recognition import RecognitionPipeline
    from milanon.usecases.anonymize import AnonymizeUseCase

    _auto_init_ref_data(repo)
    service = MappingService(repo)
    # ListRecognizer fetches municipality names from DB (None = use DB)
    pipeline = RecognitionPipeline(
        [PatternRecognizer(), MilitaryRecognizer(), ListRecognizer(repo)]
    )
    anonymizer = Anonymizer(service)
    return AnonymizeUseCase(pipeline, anonymizer, repo)


def _make_deanonymize_use_case(repo):
    from milanon.domain.deanonymizer import DeAnonymizer
    from milanon.domain.mapping_service import MappingService
    from milanon.usecases.deanonymize import DeAnonymizeUseCase

    _auto_init_ref_data(repo)
    service = MappingService(repo)
    deanonymizer = DeAnonymizer(service)
    return DeAnonymizeUseCase(deanonymizer, repo)


@click.group(invoke_without_command=True)
@click.version_option(version=__version__, prog_name="milanon")
@click.pass_context
def cli(ctx: click.Context) -> None:
    """MilAnon — Swiss Military Document Anonymizer & De-Anonymizer.

    Anonymize sensitive documents before using public LLMs,
    then de-anonymize the LLM outputs to restore original data.
    All processing is local — no data leaves your machine.
    """
    if ctx.invoked_subcommand is None:
        console.print(Panel(
            f"[bold cyan]MilAnon[/bold cyan] — Swiss Military Document Anonymizer\n"
            f"[dim]Version {__version__} • 5+2 Command Assistant[/dim]",
            box=box.DOUBLE,
            border_style="cyan",
        ))
        click.echo(ctx.get_help())


@cli.command()
@click.argument("input_path", type=click.Path(exists=True))
@click.option("--output", "-o", required=True, type=click.Path(), help="Output directory.")
@click.option("--recursive", "-r", is_flag=True, help="Process subfolders recursively.")
@click.option("--force", is_flag=True, help="Reprocess all files, ignoring cache.")
@click.option("--dry-run", is_flag=True, help="Show what would be processed without doing it.")
@click.option(
    "--embed-images",
    is_flag=True,
    help="Embed visual PDF pages (WAP/schedules) as PNG images in the output (NOT anonymized).",
)
@click.option("--clean", is_flag=True, help="Remove output files that no longer have a corresponding input file.")
def anonymize(
    input_path: str, output: str, recursive: bool, force: bool, dry_run: bool,
    embed_images: bool, clean: bool,
) -> None:
    """Anonymize documents by replacing sensitive entities with placeholders."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    repo = _make_repo()
    use_case = _make_anonymize_use_case(repo)

    result = use_case.execute(
        Path(input_path),
        Path(output),
        recursive=recursive,
        force=force,
        dry_run=dry_run,
        embed_images=embed_images,
        clean=clean,
    )

    prefix = "[dim][dry-run][/dim] " if dry_run else ""
    errors_val = f"[red bold]{result.files_error}[/red bold]" if result.files_error > 0 else f"[green]{result.files_error}[/green]"
    rows = [
        (f"{prefix}Scanned", str(result.files_scanned)),
        (f"{prefix}New", f"[green]{result.files_new}[/green]"),
        (f"{prefix}Changed", f"[yellow]{result.files_changed}[/yellow]"),
        (f"{prefix}Skipped", str(result.files_skipped)),
        (f"{prefix}Errors", errors_val),
        (f"{prefix}Entities", f"[bold cyan]{result.entities_found}[/bold cyan]"),
    ]
    if result.entities_total > result.entities_found:
        rows.append((f"{prefix}Total", f"[cyan]{result.entities_total}[/cyan] (across all tracked files)"))
    if result.files_cleaned > 0:
        rows.append((f"{prefix}Cleaned", f"[yellow]{result.files_cleaned}[/yellow] orphaned output(s)"))

    print_header("MilAnon Anonymize", input_path)
    print_result_table(rows, title="Results")

    if result.visual_page_count > 0:
        if embed_images:
            print_warning(f"{result.visual_page_count} visual page(s) embedded as PNG images (NOT anonymized).")
        else:
            print_warning(
                f"{result.visual_page_count} visual page(s) detected (WAP/schedules — "
                "not extractable as text). Use --embed-images to include as PNG."
            )

    for warning in result.warnings:
        print_warning(warning)

    if result.files_error > 0:
        sys.exit(1)


@cli.command()
@click.argument("input_path", type=click.Path(exists=True))
@click.option("--output", "-o", default=None, type=click.Path(), help="Output directory (ignored with --in-place).")
@click.option("--force", is_flag=True, help="Reprocess all files, ignoring cache.")
@click.option("--dry-run", is_flag=True, help="Show what would be processed without doing it.")
@click.option("--in-place", "in_place", is_flag=True, help="De-anonymize files directly in their current location. Creates .milanon_backup/ before modifying.")
def deanonymize(input_path: str, output: str | None, force: bool, dry_run: bool, in_place: bool) -> None:
    """De-anonymize LLM outputs by restoring original entity values."""
    if not in_place and not output:
        print_error("--output is required unless --in-place is used.")
        sys.exit(1)

    if in_place and not dry_run:
        click.confirm(
            f"This will modify files in-place at '{input_path}'. "
            "Originals will be backed up to .milanon_backup/. Continue?",
            abort=True,
        )

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    repo = _make_repo()
    use_case = _make_deanonymize_use_case(repo)

    result = use_case.execute(
        Path(input_path),
        Path(output) if output else None,
        force=force,
        dry_run=dry_run,
        in_place=in_place,
    )

    prefix = "[dim][dry-run][/dim] " if dry_run else ""
    errors_val = f"[red bold]{result.files_error}[/red bold]" if result.files_error > 0 else f"[green]{result.files_error}[/green]"
    print_result_table([
        (f"{prefix}Scanned", str(result.files_scanned)),
        (f"{prefix}New", f"[green]{result.files_new}[/green]"),
        (f"{prefix}Changed", f"[yellow]{result.files_changed}[/yellow]"),
        (f"{prefix}Skipped", str(result.files_skipped)),
        (f"{prefix}Errors", errors_val),
        (f"{prefix}Resolved", f"[bold cyan]{result.placeholders_resolved}[/bold cyan]"),
    ], title="De-Anonymize Results")

    for warning in result.warnings:
        print_warning(warning)

    if in_place and not dry_run:
        console.print(f"  [dim]Backup saved to: {Path(input_path) / '.milanon_backup'}/[/dim]")

    if result.files_error > 0:
        sys.exit(1)


@cli.command()
@click.argument("file_path", type=click.Path(exists=True))
def validate(file_path: str) -> None:
    """Validate placeholder integrity in an LLM output file."""
    from milanon.domain.deanonymizer import DeAnonymizer
    from milanon.domain.mapping_service import MappingService
    from milanon.usecases.validate_output import ValidateOutputUseCase

    repo = _make_repo()
    service = MappingService(repo)
    deanonymizer = DeAnonymizer(service)
    use_case = ValidateOutputUseCase(deanonymizer)

    result = use_case.execute(Path(file_path))

    print_result_table([
        ("File", str(result.file_path)),
        ("Placeholders", str(result.total_placeholders)),
        ("Resolved", str(result.resolved)),
        ("Unresolved", str(result.unresolved)),
    ], title="Validate")

    for ph in result.unresolved_list:
        print_error(f"UNRESOLVED: {ph}")

    if not result.is_valid:
        print_error("INVALID — unresolved placeholders found.")
        sys.exit(1)
    else:
        print_success("OK — all placeholders resolved.")


@cli.group()
def db() -> None:
    """Manage the entity mapping database."""


@db.command("init")
@click.option("--force", is_flag=True, help="Re-initialize even if data is already present.")
def db_init(force: bool) -> None:
    """Initialize reference data (Swiss municipalities + military units) in the database."""
    from milanon.usecases.init_reference_data import InitReferenceDataUseCase

    repo = _make_repo()

    if force:
        repo.clear_reference_data()

    uc = InitReferenceDataUseCase(repo, _DATA_DIR)
    result = uc.execute()

    muni_val = (
        "already loaded — skipped (use --force to reload)"
        if result.municipalities_skipped and not force
        else f"[green]{result.municipalities_loaded}[/green] loaded"
    )
    units_val = (
        "already loaded — skipped (use --force to reload)"
        if result.military_units_skipped and not force
        else f"[green]{result.military_units_loaded}[/green] loaded"
    )
    print_result_table([
        ("Municipalities", muni_val),
        ("Military units", units_val),
    ], title="DB Init")

    if result.already_initialized and not force:
        console.print("  [dim]Database already initialized. Run with --force to reload.[/dim]")
    else:
        print_success("Initialization complete.")


@db.command("reset")
@click.option(
    "--include-ref-data",
    is_flag=True,
    help="Also delete reference data (municipalities, military units).",
)
@click.confirmation_option(prompt="This will delete all entity mappings. Continue?")
def db_reset(include_ref_data: bool) -> None:
    """Reset the mapping database (delete all entity mappings and file tracking)."""
    repo = _make_repo()
    if include_ref_data:
        counts = repo.reset_everything()
        msg = "Reset complete — all tables cleared."
    else:
        counts = repo.reset_all_mappings()
        msg = "Reset complete — mappings and file tracking cleared. Reference data kept."

    table = Table(box=box.SIMPLE, show_header=True, padding=(0, 2))
    table.add_column("Table", style="cyan")
    table.add_column("Rows deleted", justify="right", style="yellow")
    for tbl, count in sorted(counts.items()):
        table.add_row(tbl, str(count))
    console.print(Panel(table, title="DB Reset", box=box.ROUNDED, border_style="cyan"))
    print_success(msg)


@db.command("import")
@click.argument("csv_path", type=click.Path(exists=True))
@click.option(
    "--format",
    "import_format",
    type=click.Choice(["pisa", "names", "miloffice"]),
    default="pisa",
    help="CSV format: 'pisa' = PISA 410 / MilOffice export; 'names' = simple Grad;Vorname;Nachname list. 'miloffice' is an alias for 'pisa'.",
)
def db_import(csv_path: str, import_format: str) -> None:
    """Import entities from a CSV file (PISA 410 or simple name list)."""
    from milanon.domain.mapping_service import MappingService

    repo = _make_repo()
    service = MappingService(repo)

    if import_format == "names":
        from milanon.usecases.import_names import ImportNamesUseCase
        use_case = ImportNamesUseCase(service)
    else:
        # "pisa" and legacy "miloffice" both use ImportEntitiesUseCase
        from milanon.usecases.import_entities import ImportEntitiesUseCase
        use_case = ImportEntitiesUseCase(service)

    result = use_case.execute(Path(csv_path), source_document=csv_path)

    print_result_table([
        ("Rows processed", str(result.rows_processed)),
        ("Rows skipped", str(result.rows_skipped)),
        ("Entities imported", f"[green bold]{result.entities_imported}[/green bold]"),
    ], title="DB Import")


@db.command("list")
@click.option("--type", "entity_type", default=None, help="Filter by entity type.")
@click.option("--limit", default=50, help="Maximum number of entries to show.")
def db_list(entity_type: str | None, limit: int) -> None:
    """List known entities in the mapping database."""
    from milanon.domain.entities import EntityType

    repo = _make_repo()
    mappings = repo.get_all_mappings()

    if entity_type:
        try:
            et = EntityType(entity_type.upper())
        except ValueError:
            print_error(f"Unknown entity type: {entity_type}")
            sys.exit(2)
        mappings = [m for m in mappings if m.entity_type == et]

    mappings = mappings[:limit]

    if not mappings:
        console.print("[dim]No entities found.[/dim]")
        return

    table = Table(box=box.SIMPLE, show_header=True, padding=(0, 2))
    table.add_column("Placeholder", style="cyan", width=22)
    table.add_column("Type", style="green", width=22)
    table.add_column("Original value", style="white")
    for m in mappings:
        table.add_row(m.placeholder, m.entity_type.value, m.original_value)
    console.print(table)


@db.command("stats")
def db_stats() -> None:
    """Show database statistics."""
    repo = _make_repo()
    total = repo.get_total_mapping_count()
    by_type = repo.get_mapping_count_by_type()

    table = Table(title="Database Statistics", box=box.ROUNDED, border_style="cyan")
    table.add_column("Type", style="cyan")
    table.add_column("Count", justify="right", style="green")

    if by_type:
        for entity_type, count in sorted(by_type.items()):
            table.add_row(entity_type, str(count))
    else:
        table.add_row("[dim]—[/dim]", "[dim]empty[/dim]")

    table.add_section()
    table.add_row("[bold]Total entities[/bold]", f"[bold cyan]{total}[/bold cyan]")
    table.add_section()
    table.add_row("[dim]Municipalities (ref)[/dim]", f"[dim]{repo.get_ref_municipality_count()}[/dim]")
    table.add_row("[dim]Military units (ref)[/dim]", f"[dim]{repo.get_ref_military_unit_count()}[/dim]")

    console.print(table)


@cli.command()
@click.option("--unit", "unit_name", default=None, help='Your unit, e.g. "Inf Kp 56/1".')
@click.option(
    "--output", "output_path", default="CONTEXT.md",
    help='Output file path (default: CONTEXT.md in working directory). '
         'Use --output to place it next to your anonymized files, e.g. '
         '"--output test_output/CONTEXT.md".',
)
def context(unit_name: str | None, output_path: str) -> None:
    """Generate an LLM context file with unit hierarchy and placeholder mapping."""
    from milanon.usecases.generate_context import GenerateContextUseCase

    repo = _make_repo()
    use_case = GenerateContextUseCase(repo)

    units = use_case.get_available_units()

    if not units:
        print_error("No units found in database. Run 'milanon db import' first.")
        sys.exit(1)

    if unit_name is None:
        # Interactive mode — show list and prompt
        table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
        table.add_column("#", style="dim", width=4)
        table.add_column("Unit", style="cyan", width=38)
        table.add_column("Level", style="dim")
        for i, u in enumerate(units, 1):
            table.add_row(str(i), u.original_value, u.level)
        console.print(Panel(table, title="Known units in database", box=box.ROUNDED, border_style="cyan"))

        choice = click.prompt("Which is your unit? Enter number", type=int)
        if not 1 <= choice <= len(units):
            print_error(f"Invalid choice: {choice}")
            sys.exit(1)
        unit_name = units[choice - 1].original_value

    # Validate unit exists (also catches --unit values not in DB)
    known_lower = {u.original_value.strip().lower() for u in units}
    if unit_name.strip().lower() not in known_lower:
        print_error(f"Unit '{unit_name}' not found in database.")
        table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
        table.add_column("Unit", style="cyan")
        table.add_column("Level", style="dim")
        for u in units:
            table.add_row(u.original_value, u.level)
        console.print(table)
        sys.exit(1)

    use_case.generate(unit_name, Path(output_path))
    print_success(f"Context file written to {output_path}")


@cli.command()
@click.argument("input_path", type=click.Path(exists=True))
@click.option("--template", "-t", "template_name", default="frei", help="Template name (frei, obsidian-notes, befehl-entwurf, analyse).")
@click.option("--workflow", default=None, help="Workflow name: analyse, ei-bf, wachtdienst, bdl, entschluss.")
@click.option("--mode", default=None, help="Mode: berrm or adf (default from config or 'berrm').")
@click.option("--step", default=None, type=int, help="5+2 step number (1-5).")
@click.option("--unit", "user_unit", default="", help='Your unit, e.g. "Inf Kp 56/1".')
@click.option("--prompt", "user_prompt", default="", help="Custom prompt text (used with template 'frei').")
@click.option("--context", "context_path", default=None, type=click.Path(), help="Path to CONTEXT.md or previous step outputs.")
@click.option("--output", "-o", "output_path", default=None, type=click.Path(), help="Write pack to this file in addition to clipboard.")
@click.option("--no-clipboard", is_flag=True, help="Do not copy to clipboard.")
@click.option("--list-templates", "list_templates_flag", is_flag=True, help="Show available templates and exit.")
def pack(
    input_path: str,
    template_name: str,
    workflow: str | None,
    mode: str | None,
    step: int | None,
    user_unit: str,
    user_prompt: str,
    context_path: str | None,
    output_path: str | None,
    no_clipboard: bool,
    list_templates_flag: bool,
) -> None:
    """Build a prompt pack (context + template + docs) and copy to clipboard."""
    from milanon.usecases.pack import PackUseCase, list_templates

    if list_templates_flag:
        templates = list_templates()
        if not templates:
            console.print("[dim]No templates found.[/dim]")
            return
        table = Table(title="Available Templates", box=box.ROUNDED, border_style="cyan")
        table.add_column("Name", style="cyan", width=25)
        table.add_column("Source", style="dim", width=10)
        table.add_column("Description", style="white")
        for t in templates:
            table.add_row(t["name"], t["source"], t["description"])
        console.print(table)
        return

    repo = _make_repo()

    if workflow:
        # Workflow mode — use WorkflowPackUseCase (5-layer doctrine-aware prompts)
        from milanon.usecases.generate_context import GenerateContextUseCase
        from milanon.usecases.workflow_pack import WorkflowPackUseCase

        ctx_gen = GenerateContextUseCase(repo)
        use_case = WorkflowPackUseCase(repo, ctx_gen)

        resolved_mode = mode or _get_config_value("mode") or "berrm"

        try:
            _, result = use_case.execute(
                workflow=workflow,
                mode=resolved_mode,
                step=step,
                input_path=Path(input_path),
                unit=user_unit,
                context_path=Path(context_path) if context_path else None,
                output_path=Path(output_path) if output_path else None,
                copy_clipboard=not no_clipboard,
            )
        except ValueError as exc:
            print_error(str(exc))
            sys.exit(1)
    else:
        # Classic mode — use PackUseCase (backward compatible)
        use_case = PackUseCase(repo)

        try:
            _, result = use_case.execute(
                Path(input_path),
                template_name=template_name,
                user_prompt=user_prompt,
                user_unit=user_unit,
                context_path=Path(context_path) if context_path else None,
                output_path=Path(output_path) if output_path else None,
                copy_clipboard=not no_clipboard,
            )
        except ValueError as exc:
            print_error(str(exc))
            sys.exit(1)

    token_estimate = result.total_chars // 4
    ctx_pct = token_estimate * 100 // 200_000
    print_result_table([
        ("Workflow", workflow or template_name),
        ("Mode", (mode or _get_config_value("mode") or "berrm") if workflow else "classic"),
        ("Step", str(step) if step else "—"),
        ("Context", "[green]✅ included[/green]" if result.context_included else "[dim]—[/dim]"),
        ("Documents", str(result.documents_included)),
        ("Total chars", f"{result.total_chars:,}"),
        ("~Tokens", f"[cyan]~{token_estimate:,}[/cyan] [dim]({ctx_pct}% of 200K context)[/dim]"),
    ], title="Pack Result")

    if result.copied_to_clipboard:
        print_success("Copied to clipboard")
    elif not no_clipboard:
        print_warning("Could not copy to clipboard.")
    if result.output_path:
        console.print(f"  [dim]Written to: {result.output_path}[/dim]")


@cli.command()
@click.option("--output", "-o", "output_dir", required=True, type=click.Path(), help="Output directory for de-anonymized files.")
@click.option("--clipboard", "from_clipboard", is_flag=True, help="Read LLM output from system clipboard.")
@click.option("--input", "input_file", default=None, type=click.Path(exists=True), help="Read LLM output from a file.")
@click.option("--split", "split_sections", is_flag=True, help="Split on --- separators and write separate files.")
@click.option("--in-place", "in_place", is_flag=True, help="Overwrite the input file in-place (requires --input).")
def unpack(
    output_dir: str,
    from_clipboard: bool,
    input_file: str | None,
    split_sections: bool,
    in_place: bool,
) -> None:
    """De-anonymize LLM output from clipboard or file."""
    if not from_clipboard and not input_file:
        print_error("one of --clipboard or --input is required.")
        sys.exit(1)

    if in_place and not input_file:
        print_error("--in-place requires --input.")
        sys.exit(1)

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    repo = _make_repo()

    from milanon.domain.deanonymizer import DeAnonymizer
    from milanon.domain.mapping_service import MappingService
    from milanon.usecases.unpack import UnpackUseCase

    service = MappingService(repo)
    deanonymizer = DeAnonymizer(service)
    use_case = UnpackUseCase(deanonymizer)

    result = use_case.execute(
        Path(output_dir),
        input_file=Path(input_file) if input_file else None,
        from_clipboard=from_clipboard,
        split_sections=split_sections,
        in_place=in_place,
    )

    print_result_table([
        ("Source", result.source),
        ("Resolved", f"[bold green]{result.placeholders_resolved}[/bold green]"),
        ("Files written", f"[green]{result.files_written}[/green]"),
    ], title="Unpack Result")

    print_file_list(result.output_files)

    for warning in result.warnings:
        print_warning(warning)

    if result.files_written == 0 and not result.warnings:
        sys.exit(0)


@cli.command()
@click.argument("input_path", type=click.Path(exists=True))
@click.option("--auto-add", is_flag=True, help="Automatically add all candidates to the database without confirmation.")
@click.option("--dry-run", is_flag=True, help="Show candidates without adding to database.")
def review(input_path: str, auto_add: bool, dry_run: bool) -> None:
    """Scan anonymized output for potential name leaks and add confirmed candidates to DB."""
    from milanon.domain.mapping_service import MappingService
    from milanon.usecases.review_candidates import ReviewCandidatesUseCase

    repo = _make_repo()
    service = MappingService(repo)
    use_case = ReviewCandidatesUseCase(service)

    result = use_case.scan(Path(input_path))

    console.print(
        f"  Scanned [cyan]{result.files_scanned}[/cyan] file(s). "
        f"Found [{'yellow' if result.candidates else 'green'}]{len(result.candidates)}[/{'yellow' if result.candidates else 'green'}] candidate(s)."
    )

    if not result.candidates:
        print_success("No undetected names found.")
        return

    table = Table(box=box.ROUNDED, border_style="yellow", title="Review Candidates")
    table.add_column("#", style="dim", width=3)
    table.add_column("Type", style="cyan", width=12)
    table.add_column("Value", style="white")
    table.add_column("Count", justify="right", style="dim", width=6)
    table.add_column("Context", style="dim")
    for i, c in enumerate(result.candidates, 1):
        flag = " ⚠ personnel" if c.near_personnel_context else ""
        snippet = c.context_snippets[0] if c.context_snippets else ""
        table.add_row(str(i), c.candidate_type, c.value + flag, str(c.occurrences), snippet)
    console.print(table)

    if dry_run:
        console.print("  [dim][dry-run] No changes made.[/dim]")
        return

    if auto_add:
        count = use_case.add_confirmed_candidates(result.candidates)
        print_success(f"Added {count} new entities to database.")
    else:
        console.print("")
        console.print("  Enter numbers to confirm (e.g. [cyan]1 3 5[/cyan]), [cyan]all[/cyan], or press Enter to skip:")
        choice = click.prompt("Your choice", default="")
        if not choice.strip():
            console.print("  [dim]No changes made.[/dim]")
            return

        if choice.strip().lower() == "all":
            confirmed = result.candidates
        else:
            try:
                indices = [int(x) - 1 for x in choice.split()]
                confirmed = [result.candidates[i] for i in indices if 0 <= i < len(result.candidates)]
            except ValueError:
                print_error("Invalid input. No changes made.")
                return

        count = use_case.add_confirmed_candidates(confirmed)
        print_success(f"Added {count} new entities to database.")


# ---------------------------------------------------------------------------
# doctrine command group (wired from doctrine_commands.py)
# ---------------------------------------------------------------------------

from milanon.cli.doctrine_commands import doctrine  # noqa: E402

cli.add_command(doctrine)


# ---------------------------------------------------------------------------
# export command
# ---------------------------------------------------------------------------

@cli.command()
@click.argument("input_path", type=click.Path(exists=True))
@click.option("--docx", is_flag=True, help="Export as DOCX.")
@click.option("--template", "template_path", default=None, type=click.Path(), help="DOCX template file (default: bundled befehl_vorlage.docx).")
@click.option("--deanonymize", is_flag=True, help="Replace placeholders with real values.")
@click.option("--output", "-o", default=None, type=click.Path(), help="Output file path.")
def export(input_path: str, docx: bool, template_path: str | None, deanonymize: bool, output: str | None) -> None:
    """Export Markdown to DOCX with optional de-anonymization."""
    if not docx:
        print_error("specify --docx for export format.")
        sys.exit(1)

    from milanon.adapters.writers.docx_befehl_writer import DocxBefehlWriter
    from milanon.usecases.export_docx import ExportDocxUseCase

    repo = _make_repo()
    writer = DocxBefehlWriter()
    use_case = ExportDocxUseCase(repo, writer)

    in_path = Path(input_path)
    tpl_path = Path(template_path) if template_path else _DATA_DIR / "templates" / "docx" / "befehl_vorlage.docx"
    out_path = Path(output) if output else in_path.with_suffix(".docx")

    if not tpl_path.exists():
        print_error(f"Template not found: {tpl_path}")
        sys.exit(1)

    print_header("MilAnon Export", f"{in_path.name} → DOCX")
    result_path = use_case.execute(in_path, out_path, tpl_path, deanonymize=deanonymize)
    print_success(f"Exported: {result_path}")
    if deanonymize:
        print_success("De-anonymization applied.")


# ---------------------------------------------------------------------------
# project command group
# ---------------------------------------------------------------------------

@cli.group()
def project() -> None:
    """Manage Claude.ai Project generation."""


@project.command("generate")
@click.option("--unit", required=True, help='Your unit, e.g. "Inf Kp 56/1".')
@click.option("--output", "-o", required=True, type=click.Path(), help="Output directory for the project folder.")
def project_generate(unit: str, output: str) -> None:
    """Generate a ready-to-import Claude.ai Project folder."""
    from milanon.usecases.generate_project import GenerateProjectUseCase

    use_case = GenerateProjectUseCase(_DATA_DIR)
    result = use_case.execute(unit, Path(output))

    print_success(f"Project generated for: {result.unit}")
    console.print(f"  [dim]Output: {result.output_dir}[/dim]")
    console.print(f"  [dim]Files:  {len(result.files_created)}[/dim]")
    print_file_list([str(f) for f in result.files_created])


# ---------------------------------------------------------------------------
# config command group
# ---------------------------------------------------------------------------

_CONFIG_PATH = Path.home() / ".milanon" / "config.json"


def _load_config() -> dict:
    """Load project config from ~/.milanon/config.json."""
    import json

    if _CONFIG_PATH.exists():
        return json.loads(_CONFIG_PATH.read_text(encoding="utf-8"))
    return {}


def _save_config(data: dict) -> None:
    """Save project config to ~/.milanon/config.json."""
    import json

    _CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    _CONFIG_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _get_config_value(key: str) -> str | None:
    """Get a single config value by key."""
    return _load_config().get(key)


@cli.group()
def config() -> None:
    """Manage project configuration."""


@config.command("set")
@click.argument("key")
@click.argument("value")
def config_set(key: str, value: str) -> None:
    """Set a config value (e.g. mode, unit)."""
    data = _load_config()
    data[key] = value
    _save_config(data)
    console.print(f"  [cyan]{key}[/cyan] = [green]{value}[/green]")


@config.command("get")
@click.argument("key")
def config_get(key: str) -> None:
    """Get a config value."""
    value = _get_config_value(key)
    if value is None:
        console.print(f"  [cyan]{key}[/cyan]: [dim](not set)[/dim]")
    else:
        console.print(f"  [cyan]{key}[/cyan] = [green]{value}[/green]")


# ---------------------------------------------------------------------------
# gui command
# ---------------------------------------------------------------------------

@cli.command()
@click.option("--port", default=8501, help="Port to run the Streamlit server on.")
def gui(port: int) -> None:
    """Launch the Streamlit web interface in the browser."""
    import subprocess

    app_path = Path(__file__).parent.parent / "gui" / "app.py"
    if not app_path.exists():
        print_error(f"GUI app not found at {app_path}")
        sys.exit(2)

    console.print(f"  Starting [bold cyan]MilAnon GUI[/bold cyan] at [link]http://localhost:{port}[/link]")
    console.print("  [dim]Press Ctrl+C to stop.[/dim]")
    subprocess.run(
        [sys.executable, "-m", "streamlit", "run", str(app_path), "--server.port", str(port)],
        check=False,
    )
