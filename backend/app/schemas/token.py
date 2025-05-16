from datetime import datetime
import uuid
from pydantic import BaseModel, ConfigDict


# Token schema for authentication
class TokenBase(BaseModel):
    """Base token schema."""

    token: str
    expires_at: datetime
    is_revoked: bool
    user_id: uuid.UUID


class TokenCreate(BaseModel):
    """Schema for creating a token."""

    user_id: uuid.UUID


class TokenInDBBase(TokenBase):
    """Base token DB schema."""

    id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(TokenInDBBase):
    """Schema for token response."""

    pass


class TokenInDB(TokenInDBBase):
    """Schema for token in DB."""

    pass


# Auth response schema (different from the DB token schema)
class TokenResponse(BaseModel):
    """Schema for token response to client."""

    access_token: str
    token_type: str = "bearer"
    expires_at: datetime
