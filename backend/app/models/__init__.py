from app.models.user import User, UserRole
from app.models.assignment import Assignment, StudentAssignment

# Re-export for easier importing
__all__ = [
    "User",
    "UserRole",
    "Assignment",
    "StudentAssignment",
]
