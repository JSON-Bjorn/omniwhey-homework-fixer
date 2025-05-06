from typing import Any, Dict, Optional, List, Union
from sqlalchemy import (
    select,
    update,
    delete,
    and_,
    insert,
    join,
    table,
    column,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select
from sqlalchemy.orm import selectinload

from app.core.security import get_password_hash, verify_password
from app.models import User, UserRole
from app.schemas.user import UserCreate, UserUpdate

# Define the association table structure for queries
teacher_student_assoc = table(
    "teacher_student_associations",
    column("teacher_id"),
    column("student_id"),
    column("created_at"),
    column("updated_at"),
)


async def get_user(db: AsyncSession, user_id: int) -> Optional[User]:
    """
    Get a user by ID.

    Args:
        db: Database session
        user_id: ID of the user to get

    Returns:
        User model or None if not found
    """
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """
    Get a user by email.

    Args:
        db: Database session
        email: User email

    Returns:
        User object or None if not found
    """
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_users(
    db: AsyncSession,
    *,
    skip: int = 0,
    limit: int = 100,
    role: Optional[UserRole] = None,
) -> List[User]:
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
    query = select(User).offset(skip).limit(limit)

    if role:
        query = query.where(User.role == role)

    result = await db.execute(query)
    return result.scalars().all()


async def create_user(db: AsyncSession, *, obj_in: UserCreate) -> User:
    """
    Create a new user.

    Args:
        db: Database session
        obj_in: User creation data

    Returns:
        Created User object
    """
    db_obj = User(
        email=obj_in.email,
        name=obj_in.name,
        hashed_password=get_password_hash(obj_in.password),
        role=obj_in.role,
        is_active=True,
        is_verified=False,  # Email verification will be required
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
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

    if update_data.get("password"):
        hashed_password = get_password_hash(update_data["password"])
        del update_data["password"]
        update_data["hashed_password"] = hashed_password

    for field, value in update_data.items():
        setattr(db_obj, field, value)

    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def delete_user(db: AsyncSession, *, user_id: int) -> Optional[User]:
    """
    Delete a user.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        Deleted User object or None if not found
    """
    user = await get_user(db, user_id)
    if user:
        await db.delete(user)
        await db.commit()
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
    user = await get_user_by_email(db, email=email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def verify_user_email(
    db: AsyncSession, *, user_id: int
) -> Optional[User]:
    """
    Mark a user's email as verified.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        Updated User object or None if not found
    """
    user = await get_user(db, user_id)
    if user:
        user.is_verified = True
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return user


async def update_gold_coins(
    db: AsyncSession, *, user_id: int, gold_coins: int
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
    db: AsyncSession, *, teacher_id: int, student_id: int
) -> bool:
    """
    Add a student to a teacher's class.

    Args:
        db: Database session
        teacher_id: Teacher user ID
        student_id: Student user ID

    Returns:
        True if the student was added, False otherwise
    """
    teacher = await get_user(db, teacher_id)
    student = await get_user(db, student_id)

    if not teacher or not student:
        return False

    if teacher.role != UserRole.TEACHER or student.role != UserRole.STUDENT:
        return False

    # Check if the relation already exists
    query = select(teacher_student_assoc).where(
        teacher_student_assoc.c.teacher_id == teacher_id,
        teacher_student_assoc.c.student_id == student_id,
    )
    result = await db.execute(query)
    existing_relation = result.scalar_one_or_none()

    if existing_relation:
        return True  # Relation already exists

    # Add the relation
    stmt = insert(teacher_student_assoc).values(
        teacher_id=teacher_id, student_id=student_id
    )
    await db.execute(stmt)
    await db.commit()

    return True


async def remove_student_from_teacher(
    db: AsyncSession, *, teacher_id: int, student_id: int
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
    query = delete(teacher_student_assoc).where(
        teacher_student_assoc.c.teacher_id == teacher_id,
        teacher_student_assoc.c.student_id == student_id,
    )
    result = await db.execute(query)
    await db.commit()
    return result.rowcount > 0


async def get_teacher_students(
    db: AsyncSession, *, teacher_id: int, skip: int = 0, limit: int = 100
) -> List[User]:
    """
    Get all students associated with a teacher.

    Args:
        db: Database session
        teacher_id: Teacher user ID
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of Student User objects
    """
    query = (
        select(User)
        .join(
            teacher_student_assoc,
            teacher_student_assoc.c.student_id == User.id,
        )
        .where(
            teacher_student_assoc.c.teacher_id == teacher_id,
            User.role == UserRole.STUDENT,
            User.is_active == True,
        )
        .offset(skip)
        .limit(limit)
    )

    result = await db.execute(query)
    return result.scalars().all()


async def get_student_teachers(
    db: AsyncSession, *, student_id: int, skip: int = 0, limit: int = 100
) -> List[User]:
    """
    Get all teachers associated with a student.

    Args:
        db: Database session
        student_id: Student user ID
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of Teacher User objects
    """
    query = (
        select(User)
        .join(
            teacher_student_assoc,
            teacher_student_assoc.c.teacher_id == User.id,
        )
        .where(
            teacher_student_assoc.c.student_id == student_id,
            User.role == UserRole.TEACHER,
            User.is_active == True,
        )
        .offset(skip)
        .limit(limit)
    )

    result = await db.execute(query)
    return result.scalars().all()
