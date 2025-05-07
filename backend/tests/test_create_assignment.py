import requests
import json
import datetime
import os


def test_create_assignment():
    """
    Test creating a new assignment as a teacher
    """
    # Base URL of the API
    base_url = "http://127.0.0.1:8000"
    endpoint = f"{base_url}/api/v1/teachers/assignments"

    # Try to read token from file
    try:
        with open("token.txt", "r") as f:
            token = f.read().strip()
    except FileNotFoundError:
        print(
            "Error: No authentication token found. Please run test_auth_login.py first."
        )
        return

    # Set deadline to tomorrow
    deadline = (
        datetime.datetime.now() + datetime.timedelta(days=1)
    ).isoformat()

    # Prepare assignment data
    assignment_data = {
        "title": "Test Assignment",
        "assignment_instructions": """
        # Python Basics Test
        
        Write a function that takes two numbers as input and returns their sum.
        
        ## Requirements:
        1. The function should be named `add_numbers`
        2. It should accept two parameters: `a` and `b`
        3. It should return the sum of `a` and `b`
        4. Include proper docstrings
        
        ## Scoring (10 gold coins total):
        - Correct function name: 2 coins
        - Proper parameters: 2 coins
        - Correct calculation: 2 coins
        - Proper docstring: 2 coins
        - Clean code formatting: 2 coins
        """,
        "max_score": 10,
        "deadline": deadline,
    }

    # Set headers with authentication token
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }

    # Make the request
    try:
        response = requests.post(
            endpoint, json=assignment_data, headers=headers
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
            print("\nAssignment creation successful!")

            # Save assignment id for future tests
            if "id" in response_data:
                with open("assignment_id.txt", "w") as f:
                    f.write(str(response_data["id"]))
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Request failed: {str(e)}")


if __name__ == "__main__":
    test_create_assignment()
