"""Tests for GenerateProjectUseCase — Claude.ai Project folder generation."""

from pathlib import Path

import pytest

from milanon.usecases.generate_project import GenerateProjectUseCase

DATA_DIR = Path("data")


@pytest.fixture
def use_case():
    return GenerateProjectUseCase(DATA_DIR)


@pytest.fixture
def output_dir(tmp_path):
    return tmp_path / "project"


class TestGenerateProjectUseCase:
    def test_generate_creates_all_expected_files(self, use_case, output_dir):
        """All expected project files are created."""
        result = use_case.execute("Inf Kp 56/1", output_dir)

        assert output_dir.exists()
        assert "SYSTEM_PROMPT.md" in result.files_created
        assert "INSTRUCTIONS.md" in result.files_created
        assert "WORKFLOWS.md" in result.files_created
        assert "knowledge/bfe_aktionsplanung.md" in result.files_created
        assert "knowledge/tf_taktik.md" in result.files_created
        assert "knowledge/wat_wachtdienst.md" in result.files_created
        assert "knowledge/fso_aktionsplanung.md" in result.files_created
        assert "knowledge/skeletons.md" in result.files_created

        # Verify files actually exist on disk
        for f in result.files_created:
            assert (output_dir / f).exists(), f"File missing: {f}"

    def test_system_prompt_contains_role_and_rules(self, use_case, output_dir):
        """SYSTEM_PROMPT.md contains Layer 1 (role) and Layer 5 (rules) content."""
        use_case.execute("Inf Kp 56/1", output_dir)
        content = (output_dir / "SYSTEM_PROMPT.md").read_text(encoding="utf-8")

        # Layer 1: role content
        assert "Swiss Army" in content
        assert "5+2 Aktionsplanungsprozess" in content
        assert "Einsatzgrundsätze" in content

        # Layer 5: rules content
        assert "Placeholder Handling" in content
        assert "[PLACEHOLDER]" in content
        assert "KDT ENTSCHEID" in content

    def test_knowledge_files_contain_doctrine_content(self, use_case, output_dir):
        """Knowledge files contain actual doctrine content from extracts."""
        use_case.execute("Inf Kp 56/1", output_dir)

        # BFE Aktionsplanung should have content from multiple BFE extracts
        bfe = (output_dir / "knowledge" / "bfe_aktionsplanung.md").read_text(
            encoding="utf-8"
        )
        assert "Problemerfassung" in bfe
        assert "Beurteilung der Lage" in bfe

        # TF Taktik should have Einsatzgrundsätze
        tf = (output_dir / "knowledge" / "tf_taktik.md").read_text(encoding="utf-8")
        assert "Einsatzgrundsätze" in tf

        # WAT should have Wachtdienstbefehl content
        wat = (output_dir / "knowledge" / "wat_wachtdienst.md").read_text(
            encoding="utf-8"
        )
        assert "Wachtdienstbefehl" in wat

        # FSO should have Aktionsplanung
        fso = (output_dir / "knowledge" / "fso_aktionsplanung.md").read_text(
            encoding="utf-8"
        )
        assert "Aktionsplanung" in fso

    def test_instructions_in_german(self, use_case, output_dir):
        """INSTRUCTIONS.md is written in German (Swiss, no ß)."""
        use_case.execute("Inf Kp 56/1", output_dir)
        content = (output_dir / "INSTRUCTIONS.md").read_text(encoding="utf-8")

        # German content markers
        assert "Was ist dieses Projekt" in content
        assert "Wie richte ich es ein" in content
        assert "Wie benutze ich es" in content
        assert "Was muss ICH als Kdt entscheiden" in content

        # No ß (Swiss German rule)
        assert "ß" not in content

    def test_unit_placeholder_replaced(self, use_case, output_dir):
        """The {unit} placeholder is replaced with the actual unit name."""
        use_case.execute("Inf Kp 56/1", output_dir)
        content = (output_dir / "SYSTEM_PROMPT.md").read_text(encoding="utf-8")

        assert "Inf Kp 56/1" in content
        assert "{unit}" not in content
