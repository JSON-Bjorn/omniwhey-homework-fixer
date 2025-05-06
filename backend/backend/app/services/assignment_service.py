from typing import Optional
from fastapi import BackgroundTasks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Assignment, StudentAssignment, User
from app.ai.services import ai_service
from app.crud import assignment as assignment_crud
from app.crud import user as user_crud


async def generate_correction_template(
    assignment: Assignment, db: AsyncSession
) -> Assignment:
    """
    Generate correction template for an assignment using AI.

    Args:
        assignment: Assignment object
        db: Database session

    Returns:
        Updated Assignment object with correction template
    """
    if not assignment.assignment_instructions:
        raise ValueError("Assignment instructions are required")

    # Generate correction template using AI
    correction_template = await ai_service.generate_correction_template(
        assignment_instructions=assignment.assignment_instructions,
        max_score=assignment.max_score,
    )

    # Update assignment with correction template
    assignment.correction_template = correction_template
    db.add(assignment)
    await db.commit()
    await db.refresh(assignment)

    return assignment


async def grade_student_assignment(
    student_assignment: StudentAssignment,
    db: AsyncSession,
    background_tasks: Optional[BackgroundTasks] = None,
) -> StudentAssignment:
    """
    Grade a student assignment using AI.

    Args:
        student_assignment: StudentAssignment object
        db: Database session
        background_tasks: Background tasks runner

    Returns:
        Updated StudentAssignment object with score
    """
    if background_tasks:
        # Add to background tasks if provided
        background_tasks.add_task(
            _grade_student_assignment_background,
            student_assignment.id,
            db,
        )
        return student_assignment
    else:
        # Otherwise run immediately
        return await _grade_student_assignment(student_assignment, db)


async def _grade_student_assignment_background(
    student_assignment_id: int, db: AsyncSession
) -> None:
    """
    Background task for grading student assignment.

    Args:
        student_assignment_id: StudentAssignment ID
        db: Database session
    """
    # Get the student assignment
    stmt = select(StudentAssignment).where(
        StudentAssignment.id == student_assignment_id
    )
    result = await db.execute(stmt)
    student_assignment = result.scalar_one_or_none()

    if student_assignment:
        await _grade_student_assignment(student_assignment, db)


async def _grade_student_assignment(
    student_assignment: StudentAssignment, db: AsyncSession
) -> StudentAssignment:
    """
    Internal function for grading student assignment.

    Args:
        student_assignment: StudentAssignment object
        db: Database session

    Returns:
        Updated StudentAssignment object with score
    """
    # Get the assignment
    assignment = await assignment_crud.get_assignment(
        db, student_assignment.assignment_id
    )

    if not assignment:
        raise ValueError("Assignment not found")

    # Use AI to grade the assignment
    score = await ai_service.grade_assignment(
        assignment_instructions=assignment.assignment_instructions,
        student_submission=student_assignment.submission_text,
        max_score=assignment.max_score,
        correction_template=assignment.correction_template,
    )

    # Update the student assignment with the score
    student_assignment.score = score
    db.add(student_assignment)
    await db.commit()
    await db.refresh(student_assignment)

    # Update the student's total gold coins
    student_id = student_assignment.student_id
    total_coins = await assignment_crud.get_student_gold_coins(db, student_id)

    await user_crud.update_gold_coins(
        db, user_id=student_id, gold_coins=total_coins
    )

    return student_assignment
