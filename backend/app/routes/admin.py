from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import math

# These imports will work properly due to sys.path manipulation in run.py
from config.database import get_db
from models import Template, User, PRD, Collaboration, Submission, Feedback
from app.auth import get_current_active_user

router = APIRouter(prefix="/api/admin", tags=["admin"])


# Check if the user is an admin
async def get_admin_user(current_user: User = Depends(get_current_active_user)):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required"
        )
    return current_user


# Pydantic models for request/response
class TemplateResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    structure: str
    is_public: bool
    creator_id: int

    class Config:
        from_attributes = True


class TemplateList(BaseModel):
    templates: List[TemplateResponse]


class UserBase(BaseModel):
    email: str
    is_active: bool
    is_admin: bool


class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserList(BaseModel):
    users: List[UserResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class SubmissionBase(BaseModel):
    title: str
    description: Optional[str] = None
    file_path: Optional[str] = None
    original_filename: Optional[str] = None
    file_type: Optional[str] = None
    status: str
    user_id: int


class SubmissionResponse(SubmissionBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SubmissionList(BaseModel):
    submissions: List[SubmissionResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


# Get all templates (admin only)
@router.get("/templates", response_model=TemplateList)
async def get_all_templates(
    db: Session = Depends(get_db), admin_user: User = Depends(get_admin_user)
):
    templates = db.query(Template).all()
    return {"templates": templates}


# Archive a template (admin only)
@router.put("/templates/{template_id}/archive", response_model=TemplateResponse)
async def archive_template(
    template_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user),
):
    template = db.query(Template).filter(Template.id == template_id).first()

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Template not found"
        )

    # Archive by setting not public and adding archived flag
    # (we would need to add an archived field to the Template model for a full implementation)
    template.is_public = False

    db.commit()
    db.refresh(template)

    return template


# Make a template the default (admin only)
@router.put("/templates/{template_id}/set-default", response_model=TemplateResponse)
async def set_default_template(
    template_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user),
):
    template = db.query(Template).filter(Template.id == template_id).first()

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Template not found"
        )

    # For a full implementation, we would add a 'is_default' field to the Template model
    # and then clear any existing default templates before setting this one
    # For now, just make it public
    template.is_public = True

    db.commit()
    db.refresh(template)

    return template


# Get usage statistics for templates (admin only)
@router.get("/templates/stats")
async def get_template_stats(
    db: Session = Depends(get_db), admin_user: User = Depends(get_admin_user)
):
    # Get all templates
    templates = db.query(Template).all()

    stats = []
    for template in templates:
        # Count PRDs using this template
        prd_count = db.query(PRD).filter(PRD.template_id == template.id).count()

        # Get the template creator
        creator = db.query(User).filter(User.id == template.creator_id).first()
        creator_email = creator.email if creator else "Unknown"

        stats.append(
            {
                "template_id": template.id,
                "title": template.title,
                "creator": creator_email,
                "usage_count": prd_count,
                "is_public": template.is_public,
            }
        )

    return {"template_stats": stats}


# Get all users with pagination (admin only)
@router.get("/users", response_model=UserList)
async def get_all_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user),
):
    # Base query
    query = db.query(User)

    # Apply search filter if provided
    if search:
        query = query.filter(User.email.ilike(f"%{search}%"))

    # Get total count for pagination
    total = query.count()

    # Calculate pagination values
    total_pages = (total + per_page - 1) // per_page
    offset = (page - 1) * per_page

    # Get paginated results
    users = query.offset(offset).limit(per_page).all()

    return {
        "users": users,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
    }


# Get user details by ID (admin only)
@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user),
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return user


# Update user admin status (admin only)
@router.patch("/users/{user_id}/set-admin")
async def set_user_admin_status(
    user_id: int,
    is_admin: bool,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user),
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    user.is_admin = is_admin
    db.commit()
    db.refresh(user)

    return {"id": user.id, "email": user.email, "is_admin": user.is_admin}


# Update user active status (admin only)
@router.patch("/users/{user_id}/set-active")
async def set_user_active_status(
    user_id: int,
    is_active: bool,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user),
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    user.is_active = is_active
    db.commit()
    db.refresh(user)

    return {"id": user.id, "email": user.email, "is_active": user.is_active}


# Get all submissions with pagination (admin only)
@router.get("/submissions", response_model=SubmissionList)
async def get_all_submissions(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user),
):
    # Base query
    query = db.query(Submission)

    # Apply filters if provided
    if status:
        query = query.filter(Submission.status == status)

    if user_id:
        query = query.filter(Submission.user_id == user_id)

    # Get total count for pagination
    total = query.count()

    # Calculate pagination values
    total_pages = (total + per_page - 1) // per_page
    offset = (page - 1) * per_page

    # Get paginated results ordered by created_at descending (newest first)
    submissions = (
        query.order_by(Submission.created_at.desc())
        .offset(offset)
        .limit(per_page)
        .all()
    )

    return {
        "submissions": submissions,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
    }


# Get submission details by ID (admin only)
@router.get("/submissions/{submission_id}", response_model=SubmissionResponse)
async def get_submission(
    submission_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user),
):
    submission = db.query(Submission).filter(Submission.id == submission_id).first()

    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found"
        )

    return submission


# Get submission statistics (admin only)
@router.get("/submissions/stats")
async def get_submission_stats(
    db: Session = Depends(get_db), admin_user: User = Depends(get_admin_user)
):
    # Count submissions by status
    pending_count = db.query(Submission).filter(Submission.status == "pending").count()
    reviewed_count = (
        db.query(Submission).filter(Submission.status == "reviewed").count()
    )
    rejected_count = (
        db.query(Submission).filter(Submission.status == "rejected").count()
    )

    # Count submissions with feedback
    with_feedback_count = db.query(Submission).join(Feedback).count()

    # Count total submissions
    total_count = db.query(Submission).count()

    # Calculate average grade if applicable
    # This assumes grades are stored as numeric strings that can be converted to float
    # In a real implementation, you'd need proper handling for non-numeric grades

    return {
        "total_submissions": total_count,
        "status_counts": {
            "pending": pending_count,
            "reviewed": reviewed_count,
            "rejected": rejected_count,
        },
        "with_feedback": with_feedback_count,
        "without_feedback": total_count - with_feedback_count,
    }
