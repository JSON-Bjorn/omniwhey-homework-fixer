from datetime import datetime, timedelta, timezone
import logging
import uuid
import secrets
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.token import Token
from app.core.config import settings
from app.utils.secure_logging import censor_uuid, censor_token

# Set up logger
logger = logging.getLogger(__name__)


async def create_token(
    db: AsyncSession, user_id: uuid.UUID, token_type: str = "access"
) -> Token:
    """
    Create a new authentication token for a user.

    Args:
        db: Database session
        user_id: ID of the user to create token for
        token_type: Type of token (default: "access")

    Returns:
        Token object
    """
    # Generate a random token using secrets
    token_value = secrets.token_urlsafe(32)

    # Set expiration time
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    expires_at = datetime.now(timezone.utc) + expires_delta

    # Create token object
    db_token = Token(
        token=token_value,
        user_id=user_id,
        expires_at=expires_at,
        is_revoked=False,
        token_type=token_type,
    )

    # Log token creation (without exposing the actual token or user_id)
    logger.info(
        f"Creating {token_type} token for user {censor_uuid(user_id)} with expiration: {expires_at}"
    )

    # Save to database
    db.add(db_token)
    await db.commit()
    await db.refresh(db_token)

    # Log successful token creation
    logger.info(
        f"{token_type.capitalize()} token created successfully with ID: {censor_uuid(db_token.id)}"
    )

    return db_token


async def get_token_by_token_string(
    db: AsyncSession, token: str
) -> Optional[Token]:
    """
    Get token by token string.

    Args:
        db: Database session
        token: Token string to look up

    Returns:
        Token object if found, None otherwise
    """
    stmt = select(Token).where(Token.token == token)
    result = await db.execute(stmt)
    token_obj = result.scalar_one_or_none()

    if token_obj:
        logger.debug(
            f"{token_obj.token_type.capitalize()} token found: ID {censor_uuid(token_obj.id)}"
        )
    else:
        logger.debug(f"Token lookup failed: token not found")

    return token_obj


async def validate_token(
    db: AsyncSession, token: str, token_type: str = None
) -> Optional[Token]:
    """
    Validate a token by checking if it exists, is not revoked, and has not expired.

    Args:
        db: Database session
        token: Token string to validate
        token_type: Optional token type to check against

    Returns:
        Token object if valid, None otherwise
    """
    db_token = await get_token_by_token_string(db, token)

    if not db_token:
        logger.warning("Token validation failed: Token not found")
        return None

    # Check if token type matches
    if token_type and db_token.token_type != token_type:
        logger.warning(
            f"Token validation failed: Token (ID: {censor_uuid(db_token.id)}) has type '{db_token.token_type}' but '{token_type}' was expected"
        )
        return None

    # Check if token is revoked
    if db_token.is_revoked:
        logger.warning(
            f"Token validation failed: {db_token.token_type.capitalize()} token (ID: {censor_uuid(db_token.id)}) is revoked for user {censor_uuid(db_token.user_id)}"
        )
        return None

    # Check if token is expired - make current time timezone-aware to match token's timezone
    current_time = datetime.now(timezone.utc)
    if db_token.expires_at < current_time:
        logger.warning(
            f"Token validation failed: {db_token.token_type.capitalize()} token (ID: {censor_uuid(db_token.id)}) expired at {db_token.expires_at} for user {censor_uuid(db_token.user_id)}"
        )
        return None

    # Token is valid
    logger.debug(
        f"{db_token.token_type.capitalize()} token (ID: {censor_uuid(db_token.id)}) validated successfully for user {censor_uuid(db_token.user_id)}"
    )
    return db_token


async def revoke_token(db: AsyncSession, token: str) -> bool:
    """
    Revoke a token by setting its is_revoked flag to True.

    Args:
        db: Database session
        token: Token string to revoke

    Returns:
        True if token was found and revoked, False otherwise
    """
    db_token = await get_token_by_token_string(db, token)

    if not db_token:
        logger.warning(f"Cannot revoke token: Token not found")
        return False

    # Log revocation attempt before it happens
    logger.info(
        f"Revoking token (ID: {censor_uuid(db_token.id)}) for user {censor_uuid(db_token.user_id)}"
    )

    # Revoke token
    db_token.is_revoked = True
    await db.commit()

    logger.info(
        f"Token (ID: {censor_uuid(db_token.id)}) successfully revoked"
    )
    return True


async def revoke_all_user_tokens(db: AsyncSession, user_id: uuid.UUID) -> int:
    """
    Revoke all tokens for a specific user.

    Args:
        db: Database session
        user_id: User ID whose tokens should be revoked

    Returns:
        Number of tokens revoked
    """
    # Log the operation attempt with censored user ID
    logger.info(
        f"Attempting to revoke all tokens for user {censor_uuid(user_id)}"
    )

    # Find all active tokens for the user
    current_time = datetime.now(timezone.utc)
    stmt = select(Token).where(
        Token.user_id == user_id,
        Token.is_revoked == False,
        Token.expires_at > current_time,
    )

    result = await db.execute(stmt)
    tokens = result.scalars().all()

    if not tokens:
        logger.info(f"No active tokens found for user {censor_uuid(user_id)}")
        return 0

    # Log individual token revocations
    for token in tokens:
        logger.debug(
            f"Revoking token (ID: {censor_uuid(token.id)}) for user {censor_uuid(user_id)}"
        )
        token.is_revoked = True

    await db.commit()

    logger.info(
        f"Successfully revoked {len(tokens)} tokens for user {censor_uuid(user_id)}"
    )
    return len(tokens)


async def clean_expired_tokens(db: AsyncSession) -> int:
    """
    Clean up expired tokens from the database.

    This is a maintenance function that can be run periodically.

    Args:
        db: Database session

    Returns:
        Number of tokens deleted
    """
    logger.info("Starting expired token cleanup")

    # Find all expired tokens
    current_time = datetime.now(timezone.utc)
    stmt = select(Token).where(Token.expires_at < current_time)
    result = await db.execute(stmt)
    expired_tokens = result.scalars().all()

    if not expired_tokens:
        logger.info("No expired tokens to clean up")
        return 0

    # Count by user for logging
    user_counts = {}
    for token in expired_tokens:
        user_id_str = str(token.user_id)
        if user_id_str in user_counts:
            user_counts[user_id_str] += 1
        else:
            user_counts[user_id_str] = 1

        # Delete the token
        await db.delete(token)

    await db.commit()

    # Log cleanup statistics with censored user IDs
    for user_id, count in user_counts.items():
        logger.debug(
            f"Cleaned {count} expired tokens for user {censor_uuid(user_id)}"
        )

    logger.info(
        f"Successfully cleaned up {len(expired_tokens)} expired tokens"
    )
    return len(expired_tokens)
