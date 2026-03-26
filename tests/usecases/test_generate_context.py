"""Tests for GenerateContextUseCase — LLM context file generation."""

from __future__ import annotations

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
        kp_indices = [i for i, lvl in enumerate(levels) if lvl == "Company"]
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

    def test_battalion_filtering_uses_parent_not_random_battalion(
        self, use_case, service, tmp_path
    ):
        # When multiple battalions exist, "Battalion level only" must use the
        # identified parent — not just the first Battalion in the list.
        placeholders = _standard_units(service)
        # Add a second, unrelated battalion
        other_bat = service.get_or_create_placeholder(EntityType.EINHEIT, "Inf Bat 20", "test")
        out = tmp_path / "CONTEXT.md"
        use_case.generate("Inf Kp 56/1", out)
        content = out.read_text(encoding="utf-8")
        bat_line = next(
            line for line in content.splitlines() if "Battalion level only" in line
        )
        # Must point to parent (Bat 56), not the unrelated Bat 20
        assert placeholders["Inf Bat 56"] in bat_line
        assert other_bat not in bat_line

    def test_battalion_filtering_falls_back_to_user_when_no_parent(
        self, use_case, service, tmp_path
    ):
        # When user IS the battalion (no slash), "Battalion level only" → user's own placeholder
        placeholders = _standard_units(service)
        out = tmp_path / "CONTEXT.md"
        use_case.generate("Inf Bat 56", out)
        content = out.read_text(encoding="utf-8")
        bat_line = next(
            line for line in content.splitlines() if "Battalion level only" in line
        )
        assert placeholders["Inf Bat 56"] in bat_line


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


# ---------------------------------------------------------------------------
# generate — DB hierarchy
# ---------------------------------------------------------------------------

def _insert_concrete_unit(
    repo: SqliteMappingRepository,
    full_name: str,
    abbreviation: str,
    parent: str,
    unit_type: str = "concrete_unit",
) -> None:
    """Insert a concrete_unit row directly into ref_military_units."""
    repo._conn.execute(
        """INSERT INTO ref_military_units
           (pattern, unit_type, parent_unit, full_name, abbreviation, level, category)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (abbreviation, unit_type, parent, full_name, abbreviation, "", ""),
    )
    repo._conn.commit()


def _build_ter_div2_hierarchy(repo: SqliteMappingRepository) -> None:
    """Insert Kdo Op → Ter Div 2 → Inf Bat 56 → companies into ref_military_units."""
    _insert_concrete_unit(repo, "Kommando Operationen", "Kdo Op", "_root")
    _insert_concrete_unit(repo, "Territorialdivision 2", "Ter Div 2", "Kommando Operationen")
    _insert_concrete_unit(repo, "Infanteriebataillon 56", "Inf Bat 56", "Territorialdivision 2")
    _insert_concrete_unit(repo, "Infanteriebataillon 11", "Inf Bat 11", "Territorialdivision 2")
    _insert_concrete_unit(repo, "Infanteriebataillon 20", "Inf Bat 20", "Territorialdivision 2")
    _insert_concrete_unit(repo, "Infanteriekompanie 56/1", "Inf Kp 56/1", "Infanteriebataillon 56")
    _insert_concrete_unit(repo, "Infanteriekompanie 56/2", "Inf Kp 56/2", "Infanteriebataillon 56")
    _insert_concrete_unit(repo, "Infanteriekompanie 56/3", "Inf Kp 56/3", "Infanteriebataillon 56")
    _insert_concrete_unit(
        repo, "Infanterie Stabskompanie 56", "Inf Stabskp 56", "Infanteriebataillon 56"
    )


class TestHierarchyFromDB:
    def test_hierarchy_from_db_shows_parent_chain(self, repo, service, tmp_path):
        """Given hierarchy data in DB, context shows full command chain."""
        _add_unit(service, "Inf Kp 56/1")
        _build_ter_div2_hierarchy(repo)
        use_case = GenerateContextUseCase(repo)
        out = tmp_path / "CONTEXT.md"
        use_case.generate("Inf Kp 56/1", out)
        content = out.read_text(encoding="utf-8")
        assert "Kdo Op → Ter Div 2 → Inf Bat 56 → Inf Kp 56/1" in content

    def test_hierarchy_fallback_without_concrete_units(self, repo, service, tmp_path):
        """Given no concrete_unit data, context falls back to slash heuristic."""
        _standard_units(service)
        use_case = GenerateContextUseCase(repo)
        out = tmp_path / "CONTEXT.md"
        use_case.generate("Inf Kp 56/1", out)
        content = out.read_text(encoding="utf-8")
        # Slash-heuristic parent detection still works
        assert "Parent unit" in content
        # No command chain section (no DB data)
        assert "Command Chain" not in content

    def test_siblings_shown_for_company(self, repo, service, tmp_path):
        """Given Inf Kp 56/1, context shows sibling companies of Inf Bat 56."""
        _add_unit(service, "Inf Kp 56/1")
        _build_ter_div2_hierarchy(repo)
        use_case = GenerateContextUseCase(repo)
        out = tmp_path / "CONTEXT.md"
        use_case.generate("Inf Kp 56/1", out)
        content = out.read_text(encoding="utf-8")
        assert "Inf Kp 56/2" in content
        assert "Inf Kp 56/3" in content

    def test_sister_battalions_shown(self, repo, service, tmp_path):
        """Given Inf Bat 56, context shows sister battalions under Ter Div 2."""
        _add_unit(service, "Inf Bat 56")
        _build_ter_div2_hierarchy(repo)
        use_case = GenerateContextUseCase(repo)
        out = tmp_path / "CONTEXT.md"
        use_case.generate("Inf Bat 56", out)
        content = out.read_text(encoding="utf-8")
        assert "Inf Bat 11" in content
        assert "Inf Bat 20" in content
