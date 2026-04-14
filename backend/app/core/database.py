"""Database connection for Epic 4 brand transparency feature.

Creates an async SQLAlchemy engine and session factory used by
brand_service to query companies and brands tables.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

engine = create_async_engine(
    settings.database_url,
    # Recycle stale connections before using them (important for Railway's PostgreSQL)
    pool_pre_ping=True,
    echo=False,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that provides a database session per request.

    Yields an AsyncSession and ensures it is closed after the request
    completes, even if an exception occurs.
    """
    async with AsyncSessionLocal() as session:
        yield session
