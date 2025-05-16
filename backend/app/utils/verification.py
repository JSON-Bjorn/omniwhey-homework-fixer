from datetime import datetime, timedelta
import uuid
import secrets
import logging
from typing import Optional, Tuple
from jose import jwt, JWTError
from pydantic import EmailStr

from app.core.config import settings
from app.db.session import get_db
from app.utils.email import send_verification_email

# Set up logger
logger = logging.getLogger(__name__)

# Constants
ALGORITHM = "HS256"
VERIFICATION_TOKEN_EXPIRE_HOURS = 24


def create_verification_token(user_id: uuid.UUID, email: str) -> str:
    """
    Create an email verification token.

    Args:
        user_id: User ID to encode in the token
        email: User's email address

    Returns:
        Encoded JWT token
    """
    # Set expiration time
    expires_delta = timedelta(hours=VERIFICATION_TOKEN_EXPIRE_HOURS)
    expire = datetime.utcnow() + expires_delta

    # Create JWT payload
    to_encode = {
        "exp": expire,
        "sub": str(user_id),
        "email": email,
        "type": "email_verification",
    }

    # Create token
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=ALGORITHM
    )

    logger.info(f"Created verification token for user {user_id}")
    return encoded_jwt


def decode_verification_token(token: str) -> Optional[dict]:
    """
    Decode and validate a verification token.

    Args:
        token: JWT token to decode

    Returns:
        Decoded token payload or None if invalid
    """
    try:
        # Decode and verify token
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[ALGORITHM]
        )

        # Check required fields
        if not all(k in payload for k in ["sub", "email", "type"]):
            logger.warning(
                "Token verification failed: Missing required fields"
            )
            return None

        # Check token type
        if payload["type"] != "email_verification":
            logger.warning(
                f"Token verification failed: Invalid token type {payload.get('type')}"
            )
            return None

        return payload

    except JWTError as e:
        logger.warning(f"Token verification failed: {str(e)}")
        return None


def get_verification_link(base_url: str, token: str) -> str:
    """
    Generate a verification link with the token.

    Args:
        base_url: Base URL for the application
        token: Verification token

    Returns:
        Complete verification link
    """
    return f"{base_url}/api/v1/auth/verify-email?token={token}"


async def send_user_verification_email(
    base_url: str, user_id: uuid.UUID, email: EmailStr, name: str
) -> bool:
    """
    Create verification token and send verification email.

    Args:
        base_url: Base URL for the application
        user_id: User ID
        email: User's email address
        name: User's name

    Returns:
        True if email was sent successfully, False otherwise
    """
    try:
        # Create verification token
        token = create_verification_token(user_id, email)

        # Generate verification link
        verification_link = get_verification_link(base_url, token)

        # Send email
        sent = await send_verification_email(
            email_to=email,
            verification_link=verification_link,
            user_name=name,
        )

        if sent:
            logger.info(f"Verification email sent to user {user_id}")
        else:
            logger.warning(
                f"Failed to send verification email to user {user_id}"
            )

        return sent

    except Exception as e:
        logger.error(f"Error sending verification email to {email}: {str(e)}")
        return False
