from typing import AsyncGenerator
import logging
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)

from app.core.config import settings

# Set up logger
logger = logging.getLogger(__name__)

# Create async engine with connection pooling
engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    echo=settings.DB_ECHO,
    pool_pre_ping=settings.DB_PRE_PING,  # Check connection health before usage
    pool_size=settings.DB_POOL_SIZE,  # Pool size from settings
    max_overflow=settings.DB_MAX_OVERFLOW,  # Allow additional connections from settings
    pool_timeout=settings.DB_POOL_TIMEOUT,  # Wait timeout from settings
    pool_recycle=settings.DB_POOL_RECYCLE,  # Recycle connections after time from settings
    # Additional settings for production workloads
    connect_args={
        "server_settings": {"application_name": "omniwhey_app"}
    },  # Identify connections in DB logs
)

# Create session factory
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def create_tables() -> None:
    """Create database tables if they don't exist."""
    from app.db.base_class import Base

    try:
        async with engine.begin() as conn:
            # This creates tables that don't exist, but doesn't modify existing ones
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database session.

    This function creates a new database session for each request and
    closes it when the request is finished.
    """
    async with async_session_factory() as session:
        try:
            # Log connection acquisition
            logger.debug("Database connection acquired")
            yield session
            await session.commit()
            logger.debug("Database session committed")
        except Exception as e:
            # Log rollback with exception info
            logger.error(
                f"Rolling back database session due to error: {str(e)}"
            )
            await session.rollback()
            raise
        finally:
            # Ensure session is properly closed
            logger.debug("Database connection closed")
            await session.close()


# Placeholder for init_limiter to be imported from app.utils.rate_limit
from app.utils.rate_limit import init_limiter
