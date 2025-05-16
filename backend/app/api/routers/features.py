from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
import logging

from app.core.deps import DbSession, CurrentTeacher
from app.schemas.feature import (
    Feature as FeatureSchema,
    FeatureCreate,
    FeatureUpdate,
)
from app.crud import feature as feature_crud

# Set up logger
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=List[FeatureSchema])
async def get_features(
    db: DbSession,
    current_teacher: CurrentTeacher,
) -> List[FeatureSchema]:
    """
    Get all feature flags.
    Only available to teachers.

    Args:
        db: Database session
        current_teacher: Current authenticated teacher

    Returns:
        List of feature flags
    """
    features = await feature_crud.get_all_features(db)
    return features


@router.get("/{feature_name}", response_model=FeatureSchema)
async def get_feature(
    feature_name: str,
    db: DbSession,
    current_teacher: CurrentTeacher,
) -> FeatureSchema:
    """
    Get a specific feature flag.
    Only available to teachers.

    Args:
        feature_name: Name of the feature flag
        db: Database session
        current_teacher: Current authenticated teacher

    Returns:
        Feature flag

    Raises:
        HTTPException: If feature flag not found
    """
    feature = await feature_crud.get_feature(db, name=feature_name)
    if not feature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feature flag not found",
        )
    return feature


@router.post("/", response_model=FeatureSchema)
async def create_feature(
    feature_in: FeatureCreate,
    db: DbSession,
    current_teacher: CurrentTeacher,
) -> FeatureSchema:
    """
    Create a new feature flag.
    Only available to teachers.

    Args:
        feature_in: Feature creation data
        db: Database session
        current_teacher: Current authenticated teacher

    Returns:
        Created feature flag
    """
    feature = await feature_crud.create_feature(
        db,
        name=feature_in.name,
        description=feature_in.description,
        enabled=feature_in.enabled,
    )
    return feature


@router.patch("/{feature_name}", response_model=FeatureSchema)
async def update_feature(
    feature_name: str,
    feature_in: FeatureUpdate,
    db: DbSession,
    current_teacher: CurrentTeacher,
) -> FeatureSchema:
    """
    Update a feature flag.
    Only available to teachers.

    Args:
        feature_name: Name of the feature flag
        feature_in: Feature update data
        db: Database session
        current_teacher: Current authenticated teacher

    Returns:
        Updated feature flag

    Raises:
        HTTPException: If feature flag not found
    """
    existing_feature = await feature_crud.get_feature(db, name=feature_name)
    if not existing_feature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feature flag not found",
        )

    update_data = feature_in.model_dump(exclude_unset=True)

    # Only update enabled status if provided
    if "enabled" in update_data:
        feature = await feature_crud.update_feature(
            db, name=feature_name, enabled=update_data["enabled"]
        )
        return feature

    # If no updates provided, return existing feature
    return existing_feature
