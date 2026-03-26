"""Tests for EINHEIT alias resolution."""


from milanon.adapters.repositories.sqlite_repository import SqliteMappingRepository
from milanon.domain.entities import EntityType
from milanon.domain.mapping_service import MappingService


class TestEinheitAliases:
    """B-018: EINHEIT alias resolution."""

    def test_ustue_kp_without_slash4_resolves_to_existing(self):
        """'Inf Ustü Kp 56' should resolve to same placeholder as 'Inf Ustü Kp 56/4'."""
        repo = SqliteMappingRepository(":memory:")
        service = MappingService(repo)

        # Create the /4 version first
        ph1 = service.get_or_create_placeholder(EntityType.EINHEIT, "Inf Ustü Kp 56/4")

        # Now the short version should resolve to the same placeholder
        ph2 = service.get_or_create_placeholder_with_alias(EntityType.EINHEIT, "Inf Ustü Kp 56")

        assert ph1 == ph2

    def test_kp_0_resolves_to_stabskp(self):
        """'Inf Kp 56/0' should resolve to same placeholder as 'Inf Stabskp 56'."""
        repo = SqliteMappingRepository(":memory:")
        service = MappingService(repo)

        # Create Stabskp first
        ph1 = service.get_or_create_placeholder(EntityType.EINHEIT, "Inf Stabskp 56")

        # Kp 56/0 should resolve to same
        ph2 = service.get_or_create_placeholder_with_alias(EntityType.EINHEIT, "Inf Kp 56/0")

        assert ph1 == ph2

    def test_normal_kp_creates_separate_placeholder(self):
        """'Inf Kp 56/1' and 'Inf Kp 56/2' should remain separate."""
        repo = SqliteMappingRepository(":memory:")
        service = MappingService(repo)

        ph1 = service.get_or_create_placeholder_with_alias(EntityType.EINHEIT, "Inf Kp 56/1")
        ph2 = service.get_or_create_placeholder_with_alias(EntityType.EINHEIT, "Inf Kp 56/2")

        assert ph1 != ph2

    def test_non_einheit_type_unaffected(self):
        """Alias resolution only applies to EINHEIT entities."""
        repo = SqliteMappingRepository(":memory:")
        service = MappingService(repo)

        ph1 = service.get_or_create_placeholder_with_alias(EntityType.PERSON, "Thomas WEGMÜLLER")
        ph2 = service.get_or_create_placeholder_with_alias(EntityType.PERSON, "Thomas WEGMÜLLER")

        assert ph1 == ph2  # same person, same placeholder (existing behavior)

    def test_ustue_with_slash4_is_canonical(self):
        """'Inf Ustü Kp 56/4' is already canonical — no double-creation."""
        repo = SqliteMappingRepository(":memory:")
        service = MappingService(repo)

        ph1 = service.get_or_create_placeholder_with_alias(EntityType.EINHEIT, "Inf Ustü Kp 56/4")
        ph2 = service.get_or_create_placeholder_with_alias(EntityType.EINHEIT, "Inf Ustü Kp 56/4")

        assert ph1 == ph2
        # Only one mapping in DB
        all_mappings = repo.get_all_mappings()
        einheiten = [m for m in all_mappings if m.entity_type == EntityType.EINHEIT]
        assert len(einheiten) == 1

    def test_alias_when_no_canonical_exists_creates_new(self):
        """If 'Inf Ustü Kp 56' is used first (before /4 version), create a new mapping."""
        repo = SqliteMappingRepository(":memory:")
        service = MappingService(repo)

        # Short version first — no /4 version exists yet
        ph1 = service.get_or_create_placeholder_with_alias(EntityType.EINHEIT, "Inf Ustü Kp 56")

        # Should have created a mapping (since /4 doesn't exist)
        assert ph1 is not None
        assert "[EINHEIT_" in ph1
