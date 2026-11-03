"""Database operations for advertisements."""

from datetime import datetime
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Advertisement
from app.schemas import AdvertisementCreate, AdvertisementUpdate


async def get_advertisement(
    session: AsyncSession,
    advertisement_id: int,
) -> Advertisement:
    """Return an advertisement or raise an HTTP 404 error."""
    advertisement = await session.get(Advertisement, advertisement_id)
    if advertisement is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="advertisement not found",
        )
    return advertisement


async def create_advertisement(
    session: AsyncSession,
    payload: AdvertisementCreate,
) -> Advertisement:
    """Create and return an advertisement."""
    advertisement = Advertisement(**payload.model_dump())
    session.add(advertisement)
    await _commit(session)
    await session.refresh(advertisement)
    return advertisement


async def search_advertisements(
    session: AsyncSession,
    *,
    title: str | None = None,
    description: str | None = None,
    price: Decimal | None = None,
    author: str | None = None,
    created_at: datetime | None = None,
) -> list[Advertisement]:
    """Return advertisements matching all provided filters."""
    query = select(Advertisement).order_by(Advertisement.id)

    if title is not None:
        query = query.where(Advertisement.title.ilike(f"%{title}%"))
    if description is not None:
        query = query.where(
            Advertisement.description.ilike(f"%{description}%")
        )
    if price is not None:
        query = query.where(Advertisement.price == price)
    if author is not None:
        query = query.where(Advertisement.author.ilike(f"%{author}%"))
    if created_at is not None:
        query = query.where(Advertisement.created_at == created_at)

    result = await session.scalars(query)
    return list(result.all())


async def update_advertisement(
    session: AsyncSession,
    advertisement_id: int,
    payload: AdvertisementUpdate,
) -> Advertisement:
    """Update and return an advertisement."""
    advertisement = await get_advertisement(session, advertisement_id)
    for field_name, value in payload.model_dump(exclude_unset=True).items():
        setattr(advertisement, field_name, value)

    await _commit(session)
    await session.refresh(advertisement)
    return advertisement


async def delete_advertisement(
    session: AsyncSession,
    advertisement_id: int,
) -> None:
    """Delete an advertisement."""
    advertisement = await get_advertisement(session, advertisement_id)
    await session.delete(advertisement)
    await _commit(session)


async def _commit(session: AsyncSession) -> None:
    """Commit a transaction and convert database errors to HTTP 500."""
    try:
        await session.commit()
    except SQLAlchemyError as error:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="database error",
        ) from error
