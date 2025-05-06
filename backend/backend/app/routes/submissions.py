from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from fastapi.responses import FileResponse
import os

# These imports will work properly due to sys.path manipulation in run.py
from config.database import get_db
from models import Submission, User
from app.auth import get_current_active_user
from app.utils.file_storage import save_uploaded_file, delete_file, get_file_path

router = APIRouter(prefix="/api/submissions", tags=["submissions"])


# Pydantic models for request/response
class SubmissionBase(BaseModel):
    title: str
    description: Optional[str] = None


class SubmissionCreate(SubmissionBase):
    pass


class SubmissionResponse(SubmissionBase):
    id: int
    file_path: Optional[str] = None
    original_filename: Optional[str] = None
    file_type: Optional[str] = None
    status: str
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SubmissionList(BaseModel):
    submissions: List[SubmissionResponse]


# Upload a new submission with file
@router.post(
    "/upload", response_model=SubmissionResponse, status_code=status.HTTP_201_CREATED
)
async def upload_submission(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        # Save file to storage
        file_path, file_type = save_uploaded_file(file, current_user.id)

        # Create submission record in database
        new_submission = Submission(
            title=title,
            description=description,
            file_path=file_path,
            original_filename=file.filename,
            file_type=file_type,
            user_id=current_user.id,
            status="pending",
        )

        db.add(new_submission)
        db.commit()
        db.refresh(new_submission)

        return new_submission

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        # Make sure to clean up file if database operation fails
        if "file_path" in locals():
            delete_file(file_path)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload submission: {str(e)}",
        )


# Get all submissions for the current user
@router.get("/", response_model=SubmissionList)
async def get_user_submissions(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    query = db.query(Submission).filter(Submission.user_id == current_user.id)

    if status:
        query = query.filter(Submission.status == status)

    submissions = query.order_by(Submission.created_at.desc()).all()

    return {"submissions": submissions}


# Get a specific submission by ID
@router.get("/{submission_id}", response_model=SubmissionResponse)
async def get_submission(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    submission = db.query(Submission).filter(Submission.id == submission_id).first()

    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found"
        )

    # Check if the user has access to this submission
    if submission.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this submission",
        )

    return submission


# Download a submission file
@router.get("/{submission_id}/download")
async def download_submission_file(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    submission = db.query(Submission).filter(Submission.id == submission_id).first()

    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found"
        )

    # Check if the user has access to this submission
    if submission.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this submission",
        )

    if not submission.file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No file associated with this submission",
        )

    # Get file path
    file_path = get_file_path(submission.file_path)

    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
        )

    # Return file as a response
    return FileResponse(
        path=str(file_path),
        filename=submission.original_filename,
        media_type=submission.file_type,
    )


# Delete a submission
@router.delete("/{submission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_submission(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    submission = db.query(Submission).filter(Submission.id == submission_id).first()

    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found"
        )

    # Check if the user is the owner of the submission
    if submission.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this submission",
        )

    # Delete file from storage if it exists
    if submission.file_path:
        delete_file(submission.file_path)

    # Delete submission from database
    db.delete(submission)
    db.commit()

    return None
