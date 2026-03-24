"""Tests for the Pack use case."""

import pytest
from pathlib import Path

from milanon.usecases.pack import PackUseCase, list_templates


class TestListTemplates:
    """Template discovery."""

    def test_builtin_templates_found(self):
        templates = list_templates()
        names = [t["name"] for t in templates]
        assert "obsidian-notes" in names
        assert "befehl-entwurf" in names
        assert "analyse" in names
        assert "frei" in names

    def test_templates_have_description(self):
        templates = list_templates()
        for t in templates:
            assert "description" in t
            assert "source" in t

    def test_builtin_templates_have_source_label(self):
        templates = list_templates()
        built_in = [t for t in templates if t["source"] == "built-in"]
        assert len(built_in) >= 4


class TestPackUseCase:
    """Building prompt packs."""

    def test_pack_includes_template(self, tmp_path):
        from milanon.adapters.repositories.sqlite_repository import SqliteMappingRepository
        repo = SqliteMappingRepository(":memory:")
        uc = PackUseCase(repo)

        input_dir = tmp_path / "anon"
        input_dir.mkdir()
        (input_dir / "test.md").write_text(
            "# Anonymized Content\n[PERSON_001] is here.", encoding="utf-8"
        )

        pack_text, result = uc.execute(
            input_path=input_dir,
            template_name="frei",
            user_prompt="Analyse this document",
            copy_clipboard=False,
        )

        assert result.template_used == "frei"
        assert result.documents_included == 1
        assert "Analyse this document" in pack_text
        assert "[PERSON_001] is here" in pack_text

    def test_pack_includes_context(self, tmp_path):
        from milanon.adapters.repositories.sqlite_repository import SqliteMappingRepository
        repo = SqliteMappingRepository(":memory:")
        uc = PackUseCase(repo)

        input_dir = tmp_path / "anon"
        input_dir.mkdir()
        (input_dir / "CONTEXT.md").write_text(
            "# Context\nYour unit is [EINHEIT_001].", encoding="utf-8"
        )
        (input_dir / "doc.md").write_text("Document content.", encoding="utf-8")

        pack_text, result = uc.execute(
            input_path=input_dir,
            template_name="frei",
            user_prompt="Summarize",
            copy_clipboard=False,
        )

        assert result.context_included is True
        assert "Your unit is [EINHEIT_001]" in pack_text
        assert "Document content" in pack_text

    def test_pack_context_not_counted_as_document(self, tmp_path):
        from milanon.adapters.repositories.sqlite_repository import SqliteMappingRepository
        repo = SqliteMappingRepository(":memory:")
        uc = PackUseCase(repo)

        input_dir = tmp_path / "anon"
        input_dir.mkdir()
        (input_dir / "CONTEXT.md").write_text("Context.", encoding="utf-8")
        (input_dir / "doc.md").write_text("Doc.", encoding="utf-8")

        _, result = uc.execute(
            input_path=input_dir,
            template_name="frei",
            user_prompt="x",
            copy_clipboard=False,
        )

        assert result.documents_included == 1  # CONTEXT.md excluded

    def test_pack_replaces_user_unit_variable(self, tmp_path):
        from milanon.adapters.repositories.sqlite_repository import SqliteMappingRepository
        repo = SqliteMappingRepository(":memory:")
        uc = PackUseCase(repo)

        input_dir = tmp_path / "anon"
        input_dir.mkdir()
        (input_dir / "doc.md").write_text("Content.", encoding="utf-8")

        pack_text, result = uc.execute(
            input_path=input_dir,
            template_name="befehl-entwurf",
            user_unit="[EINHEIT_001]",
            copy_clipboard=False,
        )

        assert "[EINHEIT_001]" in pack_text
        assert "{user_unit}" not in pack_text

    def test_pack_writes_to_file(self, tmp_path):
        from milanon.adapters.repositories.sqlite_repository import SqliteMappingRepository
        repo = SqliteMappingRepository(":memory:")
        uc = PackUseCase(repo)

        input_dir = tmp_path / "anon"
        input_dir.mkdir()
        (input_dir / "doc.md").write_text("Content.", encoding="utf-8")
        output_file = tmp_path / "pack.md"

        pack_text, result = uc.execute(
            input_path=input_dir,
            template_name="frei",
            user_prompt="Test",
            output_path=output_file,
            copy_clipboard=False,
        )

        assert output_file.exists()
        assert output_file.read_text(encoding="utf-8") == pack_text
        assert result.output_path == str(output_file)

    def test_pack_single_file_input(self, tmp_path):
        from milanon.adapters.repositories.sqlite_repository import SqliteMappingRepository
        repo = SqliteMappingRepository(":memory:")
        uc = PackUseCase(repo)

        input_file = tmp_path / "report.md"
        input_file.write_text("[PERSON_001] signed off.", encoding="utf-8")

        pack_text, result = uc.execute(
            input_path=input_file,
            template_name="frei",
            user_prompt="Review",
            copy_clipboard=False,
        )

        assert result.documents_included == 1
        assert "report.md" in pack_text

    def test_pack_invalid_template_raises(self, tmp_path):
        from milanon.adapters.repositories.sqlite_repository import SqliteMappingRepository
        repo = SqliteMappingRepository(":memory:")
        uc = PackUseCase(repo)

        input_dir = tmp_path / "anon"
        input_dir.mkdir()
        (input_dir / "doc.md").write_text("Content.", encoding="utf-8")

        with pytest.raises(ValueError, match="Template.*not found"):
            uc.execute(
                input_path=input_dir,
                template_name="nonexistent",
                copy_clipboard=False,
            )

    def test_pack_total_chars_set(self, tmp_path):
        from milanon.adapters.repositories.sqlite_repository import SqliteMappingRepository
        repo = SqliteMappingRepository(":memory:")
        uc = PackUseCase(repo)

        input_dir = tmp_path / "anon"
        input_dir.mkdir()
        (input_dir / "doc.md").write_text("Content.", encoding="utf-8")

        pack_text, result = uc.execute(
            input_path=input_dir,
            template_name="frei",
            user_prompt="x",
            copy_clipboard=False,
        )

        assert result.total_chars == len(pack_text)
        assert result.total_chars > 0

    def test_pack_explicit_context_path(self, tmp_path):
        from milanon.adapters.repositories.sqlite_repository import SqliteMappingRepository
        repo = SqliteMappingRepository(":memory:")
        uc = PackUseCase(repo)

        ctx_file = tmp_path / "MY_CONTEXT.md"
        ctx_file.write_text("# Explicit context", encoding="utf-8")
        input_dir = tmp_path / "anon"
        input_dir.mkdir()
        (input_dir / "doc.md").write_text("Doc.", encoding="utf-8")

        pack_text, result = uc.execute(
            input_path=input_dir,
            template_name="frei",
            user_prompt="x",
            context_path=ctx_file,
            copy_clipboard=False,
        )

        assert result.context_included is True
        assert "Explicit context" in pack_text
