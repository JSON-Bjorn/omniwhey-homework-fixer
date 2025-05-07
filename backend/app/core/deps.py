from typing import Annotated, AsyncGenerator, Optional
from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi.security import OAuth2PasswordBearer

from app.core.config import settings
from app.core.security import ALGORITHM
from app.db.session import get_db
from app.models import User, UserRole

# OAuth2 token bearer scheme
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> User:
    """
    Validates the token and returns the current user.

    Args:
        token: JWT token from the Authorization header
        db: Database session

    Returns:
        User model instance

    Raises:
        HTTPException: If token is invalid or user is not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    stmt = select(User).where(User.id == int(user_id), User.is_active == True)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Get current active user.

    Args:
        current_user: Authenticated user

    Returns:
        User model instance

    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user"
        )
    return current_user


async def get_current_active_verified_user(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    """
    Get current active and verified user.

    Args:
        current_user: Authenticated active user

    Returns:
        User model instance

    Raises:
        HTTPException: If user is not verified
    """
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not verified",
        )
    return current_user


async def get_current_teacher(
    current_user: Annotated[User, Depends(get_current_active_verified_user)],
) -> User:
    """
    Get current teacher user.

    Args:
        current_user: Authenticated active and verified user

    Returns:
        User model instance (teacher)

    Raises:
        HTTPException: If user is not a teacher
    """
    if current_user.role != UserRole.TEACHER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a teacher",
        )
    return current_user


async def get_current_student(
    current_user: Annotated[User, Depends(get_current_active_verified_user)],
) -> User:
    """
    Get current student user.

    Args:
        current_user: Authenticated active and verified user

    Returns:
        User model instance (student)

    Raises:
        HTTPException: If user is not a student
    """
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a student",
        )
    return current_user


# Common type annotations for dependencies
CurrentUser = Annotated[User, Depends(get_current_active_user)]
CurrentVerifiedUser = Annotated[
    User, Depends(get_current_active_verified_user)
]
CurrentTeacher = Annotated[User, Depends(get_current_teacher)]
CurrentStudent = Annotated[User, Depends(get_current_student)]
DbSession = Annotated[AsyncSession, Depends(get_db)]
