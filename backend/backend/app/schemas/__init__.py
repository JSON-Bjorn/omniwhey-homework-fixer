from app.schemas.user import (
    User,
    UserCreate,
    UserUpdate,
    UserInDB,
    Token,
    TokenPayload,
    TeacherStudentAdd,
    EmailVerification,
)
from app.schemas.assignment import (
    Assignment,
    AssignmentCreate,
    AssignmentUpdate,
    StudentAssignment,
    StudentAssignmentCreate,
    StudentAssignmentTeacherUpdate,
    StudentAssignmentWithDetails,
)

# Re-export for easier importing
__all__ = [
    "User",
    "UserCreate",
    "UserUpdate",
    "UserInDB",
    "Token",
    "TokenPayload",
    "TeacherStudentAdd",
    "EmailVerification",
    "Assignment",
    "AssignmentCreate",
    "AssignmentUpdate",
    "StudentAssignment",
    "StudentAssignmentCreate",
    "StudentAssignmentTeacherUpdate",
    "StudentAssignmentWithDetails",
]
