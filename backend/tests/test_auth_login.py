import requests
import json


def test_login():
    """
    Test user login endpoint to retrieve an authentication token
    """
    # Base URL of the API
    base_url = "http://127.0.0.1:8000"
    endpoint = f"{base_url}/api/v1/auth/login"

    # Prepare login data
    # These would be the credentials for the admin user created
    # during database initialization
    login_data = {
        "username": "admin@example.com",
        "password": "adminpassword123",
    }

    # Set headers for form data
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    # Make the request
    try:
        response = requests.post(endpoint, data=login_data, headers=headers)

        # Print response details
        print(f"Status Code: {response.status_code}")
        print(
            "Response Headers:", json.dumps(dict(response.headers), indent=2)
        )

        if response.ok:
            print("Response Body:")
            response_data = response.json()
            print(json.dumps(response_data, indent=2))

            # Save token for use in other tests
            if "access_token" in response_data:
                print("\nAccess token successfully obtained!")
                token = response_data["access_token"]
                # Save token in current directory
                with open("token.txt", "w") as f:
                    f.write(token)
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Request failed: {str(e)}")


if __name__ == "__main__":
    test_login()
