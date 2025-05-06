import requests
import json


def test_get_student_assignments():
    """
    Test getting available assignments for a student
    """
    # Base URL of the API
    base_url = "http://127.0.0.1:8000"
    endpoint = f"{base_url}/api/v1/students/assignments"

    # Login with the student (reusing the test student from submission)
    login_endpoint = f"{base_url}/api/v1/auth/login"
    student_email = "teststudent_submit@example.com"
    student_password = "student123"

    try:
        # Login with the student
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

        # Set headers with student token
        headers = {"Authorization": f"Bearer {student_token}"}

        # Make the request to get assignments
        # Include all assignments including past deadline
        params = {"include_past_deadline": True}

        response = requests.get(endpoint, headers=headers, params=params)

        # Print response details
        print(f"Status Code: {response.status_code}")
        print(
            "Response Headers:", json.dumps(dict(response.headers), indent=2)
        )

        if response.ok:
            print("Response Body:")
            response_data = response.json()
            print(json.dumps(response_data, indent=2))
            print(f"\nRetrieved {len(response_data)} assignments.")
        else:
            print(f"Error: {response.text}")

    except Exception as e:
        print(f"Request failed: {str(e)}")


if __name__ == "__main__":
    test_get_student_assignments()
