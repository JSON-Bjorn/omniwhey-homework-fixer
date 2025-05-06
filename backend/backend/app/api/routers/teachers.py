from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import DbSession, CurrentTeacher
from app.models import User, UserRole
from app.schemas.assignment import (
    Assignment as AssignmentSchema,
    AssignmentCreate,
    AssignmentUpdate,
    StudentAssignment as StudentAssignmentSchema,
    StudentAssignmentTeacherUpdate,
)
from app.schemas.user import User as UserSchema, TeacherStudentAdd
from app.services import generate_correction_template
from app.crud import assignment as assignment_crud
from app.crud import user as user_crud


router = APIRouter()


@router.post("/assignments", response_model=AssignmentSchema)
async def create_assignment(
    *,
    db: DbSession,
    current_teacher: CurrentTeacher,
    obj_in: AssignmentCreate,
    background_tasks: BackgroundTasks,
) -> Any:
    """
    Create a new assignment.

    Args:
        db: Database session
        current_teacher: Current authenticated teacher
        obj_in: Assignment creation data
        background_tasks: Background tasks

    Returns:
        Created assignment
    """
    # Create assignment
    assignment = await assignment_crud.create_assignment(
        db, obj_in=obj_in, teacher_id=current_teacher.id
    )

    # Generate correction template in background
    background_tasks.add_task(generate_correction_template, assignment, db)

    return assignment


@router.get("/assignments", response_model=List[AssignmentSchema])
async def get_teacher_assignments(
    db: DbSession,
    current_teacher: CurrentTeacher,
    skip: int = 0,
    limit: int = 100,
    include_past_deadline: bool = True,
) -> Any:
    """
    Get all assignments created by the current teacher.

    Args:
        db: Database session
        current_teacher: Current authenticated teacher
        skip: Number of records to skip
        limit: Maximum number of records to return
        include_past_deadline: Whether to include assignments past deadline

    Returns:
        List of assignments
    """
    assignments = await assignment_crud.get_assignments(
        db,
        teacher_id=current_teacher.id,
        skip=skip,
        limit=limit,
        include_past_deadline=include_past_deadline,
    )
    return assignments


@router.get("/assignments/{assignment_id}", response_model=AssignmentSchema)
async def get_teacher_assignment(
    *,
    db: DbSession,
    current_teacher: CurrentTeacher,
    assignment_id: int,
) -> Any:
    """
    Get a specific assignment created by the current teacher.

    Args:
        db: Database session
        current_teacher: Current authenticated teacher
        assignment_id: Assignment ID

    Returns:
        Assignment

    Raises:
        HTTPException: If assignment not found or does not belong to teacher
    """
    assignment = await assignment_crud.get_assignment(db, assignment_id)

    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found",
        )

    if assignment.teacher_id != current_teacher.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    return assignment


@router.put("/assignments/{assignment_id}", response_model=AssignmentSchema)
async def update_assignment(
    *,
    db: DbSession,
    current_teacher: CurrentTeacher,
    assignment_id: int,
    obj_in: AssignmentUpdate,
    background_tasks: BackgroundTasks,
) -> Any:
    """
    Update an assignment created by the current teacher.

    Args:
        db: Database session
        current_teacher: Current authenticated teacher
        assignment_id: Assignment ID
        obj_in: Assignment update data
        background_tasks: Background tasks

    Returns:
        Updated assignment

    Raises:
        HTTPException: If assignment not found, does not belong to teacher,
                       or cannot be modified
    """
    assignment = await assignment_crud.get_assignment(db, assignment_id)

    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found",
        )

    if assignment.teacher_id != current_teacher.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    # Check if assignment can be modified (no submissions yet)
    if not await assignment_crud.check_can_modify_assignment(
        db, assignment_id
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot modify assignment with existing submissions",
        )

    # Update assignment
    assignment = await assignment_crud.update_assignment(
        db, db_obj=assignment, obj_in=obj_in
    )

    # If assignment instructions were updated, regenerate correction template
    update_data = obj_in.model_dump(exclude_unset=True)
    if "assignment_instructions" in update_data:
        background_tasks.add_task(
            generate_correction_template, assignment, db
        )

    return assignment


@router.delete(
    "/assignments/{assignment_id}", response_model=AssignmentSchema
)
async def delete_assignment(
    *,
    db: DbSession,
    current_teacher: CurrentTeacher,
    assignment_id: int,
) -> Any:
    """
    Delete an assignment created by the current teacher.

    Args:
        db: Database session
        current_teacher: Current authenticated teacher
        assignment_id: Assignment ID

    Returns:
        Deleted assignment

    Raises:
        HTTPException: If assignment not found, does not belong to teacher,
                       or cannot be deleted
    """
    assignment = await assignment_crud.get_assignment(db, assignment_id)

    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found",
        )

    if assignment.teacher_id != current_teacher.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    # Check if assignment can be deleted (no submissions yet)
    if not await assignment_crud.check_can_modify_assignment(
        db, assignment_id
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete assignment with existing submissions",
        )

    # Delete assignment
    assignment = await assignment_crud.delete_assignment(
        db, assignment_id=assignment_id
    )
    return assignment


@router.get(
    "/assignments/{assignment_id}/submissions",
    response_model=List[StudentAssignmentSchema],
)
async def get_assignment_submissions(
    *,
    db: DbSession,
    current_teacher: CurrentTeacher,
    assignment_id: int,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Get all student submissions for a specific assignment.

    Args:
        db: Database session
        current_teacher: Current authenticated teacher
        assignment_id: Assignment ID
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of student assignment submissions

    Raises:
        HTTPException: If assignment not found or does not belong to teacher
    """
    assignment = await assignment_crud.get_assignment(db, assignment_id)

    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found",
        )

    if assignment.teacher_id != current_teacher.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    # Get all submissions for this assignment
    submissions = await assignment_crud.get_assignment_submissions(
        db, assignment_id=assignment_id, skip=skip, limit=limit
    )

    # Format results to match schema
    result = []
    for submission, student in submissions:
        submission_dict = {**submission.__dict__}
        submission_dict["student"] = student
        result.append(submission_dict)

    return result


@router.put(
    "/submissions/{submission_id}", response_model=StudentAssignmentSchema
)
async def update_student_submission(
    *,
    db: DbSession,
    current_teacher: CurrentTeacher,
    submission_id: int,
    obj_in: StudentAssignmentTeacherUpdate,
) -> Any:
    """
    Update a student submission.

    Args:
        db: Database session
        current_teacher: Current authenticated teacher
        submission_id: Student assignment submission ID
        obj_in: Student assignment update data

    Returns:
        Updated student assignment submission

    Raises:
        HTTPException: If submission not found or assignment does not belong to teacher
    """
    # Get the student assignment
    # This could be moved to the CRUD layer
    from sqlalchemy import select, join
    from app.models import StudentAssignment, Assignment

    query = (
        select(StudentAssignment)
        .join(Assignment, Assignment.id == StudentAssignment.assignment_id)
        .where(
            StudentAssignment.id == submission_id,
            Assignment.teacher_id == current_teacher.id,
        )
    )

    result = await db.execute(query)
    student_assignment = result.scalar_one_or_none()

    if not student_assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found or does not belong to your assignments",
        )

    # Update the student assignment
    student_assignment = (
        await assignment_crud.teacher_update_student_assignment(
            db, db_obj=student_assignment, obj_in=obj_in
        )
    )

    # If score was updated, update student's total gold coins
    update_data = obj_in.model_dump(exclude_unset=True)
    if "score" in update_data:
        student_id = student_assignment.student_id
        total_coins = await assignment_crud.get_student_gold_coins(
            db, student_id
        )
        await user_crud.update_gold_coins(
            db, user_id=student_id, gold_coins=total_coins
        )

    return student_assignment


@router.get("/students", response_model=List[UserSchema])
async def get_teacher_students(
    db: DbSession,
    current_teacher: CurrentTeacher,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Get all students associated with the current teacher.

    Args:
        db: Database session
        current_teacher: Current authenticated teacher
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of student users
    """
    students = await user_crud.get_teacher_students(
        db, teacher_id=current_teacher.id, skip=skip, limit=limit
    )
    return students


@router.post("/students/add", response_model=List[UserSchema])
async def add_students_to_teacher(
    *,
    db: DbSession,
    current_teacher: CurrentTeacher,
    obj_in: TeacherStudentAdd,
) -> Any:
    """
    Add students to teacher's class.

    Args:
        db: Database session
        current_teacher: Current authenticated teacher
        obj_in: Student IDs to add

    Returns:
        List of added student users
    """
    added_students = []

    for student_id in obj_in.student_ids:
        # Verify student exists and is actually a student
        student = await user_crud.get_user(db, user_id=student_id)
        if not student or not student.is_student():
            continue

        # Add student to teacher's class
        association = await user_crud.add_student_to_teacher(
            db, teacher_id=current_teacher.id, student_id=student_id
        )

        if association:
            added_students.append(student)

    return added_students


@router.delete("/students/{student_id}", response_model=dict)
async def remove_student_from_teacher(
    *,
    db: DbSession,
    current_teacher: CurrentTeacher,
    student_id: int,
) -> Any:
    """
    Remove a student from teacher's class.

    Args:
        db: Database session
        current_teacher: Current authenticated teacher
        student_id: Student ID to remove

    Returns:
        Success message
    """
    # Verify student exists
    student = await user_crud.get_user(db, user_id=student_id)

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )

    # Remove student from teacher's class
    success = await user_crud.remove_student_from_teacher(
        db, teacher_id=current_teacher.id, student_id=student_id
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student not found in your class",
        )

    return {"message": "Student removed successfully"}
