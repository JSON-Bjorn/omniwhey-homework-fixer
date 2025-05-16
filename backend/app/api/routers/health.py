"""
Health check endpoints for the application.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import DbSession
from app.utils.db_utils import (
    check_database_connection,
    get_connection_pool_stats,
)

router = APIRouter()


@router.get("/")
async def health_check():
    """
    Simple health check endpoint.

    Returns:
        Health status message
    """
    return {"status": "ok", "message": "Service is healthy"}


@router.get("/db")
async def database_health(db: DbSession):
    """
    Check database connection health.

    Args:
        db: Database session

    Returns:
        Database health status

    Raises:
        HTTPException: If the database connection fails
    """
    is_healthy = await check_database_connection(db)

    if not is_healthy:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failed",
        )

    return {"status": "ok", "message": "Database connection is healthy"}


@router.get("/db/stats")
async def database_stats(db: DbSession):
    """
    Get database connection pool statistics.

    Args:
        db: Database session

    Returns:
        Connection pool statistics
    """
    stats = await get_connection_pool_stats(db)
    return {"status": "ok", "pool_stats": stats}
