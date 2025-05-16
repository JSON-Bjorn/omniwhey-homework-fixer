import asyncio
import logging
import time
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db, engine
from app.crud.token import clean_expired_tokens
from app.core.config import settings

logger = logging.getLogger(__name__)


async def run_token_cleanup(interval_hours: int = None):
    """
    Run token cleanup routine at specified interval.

    Args:
        interval_hours: Hours between cleanup runs (defaults to settings.DB_MAINTENANCE_INTERVAL)
    """
    if interval_hours is None:
        interval_hours = settings.DB_MAINTENANCE_INTERVAL

    logger.info(
        f"Token cleanup service starting with {interval_hours}h interval"
    )

    while True:
        try:
            # Create a database session
            async with engine.begin() as conn:
                db = AsyncSession(bind=conn)

                start_time = time.time()
                logger.info("Starting expired token cleanup task")

                # Run the cleanup operation
                tokens_removed = await clean_expired_tokens(db)

                # Log results
                elapsed_time = time.time() - start_time
                logger.info(
                    f"Token cleanup completed in {elapsed_time:.2f}s - Removed {tokens_removed} expired tokens"
                )

        except Exception as e:
            logger.error(
                f"Error during token cleanup: {str(e)}", exc_info=True
            )

        # Sleep until next run
        next_run = datetime.utcnow() + timedelta(hours=interval_hours)
        logger.info(f"Next token cleanup scheduled for: {next_run}")
        await asyncio.sleep(interval_hours * 3600)


async def run_maintenance_tasks():
    """
    Run all maintenance tasks in separate tasks.
    This function can be called during application startup.
    """
    if not settings.ENABLE_DB_MAINTENANCE:
        logger.info("Database maintenance tasks disabled in settings")
        return

    logger.info("Starting database maintenance tasks")

    # Start token cleanup as a background task
    asyncio.create_task(run_token_cleanup())

    # Additional maintenance tasks can be added here in the future

    logger.info("Database maintenance tasks initialized")
