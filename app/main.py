"""FastAPI routes for the advertisement service."""

from datetime import datetime
from decimal import Decimal

from fastapi import FastAPI, Query, Response, status

from app import services
from app.config import get_database_url
from app.database import create_database
from app.dependencies import SessionDep
from app.lifespan import create_lifespan
from app.schemas import (
    AdvertisementCreate,
    AdvertisementResponse,
    AdvertisementUpdate,
)


def create_app(database_url: str | None = None) -> FastAPI:
    """Create and configure the FastAPI application."""
    engine, session_factory = create_database(get_database_url(database_url))

    application = FastAPI(
        title="Advertisement API",
        description="REST API for buying and selling advertisements",
        version="1.0.0",
        lifespan=create_lifespan(engine, session_factory),
    )

    @application.get("/", tags=["service"])
    async def index():
        return {
            "service": "advertisement-api",
            "documentation": "/docs",
        }

    @application.post(
        "/advertisement",
        response_model=AdvertisementResponse,
        status_code=status.HTTP_201_CREATED,
        tags=["advertisements"],
    )
    async def create_advertisement(
        payload: AdvertisementCreate,
        session: SessionDep,
    ):
        return await services.create_advertisement(session, payload)

    @application.get(
        "/advertisement/{advertisement_id}",
        response_model=AdvertisementResponse,
        tags=["advertisements"],
    )
    async def get_advertisement(
        advertisement_id: int,
        session: SessionDep,
    ):
        return await services.get_advertisement(
            session,
            advertisement_id,
        )

    @application.get(
        "/advertisement",
        response_model=list[AdvertisementResponse],
        tags=["advertisements"],
    )
    async def search_advertisements(
        session: SessionDep,
        title: str | None = Query(default=None, min_length=1),
        description: str | None = Query(default=None, min_length=1),
        price: Decimal | None = Query(default=None, ge=0),
        author: str | None = Query(default=None, min_length=1),
        created_at: datetime | None = Query(default=None),
    ):
        return await services.search_advertisements(
            session,
            title=title,
            description=description,
            price=price,
            author=author,
            created_at=created_at,
        )

    @application.patch(
        "/advertisement/{advertisement_id}",
        response_model=AdvertisementResponse,
        tags=["advertisements"],
    )
    async def update_advertisement(
        advertisement_id: int,
        payload: AdvertisementUpdate,
        session: SessionDep,
    ):
        return await services.update_advertisement(
            session,
            advertisement_id,
            payload,
        )

    @application.delete(
        "/advertisement/{advertisement_id}",
        status_code=status.HTTP_204_NO_CONTENT,
        response_class=Response,
        tags=["advertisements"],
    )
    async def delete_advertisement(
        advertisement_id: int,
        session: SessionDep,
    ):
        await services.delete_advertisement(session, advertisement_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return application


app = create_app()
