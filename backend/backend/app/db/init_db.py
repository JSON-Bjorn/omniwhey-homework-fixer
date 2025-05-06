import logging
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import async_session_factory
from app.models import User, UserRole
from app.crud import user as user_crud
from app.schemas.user import UserCreate

logger = logging.getLogger(__name__)


async def init_db() -> None:
    """
    Initialize database with initial data.

    This creates admin users if they don't exist.
    """
    async with async_session_factory() as db:
        await create_first_admin(db)


async def create_first_admin(db: AsyncSession) -> None:
    """
    Create a first admin user if it doesn't exist.

    Args:
        db: Database session
    """
    # Check if admin with default email already exists
    admin_email = "admin@example.com"
    existing_admin = await user_crud.get_user_by_email(db, email=admin_email)

    if existing_admin:
        logger.info("Admin user already exists")
        return

    # Create admin user
    admin_in = UserCreate(
        email=admin_email,
        name="Admin",
        password="adminpassword123",  # This should be changed after first login
        role=UserRole.TEACHER,
    )

    admin = await user_crud.create_user(db, obj_in=admin_in)

    # Mark admin as verified
    admin.is_verified = True
    db.add(admin)
    await db.commit()

    logger.info("Admin user created successfully")
