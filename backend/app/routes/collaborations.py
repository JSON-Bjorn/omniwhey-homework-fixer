from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

# These imports will work properly due to sys.path manipulation in run.py
from config.database import get_db
from models import Collaboration, PRD, User
from app.auth import get_current_active_user

router = APIRouter(prefix="/api/collaborations", tags=["collaborations"])


# Pydantic models for request/response
class CollaborationBase(BaseModel):
    prd_id: int
    user_id: int
    permission: str = "read"  # read, write, admin


class CollaborationCreate(CollaborationBase):
    pass


class CollaborationResponse(CollaborationBase):
    id: int

    class Config:
        from_attributes = True


class CollaborationList(BaseModel):
    collaborations: List[CollaborationResponse]


# Get all collaborations for PRDs owned by the user
@router.get("/", response_model=CollaborationList)
async def get_collaborations(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    # Get all PRDs owned by the user
    user_prds = db.query(PRD).filter(PRD.creator_id == current_user.id).all()
    prd_ids = [prd.id for prd in user_prds]

    # Get all collaborations for these PRDs
    collaborations = (
        db.query(Collaboration).filter(Collaboration.prd_id.in_(prd_ids)).all()
    )

    return {"collaborations": collaborations}


# Get collaborations for a specific PRD
@router.get("/prd/{prd_id}", response_model=CollaborationList)
async def get_prd_collaborations(
    prd_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # Check if PRD exists
    prd = db.query(PRD).filter(PRD.id == prd_id).first()
    if not prd:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="PRD not found"
        )

    # Check if the user is the creator of the PRD
    if prd.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the creator can view all collaborations",
        )

    # Get all collaborations for this PRD
    collaborations = (
        db.query(Collaboration).filter(Collaboration.prd_id == prd_id).all()
    )

    return {"collaborations": collaborations}


# Create a new collaboration (share a PRD with another user)
@router.post(
    "/", response_model=CollaborationResponse, status_code=status.HTTP_201_CREATED
)
async def create_collaboration(
    collaboration_data: CollaborationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # Check if PRD exists
    prd = db.query(PRD).filter(PRD.id == collaboration_data.prd_id).first()
    if not prd:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="PRD not found"
        )

    # Check if the user is the creator of the PRD or has admin permission
    is_creator = prd.creator_id == current_user.id
    has_admin = False

    if not is_creator:
        admin_collab = (
            db.query(Collaboration)
            .filter(
                Collaboration.prd_id == collaboration_data.prd_id,
                Collaboration.user_id == current_user.id,
                Collaboration.permission == "admin",
            )
            .first()
        )
        has_admin = admin_collab is not None

    if not (is_creator or has_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the creator or admin collaborators can share this PRD",
        )

    # Check if target user exists
    target_user = db.query(User).filter(User.id == collaboration_data.user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Target user not found"
        )

    # Check if collaboration already exists
    existing_collab = (
        db.query(Collaboration)
        .filter(
            Collaboration.prd_id == collaboration_data.prd_id,
            Collaboration.user_id == collaboration_data.user_id,
        )
        .first()
    )

    if existing_collab:
        # Update existing collaboration
        existing_collab.permission = collaboration_data.permission
        db.commit()
        db.refresh(existing_collab)
        return existing_collab

    # Create new collaboration
    new_collaboration = Collaboration(
        prd_id=collaboration_data.prd_id,
        user_id=collaboration_data.user_id,
        permission=collaboration_data.permission,
    )

    db.add(new_collaboration)
    db.commit()
    db.refresh(new_collaboration)

    return new_collaboration


# Update a collaboration
@router.put("/{collaboration_id}", response_model=CollaborationResponse)
async def update_collaboration(
    collaboration_id: int,
    collaboration_data: CollaborationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # Check if collaboration exists
    collaboration = (
        db.query(Collaboration).filter(Collaboration.id == collaboration_id).first()
    )
    if not collaboration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Collaboration not found"
        )

    # Check if PRD exists
    prd = db.query(PRD).filter(PRD.id == collaboration_data.prd_id).first()
    if not prd:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="PRD not found"
        )

    # Check if the user is the creator of the PRD or has admin permission
    is_creator = prd.creator_id == current_user.id
    has_admin = False

    if not is_creator:
        admin_collab = (
            db.query(Collaboration)
            .filter(
                Collaboration.prd_id == collaboration_data.prd_id,
                Collaboration.user_id == current_user.id,
                Collaboration.permission == "admin",
            )
            .first()
        )
        has_admin = admin_collab is not None

    if not (is_creator or has_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the creator or admin collaborators can update collaborations",
        )

    # Update collaboration
    collaboration.prd_id = collaboration_data.prd_id
    collaboration.user_id = collaboration_data.user_id
    collaboration.permission = collaboration_data.permission

    db.commit()
    db.refresh(collaboration)

    return collaboration


# Delete a collaboration
@router.delete("/{collaboration_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_collaboration(
    collaboration_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # Check if collaboration exists
    collaboration = (
        db.query(Collaboration).filter(Collaboration.id == collaboration_id).first()
    )
    if not collaboration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Collaboration not found"
        )

    # Check if the user is the creator of the PRD or has admin permission
    prd = db.query(PRD).filter(PRD.id == collaboration.prd_id).first()
    if not prd:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="PRD not found"
        )

    is_creator = prd.creator_id == current_user.id
    has_admin = False

    if not is_creator:
        admin_collab = (
            db.query(Collaboration)
            .filter(
                Collaboration.prd_id == collaboration.prd_id,
                Collaboration.user_id == current_user.id,
                Collaboration.permission == "admin",
            )
            .first()
        )
        has_admin = admin_collab is not None

    if not (is_creator or has_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the creator or admin collaborators can delete collaborations",
        )

    db.delete(collaboration)
    db.commit()

    return None
