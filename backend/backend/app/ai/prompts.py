"""
Prompt templates for AI integrations.
"""

# Template for generating a correction template from assignment instructions
GENERATE_CORRECTION_TEMPLATE_PROMPT = """
You are an AI assistant helping a teacher create a grading template for an assignment.

Below are the assignment instructions written by the teacher. The assignment has a maximum score of {max_score} gold coins.

Your task is to create a detailed correction template that will be used to evaluate student submissions. The template should:

1. Identify the key requirements and criteria from the assignment instructions
2. Establish clear grading rubrics for each section
3. Specify how points (gold coins) should be allocated for meeting each requirement
4. Include specific evaluation questions that should be asked when grading

The correction template should be designed to help another AI evaluate student submissions consistently and fairly.

ASSIGNMENT INSTRUCTIONS:
{assignment_instructions}

Please create a detailed correction template that will enable consistent and fair grading of student submissions.
"""

# Template for grading a student assignment
GRADE_ASSIGNMENT_PROMPT = """
You are an AI assistant helping grade a student's assignment submission.

Below are:
1. The assignment instructions written by the teacher
2. A correction template with grading criteria
3. The student's submission

Your task is to evaluate the student's submission according to the correction template.

ASSIGNMENT INSTRUCTIONS:
{assignment_instructions}

CORRECTION TEMPLATE:
{correction_template}

STUDENT SUBMISSION:
{student_submission}

Based on the correction template, please evaluate the student's submission and provide a final score as an integer value out of {max_score}.

The output should only contain the numeric score (as an integer) without any additional text. For example: 8
"""

# Template for fallback if correction template is not available
SIMPLE_GRADE_ASSIGNMENT_PROMPT = """
You are an AI assistant helping grade a student's assignment submission.

Below are:
1. The assignment instructions written by the teacher
2. The student's submission

The assignment has a maximum score of {max_score} gold coins.

ASSIGNMENT INSTRUCTIONS:
{assignment_instructions}

STUDENT SUBMISSION:
{student_submission}

Please evaluate the student's submission according to the assignment instructions. Allocate points (gold coins) based on how well the student has met the requirements.

The output should only contain the numeric score (as an integer) without any additional text. For example: 8
"""
