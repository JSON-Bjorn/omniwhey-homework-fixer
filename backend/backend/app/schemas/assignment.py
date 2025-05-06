from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class AssignmentBase(BaseModel):
    """Base assignment schema."""

    title: str
    assignment_instructions: str
    max_score: int = Field(gt=0)
    deadline: datetime


class AssignmentCreate(AssignmentBase):
    """Schema for creating an assignment."""

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
    teacher_id: int
    correction_template: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Assignment(AssignmentInDBBase):
    """Schema for assignment response."""

    pass


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
    student_id: int
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
