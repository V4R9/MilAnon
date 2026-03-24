"""Tests for GenerateContextUseCase — LLM context file generation."""

from __future__ import annotations

from pathlib import Path

import pytest

from milanon.adapters.repositories.sqlite_repository import SqliteMappingRepository
from milanon.domain.entities import EntityType
from milanon.domain.mapping_service import MappingService
from milanon.usecases.generate_context import GenerateContextUseCase, _parse_level


@pytest.fixture
def repo() -> SqliteMappingRepository:
    return SqliteMappingRepository(":memory:")


@pytest.fixture
def service(repo) -> MappingService:
    return MappingService(repo)


@pytest.fixture
def use_case(repo) -> GenerateContextUseCase:
    return GenerateContextUseCase(repo)


def _add_unit(service: MappingService, name: str) -> str:
    """Add a unit to the DB and return its placeholder."""
    return service.get_or_create_placeholder(EntityType.EINHEIT, name, "test")


def _standard_units(service: MappingService) -> dict[str, str]:
    """Populate a realistic unit hierarchy. Returns {name: placeholder}."""
    return {
        name: _add_unit(service, name)
        for name in [
            "Inf Bat 56",
            "Stabskp 56",
            "Inf Kp 56/1",
            "Inf Kp 56/2",
            "Inf Kp 56/3",
        ]
    }


# ---------------------------------------------------------------------------
# Level parsing
# ---------------------------------------------------------------------------

class TestParseLevelUnit:
    def test_parses_kp_level(self):
        assert _parse_level("Inf Kp 56/1") == "Company"

    def test_parses_bat_level(self):
        assert _parse_level("Inf Bat 56") == "Battalion"

    def test_parses_div_level(self):
        assert _parse_level("Ter Div 2") == "Division"

    def test_parses_stabskp_level(self):
        # "Stabskp" contains "kp" — must be caught by "stabskp" rule first
        assert _parse_level("Stabskp 56") == "Staff Company"

    def test_parses_br_level(self):
        assert _parse_level("Inf Br 5") == "Brigade"

    def test_unknown_falls_back_to_other(self):
        assert _parse_level("Logistik Zentrum") == "Other"


# ---------------------------------------------------------------------------
# get_available_units
# ---------------------------------------------------------------------------

class TestGetAvailableUnits:
    def test_returns_all_einheit_mappings(self, use_case, service):
        _standard_units(service)
        units = use_case.get_available_units()
        assert len(units) == 5

    def test_returns_sorted_list_by_level(self, use_case, service):
        _standard_units(service)
        units = use_case.get_available_units()
        levels = [u.level for u in units]
        # Battalion must come before Companies
        bat_idx = levels.index("Battalion")
        kp_indices = [i for i, l in enumerate(levels) if l == "Company"]
        assert bat_idx < min(kp_indices)

    def test_returns_empty_list_when_no_units(self, use_case):
        assert use_case.get_available_units() == []

    def test_entries_have_placeholder(self, use_case, service):
        placeholders = _standard_units(service)
        units = use_case.get_available_units()
        returned_placeholders = {u.placeholder for u in units}
        assert set(placeholders.values()) == returned_placeholders

    def test_does_not_include_non_einheit_entities(self, use_case, service):
        service.get_or_create_placeholder(EntityType.PERSON, "Thomas Wegmüller", "test")
        _add_unit(service, "Inf Bat 56")
        units = use_case.get_available_units()
        assert len(units) == 1


# ---------------------------------------------------------------------------
# generate — basic output
# ---------------------------------------------------------------------------

class TestGenerateContextBasic:
    def test_generate_creates_output_file(self, use_case, service, tmp_path):
        _standard_units(service)
        out = tmp_path / "CONTEXT.md"
        use_case.generate("Inf Kp 56/1", out)
        assert out.exists()

    def test_generate_finds_user_unit_placeholder(self, use_case, service, tmp_path):
        placeholders = _standard_units(service)
        out = tmp_path / "CONTEXT.md"
        use_case.generate("Inf Kp 56/1", out)
        content = out.read_text(encoding="utf-8")
        assert placeholders["Inf Kp 56/1"] in content

    def test_generate_marks_user_unit_in_output(self, use_case, service, tmp_path):
        _standard_units(service)
        out = tmp_path / "CONTEXT.md"
        use_case.generate("Inf Kp 56/1", out)
        content = out.read_text(encoding="utf-8")
        assert "← YOUR UNIT" in content

    def test_generate_contains_filtering_instructions(self, use_case, service, tmp_path):
        _standard_units(service)
        out = tmp_path / "CONTEXT.md"
        use_case.generate("Inf Kp 56/1", out)
        content = out.read_text(encoding="utf-8")
        assert "Filtering Instructions" in content
        assert "relevant to my unit only" in content

    def test_generate_contains_rules_section(self, use_case, service, tmp_path):
        _standard_units(service)
        out = tmp_path / "CONTEXT.md"
        use_case.generate("Inf Kp 56/1", out)
        content = out.read_text(encoding="utf-8")
        assert "Preserve all [PLACEHOLDER]" in content

    def test_generate_creates_parent_dir_if_missing(self, use_case, service, tmp_path):
        _standard_units(service)
        out = tmp_path / "nested" / "deep" / "CONTEXT.md"
        use_case.generate("Inf Kp 56/1", out)
        assert out.exists()


# ---------------------------------------------------------------------------
# generate — parent unit detection
# ---------------------------------------------------------------------------

class TestGenerateParentDetection:
    def test_generate_finds_parent_unit(self, use_case, service, tmp_path):
        placeholders = _standard_units(service)
        out = tmp_path / "CONTEXT.md"
        use_case.generate("Inf Kp 56/1", out)
        content = out.read_text(encoding="utf-8")
        # Battalion placeholder must appear as parent
        assert placeholders["Inf Bat 56"] in content
        assert "Parent unit" in content

    def test_generate_no_parent_when_no_slash_in_unit(self, use_case, service, tmp_path):
        # Battalion has no "/" → no parent detection
        _standard_units(service)
        out = tmp_path / "CONTEXT.md"
        use_case.generate("Inf Bat 56", out)
        content = out.read_text(encoding="utf-8")
        assert "Parent unit" not in content


# ---------------------------------------------------------------------------
# generate — security: no original values in output
# ---------------------------------------------------------------------------

class TestGenerateNoOriginalValues:
    def test_generate_output_contains_no_original_values(self, use_case, service, tmp_path):
        """CRITICAL: CONTEXT.md must not reveal any original unit names."""
        _standard_units(service)
        out = tmp_path / "CONTEXT.md"
        use_case.generate("Inf Kp 56/1", out)
        content = out.read_text(encoding="utf-8")
        original_names = ["Inf Bat 56", "Stabskp 56", "Inf Kp 56/1", "Inf Kp 56/2", "Inf Kp 56/3"]
        for name in original_names:
            assert name not in content, f"Original value '{name}' leaked into CONTEXT.md"


# ---------------------------------------------------------------------------
# generate — error handling
# ---------------------------------------------------------------------------

class TestGenerateErrors:
    def test_generate_unknown_unit_raises_value_error(self, use_case, service, tmp_path):
        _add_unit(service, "Inf Bat 56")
        with pytest.raises(ValueError, match="not found in database"):
            use_case.generate("Phantom Kp 99/9", tmp_path / "CONTEXT.md")

    def test_generate_single_unit_still_works(self, use_case, service, tmp_path):
        _add_unit(service, "Inf Bat 56")
        out = tmp_path / "CONTEXT.md"
        use_case.generate("Inf Bat 56", out)
        assert out.exists()
        content = out.read_text(encoding="utf-8")
        assert "← YOUR UNIT" in content
