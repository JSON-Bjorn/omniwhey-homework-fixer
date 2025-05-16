"""
Email verification utility functions.
"""

import logging
import uuid
from typing import Optional, Tuple

from app.utils.verification import decode_verification_token

# Set up logger
logger = logging.getLogger(__name__)


async def verify_email_token(
    token: str,
) -> Tuple[bool, Optional[uuid.UUID], Optional[str]]:
    """
    Verify an email verification token.

    Args:
        token: JWT verification token

    Returns:
        Tuple containing:
            - Boolean indicating if token is valid
            - User ID from token if valid, None otherwise
            - Email address from token if valid, None otherwise
    """
    # Decode and validate token
    payload = decode_verification_token(token)

    if not payload:
        logger.warning("Invalid or expired email verification token")
        return False, None, None

    try:
        # Extract user_id and email
        user_id = uuid.UUID(payload["sub"])
        email = payload["email"]

        logger.info(f"Email verified for user {user_id}")
        return True, user_id, email

    except (ValueError, KeyError) as e:
        logger.error(f"Error processing verification token: {str(e)}")
        return False, None, None
