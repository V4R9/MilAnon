"""CLI integration tests for Paket F — workflow, doctrine, export, config commands."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import click.testing
import pytest

from milanon.cli.main import cli

_DATA_DIR = Path(__file__).parent.parent.parent / "data"
_DOCTRINE_DIR = _DATA_DIR / "doctrine"


@pytest.fixture
def runner():
    return click.testing.CliRunner()


@pytest.fixture
def tmp_input(tmp_path: Path) -> Path:
    """Create a minimal Markdown input file."""
    f = tmp_path / "input.md"
    f.write_text("# Test\nHello [PERSON_001].\n", encoding="utf-8")
    return f


# ---------------------------------------------------------------------------
# pack --workflow
# ---------------------------------------------------------------------------


class TestPackWithWorkflow:
    def test_pack_without_workflow_uses_old_pack(self, runner, tmp_input):
        """Backward compat: pack without --workflow uses PackUseCase."""
        result = runner.invoke(cli, [
            "pack", str(tmp_input), "--template", "frei", "--no-clipboard",
        ])
        assert result.exit_code == 0
        assert "Template:" in result.output

    def test_pack_with_workflow_flag_uses_workflow_pack(self, runner, tmp_input):
        """--workflow triggers WorkflowPackUseCase."""
        with patch("milanon.usecases.workflow_pack.WorkflowPackUseCase") as mock_cls:
            mock_uc = MagicMock()
            mock_result = MagicMock(
                template_used="analyse",
                context_included=False,
                documents_included=1,
                total_chars=100,
                copied_to_clipboard=False,
                output_path=None,
            )
            mock_uc.execute.return_value = ("pack text", mock_result)
            mock_cls.return_value = mock_uc

            result = runner.invoke(cli, [
                "pack", str(tmp_input),
                "--workflow", "analyse",
                "--mode", "berrm",
                "--no-clipboard",
            ])
            assert result.exit_code == 0
            mock_uc.execute.assert_called_once()
            call_kwargs = mock_uc.execute.call_args
            assert call_kwargs.kwargs["workflow"] == "analyse"
            assert call_kwargs.kwargs["mode"] == "berrm"

    def test_pack_with_mode_flag_passes_through(self, runner, tmp_input):
        """--mode is forwarded to WorkflowPackUseCase."""
        with patch("milanon.usecases.workflow_pack.WorkflowPackUseCase") as mock_cls:
            mock_uc = MagicMock()
            mock_result = MagicMock(
                template_used="analyse",
                context_included=False,
                documents_included=1,
                total_chars=100,
                copied_to_clipboard=False,
                output_path=None,
            )
            mock_uc.execute.return_value = ("pack text", mock_result)
            mock_cls.return_value = mock_uc

            result = runner.invoke(cli, [
                "pack", str(tmp_input),
                "--workflow", "analyse",
                "--mode", "adf",
                "--no-clipboard",
            ])
            assert result.exit_code == 0
            assert mock_uc.execute.call_args.kwargs["mode"] == "adf"

    def test_pack_with_step_flag(self, runner, tmp_input):
        """--step is forwarded to WorkflowPackUseCase."""
        with patch("milanon.usecases.workflow_pack.WorkflowPackUseCase") as mock_cls:
            mock_uc = MagicMock()
            mock_result = MagicMock(
                template_used="analyse",
                context_included=False,
                documents_included=1,
                total_chars=100,
                copied_to_clipboard=False,
                output_path=None,
            )
            mock_uc.execute.return_value = ("pack text", mock_result)
            mock_cls.return_value = mock_uc

            result = runner.invoke(cli, [
                "pack", str(tmp_input),
                "--workflow", "analyse",
                "--step", "5",
                "--no-clipboard",
            ])
            assert result.exit_code == 0
            assert mock_uc.execute.call_args.kwargs["step"] == 5


# ---------------------------------------------------------------------------
# doctrine
# ---------------------------------------------------------------------------


class TestDoctrineCli:
    @pytest.mark.skipif(
        not (_DOCTRINE_DIR / "INDEX.yaml").exists(),
        reason="Doctrine INDEX.yaml not present",
    )
    def test_doctrine_list_exits_zero(self, runner):
        result = runner.invoke(cli, ["doctrine", "list"])
        assert result.exit_code == 0

    @pytest.mark.skipif(
        not (_DOCTRINE_DIR / "INDEX.yaml").exists(),
        reason="Doctrine INDEX.yaml not present",
    )
    def test_doctrine_extract_all_exits_zero(self, runner, tmp_path):
        result = runner.invoke(cli, ["doctrine", "extract", "--all", "-o", str(tmp_path)])
        assert result.exit_code == 0
        assert "Extracted" in result.output


# ---------------------------------------------------------------------------
# export
# ---------------------------------------------------------------------------


class TestExportCli:
    def test_export_docx_creates_file(self, runner, tmp_input, tmp_path):
        """export --docx produces a .docx file."""
        tpl = _DATA_DIR / "templates" / "docx" / "befehl_vorlage.docx"
        if not tpl.exists():
            pytest.skip("DOCX template not present")

        out = tmp_path / "output.docx"
        result = runner.invoke(cli, [
            "export", str(tmp_input),
            "--docx",
            "--template", str(tpl),
            "--output", str(out),
        ])
        assert result.exit_code == 0
        assert out.exists()

    def test_export_without_docx_flag_errors(self, runner, tmp_input):
        result = runner.invoke(cli, ["export", str(tmp_input)])
        assert result.exit_code != 0
        assert "specify --docx" in result.output


# ---------------------------------------------------------------------------
# config
# ---------------------------------------------------------------------------


class TestConfigCli:
    def test_config_set_and_get_roundtrip(self, runner, tmp_path, monkeypatch):
        """config set + config get roundtrips correctly."""
        config_file = tmp_path / "config.json"
        monkeypatch.setattr("milanon.cli.main._CONFIG_PATH", config_file)

        result = runner.invoke(cli, ["config", "set", "mode", "adf"])
        assert result.exit_code == 0
        assert "mode = adf" in result.output

        result = runner.invoke(cli, ["config", "get", "mode"])
        assert result.exit_code == 0
        assert "mode = adf" in result.output

    def test_config_get_unset_key(self, runner, tmp_path, monkeypatch):
        config_file = tmp_path / "config.json"
        monkeypatch.setattr("milanon.cli.main._CONFIG_PATH", config_file)

        result = runner.invoke(cli, ["config", "get", "nonexistent"])
        assert result.exit_code == 0
        assert "(not set)" in result.output
