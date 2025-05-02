from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import json

# These imports will work properly due to sys.path manipulation in run.py
from config.database import get_db
from models import Template, User, PRD
from app.auth import get_current_active_user

router = APIRouter(prefix="/api/templates", tags=["templates"])


# Pydantic models for request/response
class TemplateBase(BaseModel):
    title: str
    description: Optional[str] = None
    is_public: bool = False


class TemplateCreate(TemplateBase):
    structure: str  # JSON string containing template structure


class TemplateResponse(TemplateBase):
    id: int
    structure: str
    creator_id: int

    class Config:
        from_attributes = True


class TemplateList(BaseModel):
    templates: List[TemplateResponse]


# Get all templates (public or owned by the user)
@router.get("/", response_model=TemplateList)
async def get_templates(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    templates = (
        db.query(Template)
        .filter((Template.is_public == True) | (Template.creator_id == current_user.id))
        .all()
    )
    return {"templates": templates}


# Get a specific template by ID
@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    template = db.query(Template).filter(Template.id == template_id).first()

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Template not found"
        )

    # Check if the user has access to this template
    if not template.is_public and template.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this template",
        )

    return template


# Create a new template
@router.post("/", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    template_data: TemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # Validate JSON structure
    try:
        json.loads(template_data.structure)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON structure"
        )

    # Create new template
    new_template = Template(
        title=template_data.title,
        description=template_data.description,
        structure=template_data.structure,
        is_public=template_data.is_public,
        creator_id=current_user.id,
    )

    db.add(new_template)
    db.commit()
    db.refresh(new_template)

    return new_template


# Update an existing template
@router.put("/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: int,
    template_data: TemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    template = db.query(Template).filter(Template.id == template_id).first()

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Template not found"
        )

    # Check if the user is the creator of the template
    if template.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own templates",
        )

    # Validate JSON structure
    try:
        json.loads(template_data.structure)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON structure"
        )

    # Update template fields
    template.title = template_data.title
    template.description = template_data.description
    template.structure = template_data.structure
    template.is_public = template_data.is_public

    db.commit()
    db.refresh(template)

    return template


# Delete a template
@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    template = db.query(Template).filter(Template.id == template_id).first()

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Template not found"
        )

    # Check if the user is the creator of the template
    if template.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own templates",
        )

    db.delete(template)
    db.commit()

    return None
