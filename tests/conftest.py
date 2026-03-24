"""Shared test fixtures for MilAnon test suite."""

from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "e2e" / "fixtures"


@pytest.fixture
def fixtures_dir() -> Path:
    """Path to the test fixtures directory."""
    return FIXTURES_DIR


@pytest.fixture
def tmp_output(tmp_path: Path) -> Path:
    """Temporary output directory for test runs."""
    output = tmp_path / "output"
    output.mkdir()
    return output
