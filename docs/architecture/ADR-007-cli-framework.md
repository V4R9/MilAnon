# ADR-007: CLI Framework

## Status
Accepted — 2026-03-23

## Context
MilAnon MVP is a command-line tool. We need a CLI framework that supports subcommands (`anonymize`, `deanonymize`, `db`), options, flags, progress output, and good error messages.

## Options Considered

### Option A: click
- **Pro:** Most popular Python CLI framework. Clean decorator-based API. Built-in support for subcommands (groups), options, types, help generation, progress bars. Well-documented. Used by pip, Flask, and many major projects.
- **Con:** External dependency (but small and stable).

### Option B: argparse (stdlib)
- **Pro:** No external dependency. Part of Python stdlib.
- **Con:** Verbose for subcommands. No built-in progress bars. Error messages less user-friendly. More boilerplate.

### Option C: typer
- **Pro:** Modern, type-hint-based API. Built on click. Less boilerplate than click.
- **Con:** Additional abstraction layer. Less mature than click. Some advanced click features require dropping down to click anyway.

## Decision
**click 8.x** — proven, stable, excellent subcommand support.

## CLI Structure

```
milanon
├── anonymize <input> --output <output> [--recursive] [--db-path <path>]
├── deanonymize <input> --output <output> [--db-path <path>]
├── validate <file> [--db-path <path>]
└── db
    ├── import <csv_path> [--format miloffice|generic]
    ├── list [--type PERSON|ORT|...] [--limit N]
    └── stats
```

## Consequences
- `click` is added as a project dependency.
- CLI entry point defined in `pyproject.toml` as `[project.scripts] milanon = "milanon.cli.main:cli"`.
- Each subcommand in its own file under `src/milanon/cli/`.
- Progress bars use `click.progressbar()` for batch operations.
- Error output via `click.echo()` to stderr with appropriate exit codes.
