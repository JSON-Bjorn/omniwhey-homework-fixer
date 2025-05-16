import logging
from typing import Any, List, Optional
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    BackgroundTasks,
    status,
    Body,
)
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from datetime import datetime, timezone

from app.core.deps import get_current_teacher, get_current_student
from app.models import User, UserRole
from app.schemas.user import User as UserSchema, TeacherStudentAdd
from app.schemas.assignment import (
    Assignment as AssignmentSchema,
    AssignmentCreate,
    AssignmentUpdate,
    AssignmentDeadlineExtend,
    StudentAssignment as StudentAssignmentSchema,
    StudentAssignmentTeacherUpdate,
    StudentAssignmentWithGrading,
    StudentAssignmentCreate,
)
from app.services import (
    generate_correction_template,
    generate_template_for_approval,
    approve_correction_template,
)
from app.crud import assignment as assignment_crud
from app.crud import user as user_crud
from app.core import deps
from app.db.session import get_db

# Set up logger
logger = logging.getLogger(__name__)

router = APIRouter()

# Type aliases for cleaner function signatures
AsyncDbSession = AsyncSession
CurrentTeacher = User
CurrentStudent = User


@router.post("/assignments", response_model=AssignmentSchema)
async def create_assignment(
    *,
    db: AsyncDbSession,
    current_teacher: CurrentTeacher,
    obj_in: AssignmentCreate,
) -> Any:
    """
    Create a new assignment.

    Args:
        db: Database session
        current_teacher: Current authenticated teacher
        obj_in: Assignment creation data

    Returns:
        Created assignment
    """
    try:
        # Create assignment
        assignment = await assignment_crud.create_assignment(
            db, obj_in=obj_in, teacher_id=current_teacher.id
        )

        logger.info(
            f"Assignment created with ID {assignment.id} by teacher {current_teacher.id}"
        )

        # Note: Template generation now requires a separate API call

        return assignment
    except Exception as e:
        logger.error(f"Error creating assignment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating assignment: {str(e)}",
        )


@router.get(
    "/assignments/{assignment_id}/template",
    response_model=TemplateGenerationResponse,
)
async def get_assignment_template(
    *,
    db: AsyncDbSession,
    current_teacher: CurrentTeacher,
    assignment_id: int,
) -> Any:
    """
    Generate or get an AI-generated template for an assignment.

    If the assignment already has a template, it will be returned.
    Otherwise, a new template will be generated but not saved to the database.

    Args:
        db: Database session
        current_teacher: Current authenticated teacher
        assignment_id: Assignment ID

    Returns:
        Generated template for teacher approval

    Raises:
        HTTPException: If assignment not found or does not belong to teacher
    """
    # Get assignment
    assignment = await assignment_crud.get_assignment(db, assignment_id)

    if not assignment:
        logger.warning(f"Assignment with ID {assignment_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found",
        )

    # Verify ownership
    if assignment.teacher_id != current_teacher.id:
        logger.warning(
            f"Teacher {current_teacher.id} attempted to access assignment {assignment_id} belonging to teacher {assignment.teacher_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    # Check if the assignment can be modified
    can_be_modified = await assignment_crud.check_can_modify_assignment(
        db, assignment_id
    )

    try:
        # Generate template or get existing one
        assignment, generated_template = await generate_template_for_approval(
            assignment_id, db
        )

        logger.info(
            f"Template generated/retrieved for assignment {assignment_id} by teacher {current_teacher.id}"
        )

        # Return template for teacher approval
        return TemplateGenerationResponse(
            assignment_id=assignment_id,
            title=assignment.title,
            generated_template=generated_template,
            can_be_modified=can_be_modified,
        )

    except Exception as e:
        logger.error(
            f"Error generating template for assignment {assignment_id}: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating template",
        )


@router.post(
    "/assignments/{assignment_id}/approve-template",
    response_model=AssignmentSchema,
)
async def approve_assignment_template(
    *,
    db: AsyncDbSession,
    current_teacher: CurrentTeacher,
    assignment_id: int,
    template_data: TemplateApprovalRequest,
) -> Any:
    """
    Approve or modify a generated template for an assignment.

    Args:
        db: Database session
        current_teacher: Current authenticated teacher
        assignment_id: Assignment ID
        template_data: Template approval data

    Returns:
        Updated assignment with approved template

    Raises:
        HTTPException: If assignment not found, does not belong to teacher,
                      or cannot be modified
    """
    # Verify assignment ID in path matches the one in request body
    if assignment_id != template_data.assignment_id:
        logger.warning(
            f"Mismatched assignment IDs: {assignment_id} in path vs {template_data.assignment_id} in body"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Assignment ID in path must match ID in request body",
        )

    # Get assignment
    assignment = await assignment_crud.get_assignment(db, assignment_id)

    if not assignment:
        logger.warning(f"Assignment with ID {assignment_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found",
        )

    # Verify ownership
    if assignment.teacher_id != current_teacher.id:
        logger.warning(
            f"Teacher {current_teacher.id} attempted to update assignment {assignment_id} belonging to teacher {assignment.teacher_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    try:
        # Save the approved template
        updated_assignment = await approve_correction_template(
            assignment_id, template_data.correction_template, db
        )

        logger.info(
            f"Template approved for assignment {assignment_id} by teacher {current_teacher.id}"
        )

        return updated_assignment

    except HTTPException:
        # Propagate HTTP exceptions from the service
        raise
    except Exception as e:
        logger.error(
            f"Error approving template for assignment {assignment_id}: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error saving template",
        )


@router.get("/assignments", response_model=List[AssignmentSchema])
async def get_teacher_assignments(
    db: AsyncDbSession,
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
    db: AsyncDbSession,
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
    db: AsyncDbSession,
    current_teacher: CurrentTeacher,
    assignment_id: int,
    obj_in: AssignmentUpdate,
) -> Any:
    """
    Update an assignment created by the current teacher.

    Args:
        db: Database session
        current_teacher: Current authenticated teacher
        assignment_id: Assignment ID
        obj_in: Assignment update data

    Returns:
        Updated assignment

    Raises:
        HTTPException: If assignment not found, does not belong to teacher,
                       or cannot be modified
    """
    assignment = await assignment_crud.get_assignment(db, assignment_id)

    if not assignment:
        logger.warning(f"Assignment with ID {assignment_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found",
        )

    if assignment.teacher_id != current_teacher.id:
        logger.warning(
            f"Teacher {current_teacher.id} attempted to update assignment {assignment_id} belonging to teacher {assignment.teacher_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    # Check if assignment can be modified (no submissions yet)
    if not await assignment_crud.check_can_modify_assignment(
        db, assignment_id
    ):
        logger.warning(
            f"Cannot modify assignment {assignment_id} with existing submissions"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot modify assignment with existing submissions",
        )

    # Extract update data
    update_data = obj_in.model_dump(exclude_unset=True)

    # If assignment instructions are being updated, remove any existing template
    if "assignment_instructions" in update_data:
        logger.info(
            f"Instructions updated for assignment {assignment_id}, clearing template"
        )
        update_data["correction_template"] = None

    try:
        # Update assignment
        updated_assignment = await assignment_crud.update_assignment(
            db, db_obj=assignment, obj_in=update_data
        )

        logger.info(
            f"Assignment {assignment_id} successfully updated by teacher {current_teacher.id}"
        )

        return updated_assignment
    except Exception as e:
        logger.error(f"Error updating assignment {assignment_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating assignment",
        )


@router.delete(
    "/assignments/{assignment_id}", response_model=AssignmentSchema
)
async def delete_assignment(
    *,
    db: AsyncDbSession,
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


@router.post(
    "/assignments/{assignment_id}/extend", response_model=AssignmentSchema
)
async def extend_assignment_deadline(
    *,
    db: AsyncDbSession,
    current_teacher: CurrentTeacher,
    assignment_id: int,
    extend_data: AssignmentDeadlineExtend,
) -> Any:
    """
    Extend the deadline of an assignment created by the current teacher.

    Args:
        db: Database session
        current_teacher: Current authenticated teacher
        assignment_id: Assignment ID
        extend_data: New deadline data

    Returns:
        Updated assignment

    Raises:
        HTTPException: If assignment not found, does not belong to teacher,
                       deadline is in the past, or assignment can't be modified
    """
    # Get the assignment
    assignment = await assignment_crud.get_assignment(db, assignment_id)

    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found",
        )

    # Check if the assignment belongs to the current teacher
    if assignment.teacher_id != current_teacher.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    # Check if the new deadline is in the future
    now = datetime.now(timezone.utc)
    if extend_data.deadline <= now:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Deadline must be in the future",
        )

    # Check if the assignment can be modified (implementation depends on your requirements)
    # Uncomment the following if needed:
    # if not await assignment_crud.check_can_modify_assignment(db, assignment_id):
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="Cannot modify this assignment",
    #     )

    # Update the assignment with the new deadline
    try:
        updated_assignment = await assignment_crud.update_assignment_deadline(
            db, assignment_id=assignment_id, deadline=extend_data.deadline
        )
        return updated_assignment
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update assignment: {str(e)}",
        )


@router.get(
    "/assignments/{assignment_id}/submissions",
    response_model=List[StudentAssignmentSchema],
)
async def get_assignment_submissions(
    *,
    db: AsyncDbSession,
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
    db: AsyncDbSession,
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
    db: AsyncDbSession,
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
    db: AsyncDbSession,
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
    db: AsyncDbSession,
    current_teacher: CurrentTeacher,
    student_id: uuid.UUID,
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


@router.post(
    "/assignments/{assignment_id}/submit",
    response_model=StudentAssignmentSchema,
)
async def submit_assignment(
    assignment_id: int,
    *,
    db: AsyncDbSession,
    current_student: CurrentStudent = Depends(get_current_student),
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
        logger.warning(
            f"Student attempted to submit to nonexistent assignment {assignment_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found",
        )

    if assignment.is_past_deadline:
        logger.warning(
            f"Student attempted to submit past deadline for assignment {assignment_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Assignment is past deadline",
        )

    # Check if student has already submitted
    existing_submission = await assignment_crud.get_student_assignment(
        db, assignment_id=assignment_id, student_id=current_student.id
    )

    if existing_submission:
        logger.warning(
            f"Student attempted to submit duplicate submission for assignment {assignment_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already submitted this assignment",
        )

    try:
        # Create student assignment submission
        student_assignment = await assignment_crud.create_student_assignment(
            db,
            obj_in=obj_in,
            student_id=current_student.id,
        )

        logger.info(
            f"Student {current_student.id} submitted assignment {assignment_id}"
        )

        # If auto-grading is enabled, queue it as a background task
        if (
            hasattr(assignment, "enable_auto_grading")
            and assignment.enable_auto_grading
        ):
            background_tasks.add_task(
                grade_student_assignment,
                student_assignment_id=student_assignment.id,
                db=db,
            )

        return student_assignment
    except ValueError as e:
        logger.error(f"Error submitting assignment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Unexpected error submitting assignment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit assignment",
        )


@router.post(
    "/assignments/{assignment_id}/submissions/{submission_id}/evaluate",
    response_model=StudentAssignmentSchema,
)
async def evaluate_student_submission(
    *,
    db: AsyncDbSession,
    current_teacher: CurrentTeacher,
    assignment_id: int,
    submission_id: int,
    obj_in: StudentAssignmentTeacherUpdate,
) -> Any:
    """
    Evaluate a student's assignment submission.

    Args:
        db: Database session
        current_teacher: Current authenticated teacher
        assignment_id: Assignment ID
        submission_id: Student assignment submission ID
        obj_in: Evaluation data including feedback and score

    Returns:
        Updated student assignment submission

    Raises:
        HTTPException: If submission not found, assignment not found,
                       or assignment does not belong to teacher
    """
    # Verify assignment exists and belongs to the teacher
    assignment = await assignment_crud.get_assignment(db, assignment_id)
    if not assignment:
        logger.warning(f"Assignment with ID {assignment_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found",
        )

    if assignment.teacher_id != current_teacher.id:
        logger.warning(
            f"Teacher {current_teacher.id} attempted to evaluate submission for assignment {assignment_id} belonging to teacher {assignment.teacher_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    # Get the student assignment
    from sqlalchemy import select
    from app.models import StudentAssignment

    query = select(StudentAssignment).where(
        StudentAssignment.id == submission_id,
        StudentAssignment.assignment_id == assignment_id,
    )

    result = await db.execute(query)
    student_assignment = result.scalar_one_or_none()

    if not student_assignment:
        logger.warning(
            f"Submission with ID {submission_id} not found for assignment {assignment_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found or does not belong to this assignment",
        )

    try:
        # Update the student assignment with teacher feedback and score
        student_assignment = (
            await assignment_crud.teacher_update_student_assignment(
                db, db_obj=student_assignment, obj_in=obj_in
            )
        )

        logger.info(
            f"Teacher {current_teacher.id} evaluated submission {submission_id} for assignment {assignment_id}"
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
    except ValueError as e:
        logger.error(f"Error evaluating submission: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Unexpected error evaluating submission: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to evaluate submission",
        )
