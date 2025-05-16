from fastapi import APIRouter

from app.api.routers import (
    auth,
    students,
    teachers,
    health,
    features,
)
from app.core.config import settings

api_router = APIRouter()

# Include authentication routes
api_router.include_router(
    auth.router, prefix="/auth", tags=["authentication"]
)

# Include student routes
api_router.include_router(
    students.router, prefix="/students", tags=["students"]
)

# Include teacher routes
api_router.include_router(
    teachers.router, prefix="/teachers", tags=["teachers"]
)

# Include health check routes
api_router.include_router(health.router, prefix="/health", tags=["health"])

# Include feature flag routes
api_router.include_router(
    features.router, prefix="/features", tags=["features"]
)

# Export router
__all__ = ["api_router"]
