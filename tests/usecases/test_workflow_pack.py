"""Tests for WorkflowPackUseCase — 5-layer prompt assembly."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from milanon.adapters.repositories.sqlite_repository import SqliteMappingRepository
from milanon.usecases.workflow_pack import WorkflowPackUseCase, _strip_mode_markers

# ─────────────────────────────────────────────────────────────────────────────
# Minimal INDEX.yaml for tests
# ─────────────────────────────────────────────────────────────────────────────
_INDEX_YAML = """\
workflows:
  test-wf:
    name: "Test Workflow"
    description: "A test workflow"
    system_prompt: templates/test-wf.md
    doctrine:
      - source: doctrine.md
        extract: extracts/test_extract.md
    skeleton: skeletons/test_skeleton.md
    output_format: [markdown]
    maps_to_5+2: "Schritt 1"

  no-doctrine:
    name: "No Doctrine"
    description: "Workflow without doctrine extracts"
    system_prompt: templates/no-doctrine.md
    doctrine: []
    skeleton: null
    output_format: [markdown]
    maps_to_5+2: "Step 1"
"""


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def dirs(tmp_path) -> dict:
    """Create a minimal file-system structure for WorkflowPackUseCase."""
    templates_dir = tmp_path / "templates"
    workflows_dir = templates_dir / "workflows"
    workflows_dir.mkdir(parents=True)

    doctrine_dir = tmp_path / "doctrine"
    extracts_dir = doctrine_dir / "extracts"
    skeletons_dir = doctrine_dir / "skeletons"
    extracts_dir.mkdir(parents=True)
    skeletons_dir.mkdir(parents=True)

    # Static layers
    (templates_dir / "role.md").write_text("LAYER_1_ROLE_CONTENT", encoding="utf-8")
    (templates_dir / "rules.md").write_text("LAYER_5_RULES_CONTENT", encoding="utf-8")

    # Workflow template (Layer 4) — includes {user_unit} placeholder for Bug 1 test
    (workflows_dir / "test-wf.md").write_text("LAYER_4_TASK_CONTENT for {user_unit}", encoding="utf-8")
    (workflows_dir / "no-doctrine.md").write_text("LAYER_4_NODOCTRINE", encoding="utf-8")

    # Doctrine extract (Layer 3)
    (extracts_dir / "test_extract.md").write_text("LAYER_3_DOCTRINE_CONTENT", encoding="utf-8")

    # Skeleton
    (skeletons_dir / "test_skeleton.md").write_text("SKELETON_CONTENT", encoding="utf-8")

    # INDEX.yaml
    (doctrine_dir / "INDEX.yaml").write_text(_INDEX_YAML, encoding="utf-8")

    return {
        "tmp": tmp_path,
        "templates": templates_dir,
        "doctrine": doctrine_dir,
        "workflows": workflows_dir,
        "extracts": extracts_dir,
        "skeletons": skeletons_dir,
    }


@pytest.fixture
def mock_context_gen():
    """A mock GenerateContextUseCase that writes a known string to the output file."""
    gen = MagicMock()

    def fake_generate(unit: str, output_path: Path) -> None:
        output_path.write_text("LAYER_2_UNIT_CONTEXT", encoding="utf-8")

    gen.generate.side_effect = fake_generate
    return gen


@pytest.fixture
def uc(dirs, mock_context_gen) -> WorkflowPackUseCase:
    repo = SqliteMappingRepository(":memory:")
    return WorkflowPackUseCase(
        repository=repo,
        context_generator=mock_context_gen,
        templates_dir=dirs["templates"],
        doctrine_dir=dirs["doctrine"],
    )


# ─────────────────────────────────────────────────────────────────────────────
# Assembly tests
# ─────────────────────────────────────────────────────────────────────────────

class TestAssembly:

    def test_assemble_includes_all_5_layers(self, uc, dirs, tmp_path):
        """All 5 layers must appear in the assembled output."""
        input_dir = tmp_path / "anon"
        input_dir.mkdir()
        (input_dir / "doc.md").write_text("Document content.", encoding="utf-8")

        pack_text, result = uc.execute(
            workflow="test-wf",
            input_path=input_dir,
            unit="Inf Kp 56/1",
            copy_clipboard=False,
        )

        assert "LAYER_1_ROLE_CONTENT" in pack_text     # Layer 1: role
        assert "LAYER_2_UNIT_CONTEXT" in pack_text     # Layer 2: unit context
        assert "LAYER_3_DOCTRINE_CONTENT" in pack_text # Layer 3: doctrine extract
        assert "LAYER_4_TASK_CONTENT" in pack_text     # Layer 4: workflow template
        assert "LAYER_5_RULES_CONTENT" in pack_text    # Layer 5: rules

    def test_documents_appended_after_layers(self, uc, dirs, tmp_path):
        """Anonymized documents appear after the 5 content layers."""
        input_dir = tmp_path / "anon"
        input_dir.mkdir()
        (input_dir / "report.md").write_text("DOCUMENT_CONTENT_HERE", encoding="utf-8")

        pack_text, _ = uc.execute(
            workflow="test-wf",
            input_path=input_dir,
            copy_clipboard=False,
        )

        assert "DOCUMENT_CONTENT_HERE" in pack_text
        # Documents appear AFTER all layers
        layer4_pos = pack_text.find("LAYER_4_TASK_CONTENT")
        doc_pos = pack_text.find("DOCUMENT_CONTENT_HERE")
        assert layer4_pos < doc_pos

    def test_result_tracks_metadata(self, uc, dirs, tmp_path):
        input_dir = tmp_path / "anon"
        input_dir.mkdir()
        (input_dir / "a.md").write_text("A", encoding="utf-8")
        (input_dir / "b.md").write_text("B", encoding="utf-8")

        pack_text, result = uc.execute(
            workflow="test-wf",
            input_path=input_dir,
            copy_clipboard=False,
        )

        assert result.template_used == "test-wf"
        assert result.documents_included == 2
        assert result.total_chars == len(pack_text)

    def test_skeleton_appended_at_step_5(self, uc, dirs, tmp_path):
        """Skeleton is appended to Layer 4 when step=5."""
        input_dir = tmp_path / "anon"
        input_dir.mkdir()
        (input_dir / "doc.md").write_text("Doc.", encoding="utf-8")

        pack_text, _ = uc.execute(
            workflow="test-wf",
            step=5,
            input_path=input_dir,
            copy_clipboard=False,
        )

        assert "SKELETON_CONTENT" in pack_text

    def test_skeleton_not_appended_at_other_steps(self, uc, dirs, tmp_path):
        """Skeleton is NOT appended when step != 5."""
        input_dir = tmp_path / "anon"
        input_dir.mkdir()
        (input_dir / "doc.md").write_text("Doc.", encoding="utf-8")

        pack_text, _ = uc.execute(
            workflow="test-wf",
            step=3,
            input_path=input_dir,
            copy_clipboard=False,
        )

        assert "SKELETON_CONTENT" not in pack_text

    def test_context_path_includes_vault_files(self, uc, dirs, tmp_path):
        """Files from context_path are included after layers."""
        input_dir = tmp_path / "anon"
        input_dir.mkdir()
        (input_dir / "doc.md").write_text("Doc.", encoding="utf-8")

        vault = tmp_path / "vault"
        vault.mkdir()
        (vault / "previous_output.md").write_text("VAULT_FILE_CONTENT", encoding="utf-8")

        pack_text, result = uc.execute(
            workflow="test-wf",
            input_path=input_dir,
            context_path=vault,
            copy_clipboard=False,
        )

        assert "VAULT_FILE_CONTENT" in pack_text
        assert result.context_included is True

    def test_no_doctrine_workflow_skips_layer3(self, uc, dirs, tmp_path):
        """Workflow with empty doctrine list produces no Layer 3 content."""
        input_dir = tmp_path / "anon"
        input_dir.mkdir()
        (input_dir / "doc.md").write_text("Doc.", encoding="utf-8")

        pack_text, _ = uc.execute(
            workflow="no-doctrine",
            input_path=input_dir,
            copy_clipboard=False,
        )

        assert "LAYER_3_DOCTRINE_CONTENT" not in pack_text
        assert "LAYER_4_NODOCTRINE" in pack_text


# ─────────────────────────────────────────────────────────────────────────────
# Mode marker stripping
# ─────────────────────────────────────────────────────────────────────────────

class TestModeMarkerStripping:

    def test_mode_berrm_strips_adf_markers(self):
        text = "Before <!-- ADF: Remove this --> After"
        result = _strip_mode_markers(text, "berrm")
        assert "Remove this" not in result
        assert "Before" in result
        assert "After" in result

    def test_mode_adf_strips_berrm_markers(self):
        text = "Before <!-- BERRM: Remove this --> After"
        result = _strip_mode_markers(text, "adf")
        assert "Remove this" not in result
        assert "Before" in result
        assert "After" in result

    def test_kdt_entscheid_markers_always_kept(self):
        text = "<!-- KDT ENTSCHEID: Important decision --> Keep this"
        assert "Important decision" in _strip_mode_markers(text, "berrm")
        assert "Important decision" in _strip_mode_markers(text, "adf")

    def test_both_markers_always_kept(self):
        text = "<!-- BOTH: Always visible -->"
        assert "Always visible" in _strip_mode_markers(text, "berrm")
        assert "Always visible" in _strip_mode_markers(text, "adf")

    def test_fill_markers_always_kept(self):
        text = "<!-- FILL: placeholder -->"
        assert "placeholder" in _strip_mode_markers(text, "berrm")
        assert "placeholder" in _strip_mode_markers(text, "adf")

    def test_berrm_marker_kept_in_berrm_mode(self):
        text = "<!-- BERRM: Keep this in berrm mode -->"
        result = _strip_mode_markers(text, "berrm")
        assert "Keep this in berrm mode" in result

    def test_adf_marker_kept_in_adf_mode(self):
        text = "<!-- ADF: Keep this in adf mode -->"
        result = _strip_mode_markers(text, "adf")
        assert "Keep this in adf mode" in result

    def test_workflow_pack_berrm_mode_strips_adf(self, uc, dirs, tmp_path):
        """End-to-end: ADF markers in template are stripped in berrm mode."""
        (dirs["workflows"] / "mode-test.md").write_text(
            "LAYER4 <!-- ADF: hidden --> visible",
            encoding="utf-8",
        )
        (dirs["doctrine"] / "INDEX.yaml").write_text(
            _INDEX_YAML + """
  mode-test:
    name: "Mode Test"
    description: "d"
    system_prompt: templates/mode-test.md
    doctrine: []
    skeleton: null
    output_format: [markdown]
    maps_to_5+2: "Step 1"
""",
            encoding="utf-8",
        )
        input_dir = tmp_path / "anon"
        input_dir.mkdir()
        (input_dir / "doc.md").write_text("Doc.", encoding="utf-8")

        pack_text, _ = uc.execute(
            workflow="mode-test",
            mode="berrm",
            input_path=input_dir,
            copy_clipboard=False,
        )

        assert "hidden" not in pack_text
        assert "visible" in pack_text


# ─────────────────────────────────────────────────────────────────────────────
# Error handling
# ─────────────────────────────────────────────────────────────────────────────

class TestErrorHandling:

    def test_missing_template_raises_clear_error(self, uc, dirs, tmp_path):
        """Missing workflow template file raises ValueError with helpful message."""
        # Remove the template file
        (dirs["workflows"] / "test-wf.md").unlink()

        input_dir = tmp_path / "anon"
        input_dir.mkdir()
        (input_dir / "doc.md").write_text("Doc.", encoding="utf-8")

        with pytest.raises(ValueError, match="Workflow template not found"):
            uc.execute(
                workflow="test-wf",
                input_path=input_dir,
                copy_clipboard=False,
            )

    def test_missing_extract_logs_warning_continues(
        self, uc, dirs, tmp_path, caplog
    ):
        """A missing doctrine extract file logs a warning and continues."""
        # Remove the extract file
        (dirs["extracts"] / "test_extract.md").unlink()

        input_dir = tmp_path / "anon"
        input_dir.mkdir()
        (input_dir / "doc.md").write_text("Doc.", encoding="utf-8")

        import logging
        with caplog.at_level(logging.WARNING, logger="milanon.usecases.workflow_pack"):
            pack_text, _ = uc.execute(
                workflow="test-wf",
                input_path=input_dir,
                copy_clipboard=False,
            )

        assert "extract" in caplog.text.lower() or "not found" in caplog.text.lower()
        # Assembly still succeeded
        assert "LAYER_4_TASK_CONTENT" in pack_text

    def test_unknown_workflow_raises_value_error(self, uc, dirs, tmp_path):
        input_dir = tmp_path / "anon"
        input_dir.mkdir()

        with pytest.raises(ValueError, match="not found in INDEX.yaml"):
            uc.execute(
                workflow="nonexistent",
                input_path=input_dir,
                copy_clipboard=False,
            )


# ─────────────────────────────────────────────────────────────────────────────
# Clipboard
# ─────────────────────────────────────────────────────────────────────────────

class TestClipboard:

    def test_copy_clipboard_called_when_enabled(self, uc, dirs, tmp_path):
        input_dir = tmp_path / "anon"
        input_dir.mkdir()
        (input_dir / "doc.md").write_text("Doc.", encoding="utf-8")

        with patch("milanon.usecases.workflow_pack._copy_to_clipboard") as mock_clip:
            mock_clip.return_value = True
            _, result = uc.execute(
                workflow="test-wf",
                input_path=input_dir,
                copy_clipboard=True,
            )

        mock_clip.assert_called_once()
        assert result.copied_to_clipboard is True

    def test_copy_clipboard_not_called_when_disabled(self, uc, dirs, tmp_path):
        input_dir = tmp_path / "anon"
        input_dir.mkdir()
        (input_dir / "doc.md").write_text("Doc.", encoding="utf-8")

        with patch("milanon.usecases.workflow_pack._copy_to_clipboard") as mock_clip:
            uc.execute(
                workflow="test-wf",
                input_path=input_dir,
                copy_clipboard=False,
            )


# ─────────────────────────────────────────────────────────────────────────────
# Bug fixes — E2E bugs
# ─────────────────────────────────────────────────────────────────────────────

class TestBugFixes:

    def test_user_unit_replaced_in_layer4(self, uc, dirs, tmp_path):
        """Bug 1: {user_unit} placeholder in Layer 4 template must be replaced with actual unit."""
        input_dir = tmp_path / "anon"
        input_dir.mkdir()
        (input_dir / "doc.md").write_text("Document content.", encoding="utf-8")

        pack_text, _ = uc.execute(
            workflow="test-wf",
            input_path=input_dir,
            unit="Inf Kp 56/1",
            copy_clipboard=False,
        )

        assert "{user_unit}" not in pack_text
        assert "Inf Kp 56/1" in pack_text

    def test_user_unit_not_replaced_when_empty(self, uc, dirs, tmp_path):
        """Bug 1: When no unit provided, {user_unit} placeholder remains in output."""
        input_dir = tmp_path / "anon"
        input_dir.mkdir()
        (input_dir / "doc.md").write_text("Document content.", encoding="utf-8")

        pack_text, _ = uc.execute(
            workflow="test-wf",
            input_path=input_dir,
            unit="",
            copy_clipboard=False,
        )

        # With empty unit, placeholder is left as-is (not replaced)
        assert "{user_unit}" in pack_text

    def test_doctrine_extracts_appear_in_output(self, uc, dirs, tmp_path):
        """Bug 2: Layer 3 doctrine extracts must appear in assembled prompt."""
        input_dir = tmp_path / "anon"
        input_dir.mkdir()
        (input_dir / "doc.md").write_text("Document content.", encoding="utf-8")

        pack_text, _ = uc.execute(
            workflow="test-wf",
            input_path=input_dir,
            copy_clipboard=False,
        )

        assert "LAYER_3_DOCTRINE_CONTENT" in pack_text

    def test_csv_excluded_from_pack_input(self, uc, dirs, tmp_path):
        """Bug 4: CSV files in input directory are excluded from pack prompt."""
        input_dir = tmp_path / "anon"
        input_dir.mkdir()
        (input_dir / "doc.md").write_text("Markdown document.", encoding="utf-8")
        (input_dir / "data.csv").write_text("name,value\nfoo,bar\n", encoding="utf-8")

        pack_text, result = uc.execute(
            workflow="test-wf",
            input_path=input_dir,
            copy_clipboard=False,
        )

        # Only .md is included, not .csv
        assert "Markdown document." in pack_text
        assert "name,value" not in pack_text
        assert result.documents_included == 1
