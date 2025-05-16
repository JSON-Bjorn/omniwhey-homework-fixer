from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class FeatureBase(BaseModel):
    """Base feature schema."""

    name: str = Field(min_length=1, max_length=50)
    description: Optional[str] = None
    enabled: bool = False


class FeatureCreate(FeatureBase):
    """Schema for creating a feature."""

    pass


class FeatureUpdate(BaseModel):
    """Schema for updating a feature."""

    description: Optional[str] = None
    enabled: Optional[bool] = None


class FeatureInDBBase(FeatureBase):
    """Base feature DB schema."""

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Feature(FeatureInDBBase):
    """Schema for feature response."""

    pass
