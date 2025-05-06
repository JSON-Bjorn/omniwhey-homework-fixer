from app.services.assignment_service import (
    generate_correction_template,
    grade_student_assignment,
)

# Re-export for easier importing
__all__ = [
    "generate_correction_template",
    "grade_student_assignment",
]
