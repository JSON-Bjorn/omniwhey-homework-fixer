import requests
import json
import os


def test_submit_assignment():
    """
    Test submitting an assignment as a student
    """
    # Base URL of the API
    base_url = "http://127.0.0.1:8000"
    endpoint = f"{base_url}/api/v1/students/submit"

    # First, we need to get the student token
    # For this test, we'll first register a student and then log in with that student

    # 1. Register a student
    register_endpoint = f"{base_url}/api/v1/auth/register/student"
    student_email = "teststudent_submit@example.com"
    student_password = "student123"

    register_data = {
        "email": student_email,
        "name": "Test Student for Submission",
        "password": student_password,
        "role": "student",
    }

    try:
        # First, try to register the student
        register_response = requests.post(
            register_endpoint,
            json=register_data,
            headers={"Content-Type": "application/json"},
        )

        # If registration fails with 400, it's probably because the user already exists
        # We'll proceed to login

        # 2. Login with the student
        login_endpoint = f"{base_url}/api/v1/auth/login"
        login_data = {"username": student_email, "password": student_password}

        login_response = requests.post(
            login_endpoint,
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        if not login_response.ok:
            print(f"Student login failed: {login_response.text}")
            return

        student_token = login_response.json()["access_token"]
        print("Student authenticated successfully!")

        # 3. Try to read assignment ID from file
        try:
            with open("assignment_id.txt", "r") as f:
                assignment_id = f.read().strip()
        except FileNotFoundError:
            print(
                "Error: No assignment ID found. Please run test_create_assignment.py first."
            )
            return

        # 4. Submit the assignment
        submission_data = {
            "assignment_id": int(assignment_id),
            "submission_text": """
            def add_numbers(a, b):
                \"\"\"
                Add two numbers and return the result.
                
                Args:
                    a: First number
                    b: Second number
                    
                Returns:
                    The sum of a and b
                \"\"\"
                return a + b
            """,
        }

        # Set headers with student token
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {student_token}",
        }

        # Make the submit request
        response = requests.post(
            endpoint, json=submission_data, headers=headers
        )

        # Print response details
        print(f"\nSubmission Status Code: {response.status_code}")
        print(
            "Response Headers:", json.dumps(dict(response.headers), indent=2)
        )

        if response.ok:
            print("Response Body:")
            response_data = response.json()
            print(json.dumps(response_data, indent=2))
            print("\nAssignment submission successful!")
        else:
            print(f"Error: {response.text}")

    except Exception as e:
        print(f"Request failed: {str(e)}")


if __name__ == "__main__":
    test_submit_assignment()
