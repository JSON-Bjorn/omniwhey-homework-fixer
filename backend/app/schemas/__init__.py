from app.schemas.user import (
    User,
    UserCreate,
    UserUpdate,
    UserInDB,
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
    TemplateGenerationResponse,
    TemplateApprovalRequest,
)
from app.schemas.token import (
    Token,
    TokenCreate,
    TokenInDB,
    TokenResponse,
)
from app.schemas.feature import (
    Feature,
    FeatureCreate,
    FeatureUpdate,
)

# Re-export for easier importing
__all__ = [
    "User",
    "UserCreate",
    "UserUpdate",
    "UserInDB",
    "TeacherStudentAdd",
    "EmailVerification",
    "Assignment",
    "AssignmentCreate",
    "AssignmentUpdate",
    "StudentAssignment",
    "StudentAssignmentCreate",
    "StudentAssignmentTeacherUpdate",
    "StudentAssignmentWithDetails",
    "Token",
    "TokenCreate",
    "TokenInDB",
    "TokenResponse",
    "TemplateGenerationResponse",
    "TemplateApprovalRequest",
    "Feature",
    "FeatureCreate",
    "FeatureUpdate",
]
