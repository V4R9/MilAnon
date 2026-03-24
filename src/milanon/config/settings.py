"""Application settings — paths, defaults, constants."""

from __future__ import annotations

import os
from pathlib import Path

# Database location: configurable via MILANON_DB_PATH env var
DEFAULT_DB_DIR = Path.home() / ".milanon"
DEFAULT_DB_PATH = DEFAULT_DB_DIR / "milanon.db"


def get_db_path() -> Path:
    """Return the database path, respecting MILANON_DB_PATH env var."""
    env_path = os.environ.get("MILANON_DB_PATH")
    if env_path:
        return Path(env_path)
    return DEFAULT_DB_PATH


def ensure_db_dir(db_path: Path | None = None) -> Path:
    """Ensure the database directory exists and return the db path."""
    path = db_path or get_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


# Schema version for future migrations
SCHEMA_VERSION = 1
