import requests
import json


def test_login_success():
    """Test successful login with correct credentials"""
    response = requests.post(
        "http://localhost:8000/api/login",
        json={"email": "user@example.com", "password": "password123"},
    )
    print("Success test:", response.status_code)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    print("Success test passed!")


def test_login_wrong_password():
    """Test login with wrong password"""
    response = requests.post(
        "http://localhost:8000/api/login",
        json={"email": "user@example.com", "password": "wrongpassword"},
    )
    print("Wrong password test:", response.status_code)
    assert response.status_code == 401
    print("Wrong password test passed!")


def test_login_nonexistent_user():
    """Test login with nonexistent user"""
    response = requests.post(
        "http://localhost:8000/api/login",
        json={"email": "nonexistent@example.com", "password": "password123"},
    )
    print("Nonexistent user test:", response.status_code)
    assert response.status_code == 401
    print("Nonexistent user test passed!")


if __name__ == "__main__":
    print("Running API tests...")
    test_login_success()
    test_login_wrong_password()
    test_login_nonexistent_user()
    print("All tests passed!")
