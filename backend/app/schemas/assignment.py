from typing import List, Optional
from datetime import datetime
import uuid
from pydantic import BaseModel, Field, ConfigDict


class AssignmentBase(BaseModel):
    """Base assignment schema."""

    title: str
    assignment_instructions: str
    max_score: int = Field(gt=0)
    deadline: datetime


class AssignmentCreate(AssignmentBase):
    """Schema for creating a new assignment."""

    pass


class AssignmentUpdate(BaseModel):
    """Schema for updating an assignment."""

    title: Optional[str] = None
    assignment_instructions: Optional[str] = None
    max_score: Optional[int] = Field(default=None, gt=0)
    deadline: Optional[datetime] = None
    correction_template: Optional[str] = None


class AssignmentInDBBase(AssignmentBase):
    """Base assignment DB schema."""

    id: int
    teacher_id: uuid.UUID
    correction_template: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Assignment(AssignmentInDBBase):
    """Schema for a complete assignment."""

    pass


class TemplateGenerationResponse(BaseModel):
    """Schema for template generation response."""

    assignment_id: int
    title: str
    generated_template: str
    can_be_modified: bool = True


class TemplateApprovalRequest(BaseModel):
    """Schema for template approval request."""

    assignment_id: int
    correction_template: str


class StudentAssignmentBase(BaseModel):
    """Base student assignment schema."""

    submission_text: str


class StudentAssignmentCreate(StudentAssignmentBase):
    """Schema for creating a student assignment submission."""

    assignment_id: int


class StudentAssignmentTeacherUpdate(BaseModel):
    """Schema for teacher updating a student assignment."""

    teacher_feedback: Optional[str] = None
    score: Optional[int] = Field(default=None, ge=0)


class StudentAssignmentInDBBase(StudentAssignmentBase):
    """Base student assignment DB schema."""

    id: int
    student_id: uuid.UUID
    assignment_id: int
    score: Optional[int] = None
    teacher_feedback: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StudentAssignment(StudentAssignmentInDBBase):
    """Schema for student assignment response."""

    pass


class StudentAssignmentWithDetails(StudentAssignment):
    """Schema for student assignment with details."""

    assignment: Assignment

    model_config = ConfigDict(from_attributes=True)


class StudentAssignmentWithGrading(StudentAssignment):
    """Schema for student assignment with grading details."""

    # Include all fields from StudentAssignment via inheritance
    # Add additional fields specific to grading
    student_name: Optional[str] = None
    student_email: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class AssignmentDeadlineExtend(BaseModel):
    """Schema for extending an assignment deadline."""

    deadline: datetime

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "deadline": "2023-12-31T23:59:59Z",
            }
        }
    )
