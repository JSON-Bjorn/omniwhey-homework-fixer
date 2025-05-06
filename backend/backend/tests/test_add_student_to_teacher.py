import requests
import json


def test_add_student_to_teacher():
    """
    Test adding a student to a teacher's class
    """
    # Base URL of the API
    base_url = "http://127.0.0.1:8000"
    endpoint = f"{base_url}/api/v1/teachers/students/add"

    # Try to read teacher token from file
    try:
        with open("token.txt", "r") as f:
            token = f.read().strip()
    except FileNotFoundError:
        print(
            "Error: No authentication token found. Please run test_auth_login.py first."
        )
        return

    # First, we need to get the student ID
    # For this, we'll fetch all users and find our test student

    try:
        # 1. Login with the student to make sure it exists
        login_endpoint = f"{base_url}/api/v1/auth/login"
        student_email = "teststudent_submit@example.com"
        student_password = "student123"

        login_data = {"username": student_email, "password": student_password}

        login_response = requests.post(
            login_endpoint,
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        if not login_response.ok:
            print(f"Student login failed: {login_response.text}")
            print("Creating a new student instead...")

            # Create a new student
            register_endpoint = f"{base_url}/api/v1/auth/register/student"
            register_data = {
                "email": student_email,
                "name": "Test Student for Class",
                "password": student_password,
                "role": "student",
            }

            register_response = requests.post(
                register_endpoint,
                json=register_data,
                headers={"Content-Type": "application/json"},
            )

            if not register_response.ok:
                print(
                    f"Student registration failed: {register_response.text}"
                )
                return

            student_data = register_response.json()
            student_id = student_data["id"]
            print(f"New student created with ID: {student_id}")
        else:
            # We need to get the student ID
            # But we can't directly get it from the login response
            # For simplicity, we'll assume student ID is 2 (first registered student)
            student_id = 2
            print(f"Using existing student with assumed ID: {student_id}")

        # 2. Add the student to the teacher's class
        add_data = {"student_ids": [student_id]}

        # Set headers with authentication token
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }

        # Make the request
        response = requests.post(endpoint, json=add_data, headers=headers)

        # Print response details
        print(f"Status Code: {response.status_code}")
        print(
            "Response Headers:", json.dumps(dict(response.headers), indent=2)
        )

        if response.ok:
            print("Response Body:")
            response_data = response.json()
            print(json.dumps(response_data, indent=2))
            print(
                f"\nAdded {len(response_data)} student(s) to teacher's class."
            )
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Request failed: {str(e)}")


if __name__ == "__main__":
    test_add_student_to_teacher()
