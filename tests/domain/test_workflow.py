"""Tests for WorkflowConfig domain model and INDEX.yaml parsing."""

from __future__ import annotations

from pathlib import Path

import pytest

from milanon.domain.workflow import DoctrineRef, WorkflowConfig, load_workflows

# Minimal INDEX.yaml content for isolated unit tests
_MINIMAL_INDEX = """\
workflows:
  test-analyse:
    name: "Test Analyse"
    description: "A test analyse workflow"
    system_prompt: templates/test-analyse.md
    doctrine:
      - source: some_doctrine.md
        extract: extracts/test_extract.md
      - source: another_doctrine.md
        extract: null
    skeleton: null
    output_format: [markdown]
    maps_to_5+2: "Schritt 1: Problemerfassung"

  test-order:
    name: "Test Order"
    description: "A test order workflow"
    system_prompt: templates/test-order.md
    doctrine:
      - source: bfe_einsatz.md
        extract: extracts/bfe_schema.md
    skeleton: skeletons/test_skeleton.md
    output_format: [markdown, docx]
    maps_to_5+2: "Schritt 5: Befehlsgebung"
    depends_on: [test-analyse]

  no-map:
    name: "No Map"
    description: "Workflow without maps_to_5+2"
    system_prompt: templates/no-map.md
    doctrine: []
    skeleton: null
    output_format: [markdown]
"""


@pytest.fixture
def index_path(tmp_path) -> Path:
    p = tmp_path / "INDEX.yaml"
    p.write_text(_MINIMAL_INDEX, encoding="utf-8")
    return p


class TestLoadWorkflows:
    """Parsing INDEX.yaml into WorkflowConfig objects."""

    def test_load_workflows_parses_index_yaml(self, index_path):
        workflows = load_workflows(index_path)
        assert "test-analyse" in workflows
        assert "test-order" in workflows

    def test_workflow_config_has_required_fields(self, index_path):
        workflows = load_workflows(index_path)
        wf = workflows["test-analyse"]

        assert isinstance(wf, WorkflowConfig)
        assert wf.name == "Test Analyse"
        assert wf.description == "A test analyse workflow"
        assert wf.system_prompt == "templates/test-analyse.md"
        assert wf.skeleton is None
        assert wf.output_format == ["markdown"]
        assert wf.maps_to_5plus2 == "Schritt 1: Problemerfassung"

    def test_doctrine_refs_parsed(self, index_path):
        workflows = load_workflows(index_path)
        wf = workflows["test-analyse"]

        assert len(wf.doctrine) == 2
        assert isinstance(wf.doctrine[0], DoctrineRef)
        assert wf.doctrine[0].source == "some_doctrine.md"
        assert wf.doctrine[0].extract == "extracts/test_extract.md"
        assert wf.doctrine[1].extract is None

    def test_skeleton_parsed(self, index_path):
        workflows = load_workflows(index_path)
        wf = workflows["test-order"]
        assert wf.skeleton == "skeletons/test_skeleton.md"

    def test_depends_on_parsed(self, index_path):
        workflows = load_workflows(index_path)
        wf = workflows["test-order"]
        assert wf.depends_on == ["test-analyse"]

    def test_depends_on_defaults_to_empty(self, index_path):
        workflows = load_workflows(index_path)
        wf = workflows["test-analyse"]
        assert wf.depends_on == []

    def test_maps_to_5plus2_defaults_to_empty(self, index_path):
        """Workflows without maps_to_5+2 get empty string default."""
        workflows = load_workflows(index_path)
        wf = workflows["no-map"]
        assert wf.maps_to_5plus2 == ""

    def test_unknown_workflow_raises_keyerror(self, index_path):
        workflows = load_workflows(index_path)
        with pytest.raises(KeyError):
            _ = workflows["nonexistent-workflow"]

    def test_missing_index_raises_file_not_found(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            load_workflows(tmp_path / "MISSING.yaml")

    def test_real_index_yaml_loads(self):
        """The real data/doctrine/INDEX.yaml parses without errors."""
        real_index = (
            Path(__file__).parent.parent.parent / "data" / "doctrine" / "INDEX.yaml"
        )
        workflows = load_workflows(real_index)
        # Verify key workflows are present
        assert "analyse" in workflows
        assert "wachtdienst" in workflows
        assert "einsatzbefehl" in workflows
