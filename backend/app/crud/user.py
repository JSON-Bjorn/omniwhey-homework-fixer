from typing import Any, Dict, Optional, List, Union, Sequence
import uuid
import logging
from sqlalchemy import (
    select,
    update,
    delete,
    and_,
    insert,
    Table,
    func,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import get_password_hash, verify_password
from app.models import User, UserRole, teacher_student_association
from app.schemas.user import UserCreate, UserUpdate
from app.utils.secure_logging import censor_email, censor_uuid, censor_name

# Set up logger
logger = logging.getLogger(__name__)


async def get_user(db: AsyncSession, user_id: uuid.UUID) -> Optional[User]:
    """
    Get a user by ID.

    Args:
        db: Database session
        user_id: ID of the user to get

    Returns:
        User model or None if not found
    """
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user:
        logger.debug(f"Retrieved user with ID: {censor_uuid(user_id)}")
    else:
        logger.debug(f"User not found with ID: {censor_uuid(user_id)}")

    return user


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """
    Get a user by email.

    Args:
        db: Database session
        email: User email

    Returns:
        User object or None if not found
    """
    stmt = select(User).where(func.lower(User.email) == func.lower(email))
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user:
        logger.debug(f"Retrieved user with email: {censor_email(email)}")
    else:
        logger.debug(f"User not found with email: {censor_email(email)}")

    return user


async def get_users(
    db: AsyncSession,
    *,
    skip: int = 0,
    limit: int = 100,
    role: Optional[UserRole] = None,
) -> Sequence[User]:
    """
    Get multiple users with filtering options.

    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        role: Filter by user role

    Returns:
        List of User objects
    """
    stmt = select(User).offset(skip).limit(limit)

    if role:
        stmt = stmt.where(User.role == role)

    result = await db.execute(stmt)
    users = result.scalars().all()

    logger.info(
        f"Retrieved {len(users)} users with skip={skip}, limit={limit}"
    )
    return users


async def create_user(db: AsyncSession, *, obj_in: UserCreate) -> User:
    """
    Create a new user.

    Args:
        db: Database session
        obj_in: User creation data

    Returns:
        Created User object
    """
    logger.info(f"Creating new user with email: {censor_email(obj_in.email)}")

    db_obj = User(
        email=obj_in.email,
        name=obj_in.name,
        hashed_password=get_password_hash(obj_in.password),
        role=obj_in.role,
        is_active=False,  # Default to inactive until email is verified
        is_verified=False,  # Email verification will be required
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)

    logger.info(
        f"User created successfully: ID={censor_uuid(db_obj.id)}, name={censor_name(db_obj.name)}"
    )
    return db_obj


async def update_user(
    db: AsyncSession,
    *,
    db_obj: User,
    obj_in: Union[UserUpdate, Dict[str, Any]],
) -> User:
    """
    Update a user.

    Args:
        db: Database session
        db_obj: User object to update
        obj_in: User update data

    Returns:
        Updated User object
    """
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.model_dump(exclude_unset=True)

    # Log the update operation with censored data
    log_data = {}
    for key, value in update_data.items():
        if key == "email":
            log_data[key] = censor_email(value)
        elif key == "name":
            log_data[key] = censor_name(value)
        elif key == "password":
            log_data[key] = "********"
        else:
            log_data[key] = value

    logger.info(
        f"Updating user ID={censor_uuid(db_obj.id)} with attributes: {log_data}"
    )

    if update_data.get("password"):
        hashed_password = get_password_hash(update_data["password"])
        del update_data["password"]
        update_data["hashed_password"] = hashed_password

    for field, value in update_data.items():
        setattr(db_obj, field, value)

    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)

    logger.info(f"User ID={censor_uuid(db_obj.id)} updated successfully")
    return db_obj


async def delete_user(
    db: AsyncSession, *, user_id: uuid.UUID
) -> Optional[User]:
    """
    Delete a user.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        Deleted User object or None if not found
    """
    logger.info(f"Deleting user with ID: {censor_uuid(user_id)}")

    user = await get_user(db, user_id)
    if user:
        await db.delete(user)
        await db.commit()

    logger.info(f"User ID={censor_uuid(user_id)} deleted successfully")
    return user


async def authenticate_user(
    db: AsyncSession, *, email: str, password: str
) -> Optional[User]:
    """
    Authenticate a user with email and password.

    Args:
        db: Database session
        email: User email
        password: User password

    Returns:
        Authenticated User object or None if authentication fails
    """
    logger.debug(f"Authenticating user with email: {censor_email(email)}")

    user = await get_user_by_email(db, email=email)
    if not user:
        logger.warning(
            f"Authentication failed: User not found with email: {censor_email(email)}"
        )
        return None
    if not verify_password(password, user.hashed_password):
        logger.warning(
            f"Authentication failed: Invalid password for user ID: {censor_uuid(user.id)}"
        )
        return None

    logger.info(f"User {censor_uuid(user.id)} authenticated successfully")
    return user


async def verify_user_email(
    db: AsyncSession, *, user_id: uuid.UUID
) -> Optional[User]:
    """
    Mark a user's email as verified and activate their account.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        Updated User object or None if not found
    """
    user = await get_user(db, user_id)
    if user:
        user.is_verified = True
        user.is_active = True
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return user


async def update_gold_coins(
    db: AsyncSession, *, user_id: uuid.UUID, gold_coins: int
) -> Optional[User]:
    """
    Update a student's gold coins.

    Args:
        db: Database session
        user_id: User ID
        gold_coins: New gold coins value

    Returns:
        Updated User object or None if not found
    """
    user = await get_user(db, user_id)
    if user and user.role == UserRole.STUDENT:
        user.total_gold_coins = gold_coins
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return user


async def add_student_to_teacher(
    db: AsyncSession, *, teacher_id: uuid.UUID, student_id: uuid.UUID
) -> bool:
    """
    Add a student to a teacher's class.

    Args:
        db: Database session
        teacher_id: Teacher user ID
        student_id: Student user ID

    Returns:
        True if successful, False otherwise
    """
    # Check if the association already exists
    stmt = select(teacher_student_association).where(
        and_(
            teacher_student_association.c.teacher_id == teacher_id,
            teacher_student_association.c.student_id == student_id,
        )
    )
    result = await db.execute(stmt)
    if result.first() is not None:
        return False  # Association already exists

    # Add the association
    stmt = insert(teacher_student_association).values(
        teacher_id=teacher_id, student_id=student_id
    )
    await db.execute(stmt)
    await db.commit()
    return True


async def remove_student_from_teacher(
    db: AsyncSession, *, teacher_id: uuid.UUID, student_id: uuid.UUID
) -> bool:
    """
    Remove a student from a teacher's class.

    Args:
        db: Database session
        teacher_id: Teacher user ID
        student_id: Student user ID

    Returns:
        True if the relation was deleted, False if not found
    """
    query = delete(teacher_student_association).where(
        teacher_student_association.c.teacher_id == teacher_id,
        teacher_student_association.c.student_id == student_id,
    )
    result = await db.execute(query)
    await db.commit()
    return result.rowcount > 0


async def get_teacher_students(
    db: AsyncSession,
    *,
    teacher_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
) -> Sequence[User]:
    """
    Get all students for a teacher.

    Args:
        db: Database session
        teacher_id: Teacher user ID
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of User objects (students)
    """
    # Use a join to get all students associated with the teacher
    stmt = (
        select(User)
        .join(
            teacher_student_association,
            User.id == teacher_student_association.c.student_id,
        )
        .where(teacher_student_association.c.teacher_id == teacher_id)
        .where(User.role == UserRole.STUDENT)
        .offset(skip)
        .limit(limit)
    )

    result = await db.execute(stmt)
    return result.scalars().all()


async def get_student_teachers(
    db: AsyncSession,
    *,
    student_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
) -> Sequence[User]:
    """
    Get all teachers for a student.

    Args:
        db: Database session
        student_id: Student user ID
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of User objects (teachers)
    """
    # Use a join to get all teachers associated with the student
    stmt = (
        select(User)
        .join(
            teacher_student_association,
            User.id == teacher_student_association.c.teacher_id,
        )
        .where(teacher_student_association.c.student_id == student_id)
        .where(User.role == UserRole.TEACHER)
        .offset(skip)
        .limit(limit)
    )

    result = await db.execute(stmt)
    return result.scalars().all()
