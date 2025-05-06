import logging
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base_class import Base
from app.db.session import engine

logger = logging.getLogger(__name__)


async def create_tables() -> None:
    """Create database tables if they don't exist."""
    try:
        async with engine.begin() as conn:
            # This creates tables that don't exist, but doesn't modify existing ones
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise
