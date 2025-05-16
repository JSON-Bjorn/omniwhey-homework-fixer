from typing import Any, Optional
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    BackgroundTasks,
    Request,
    Response,
)
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from pydantic import EmailStr
import uuid
from sqlalchemy import select, func

from app.core.config import settings
from app.core.deps import DbSession, CurrentUser
from app.crud import user as user_crud
from app.crud import token as token_crud
from app.models.user import UserRole
from app.schemas.user import UserCreate, User as UserSchema, EmailVerification
from app.schemas.token import TokenResponse
from app.utils.verification import (
    decode_verification_token,
    send_user_verification_email,
)
from app.utils.secure_logging import (
    censor_email,
    censor_uuid,
    censor_ip_address,
)

# Set up logger
logger = logging.getLogger(__name__)

# OAuth2 scheme for logout endpoint
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(
    db: DbSession,
    request: Request = None,
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.

    Args:
        db: Database session
        request: Request object
        form_data: OAuth2 password request form

    Returns:
        Access token

    Raises:
        HTTPException: If authentication fails
    """
    client_ip = (
        request.client.host
        if request and hasattr(request, "client")
        else "unknown"
    )
    censored_ip = censor_ip_address(client_ip)

    logger.info(
        f"Login attempt for email {censor_email(form_data.username)} from IP {censored_ip}"
    )

    user = await user_crud.authenticate_user(
        db, email=form_data.username, password=form_data.password
    )

    if not user:
        logger.warning(
            f"Login failed: Incorrect email or password, IP: {censored_ip}"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        logger.warning(
            f"Login failed: Unverified email for user ID {censor_uuid(user.id)}, IP: {censored_ip}"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email not verified. Please check your inbox for the verification email.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create database token
    db_token = await token_crud.create_token(db, user.id)
    logger.info(f"User {user.id} logged in successfully, IP: {censored_ip}")

    # Return token response
    return {
        "access_token": db_token.token,
        "token_type": "bearer",
        "expires_at": db_token.expires_at,
    }


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    response: Response,
    db: DbSession,
    token: str = Depends(oauth2_scheme),
    request: Request = None,
) -> Any:
    """
    Logout user by revoking the current token.

    Args:
        response: FastAPI response object
        db: Database session
        token: Current authentication token
        request: FastAPI request object

    Returns:
        Success message
    """
    client_ip = (
        request.client.host
        if request and hasattr(request, "client")
        else "unknown"
    )
    censored_ip = censor_ip_address(client_ip)

    logger.info(f"Logout attempt for token, IP: {censored_ip}")

    success = await token_crud.revoke_token(db, token)
    if success:
        logger.info(f"User logged out successfully, IP: {censored_ip}")
        return {"detail": "Successfully logged out"}
    else:
        logger.error(f"Logout failed: Invalid token, IP: {censored_ip}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token"
        )


@router.post("/register/student", response_model=UserSchema)
async def register_student(
    request: Request,
    background_tasks: BackgroundTasks,
    *,
    db: DbSession,
    user_in: UserCreate,
) -> Any:
    """
    Register a new student user.

    Args:
        request: Request object
        background_tasks: Background task manager
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
        logger.warning(
            f"Registration attempt with existing email: {user_in.email}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists",
        )

    # Create new student user
    user = await user_crud.create_user(db, obj_in=user_in)
    logger.info(f"New student registered: {user.id} ({user.email})")

    # Get base URL from request
    base_url = str(request.base_url).rstrip("/")

    # Send verification email in background
    background_tasks.add_task(
        send_user_verification_email,
        base_url=base_url,
        user_id=user.id,
        email=user.email,
        name=user.name,
    )

    logger.info(f"Verification email scheduled for user {user.id}")

    # Return user without sending the password or token
    return user


@router.post("/register/teacher", response_model=UserSchema)
async def register_teacher(
    request: Request,
    background_tasks: BackgroundTasks,
    *,
    db: DbSession,
    user_in: UserCreate,
) -> Any:
    """
    Register a new teacher user.

    Args:
        request: Request object
        background_tasks: Background task manager
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
        logger.warning(
            f"Registration attempt with existing email: {user_in.email}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists",
        )

    # Create new teacher user
    user = await user_crud.create_user(db, obj_in=user_in)
    logger.info(f"New teacher registered: {user.id} ({user.email})")

    # Get base URL from request
    base_url = str(request.base_url).rstrip("/")

    # Send verification email in background
    background_tasks.add_task(
        send_user_verification_email,
        base_url=base_url,
        user_id=user.id,
        email=user.email,
        name=user.name,
    )

    logger.info(f"Verification email scheduled for user {user.id}")

    # Return user without sending the password or token
    return user


@router.get("/verify-email", response_model=UserSchema)
async def verify_email(*, db: DbSession, token: str) -> Any:
    """
    Verify user email with token.

    Args:
        db: Database session
        token: Email verification token

    Returns:
        Updated user

    Raises:
        HTTPException: If token is invalid
    """
    # Decode and validate token
    payload = decode_verification_token(token)

    if not payload:
        logger.warning(f"Email verification failed: Invalid token")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token",
        )

    try:
        # Extract user ID from payload
        user_id = uuid.UUID(payload["sub"])
        email = payload.get("email")

        # Get user from database
        user = await user_crud.get_user(db, user_id=user_id)

        # Verify user exists
        if not user:
            logger.warning(
                f"Email verification failed: User not found for ID {user_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        # Check email matches
        if user.email != email:
            logger.warning(
                f"Email verification failed: Email mismatch for user {user_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification token",
            )

        # Check if already verified
        if user.is_verified:
            logger.info(f"User {user_id} already verified")
            return user

        # Verify user's email
        user = await user_crud.verify_user_email(db, user_id=user_id)

        logger.info(f"Email verified successfully for user {user_id}")
        return user

    except (ValueError, TypeError) as e:
        logger.error(f"Error verifying email: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token",
        )


@router.post("/resend-verification", status_code=status.HTTP_200_OK)
async def resend_verification_email(
    request: Request,
    background_tasks: BackgroundTasks,
    email: EmailStr,
    db: DbSession,
) -> Any:
    """
    Resend verification email.

    Args:
        request: Request object
        background_tasks: Background task manager
        email: User's email address
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException: If user not found
    """
    # Find user by email
    user = await user_crud.get_user_by_email(db, email=email)

    if not user:
        # For security reasons, don't reveal if the email exists or not
        return {
            "detail": "If the email exists, a verification link has been sent"
        }

    if user.is_verified:
        return {"detail": "Email already verified"}

    # Get base URL from request
    base_url = str(request.base_url).rstrip("/")

    # Send verification email in background
    background_tasks.add_task(
        send_user_verification_email,
        base_url=base_url,
        user_id=user.id,
        email=user.email,
        name=user.name,
    )

    logger.info(f"Verification email resent for user {user.id}")

    return {
        "detail": "If the email exists, a verification link has been sent"
    }


@router.get("/me", response_model=UserSchema)
async def get_current_user_profile(current_user: CurrentUser) -> Any:
    """
    Get current user profile.

    Args:
        current_user: Current authenticated user

    Returns:
        User profile information

    Raises:
        HTTPException: If not authenticated
    """
    try:
        # Print detailed debug information
        logger.info(
            f"User profile requested. Current user type: {type(current_user)}"
        )
        logger.info(
            f"User ID: {current_user.id if hasattr(current_user, 'id') else 'No ID'}"
        )
        logger.info(f"User attributes: {dir(current_user)}")

        logger.info(
            f"User {censor_uuid(current_user.id)} requested profile information"
        )

        # Create a minimal dict with just the needed attributes
        # This avoids serialization issues with SQLAlchemy models
        return {
            "id": str(current_user.id),
            "email": current_user.email,
            "name": current_user.name,
            "role": current_user.role.value
            if hasattr(current_user.role, "value")
            else str(current_user.role),
            "is_active": current_user.is_active,
            "is_verified": current_user.is_verified,
            "total_gold_coins": current_user.total_gold_coins or 0,
            "created_at": current_user.created_at.isoformat()
            if hasattr(current_user, "created_at") and current_user.created_at
            else None,
            "updated_at": current_user.updated_at.isoformat()
            if hasattr(current_user, "updated_at") and current_user.updated_at
            else None,
        }
    except Exception as e:
        logger.error(f"Error in get_current_user_profile: {str(e)}")
        logger.exception("Full exception details:")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@router.get("/verify-test/{user_id}", include_in_schema=False)
async def verify_user_for_testing(user_id: uuid.UUID, db: DbSession) -> Any:
    """
    Verify user email bypassing the token check (for testing only).
    This endpoint is hidden from the OpenAPI schema.

    Args:
        user_id: User ID
        db: Database session

    Returns:
        Verified user
    """
    try:
        logger.info(f"Verify test endpoint called for user ID: {user_id}")

        # In production, this endpoint should not exist or be protected by admin auth
        # Here we're using it purely for testing

        # Safety check - only allow this endpoint in non-production environments
        if settings.ENVIRONMENT == "production":
            logger.warning(
                f"Verify test endpoint called in production environment"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Endpoint not found",
            )

        # Get user from database
        logger.info(f"Fetching user with ID: {user_id}")
        user = await user_crud.get_user(db, user_id=user_id)

        # Verify user exists
        if not user:
            logger.warning(
                f"Verification test failed: User not found for ID {user_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        logger.info(
            f"User found: {user.id}, is_active={user.is_active}, is_verified={user.is_verified}"
        )

        # Verify user's email
        logger.info(f"Verifying user email for user ID: {user_id}")
        user = await user_crud.verify_user_email(db, user_id=user_id)

        if not user:
            logger.error(f"Failed to verify user ID: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to verify user",
            )

        logger.info(
            f"User {user_id} verified for testing, is_active={user.is_active}, is_verified={user.is_verified}"
        )

        # Convert to dict for safer serialization
        user_dict = {
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
            "role": str(user.role),
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "created_at": user.created_at.isoformat()
            if user.created_at
            else None,
            "updated_at": user.updated_at.isoformat()
            if user.updated_at
            else None,
            "total_gold_coins": user.total_gold_coins,
        }

        logger.info(f"Returning user data: {user_dict}")
        return user_dict

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error in verify_user_for_testing: {str(e)}")
        logger.exception("Full exception details:")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )
