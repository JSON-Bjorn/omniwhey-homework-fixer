from typing import Any, Dict, List, Optional, Union, Tuple
from datetime import datetime
from sqlalchemy import select, func, and_, or_, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Assignment, StudentAssignment, User, UserRole
from app.crud import user as user_crud
from app.schemas.assignment import AssignmentCreate, AssignmentUpdate
from app.schemas.assignment import (
    StudentAssignmentCreate,
    StudentAssignmentTeacherUpdate,
)


async def get_assignment(
    db: AsyncSession, assignment_id: int
) -> Optional[Assignment]:
    """
    Get an assignment by ID.

    Args:
        db: Database session
        assignment_id: Assignment ID

    Returns:
        Assignment object or None if not found
    """
    result = await db.execute(
        select(Assignment).where(Assignment.id == assignment_id)
    )
    return result.scalar_one_or_none()


async def get_assignments(
    db: AsyncSession,
    *,
    skip: int = 0,
    limit: int = 100,
    teacher_id: Optional[int] = None,
    include_past_deadline: bool = True,
) -> List[Assignment]:
    """
    Get multiple assignments with filtering options.

    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        teacher_id: Filter by teacher ID
        include_past_deadline: Whether to include assignments past deadline

    Returns:
        List of Assignment objects
    """
    query = select(Assignment).offset(skip).limit(limit)

    if teacher_id:
        query = query.where(Assignment.teacher_id == teacher_id)

    if not include_past_deadline:
        query = query.where(Assignment.deadline >= datetime.now())

    query = query.order_by(Assignment.deadline)

    result = await db.execute(query)
    return result.scalars().all()


async def create_assignment(
    db: AsyncSession, *, obj_in: AssignmentCreate, teacher_id: int
) -> Assignment:
    """
    Create a new assignment.

    Args:
        db: Database session
        obj_in: Assignment creation data
        teacher_id: Teacher user ID

    Returns:
        Created Assignment object
    """
    db_obj = Assignment(
        title=obj_in.title,
        assignment_instructions=obj_in.assignment_instructions,
        max_score=obj_in.max_score,
        deadline=obj_in.deadline,
        teacher_id=teacher_id,
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def update_assignment(
    db: AsyncSession,
    *,
    db_obj: Assignment,
    obj_in: Union[AssignmentUpdate, Dict[str, Any]],
) -> Assignment:
    """
    Update an assignment.

    Args:
        db: Database session
        db_obj: Assignment object to update
        obj_in: Assignment update data

    Returns:
        Updated Assignment object
    """
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.model_dump(exclude_unset=True)

    for field in update_data:
        setattr(db_obj, field, update_data[field])

    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def delete_assignment(
    db: AsyncSession, *, assignment_id: int
) -> Optional[Assignment]:
    """
    Delete an assignment.

    Args:
        db: Database session
        assignment_id: Assignment ID

    Returns:
        Deleted Assignment object or None if not found
    """
    assignment = await get_assignment(db, assignment_id)
    if assignment:
        await db.delete(assignment)
        await db.commit()
    return assignment


async def check_can_modify_assignment(
    db: AsyncSession, assignment_id: int
) -> bool:
    """
    Check if an assignment can be modified.

    An assignment can be modified only if no student has submitted a solution yet.

    Args:
        db: Database session
        assignment_id: Assignment ID

    Returns:
        True if assignment can be modified, False otherwise
    """
    # Check if any student submissions exist
    query = select(func.count()).where(
        StudentAssignment.assignment_id == assignment_id
    )
    result = await db.execute(query)
    count = result.scalar_one()
    return count == 0


async def get_student_assignment(
    db: AsyncSession, assignment_id: int, student_id: int
) -> Optional[StudentAssignment]:
    """
    Get a student's assignment submission.

    Args:
        db: Database session
        assignment_id: Assignment ID
        student_id: Student user ID

    Returns:
        StudentAssignment object or None if not found
    """
    query = select(StudentAssignment).where(
        StudentAssignment.assignment_id == assignment_id,
        StudentAssignment.student_id == student_id,
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_student_assignments(
    db: AsyncSession,
    *,
    student_id: int,
    skip: int = 0,
    limit: int = 100,
    include_past_deadline: bool = True,
) -> List[Tuple[StudentAssignment, Assignment]]:
    """
    Get all assignment submissions for a student.

    Args:
        db: Database session
        student_id: Student user ID
        skip: Number of records to skip
        limit: Maximum number of records to return
        include_past_deadline: Whether to include assignments past deadline

    Returns:
        List of tuples (StudentAssignment, Assignment)
    """
    query = (
        select(StudentAssignment, Assignment)
        .join(Assignment, StudentAssignment.assignment_id == Assignment.id)
        .where(StudentAssignment.student_id == student_id)
        .offset(skip)
        .limit(limit)
    )

    if not include_past_deadline:
        query = query.where(Assignment.deadline >= datetime.now())

    query = query.order_by(Assignment.deadline)

    result = await db.execute(query)
    return result.all()


async def get_assignment_submissions(
    db: AsyncSession, *, assignment_id: int, skip: int = 0, limit: int = 100
) -> List[Tuple[StudentAssignment, User]]:
    """
    Get all student submissions for an assignment.

    Args:
        db: Database session
        assignment_id: Assignment ID
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of tuples (StudentAssignment, User)
    """
    query = (
        select(StudentAssignment, User)
        .join(User, StudentAssignment.student_id == User.id)
        .where(StudentAssignment.assignment_id == assignment_id)
        .offset(skip)
        .limit(limit)
    )

    result = await db.execute(query)
    return result.all()


async def create_student_assignment(
    db: AsyncSession, *, obj_in: StudentAssignmentCreate, student_id: int
) -> StudentAssignment:
    """
    Create a new student assignment submission.

    Args:
        db: Database session
        obj_in: StudentAssignment creation data
        student_id: Student user ID

    Returns:
        Created StudentAssignment object
    """
    # Check if student has already submitted an assignment
    existing = await get_student_assignment(
        db, obj_in.assignment_id, student_id
    )
    if existing:
        raise ValueError("Student has already submitted this assignment")

    # Check if assignment is past deadline
    assignment = await get_assignment(db, obj_in.assignment_id)
    if not assignment:
        raise ValueError("Assignment not found")

    if assignment.is_past_deadline:
        raise ValueError("Assignment is past deadline")

    db_obj = StudentAssignment(
        student_id=student_id,
        assignment_id=obj_in.assignment_id,
        submission_text=obj_in.submission_text,
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def teacher_update_student_assignment(
    db: AsyncSession,
    *,
    db_obj: StudentAssignment,
    obj_in: StudentAssignmentTeacherUpdate,
) -> StudentAssignment:
    """
    Teacher update of a student assignment.

    Args:
        db: Database session
        db_obj: StudentAssignment object to update
        obj_in: StudentAssignment update data

    Returns:
        Updated StudentAssignment object
    """
    update_data = obj_in.model_dump(exclude_unset=True)

    for field in update_data:
        setattr(db_obj, field, update_data[field])

    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def get_student_gold_coins(db: AsyncSession, student_id: int) -> int:
    """
    Calculate total gold coins for a student from all assignments.

    Args:
        db: Database session
        student_id: Student user ID

    Returns:
        Total gold coins
    """
    query = select(func.sum(StudentAssignment.score)).where(
        StudentAssignment.student_id == student_id,
        StudentAssignment.score.isnot(None),
    )

    result = await db.execute(query)
    total = result.scalar_one_or_none()
    return total or 0


async def update_student_assignment_score(
    db: AsyncSession, *, student_assignment_id: int, score: int
) -> Optional[StudentAssignment]:
    """
    Update the score of a student assignment submission.

    Args:
        db: Database session
        student_assignment_id: StudentAssignment ID
        score: New score

    Returns:
        Updated StudentAssignment object or None if not found
    """
    stmt = select(StudentAssignment).where(
        StudentAssignment.id == student_assignment_id
    )
    result = await db.execute(stmt)
    student_assignment = result.scalar_one_or_none()

    if student_assignment:
        student_assignment.score = score
        db.add(student_assignment)
        await db.commit()
        await db.refresh(student_assignment)

    return student_assignment
