from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import DbSession, CurrentStudent
from app.models import User, Assignment, StudentAssignment
from app.schemas.assignment import (
    Assignment as AssignmentSchema,
    StudentAssignment as StudentAssignmentSchema,
    StudentAssignmentCreate,
    StudentAssignmentWithDetails,
)
from app.services import grade_student_assignment
from app.crud import assignment as assignment_crud
from app.crud import user as user_crud


router = APIRouter()


@router.get("/assignments", response_model=List[AssignmentSchema])
async def get_student_available_assignments(
    db: DbSession,
    current_student: CurrentStudent,
    skip: int = 0,
    limit: int = 100,
    include_past_deadline: bool = False,
) -> Any:
    """
    Get all assignments available for the current student.

    Args:
        db: Database session
        current_student: Current authenticated student
        skip: Number of records to skip
        limit: Maximum number of records to return
        include_past_deadline: Whether to include assignments past deadline

    Returns:
        List of assignments
    """
    # Get all assignments from teachers that the student has
    # This can be improved by adding a specific query in the CRUD layer

    # Get all teachers for the student
    teachers = await user_crud.get_student_teachers(
        db, student_id=current_student.id, skip=skip, limit=limit
    )

    # Return empty list if no teachers found
    if not teachers:
        return []

    teacher_ids = [teacher.id for teacher in teachers]

    # If no teacher IDs, return empty list
    if not teacher_ids:
        return []

    # Get all assignments from those teachers
    assignments = []
    for teacher_id in teacher_ids:
        try:
            teacher_assignments = await assignment_crud.get_assignments(
                db,
                teacher_id=teacher_id,
                skip=skip,
                limit=limit,
                include_past_deadline=include_past_deadline,
            )
            assignments.extend(teacher_assignments)
        except Exception as e:
            # Log the error but continue with other teachers
            print(
                f"Error getting assignments for teacher {teacher_id}: {str(e)}"
            )
            continue

    # Filter assignments to exclude those already submitted
    try:
        submitted_assignments_query = await db.execute(
            StudentAssignment.__table__.select()
            .where(StudentAssignment.student_id == current_student.id)
            .with_only_columns([StudentAssignment.assignment_id])
        )
        submitted_assignment_ids = {
            row[0] for row in submitted_assignments_query
        }

        # Remove assignments that student has already submitted
        assignments = [
            a for a in assignments if a.id not in submitted_assignment_ids
        ]
    except Exception as e:
        # Log error but continue with unfiltered assignments
        print(f"Error filtering submitted assignments: {str(e)}")

    # Convert SQLAlchemy objects to dictionaries for serialization
    result = []
    for assignment in assignments:
        # Create a clean dict without SQLAlchemy state attributes
        assignment_dict = {
            key: value
            for key, value in assignment.__dict__.items()
            if not key.startswith("_")
        }
        result.append(assignment_dict)

    return result


@router.get("/assignments/{assignment_id}", response_model=AssignmentSchema)
async def get_student_assignment_by_id(
    assignment_id: int,
    db: DbSession,
    current_student: CurrentStudent,
) -> Any:
    """
    Get a specific assignment by ID for a student.

    Args:
        assignment_id: The ID of the assignment to retrieve
        db: Database session
        current_student: Current authenticated student

    Returns:
        Assignment

    Raises:
        HTTPException: If assignment not found
    """
    # Get assignment from database
    assignment = await assignment_crud.get_assignment(db, assignment_id)

    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found",
        )

    # TODO: Add check to verify student has access to this assignment (optional)

    return assignment


@router.get("/submissions", response_model=List[StudentAssignmentWithDetails])
async def get_student_submissions(
    db: DbSession,
    current_student: CurrentStudent,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Get all submissions from the current student.

    Args:
        db: Database session
        current_student: Current authenticated student
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of student assignment submissions with assignment details
    """
    submissions = await assignment_crud.get_student_assignments(
        db, student_id=current_student.id, skip=skip, limit=limit
    )

    # Format results to match schema
    result = []
    for submission, assignment in submissions:
        # Create a clean dict without SQLAlchemy state attributes
        submission_dict = {
            key: value
            for key, value in submission.__dict__.items()
            if not key.startswith("_")
        }
        # Same for assignment
        assignment_dict = {
            key: value
            for key, value in assignment.__dict__.items()
            if not key.startswith("_")
        }

        submission_dict["assignment"] = assignment_dict
        result.append(submission_dict)

    return result


@router.get(
    "/assignments/{assignment_id}/submission",
    response_model=StudentAssignmentSchema,
)
async def get_student_assignment_submission(
    assignment_id: int,
    db: DbSession,
    current_student: CurrentStudent,
) -> Any:
    """
    Get student's submission for a specific assignment.

    Args:
        assignment_id: Assignment ID
        db: Database session
        current_student: Current authenticated student

    Returns:
        Student's assignment submission

    Raises:
        HTTPException: If submission not found
    """
    # First check if assignment exists
    assignment = await assignment_crud.get_assignment(db, assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found",
        )

    # Get student's submission
    submission = await assignment_crud.get_student_assignment(
        db, assignment_id=assignment_id, student_id=current_student.id
    )

    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No submission found for this assignment",
        )

    return submission


@router.post(
    "/assignments/{assignment_id}/submit",
    response_model=StudentAssignmentSchema,
)
async def submit_assignment_by_id(
    assignment_id: int,
    *,
    db: DbSession,
    current_student: CurrentStudent,
    obj_in: StudentAssignmentCreate,
    background_tasks: BackgroundTasks,
) -> Any:
    """
    Submit a solution for a specific assignment.

    Args:
        assignment_id: ID of the assignment to submit
        db: Database session
        current_student: Current authenticated student
        obj_in: Assignment submission data
        background_tasks: Background tasks

    Returns:
        Created student assignment submission

    Raises:
        HTTPException: If submission fails
    """
    # Verify assignment exists and is not past deadline
    assignment = await assignment_crud.get_assignment(db, assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found",
        )

    if assignment.is_past_deadline:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Assignment is past deadline",
        )

    # Check if student has already submitted
    existing_submission = await assignment_crud.get_student_assignment(
        db, assignment_id=assignment_id, student_id=current_student.id
    )

    if existing_submission:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already submitted this assignment",
        )

    # Create student assignment submission
    student_assignment = await assignment_crud.create_student_assignment(
        db,
        student_id=current_student.id,
        assignment_id=assignment_id,
        submission_text=obj_in.submission_text,
    )

    # If auto-grading is enabled, queue it as a background task
    if assignment.enable_auto_grading:
        background_tasks.add_task(
            grade_student_assignment,
            student_assignment_id=student_assignment.id,
            db=db,
        )

    return student_assignment


@router.get("/gold-coins", response_model=int)
async def get_student_gold_coins(
    db: DbSession,
    current_student: CurrentStudent,
) -> Any:
    """
    Get the number of gold coins for the current student.

    Args:
        db: Database session
        current_student: Current authenticated student

    Returns:
        Number of gold coins
    """
    # In a real implementation, this would fetch from the database
    # Here we're just returning a placeholder value
    return 100  # Placeholder value
