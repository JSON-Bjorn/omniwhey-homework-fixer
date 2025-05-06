from typing import List, Optional, TYPE_CHECKING
from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.user import User


class Assignment(Base):
    """Assignment model for teacher-created assignments."""

    __tablename__ = "assignments"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    assignment_instructions: Mapped[str] = mapped_column(Text, nullable=False)
    max_score: Mapped[int] = mapped_column(Integer, nullable=False)
    correction_template: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )
    deadline: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    # Foreign keys
    teacher_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # Relationships
    teacher: Mapped["User"] = relationship(
        back_populates="created_assignments", foreign_keys=[teacher_id]
    )
    student_submissions: Mapped[List["StudentAssignment"]] = relationship(
        back_populates="assignment", cascade="all, delete-orphan"
    )

    @property
    def is_past_deadline(self) -> bool:
        """Check if the assignment is past its deadline."""
        return (
            datetime.now().replace(tzinfo=self.deadline.tzinfo)
            > self.deadline
        )


class StudentAssignment(Base):
    """Student assignment submission model."""

    __tablename__ = "student_assignments"

    submission_text: Mapped[str] = mapped_column(Text, nullable=False)
    score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    teacher_feedback: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )

    # Foreign keys
    student_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    assignment_id: Mapped[int] = mapped_column(
        ForeignKey("assignments.id", ondelete="CASCADE"), nullable=False
    )

    # Relationships
    student: Mapped["User"] = relationship(
        back_populates="student_assignments", foreign_keys=[student_id]
    )
    assignment: Mapped["Assignment"] = relationship(
        back_populates="student_submissions", foreign_keys=[assignment_id]
    )
