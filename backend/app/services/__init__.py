from app.services.assignment_service import (
    generate_correction_template,
    grade_student_assignment,
    generate_template_for_approval,
    approve_correction_template,
)

# Re-export for easier importing
__all__ = [
    "generate_correction_template",
    "grade_student_assignment",
    "generate_template_for_approval",
    "approve_correction_template",
]
