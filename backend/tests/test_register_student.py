import requests
import json
import uuid


def test_register_student():
    """
    Test student registration endpoint
    """
    # Base URL of the API
    base_url = "http://127.0.0.1:8000"
    endpoint = f"{base_url}/api/v1/auth/register/student"

    # Generate a unique email to avoid conflicts with existing users
    unique_id = uuid.uuid4().hex[:6]
    email = f"student_{unique_id}@example.com"

    # Prepare registration data
    registration_data = {
        "email": email,
        "name": f"Test Student {unique_id}",
        "password": "student123",
        "role": "student",
    }

    # Set headers
    headers = {"Content-Type": "application/json"}

    # Make the request
    try:
        response = requests.post(
            endpoint, json=registration_data, headers=headers
        )

        # Print response details
        print(f"Status Code: {response.status_code}")
        print(
            "Response Headers:", json.dumps(dict(response.headers), indent=2)
        )

        if response.ok:
            print("Response Body:")
            response_data = response.json()
            print(json.dumps(response_data, indent=2))
            print("\nStudent registration successful!")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Request failed: {str(e)}")


if __name__ == "__main__":
    test_register_student()
