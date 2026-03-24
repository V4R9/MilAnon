"""MilAnon CLI — main entry point."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import click

from milanon import __version__
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


@click.group()
@click.version_option(version=__version__, prog_name="milanon")
def cli() -> None:
    """MilAnon — Swiss Military Document Anonymizer & De-Anonymizer.

    Anonymize sensitive documents before using public LLMs,
    then de-anonymize the LLM outputs to restore original data.
    All processing is local — no data leaves your machine.
    """


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
def anonymize(
    input_path: str, output: str, recursive: bool, force: bool, dry_run: bool,
    embed_images: bool,
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
    )

    mode = "[dry-run] " if dry_run else ""
    click.echo(click.style(f"{mode}Scanned:   {result.files_scanned}", fg="cyan"))
    click.echo(click.style(f"{mode}New:       {result.files_new}", fg="green"))
    click.echo(click.style(f"{mode}Changed:   {result.files_changed}", fg="yellow"))
    click.echo(click.style(f"{mode}Skipped:   {result.files_skipped}", fg="white"))
    if result.files_error > 0:
        click.echo(click.style(f"{mode}Errors:    {result.files_error}", fg="red", bold=True))
    else:
        click.echo(click.style(f"{mode}Errors:    {result.files_error}", fg="green"))
    click.echo(click.style(f"{mode}Entities:  {result.entities_found}", fg="cyan", bold=True))

    if result.visual_page_count > 0:
        if embed_images:
            click.echo(
                f"⚠ {result.visual_page_count} visual page(s) embedded as PNG images (NOT anonymized).",
                err=True,
            )
        else:
            click.echo(
                f"⚠ {result.visual_page_count} visual page(s) detected (WAP/schedules — "
                "not extractable as text). Use --embed-images to include as PNG.",
                err=True,
            )

    for warning in result.warnings:
        click.echo(f"  WARNING: {warning}", err=True)

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
        click.echo("Error: --output is required unless --in-place is used.", err=True)
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

    mode = "[dry-run] " if dry_run else ""
    click.echo(click.style(f"{mode}Scanned:    {result.files_scanned}", fg="cyan"))
    click.echo(click.style(f"{mode}New:        {result.files_new}", fg="green"))
    click.echo(click.style(f"{mode}Changed:    {result.files_changed}", fg="yellow"))
    click.echo(click.style(f"{mode}Skipped:    {result.files_skipped}", fg="white"))
    if result.files_error > 0:
        click.echo(click.style(f"{mode}Errors:     {result.files_error}", fg="red", bold=True))
    else:
        click.echo(click.style(f"{mode}Errors:     {result.files_error}", fg="green"))
    click.echo(click.style(f"{mode}Resolved:   {result.placeholders_resolved}", fg="cyan", bold=True))

    for warning in result.warnings:
        click.echo(f"  WARNING: {warning}", err=True)

    if in_place and not dry_run:
        click.echo(f"Backup saved to: {Path(input_path) / '.milanon_backup'}/")

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

    click.echo(f"File:        {result.file_path}")
    click.echo(f"Placeholders: {result.total_placeholders}")
    click.echo(f"Resolved:    {result.resolved}")
    click.echo(f"Unresolved:  {result.unresolved}")

    for ph in result.unresolved_list:
        click.echo(f"  UNRESOLVED: {ph}", err=True)

    if not result.is_valid:
        click.echo("INVALID — unresolved placeholders found.", err=True)
        sys.exit(1)
    else:
        click.echo("OK")


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

    if result.municipalities_skipped and not force:
        click.echo("Municipalities: already loaded — skipped (use --force to reload)")
    else:
        click.echo(f"Municipalities: {result.municipalities_loaded} loaded")

    if result.military_units_skipped and not force:
        click.echo("Military units: already loaded — skipped (use --force to reload)")
    else:
        click.echo(f"Military units: {result.military_units_loaded} loaded")

    if result.already_initialized and not force:
        click.echo("Database already initialized. Run with --force to reload.")
    else:
        click.echo("Initialization complete.")


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
        click.echo("Reset complete — all tables cleared.")
    else:
        counts = repo.reset_all_mappings()
        click.echo("Reset complete — mappings and file tracking cleared. Reference data kept.")
    for table, count in sorted(counts.items()):
        click.echo(f"  {table:<30} {count} rows deleted")


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

    click.echo(f"Rows processed:  {result.rows_processed}")
    click.echo(f"Rows skipped:    {result.rows_skipped}")
    click.echo(f"Entities imported: {result.entities_imported}")


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
            click.echo(f"Unknown entity type: {entity_type}", err=True)
            sys.exit(2)
        mappings = [m for m in mappings if m.entity_type == et]

    mappings = mappings[:limit]

    if not mappings:
        click.echo("No entities found.")
        return

    for m in mappings:
        click.echo(f"{m.placeholder:<20} {m.entity_type.value:<20} {m.original_value}")


@db.command("stats")
def db_stats() -> None:
    """Show database statistics."""
    repo = _make_repo()
    total = repo.get_total_mapping_count()
    by_type = repo.get_mapping_count_by_type()

    click.echo("milanon — database statistics")
    click.echo(f"Total entities: {total}")
    click.echo("")
    if by_type:
        click.echo("By type:")
        for entity_type, count in sorted(by_type.items()):
            click.echo(f"  {entity_type:<25} {count}")
    else:
        click.echo("Database is empty.")
    click.echo("")
    click.echo("Reference data:")
    click.echo(f"  Municipalities:    {repo.get_ref_municipality_count()}")
    click.echo(f"  Military units:    {repo.get_ref_military_unit_count()}")


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
        click.echo("No units found in database. Run 'milanon db import' first.", err=True)
        sys.exit(1)

    if unit_name is None:
        # Interactive mode — show list and prompt
        click.echo("Known units in database:\n")
        for i, u in enumerate(units, 1):
            click.echo(f"  {i:2}. {u.original_value:<35} ({u.level})")
        click.echo("")
        choice = click.prompt("Which is your unit? Enter number", type=int)
        if not 1 <= choice <= len(units):
            click.echo(f"Invalid choice: {choice}", err=True)
            sys.exit(1)
        unit_name = units[choice - 1].original_value

    # Validate unit exists (also catches --unit values not in DB)
    known_lower = {u.original_value.strip().lower() for u in units}
    if unit_name.strip().lower() not in known_lower:
        click.echo(f"Unit '{unit_name}' not found in database.", err=True)
        click.echo("\nKnown units:")
        for u in units:
            click.echo(f"  {u.original_value:<35} ({u.level})")
        sys.exit(1)

    use_case.generate(unit_name, Path(output_path))
    click.echo(f"Context file written to {output_path}")


@cli.command()
@click.argument("input_path", type=click.Path(exists=True))
@click.option("--template", "-t", "template_name", default="frei", help="Template name (frei, obsidian-notes, befehl-entwurf, analyse).")
@click.option("--unit", "user_unit", default="", help='Your unit, e.g. "Inf Kp 56/1".')
@click.option("--prompt", "user_prompt", default="", help="Custom prompt text (used with template 'frei').")
@click.option("--context", "context_path", default=None, type=click.Path(), help="Path to CONTEXT.md (auto-detected if omitted).")
@click.option("--output", "-o", "output_path", default=None, type=click.Path(), help="Write pack to this file in addition to clipboard.")
@click.option("--no-clipboard", is_flag=True, help="Do not copy to clipboard.")
@click.option("--list-templates", "list_templates_flag", is_flag=True, help="Show available templates and exit.")
def pack(
    input_path: str,
    template_name: str,
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
            click.echo("No templates found.")
            return
        for t in templates:
            click.echo(f"  {t['name']:<25} [{t['source']}]  {t['description']}")
        return

    repo = _make_repo()
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
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)

    click.echo(click.style(f"Template:    {result.template_used}", fg="cyan"))
    click.echo(click.style(f"Context:     {'yes' if result.context_included else 'no'}", fg="cyan"))
    click.echo(click.style(f"Documents:   {result.documents_included}", fg="green"))
    click.echo(click.style(f"Total chars: {result.total_chars}", fg="cyan"))
    if result.copied_to_clipboard:
        click.echo(click.style("Copied to clipboard.", fg="green", bold=True))
    elif not no_clipboard:
        click.echo("Note: Could not copy to clipboard.", err=True)
    if result.output_path:
        click.echo(f"Written to:  {result.output_path}")


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
        click.echo("Error: one of --clipboard or --input is required.", err=True)
        sys.exit(1)

    if in_place and not input_file:
        click.echo("Error: --in-place requires --input.", err=True)
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

    click.echo(click.style(f"Source:        {result.source}", fg="cyan"))
    click.echo(click.style(f"Resolved:      {result.placeholders_resolved}", fg="green", bold=True))
    click.echo(click.style(f"Files written: {result.files_written}", fg="green"))
    for f in result.output_files:
        click.echo(f"  → {f}")
    for warning in result.warnings:
        click.echo(f"  WARNING: {warning}", err=True)

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

    click.echo(f"Scanned {result.files_scanned} file(s). Found {len(result.candidates)} candidate(s).")

    if not result.candidates:
        click.echo("No undetected names found.")
        return

    for i, c in enumerate(result.candidates, 1):
        flag = "  ⚠ near personnel context" if c.near_personnel_context else ""
        click.echo(f"  {i:2}. [{c.candidate_type}] {c.value} ({c.occurrences}x){flag}")
        for snippet in c.context_snippets[:1]:
            click.echo(f"       {snippet}")

    if dry_run:
        click.echo("[dry-run] No changes made.")
        return

    if auto_add:
        count = use_case.add_confirmed_candidates(result.candidates)
        click.echo(click.style(f"Added {count} new entities to database.", fg="green", bold=True))
    else:
        click.echo("")
        click.echo("Enter numbers to confirm (e.g. '1 3 5'), 'all', or press Enter to skip:")
        choice = click.prompt("Your choice", default="")
        if not choice.strip():
            click.echo("No changes made.")
            return

        if choice.strip().lower() == "all":
            confirmed = result.candidates
        else:
            try:
                indices = [int(x) - 1 for x in choice.split()]
                confirmed = [result.candidates[i] for i in indices if 0 <= i < len(result.candidates)]
            except ValueError:
                click.echo("Invalid input. No changes made.", err=True)
                return

        count = use_case.add_confirmed_candidates(confirmed)
        click.echo(click.style(f"Added {count} new entities to database.", fg="green", bold=True))


@cli.command()
@click.option("--port", default=8501, help="Port to run the Streamlit server on.")
def gui(port: int) -> None:
    """Launch the Streamlit web interface in the browser."""
    import subprocess

    app_path = Path(__file__).parent.parent / "gui" / "app.py"
    if not app_path.exists():
        click.echo(f"GUI app not found at {app_path}", err=True)
        sys.exit(2)

    click.echo(f"Starting MilAnon GUI at http://localhost:{port}")
    click.echo("Press Ctrl+C to stop.")
    subprocess.run(
        [sys.executable, "-m", "streamlit", "run", str(app_path), "--server.port", str(port)],
        check=False,
    )
