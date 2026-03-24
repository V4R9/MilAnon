"""Tests for the Unpack use case."""

import pytest
from pathlib import Path

from milanon.adapters.repositories.sqlite_repository import SqliteMappingRepository
from milanon.domain.entities import EntityType
from milanon.domain.mapping_service import MappingService
from milanon.domain.deanonymizer import DeAnonymizer
from milanon.usecases.unpack import UnpackUseCase


@pytest.fixture
def unpack_setup():
    repo = SqliteMappingRepository(":memory:")
    repo.create_mapping(EntityType.PERSON, "Thomas WEGMÜLLER")
    repo.create_mapping(EntityType.ORT, "Zürich")
    service = MappingService(repo)
    da = DeAnonymizer(service)
    return UnpackUseCase(da)


class TestUnpackFromText:

    def test_deanonymize_text_to_file(self, unpack_setup, tmp_path):
        uc = unpack_setup
        output_dir = tmp_path / "vault"

        result = uc.execute(
            output_dir=output_dir,
            input_text="# Report\n[PERSON_001] lives in [ORT_001].",
        )

        assert result.placeholders_resolved == 2
        assert result.files_written == 1
        content = (output_dir / "llm_output.md").read_text(encoding="utf-8")
        assert "Thomas WEGMÜLLER" in content
        assert "Zürich" in content

    def test_empty_text_no_crash(self, unpack_setup, tmp_path):
        uc = unpack_setup
        result = uc.execute(output_dir=tmp_path, input_text="No placeholders here.")
        assert result.placeholders_resolved == 0
        assert result.files_written == 1

    def test_source_is_text(self, unpack_setup, tmp_path):
        uc = unpack_setup
        result = uc.execute(output_dir=tmp_path, input_text="Hello.")
        assert result.source == "text"

    def test_output_dir_created_if_missing(self, unpack_setup, tmp_path):
        uc = unpack_setup
        output_dir = tmp_path / "new" / "nested"
        result = uc.execute(output_dir=output_dir, input_text="Content.")
        assert output_dir.exists()
        assert result.files_written == 1


class TestUnpackFromFile:

    def test_deanonymize_from_file(self, unpack_setup, tmp_path):
        uc = unpack_setup
        input_file = tmp_path / "llm_response.md"
        input_file.write_text("Hello [PERSON_001]!", encoding="utf-8")
        output_dir = tmp_path / "output"

        result = uc.execute(output_dir=output_dir, input_file=input_file)

        assert result.placeholders_resolved == 1
        assert result.source == "file:llm_response.md"

    def test_in_place_overwrites_input(self, unpack_setup, tmp_path):
        uc = unpack_setup
        input_file = tmp_path / "response.md"
        input_file.write_text("[PERSON_001] reporting.", encoding="utf-8")

        result = uc.execute(
            output_dir=tmp_path,
            input_file=input_file,
            in_place=True,
        )

        content = input_file.read_text(encoding="utf-8")
        assert "Thomas WEGMÜLLER" in content
        assert result.files_written == 1
        assert str(input_file) in result.output_files

    def test_in_place_writes_to_input_file_not_output_dir(self, unpack_setup, tmp_path):
        uc = unpack_setup
        input_file = tmp_path / "source.md"
        input_file.write_text("[ORT_001] is the location.", encoding="utf-8")
        output_dir = tmp_path / "other"

        result = uc.execute(
            output_dir=output_dir,
            input_file=input_file,
            in_place=True,
        )

        # output_dir should NOT be created (in-place writes to input)
        assert not output_dir.exists()
        assert "Zürich" in input_file.read_text(encoding="utf-8")


class TestUnpackSplitSections:

    def test_split_on_separator(self, unpack_setup, tmp_path):
        uc = unpack_setup
        text = (
            "# section_001.md\n\nFirst section about [PERSON_001].\n"
            "\n---\n"
            "\n# section_002.md\n\nSecond section in [ORT_001]."
        )
        output_dir = tmp_path / "vault"

        result = uc.execute(
            output_dir=output_dir,
            input_text=text,
            split_sections=True,
        )

        assert result.files_written == 2
        assert (output_dir / "section_001.md").exists()
        assert (output_dir / "section_002.md").exists()
        content_1 = (output_dir / "section_001.md").read_text(encoding="utf-8")
        content_2 = (output_dir / "section_002.md").read_text(encoding="utf-8")
        assert "Thomas WEGMÜLLER" in content_1
        assert "Zürich" in content_2

    def test_split_auto_numbers_without_header(self, unpack_setup, tmp_path):
        uc = unpack_setup
        text = "First part.\n\n---\n\nSecond part."
        output_dir = tmp_path / "vault"

        result = uc.execute(
            output_dir=output_dir,
            input_text=text,
            split_sections=True,
        )

        assert result.files_written == 2
        files = sorted(f.name for f in output_dir.iterdir())
        assert any("section_" in f for f in files)

    def test_split_extracts_filename_from_header(self, unpack_setup, tmp_path):
        uc = unpack_setup
        text = "# Wegmüller_Thomas.md\n\nContent about [PERSON_001]."
        output_dir = tmp_path / "vault"

        result = uc.execute(
            output_dir=output_dir,
            input_text=text,
            split_sections=True,
        )

        assert result.files_written == 1
        assert (output_dir / "Wegmüller_Thomas.md").exists()

    def test_split_skips_empty_sections(self, unpack_setup, tmp_path):
        uc = unpack_setup
        # Two separators in a row → empty section in between
        text = "Part one.\n\n---\n\n\n\n---\n\nPart two."
        output_dir = tmp_path / "vault"

        result = uc.execute(
            output_dir=output_dir,
            input_text=text,
            split_sections=True,
        )

        assert result.files_written == 2


class TestUnpackValidation:

    def test_no_input_raises(self, unpack_setup, tmp_path):
        uc = unpack_setup
        with pytest.raises(ValueError, match="One of"):
            uc.execute(output_dir=tmp_path)

    def test_unresolved_placeholders_in_warnings(self, unpack_setup, tmp_path):
        uc = unpack_setup
        result = uc.execute(
            output_dir=tmp_path,
            input_text="[PERSON_999] is unknown.",
        )
        assert len(result.warnings) == 1
        assert "PERSON_999" in result.warnings[0]

    def test_unresolved_does_not_count_as_resolved(self, unpack_setup, tmp_path):
        uc = unpack_setup
        result = uc.execute(
            output_dir=tmp_path,
            input_text="[PERSON_001] and [PERSON_999].",
        )
        # PERSON_001 resolved, PERSON_999 not
        assert result.placeholders_resolved == 1
        assert len(result.warnings) == 1
