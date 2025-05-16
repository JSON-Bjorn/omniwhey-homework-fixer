from typing import List, Optional
import uuid
from pydantic import BaseModel, EmailStr, Field, ConfigDict

from app.models.user import UserRole


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    name: str
    role: UserRole


class UserCreate(UserBase):
    """Schema for creating a user."""

    password: str = Field(min_length=8)


class UserUpdate(BaseModel):
    """Schema for updating a user."""

    email: Optional[EmailStr] = None
    name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None


class UserInDBBase(UserBase):
    """Base user DB schema."""

    id: uuid.UUID
    is_active: bool
    is_verified: bool
    total_gold_coins: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)


class User(UserInDBBase):
    """Schema for user response."""

    pass


class UserInDB(UserInDBBase):
    """Schema for user in DB."""

    hashed_password: str


class TeacherStudentAdd(BaseModel):
    """Schema for adding students to teacher's class."""

    student_ids: List[uuid.UUID]


class EmailVerification(BaseModel):
    """Schema for email verification."""

    token: str
