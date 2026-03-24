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
    click.echo(f"{mode}Scanned:   {result.files_scanned}")
    click.echo(f"{mode}New:       {result.files_new}")
    click.echo(f"{mode}Changed:   {result.files_changed}")
    click.echo(f"{mode}Skipped:   {result.files_skipped}")
    click.echo(f"{mode}Errors:    {result.files_error}")
    click.echo(f"{mode}Entities:  {result.entities_found}")

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
@click.option("--output", "-o", required=True, type=click.Path(), help="Output directory.")
@click.option("--force", is_flag=True, help="Reprocess all files, ignoring cache.")
@click.option("--dry-run", is_flag=True, help="Show what would be processed without doing it.")
def deanonymize(input_path: str, output: str, force: bool, dry_run: bool) -> None:
    """De-anonymize LLM outputs by restoring original entity values."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    repo = _make_repo()
    use_case = _make_deanonymize_use_case(repo)

    result = use_case.execute(
        Path(input_path),
        Path(output),
        force=force,
        dry_run=dry_run,
    )

    mode = "[dry-run] " if dry_run else ""
    click.echo(f"{mode}Scanned:    {result.files_scanned}")
    click.echo(f"{mode}New:        {result.files_new}")
    click.echo(f"{mode}Changed:    {result.files_changed}")
    click.echo(f"{mode}Skipped:    {result.files_skipped}")
    click.echo(f"{mode}Errors:     {result.files_error}")
    click.echo(f"{mode}Resolved:   {result.placeholders_resolved}")

    for warning in result.warnings:
        click.echo(f"  WARNING: {warning}", err=True)

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
        # Clear existing ref data to allow re-initialization
        repo._conn.execute("DELETE FROM ref_municipalities")
        repo._conn.execute("DELETE FROM ref_military_units")
        repo._conn.commit()

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
