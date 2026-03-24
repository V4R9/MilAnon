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
        assert "README.md" in result.files_created
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

    def test_unit_placeholder_replaced(self, use_case, output_dir):
        """The {unit} placeholder is replaced with the actual unit name."""
        use_case.execute("Inf Kp 56/1", output_dir)
        content = (output_dir / "SYSTEM_PROMPT.md").read_text(encoding="utf-8")

        assert "Inf Kp 56/1" in content
        assert "{unit}" not in content

    def test_generate_creates_readme_not_instructions(self, use_case, output_dir):
        """README.md is created; INSTRUCTIONS.md and WORKFLOWS.md are not."""
        result = use_case.execute("Inf Kp 56/1", output_dir)

        assert (output_dir / "README.md").exists()
        assert not (output_dir / "INSTRUCTIONS.md").exists()
        assert not (output_dir / "WORKFLOWS.md").exists()
        assert "README.md" in result.files_created
        assert "INSTRUCTIONS.md" not in result.files_created
        assert "WORKFLOWS.md" not in result.files_created

    def test_readme_contains_setup_steps(self, use_case, output_dir):
        """README.md contains the 4-step setup guide in German."""
        use_case.execute("Inf Kp 56/1", output_dir)
        content = (output_dir / "README.md").read_text(encoding="utf-8")

        assert "Schritt 1" in content
        assert "Schritt 2" in content
        assert "Schritt 3" in content
        assert "Schritt 4" in content
        assert "SYSTEM_PROMPT.md" in content
        assert "knowledge/" in content
        assert "ß" not in content  # Swiss German — no ß

    def test_generate_includes_cheat_sheet(self, use_case, output_dir):
        """CHEAT_SHEET.md is included if it exists in data/templates/."""
        result = use_case.execute("Inf Kp 56/1", output_dir)

        cheat_sheet_src = DATA_DIR / "templates" / "CHEAT_SHEET.md"
        if cheat_sheet_src.exists():
            assert (output_dir / "CHEAT_SHEET.md").exists()
            assert "CHEAT_SHEET.md" in result.files_created
        else:
            pytest.skip("CHEAT_SHEET.md not found in data/templates/ — skipping")

    def test_generate_copies_anonymized_documents_into_knowledge(
        self, use_case, output_dir, tmp_path
    ):
        """--input flag copies .md files from input_path into knowledge/."""
        input_dir = tmp_path / "anon"
        input_dir.mkdir()
        (input_dir / "rapport_kp.md").write_text("# Rapport [EINHEIT_001]", encoding="utf-8")
        (input_dir / "dossier.md").write_text("# Dossier [PERSON_001]", encoding="utf-8")

        result = use_case.execute("Inf Kp 56/1", output_dir, input_path=input_dir)

        assert (output_dir / "knowledge" / "rapport_kp.md").exists()
        assert (output_dir / "knowledge" / "dossier.md").exists()
        assert "knowledge/rapport_kp.md" in result.files_created
        assert "knowledge/dossier.md" in result.files_created

        content = (output_dir / "knowledge" / "rapport_kp.md").read_text(encoding="utf-8")
        assert "[EINHEIT_001]" in content

    def test_generate_copies_pngs_when_include_images_flag(
        self, use_case, output_dir, tmp_path
    ):
        """--include-images flag copies PNG files from input_path into knowledge/."""
        input_dir = tmp_path / "anon"
        input_dir.mkdir()
        (input_dir / "dossier.md").write_text("# Doc", encoding="utf-8")
        (input_dir / "page_10.png").write_bytes(b"\x89PNG\r\n\x1a\n")  # minimal PNG header
        (input_dir / "page_12.png").write_bytes(b"\x89PNG\r\n\x1a\n")

        result = use_case.execute(
            "Inf Kp 56/1", output_dir, input_path=input_dir, include_images=True
        )

        assert (output_dir / "knowledge" / "page_10.png").exists()
        assert (output_dir / "knowledge" / "page_12.png").exists()
        assert "knowledge/page_10.png" in result.files_created
        assert "knowledge/page_12.png" in result.files_created

    def test_generate_pngs_not_copied_without_flag(
        self, use_case, output_dir, tmp_path
    ):
        """PNG files are NOT copied when include_images=False (default)."""
        input_dir = tmp_path / "anon"
        input_dir.mkdir()
        (input_dir / "dossier.md").write_text("# Doc", encoding="utf-8")
        (input_dir / "page_10.png").write_bytes(b"\x89PNG\r\n\x1a\n")

        result = use_case.execute("Inf Kp 56/1", output_dir, input_path=input_dir)

        assert not (output_dir / "knowledge" / "page_10.png").exists()
        assert "knowledge/page_10.png" not in result.files_created

    def test_generate_without_input_still_works(self, use_case, output_dir):
        """Backward compat: execute() without input_path still works."""
        result = use_case.execute("Inf Kp 56/1", output_dir)

        assert "SYSTEM_PROMPT.md" in result.files_created
        assert "README.md" in result.files_created
        assert "knowledge/bfe_aktionsplanung.md" in result.files_created
        # No input docs in knowledge — only doctrine
        knowledge_files = [f for f in result.files_created if f.startswith("knowledge/")]
        doc_files = [f for f in knowledge_files if f not in [
            "knowledge/bfe_aktionsplanung.md",
            "knowledge/tf_taktik.md",
            "knowledge/wat_wachtdienst.md",
            "knowledge/fso_aktionsplanung.md",
            "knowledge/skeletons.md",
        ]]
        assert doc_files == []
