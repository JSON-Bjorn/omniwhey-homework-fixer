# API Test Scripts

This directory contains test scripts for testing the API endpoints of the Omniwhey Homework Fixer application.

## Requirements

Before running these tests, make sure you have:

1. The FastAPI application running (`python -m uvicorn app.main:app --reload`)
2. The required Python libraries installed:
   ```
   pip install requests
   ```

## Test Order

The test scripts should be run in the following order to ensure proper dependencies:

1. `test_auth_login.py` - Logs in as admin and saves the auth token for other tests
2. `test_register_student.py` - Registers a new student
3. `test_add_student_to_teacher.py` - Adds the student to the teacher's class
4. `test_create_assignment.py` - Creates a new assignment as the teacher
5. `test_get_teacher_students.py` - Gets the teacher's students
6. `test_submit_assignment.py` - Submits an assignment as the student
7. `test_get_student_assignments.py` - Gets the student's available assignments
8. `test_get_student_submissions.py` - Gets the student's submitted assignments

## Running the Tests

Run each test individually from the command line:

```bash
# First, make sure the API server is running
# From the project root:
python -m uvicorn app.main:app --reload

# In a separate terminal, navigate to the tests directory
cd tests

# Run the tests in the recommended order
python test_auth_login.py
python test_register_student.py
# ... and so on
```

## Test Files

- `test_auth_login.py` - Tests the login endpoint and saves token to current directory
- `test_register_student.py` - Tests student registration
- `test_add_student_to_teacher.py` - Tests adding a student to teacher's class
- `test_create_assignment.py` - Tests creating a new assignment and saves assignment ID
- `test_get_teacher_students.py` - Tests retrieving teacher's students
- `test_submit_assignment.py` - Tests submitting an assignment
- `test_get_student_assignments.py` - Tests retrieving available student assignments
- `test_get_student_submissions.py` - Tests retrieving student's submitted assignments

## Generated Files

During test runs, the scripts will create the following files in the current directory:
- `token.txt` - Contains the authentication token for the admin/teacher user
- `assignment_id.txt` - Contains the ID of the created assignment

## Important Notes

- These tests are designed to be run against a fresh database, but they will also work with an existing database.
- Some tests depend on others (e.g., submitting an assignment requires an assignment to exist first).
- The script may occasionally use assumed IDs for entities when it's not practical to retrieve them dynamically. 