from typing import Optional, Tuple
from fastapi import BackgroundTasks, HTTPException, status
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Assignment, StudentAssignment, User
from app.ai.services import ai_service
from app.crud import assignment as assignment_crud
from app.crud import user as user_crud

# Set up logger
logger = logging.getLogger(__name__)


async def generate_template_for_approval(
    assignment_id: int, db: AsyncSession
) -> Tuple[Assignment, str]:
    """
    Generate a correction template for teacher approval.

    Args:
        assignment_id: Assignment ID
        db: Database session

    Returns:
        Tuple of (Assignment object, generated template)

    Raises:
        HTTPException: If assignment not found
    """
    # Get assignment from database
    assignment = await assignment_crud.get_assignment(db, assignment_id)
    if not assignment:
        logger.error(f"Assignment not found for ID: {assignment_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found",
        )

    # Check if the assignment already has a correction template
    if assignment.correction_template:
        logger.warning(
            f"Assignment ID {assignment_id} already has a correction template"
        )
        # Return existing template for editing
        return assignment, assignment.correction_template

    if not assignment.assignment_instructions:
        logger.error(f"Assignment ID {assignment_id} has no instructions")
        raise ValueError("Assignment instructions are required")

    try:
        # Generate correction template using AI
        correction_template = await ai_service.generate_correction_template(
            assignment_instructions=assignment.assignment_instructions,
            max_score=assignment.max_score,
        )

        logger.info(
            f"Successfully generated template for assignment ID {assignment_id}"
        )
        return assignment, correction_template

    except Exception as e:
        logger.error(
            f"Error generating template for assignment ID {assignment_id}: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate correction template. Please try again later.",
        )


async def approve_correction_template(
    assignment_id: int, correction_template: str, db: AsyncSession
) -> Assignment:
    """
    Save an approved correction template to an assignment.

    Args:
        assignment_id: Assignment ID
        correction_template: The approved correction template
        db: Database session

    Returns:
        Updated Assignment object

    Raises:
        HTTPException: If assignment not found or cannot be modified
    """
    # Get assignment from database
    assignment = await assignment_crud.get_assignment(db, assignment_id)
    if not assignment:
        logger.error(f"Assignment not found for ID: {assignment_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found",
        )

    # Check if assignment can be modified (no submissions yet)
    if not await assignment_crud.check_can_modify_assignment(
        db, assignment_id
    ):
        logger.warning(
            f"Cannot modify template for assignment ID {assignment_id} with existing submissions"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot modify template for assignment with existing submissions",
        )

    try:
        # Update assignment with the approved template
        update_data = {"correction_template": correction_template}
        updated_assignment = await assignment_crud.update_assignment(
            db, db_obj=assignment, obj_in=update_data
        )

        logger.info(
            f"Correction template approved and saved for assignment ID {assignment_id}"
        )
        return updated_assignment

    except Exception as e:
        logger.error(
            f"Error saving template for assignment ID {assignment_id}: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save correction template.",
        )


async def generate_correction_template(
    assignment: Assignment, db: AsyncSession
) -> Assignment:
    """
    Generate correction template for an assignment using AI and save it directly.
    This is a legacy function that will be used for backward compatibility.

    Args:
        assignment: Assignment object
        db: Database session

    Returns:
        Updated Assignment object with correction template
    """
    if not assignment.assignment_instructions:
        logger.error(f"Assignment ID {assignment.id} has no instructions")
        raise ValueError("Assignment instructions are required")

    try:
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

        logger.info(
            f"Correction template generated and saved for assignment ID {assignment.id}"
        )
        return assignment

    except Exception as e:
        logger.error(
            f"Error generating template for assignment ID {assignment.id}: {str(e)}"
        )
        # We don't raise an exception here to avoid breaking background tasks
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
    else:
        logger.error(
            f"Student assignment not found for ID: {student_assignment_id}"
        )


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
        logger.error(
            f"Assignment not found for ID: {student_assignment.assignment_id}"
        )
        raise ValueError("Assignment not found")

    try:
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
        total_coins = await assignment_crud.get_student_gold_coins(
            db, student_id
        )

        await user_crud.update_gold_coins(
            db, user_id=student_id, gold_coins=total_coins
        )

        logger.info(
            f"Assignment ID {student_assignment.assignment_id} graded for student ID {student_assignment.student_id} with score {score}"
        )
        return student_assignment

    except Exception as e:
        logger.error(
            f"Error grading assignment ID {student_assignment.assignment_id} for student ID {student_assignment.student_id}: {str(e)}"
        )
        raise
