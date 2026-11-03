"""Application startup and shutdown."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
)

from app.database import Base


def create_lifespan(
    engine: AsyncEngine,
    session_factory: async_sessionmaker[AsyncSession],
):
    """Create a lifespan handler for the configured database."""

    @asynccontextmanager
    async def lifespan(application: FastAPI):
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

        application.state.session_factory = session_factory
        try:
            yield
        finally:
            await engine.dispose()

    return lifespan
