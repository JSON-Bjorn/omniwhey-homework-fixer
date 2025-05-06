from typing import List, Optional, TYPE_CHECKING
import enum
import datetime
from sqlalchemy import (
    String,
    Boolean,
    Integer,
    ForeignKey,
    Enum,
    Table,
    Column,
    DateTime,
    func,
)
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
    DeclarativeBase,
)

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.assignment import Assignment, StudentAssignment


class UserRole(enum.Enum):
    """User role enum."""

    STUDENT = "student"
    TEACHER = "teacher"


# Define association table using SQLAlchemy's Table construct
teacher_student_association = Table(
    "teacher_student_associations",
    Base.metadata,
    Column(
        "teacher_id",
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "student_id",
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "created_at",
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    ),
    Column(
        "updated_at",
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    ),
)


class User(Base):
    """Base User model for both teachers and students."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False)

    # Common fields for all users

    # Student-specific fields
    total_gold_coins: Mapped[Optional[int]] = mapped_column(
        Integer, default=0, nullable=True
    )

    # Relationships
    student_assignments: Mapped[List["StudentAssignment"]] = relationship(
        back_populates="student",
        foreign_keys="[StudentAssignment.student_id]",
        cascade="all, delete-orphan",
    )

    # Teacher-specific relationships
    created_assignments: Mapped[List["Assignment"]] = relationship(
        back_populates="teacher",
        foreign_keys="[Assignment.teacher_id]",
        cascade="all, delete-orphan",
    )

    # Teacher-student relationship (many-to-many)
    # For teachers: students in their classes
    students: Mapped[List["User"]] = relationship(
        "User",
        secondary="teacher_student_associations",
        primaryjoin="User.id==teacher_student_associations.c.teacher_id",
        secondaryjoin="User.id==teacher_student_associations.c.student_id",
        backref="teachers",  # For students: teachers they have
        uselist=True,
    )

    def is_teacher(self) -> bool:
        """Check if user is a teacher."""
        return self.role == UserRole.TEACHER

    def is_student(self) -> bool:
        """Check if user is a student."""
        return self.role == UserRole.STUDENT
