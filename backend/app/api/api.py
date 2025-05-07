from fastapi import APIRouter

from app.api.routers import auth, students, teachers
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

# Export router
__all__ = ["api_router"]
