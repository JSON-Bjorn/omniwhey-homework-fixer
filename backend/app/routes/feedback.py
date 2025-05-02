from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

# These imports will work properly due to sys.path manipulation in run.py
from config.database import get_db
from models import Submission, User, Feedback
from app.auth import get_current_active_user

router = APIRouter(prefix="/api/feedback", tags=["feedback"])


# Pydantic models for request/response
class FeedbackBase(BaseModel):
    content: str
    grade: Optional[str] = None


class FeedbackCreate(FeedbackBase):
    submission_id: int


class FeedbackResponse(FeedbackBase):
    id: int
    submission_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class FeedbackList(BaseModel):
    feedback: List[FeedbackResponse]


# Get feedback for a specific submission
@router.get("/{submission_id}", response_model=FeedbackResponse)
async def get_feedback_for_submission(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # First check if the submission exists
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found"
        )

    # Check if the user has access to this submission's feedback
    if submission.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this submission's feedback",
        )

    # Get the feedback
    feedback = (
        db.query(Feedback).filter(Feedback.submission_id == submission_id).first()
    )
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No feedback found for this submission",
        )

    return feedback


# List all feedback for the current user
@router.get("/list", response_model=FeedbackList)
async def list_user_feedback(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # Get all submissions by the user
    user_submissions = (
        db.query(Submission).filter(Submission.user_id == current_user.id).all()
    )
    submission_ids = [submission.id for submission in user_submissions]

    # Get all feedback for these submissions
    feedback_list = (
        db.query(Feedback).filter(Feedback.submission_id.in_(submission_ids)).all()
    )

    return {"feedback": feedback_list}


# Create feedback for a submission (admin only)
@router.post("/", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def create_feedback(
    feedback_data: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # Check if user is admin
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can create feedback",
        )

    # Check if the submission exists
    submission = (
        db.query(Submission)
        .filter(Submission.id == feedback_data.submission_id)
        .first()
    )
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found"
        )

    # Check if feedback already exists for this submission
    existing_feedback = (
        db.query(Feedback)
        .filter(Feedback.submission_id == feedback_data.submission_id)
        .first()
    )
    if existing_feedback:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Feedback already exists for this submission. Use PATCH to update.",
        )

    # Create new feedback
    new_feedback = Feedback(
        content=feedback_data.content,
        grade=feedback_data.grade,
        submission_id=feedback_data.submission_id,
    )

    # Update the submission status to reviewed
    submission.status = "reviewed"

    db.add(new_feedback)
    db.commit()
    db.refresh(new_feedback)

    return new_feedback


# Update feedback for a submission (admin only)
@router.patch("/{feedback_id}", response_model=FeedbackResponse)
async def update_feedback(
    feedback_id: int,
    feedback_data: FeedbackBase,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # Check if user is admin
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can update feedback",
        )

    # Check if the feedback exists
    feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found"
        )

    # Update feedback fields
    feedback.content = feedback_data.content
    feedback.grade = feedback_data.grade

    db.commit()
    db.refresh(feedback)

    return feedback


# Delete feedback (admin only)
@router.delete("/{feedback_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_feedback(
    feedback_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # Check if user is admin
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can delete feedback",
        )

    # Check if the feedback exists
    feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found"
        )

    # Get the associated submission to update its status
    submission = (
        db.query(Submission).filter(Submission.id == feedback.submission_id).first()
    )
    if submission:
        submission.status = "pending"  # Reset to pending

    # Delete the feedback
    db.delete(feedback)
    db.commit()

    return None
