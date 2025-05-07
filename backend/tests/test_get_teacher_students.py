import requests
import json


def test_get_teacher_students():
    """
    Test getting the list of students for a teacher
    """
    # Base URL of the API
    base_url = "http://127.0.0.1:8000"
    endpoint = f"{base_url}/api/v1/teachers/students"

    # Try to read teacher token from file
    try:
        with open("token.txt", "r") as f:
            token = f.read().strip()
    except FileNotFoundError:
        print(
            "Error: No authentication token found. Please run test_auth_login.py first."
        )
        return

    # Set headers with authentication token
    headers = {"Authorization": f"Bearer {token}"}

    # Make the request
    try:
        response = requests.get(endpoint, headers=headers)

        # Print response details
        print(f"Status Code: {response.status_code}")
        print(
            "Response Headers:", json.dumps(dict(response.headers), indent=2)
        )

        if response.ok:
            print("Response Body:")
            response_data = response.json()
            print(json.dumps(response_data, indent=2))
            print(f"\nRetrieved {len(response_data)} students.")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Request failed: {str(e)}")


if __name__ == "__main__":
    test_get_teacher_students()
