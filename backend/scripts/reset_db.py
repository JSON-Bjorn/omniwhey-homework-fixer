import asyncio
import logging
import sys
import os

# Add the parent directory to Python path
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

from sqlalchemy.schema import DropTable
from sqlalchemy.ext.compiler import compiles

from app.db.session import engine
from app.db.init_db import init_db
from app.db.base import Base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@compiles(DropTable, "postgresql")
def _compile_drop_table(element, compiler, **kwargs):
    return compiler.visit_drop_table(element) + " CASCADE"


async def reset_db() -> None:
    """Drop all tables and recreate them."""
    async with engine.begin() as conn:
        logger.info("Dropping all tables...")
        await conn.run_sync(Base.metadata.drop_all)

        logger.info("Creating all tables...")
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Initializing database with default data...")
    await init_db()

    logger.info("Database reset complete!")


if __name__ == "__main__":
    asyncio.run(reset_db())
