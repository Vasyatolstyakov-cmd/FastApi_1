"""Application configuration."""

import os

DEFAULT_DATABASE_URL = "sqlite+aiosqlite:///./advertisements.db"


def get_database_url(database_url: str | None = None) -> str:
    """Return an explicitly provided URL or the configured default."""
    return database_url or os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)
