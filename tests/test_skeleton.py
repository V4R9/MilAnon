"""Tests to verify the project skeleton is correctly set up."""

from click.testing import CliRunner

from milanon import __version__
from milanon.cli.main import cli


class TestProjectSkeleton:
    """Verify basic project setup and CLI entry point."""

    def test_version_is_defined(self) -> None:
        """Version string should be defined and follow semver."""
        assert __version__ is not None
        parts = __version__.split(".")
        assert len(parts) == 3, f"Expected semver format, got: {__version__}"

    def test_cli_version_flag(self) -> None:
        """'milanon --version' should print the version and exit cleanly."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert __version__ in result.output

    def test_cli_help(self) -> None:
        """'milanon --help' should show all commands."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "anonymize" in result.output
        assert "deanonymize" in result.output
        assert "validate" in result.output
        assert "db" in result.output

    def test_cli_anonymize_help(self) -> None:
        """'milanon anonymize --help' should describe the command."""
        runner = CliRunner()
        result = runner.invoke(cli, ["anonymize", "--help"])
        assert result.exit_code == 0
        assert "--output" in result.output
        assert "--recursive" in result.output
        assert "--force" in result.output
        assert "--dry-run" in result.output

    def test_cli_deanonymize_help(self) -> None:
        """'milanon deanonymize --help' should describe the command."""
        runner = CliRunner()
        result = runner.invoke(cli, ["deanonymize", "--help"])
        assert result.exit_code == 0
        assert "--output" in result.output
        assert "--force" in result.output

    def test_cli_db_subcommands(self) -> None:
        """'milanon db --help' should list import, list, stats."""
        runner = CliRunner()
        result = runner.invoke(cli, ["db", "--help"])
        assert result.exit_code == 0
        assert "import" in result.output
        assert "list" in result.output
        assert "stats" in result.output

    def test_cli_db_stats_placeholder(self) -> None:
        """'milanon db stats' should run without error (placeholder output)."""
        runner = CliRunner()
        result = runner.invoke(cli, ["db", "stats"])
        assert result.exit_code == 0
        assert "milanon" in result.output.lower()
