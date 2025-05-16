from typing import List, Optional
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.feature import Feature

# Set up logger
logger = logging.getLogger(__name__)


async def get_feature(db: AsyncSession, *, name: str) -> Optional[Feature]:
    """
    Get a feature flag by name.

    Args:
        db: Database session
        name: Feature flag name

    Returns:
        Feature model or None if not found
    """
    stmt = select(Feature).where(Feature.name == name)
    result = await db.execute(stmt)
    feature = result.scalar_one_or_none()

    if feature:
        logger.debug(f"Retrieved feature flag '{name}'")
    else:
        logger.debug(f"Feature flag '{name}' not found")

    return feature


async def get_all_features(db: AsyncSession) -> List[Feature]:
    """
    Get all feature flags.

    Args:
        db: Database session

    Returns:
        List of Feature models
    """
    stmt = select(Feature)
    result = await db.execute(stmt)
    features = result.scalars().all()

    logger.debug(f"Retrieved {len(features)} feature flags")
    return features


async def is_feature_enabled(db: AsyncSession, *, name: str) -> bool:
    """
    Check if a feature flag is enabled.

    Args:
        db: Database session
        name: Feature flag name

    Returns:
        True if feature exists and is enabled, False otherwise
    """
    feature = await get_feature(db, name=name)
    enabled = feature is not None and feature.enabled

    if feature:
        logger.debug(
            f"Feature flag '{name}' is {'enabled' if enabled else 'disabled'}"
        )
    else:
        logger.debug(
            f"Feature flag '{name}' not found, defaulting to disabled"
        )

    return enabled


async def update_feature(
    db: AsyncSession, *, name: str, enabled: bool
) -> Optional[Feature]:
    """
    Update a feature flag.

    Args:
        db: Database session
        name: Feature flag name
        enabled: Whether the feature should be enabled

    Returns:
        Updated Feature model or None if not found
    """
    feature = await get_feature(db, name=name)

    if feature:
        feature.enabled = enabled
        db.add(feature)
        await db.commit()
        await db.refresh(feature)

        logger.info(
            f"Feature flag '{name}' {'enabled' if enabled else 'disabled'}"
        )
    else:
        logger.warning(
            f"Attempted to update non-existent feature flag '{name}'"
        )

    return feature


async def create_feature(
    db: AsyncSession,
    *,
    name: str,
    description: Optional[str] = None,
    enabled: bool = False,
) -> Feature:
    """
    Create a new feature flag.

    Args:
        db: Database session
        name: Feature flag name
        description: Feature flag description
        enabled: Whether the feature should be enabled

    Returns:
        Created Feature model
    """
    # Check if feature already exists
    existing = await get_feature(db, name=name)
    if existing:
        logger.warning(
            f"Feature flag '{name}' already exists, updating instead"
        )
        return await update_feature(db, name=name, enabled=enabled)

    # Create new feature
    feature = Feature(
        name=name,
        description=description,
        enabled=enabled,
    )

    db.add(feature)
    await db.commit()
    await db.refresh(feature)

    logger.info(f"Created new feature flag '{name}' (enabled={enabled})")
    return feature
