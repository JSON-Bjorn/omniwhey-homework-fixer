from typing import Any
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_access_token
from app.core.deps import DbSession
from app.crud import user as user_crud
from app.models.user import UserRole
from app.schemas.user import Token, UserCreate, User, EmailVerification

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(
    db: DbSession, form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.

    Args:
        db: Database session
        form_data: OAuth2 password request form

    Returns:
        Access token

    Raises:
        HTTPException: If authentication fails
    """
    user = await user_crud.authenticate_user(
        db, email=form_data.username, password=form_data.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )

    # Create access token
    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    access_token = create_access_token(
        subject=str(user.id), expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register/student", response_model=User)
async def register_student(*, db: DbSession, user_in: UserCreate) -> Any:
    """
    Register a new student user.

    Args:
        db: Database session
        user_in: User creation data

    Returns:
        Created user

    Raises:
        HTTPException: If user already exists
    """
    # Force role to student
    user_in.role = UserRole.STUDENT

    # Check if user with this email already exists
    user = await user_crud.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists",
        )

    # Create new student user
    user = await user_crud.create_user(db, obj_in=user_in)

    # TODO: Send verification email

    return user


@router.post("/register/teacher", response_model=User)
async def register_teacher(*, db: DbSession, user_in: UserCreate) -> Any:
    """
    Register a new teacher user.

    Args:
        db: Database session
        user_in: User creation data

    Returns:
        Created user

    Raises:
        HTTPException: If user already exists
    """
    # Force role to teacher
    user_in.role = UserRole.TEACHER

    # Check if user with this email already exists
    user = await user_crud.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists",
        )

    # Create new teacher user
    user = await user_crud.create_user(db, obj_in=user_in)

    # TODO: Send verification email

    return user


@router.post("/verify-email", response_model=User)
async def verify_email(
    *, db: DbSession, verification_data: EmailVerification
) -> Any:
    """
    Verify user email with token.

    Args:
        db: Database session
        verification_data: Email verification token

    Returns:
        Updated user

    Raises:
        HTTPException: If token is invalid
    """
    # TODO: Implement token verification logic
    # This is a placeholder
    # In a real implementation, the token would be verified and used to identify the user

    # For now, we'll just return a 501 Not Implemented
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Email verification not implemented yet",
    )
