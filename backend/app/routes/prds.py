from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import json

# These imports will work properly due to sys.path manipulation in run.py
from config.database import get_db
from models import PRD, Template, User, Collaboration
from app.auth import get_current_active_user

router = APIRouter(prefix="/api/prds", tags=["prds"])


# Pydantic models for request/response
class PRDBase(BaseModel):
    title: str
    is_published: bool = False


class PRDCreate(PRDBase):
    template_id: int
    content: str  # JSON string containing PRD content based on template structure


class PRDResponse(PRDBase):
    id: int
    content: str
    template_id: int
    creator_id: int

    class Config:
        from_attributes = True


class PRDList(BaseModel):
    prds: List[PRDResponse]


# Get all PRDs owned by or shared with the user
@router.get("/", response_model=PRDList)
async def get_prds(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    # Get PRDs created by the user
    owned_prds = db.query(PRD).filter(PRD.creator_id == current_user.id).all()

    # Get PRDs shared with the user through collaborations
    collaborations = (
        db.query(Collaboration).filter(Collaboration.user_id == current_user.id).all()
    )
    shared_prd_ids = [collab.prd_id for collab in collaborations]
    shared_prds = db.query(PRD).filter(PRD.id.in_(shared_prd_ids)).all()

    # Combine the lists
    all_prds = owned_prds + shared_prds

    return {"prds": all_prds}


# Get a specific PRD by ID
@router.get("/{prd_id}", response_model=PRDResponse)
async def get_prd(
    prd_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    prd = db.query(PRD).filter(PRD.id == prd_id).first()

    if not prd:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="PRD not found"
        )

    # Check if the user has access to this PRD (owner or collaborator)
    has_access = prd.creator_id == current_user.id

    if not has_access:
        collaboration = (
            db.query(Collaboration)
            .filter(
                Collaboration.prd_id == prd_id, Collaboration.user_id == current_user.id
            )
            .first()
        )
        has_access = collaboration is not None

    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this PRD",
        )

    return prd


# Create a new PRD
@router.post("/", response_model=PRDResponse, status_code=status.HTTP_201_CREATED)
async def create_prd(
    prd_data: PRDCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # Check if template exists
    template = db.query(Template).filter(Template.id == prd_data.template_id).first()
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Template not found"
        )

    # Check if user has access to the template
    if not template.is_public and template.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this template",
        )

    # Validate JSON content
    try:
        content_json = json.loads(prd_data.content)
        template_structure = json.loads(template.structure)

        # Basic validation that content matches template structure
        # This is a simplified validation and could be enhanced based on specific requirements
        for section in template_structure:
            if section not in content_json:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Content is missing required section: {section}",
                )
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON content"
        )

    # Create new PRD
    new_prd = PRD(
        title=prd_data.title,
        content=prd_data.content,
        template_id=prd_data.template_id,
        is_published=prd_data.is_published,
        creator_id=current_user.id,
    )

    db.add(new_prd)
    db.commit()
    db.refresh(new_prd)

    return new_prd


# Update an existing PRD
@router.put("/{prd_id}", response_model=PRDResponse)
async def update_prd(
    prd_id: int,
    prd_data: PRDCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    prd = db.query(PRD).filter(PRD.id == prd_id).first()

    if not prd:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="PRD not found"
        )

    # Check if the user has write access to this PRD
    has_write_access = prd.creator_id == current_user.id

    if not has_write_access:
        collaboration = (
            db.query(Collaboration)
            .filter(
                Collaboration.prd_id == prd_id,
                Collaboration.user_id == current_user.id,
                Collaboration.permission.in_(["write", "admin"]),
            )
            .first()
        )
        has_write_access = collaboration is not None

    if not has_write_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have write access to this PRD",
        )

    # Check if changing template (only creator can do this)
    if prd_data.template_id != prd.template_id and prd.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the creator can change the template",
        )

    # Check if new template exists
    template = db.query(Template).filter(Template.id == prd_data.template_id).first()
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Template not found"
        )

    # Validate JSON content
    try:
        content_json = json.loads(prd_data.content)
        template_structure = json.loads(template.structure)

        # Basic validation that content matches template structure
        for section in template_structure:
            if section not in content_json:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Content is missing required section: {section}",
                )
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON content"
        )

    # Update PRD fields
    prd.title = prd_data.title
    prd.content = prd_data.content
    prd.template_id = prd_data.template_id
    prd.is_published = prd_data.is_published

    db.commit()
    db.refresh(prd)

    return prd


# Delete a PRD
@router.delete("/{prd_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_prd(
    prd_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    prd = db.query(PRD).filter(PRD.id == prd_id).first()

    if not prd:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="PRD not found"
        )

    # Only the creator can delete the PRD
    if prd.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the creator can delete a PRD",
        )

    db.delete(prd)
    db.commit()

    return None
